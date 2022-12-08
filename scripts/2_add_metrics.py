import os
import sys
import json
import csv
import logging
import argparse
from typing import *
import torch
import bert_score
import warnings

from rouge_score import rouge_scorer

from sentence_transformers import SentenceTransformer, util

from ms2.models.evidence_inference_models import initialize_models
from ms2.evaluation.utils import clean, entailment_scores


DATASET = 'Cochrane'
METRICS_TO_COMPUTE = {
    'rouge',
    'bertscore',
    'ei_divergence',
    'nli',
    'sts',
    'claimver'
}

device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

if os.path.exists('config.json'):
    CONFIG = json.load(open('config.json', 'r'))


def calculate_rouge(targets: List[str], generated: List[str]) -> Dict:
    logging.info(f"Computing ROUGE...")
    rouge_types = ["rouge1", "rouge2", "rougeL", "rougeLsum"]
    scorer = rouge_scorer.RougeScorer(rouge_types=rouge_types, use_stemmer=False)
    
    rouge_vals = []
    for ref, pred in zip(targets, generated):
        score = scorer.score(ref, pred)
        rouge_vals.append(score)
        
    rouge_results = {}
    for key in rouge_vals[0]:
        rouge_results[key+'_p'] = [val[key].precision for val in rouge_vals]
        rouge_results[key+'_r'] = [val[key].recall for val in rouge_vals]
        rouge_results[key+'_f'] = [val[key].fmeasure for val in rouge_vals]
        
    return rouge_results


def calculate_bertscore(targets: List[str], generated: List[str], model_type="roberta-large") -> Dict:
    logging.info(f"Computing BERTscore...")
    bs_ps, bs_rs, bs_fs = bert_score.score(generated, targets, model_type=model_type)
    return {
        "bertscore_p": list(bs_ps.numpy()),
        "bertscore_r": list(bs_rs.numpy()),
        "bertscore_f": list(bs_fs.numpy())
    }


def calculate_evidence_inference_divergence(
        targets: List[str],
        generated: List[str],
        prefaces: List[str],
        ei_param_file: str = CONFIG['ei_param_file'],
        ei_model_dir: str = CONFIG['ei_model_dir'],
        ei_use_unconditional: bool = False
) -> Dict:
    logging.info(f"Computing Delta Evidence Inference scores...")
    targets = list(map(clean, targets))
    generated = list(map(clean, generated))
    prefaces = list(map(clean, prefaces))

    # evidence inference scoring
    with open(ei_param_file, 'r') as inf:
        params = json.loads(inf.read())
    _, evidence_inference_classifier, _, _, _, evidence_inference_tokenizer = initialize_models(params)
    if ei_use_unconditional:
        classifier_file = os.path.join(ei_model_dir, 'unconditioned_evidence_classifier', 'unconditioned_evidence_classifier.pt')
    else:
        classifier_file = os.path.join(ei_model_dir, 'evidence_classifier', 'evidence_classifier.pt')
    #evidence_inference_classifier.load_state_dict(torch.load(classifier_file))
    # pooler parameters are added by default in an older transformers, so we have to ignore that those are uninitialized.
    evidence_inference_classifier.load_state_dict(torch.load(classifier_file, map_location=device), strict=False)
    if torch.cuda.is_available():
        evidence_inference_classifier.cuda()

    entailment_results = entailment_scores(
        evidence_inference_classifier, evidence_inference_tokenizer,
        generated, targets, prefaces,
        use_ios=ei_use_unconditional
    )

    return entailment_results


def calculate_sts(
    name: str,
    targets: List[str],
    generated: List[str],
    model_name: str = 'stsb-roberta-base-v2'
):
    model = SentenceTransformer(model_name)

    #Compute embeddings
    target_embeddings = model.encode(targets)
    generated_embeddings = model.encode(generated)
    
    #Pairwise cosine
    scores = []
    for tembed, gembed in zip(target_embeddings, generated_embeddings):
        cosine_score = util.cos_sim([tembed], [gembed])
        scores.append(cosine_score.numpy()[0][0])
        
    return {name: scores}
        

def calculate_scientific_claim_verification(
    targets: List[str],
    generated: List[str],
):
    raise NotImplementedError("Not implemented!")


if __name__ == '__main__':
    # read data
    data = []
    with open('data/processed_data.json', 'r') as f:
        for row in f:
            data.append(json.loads(row))
            
    review_ids = []
    exp_shorts = []
    target_summaries = []
    generated_summaries = []
    
    for entry in data:
        for pred in entry['predictions']:
            review_ids.append(entry['review_id'])
            exp_shorts.append(pred['exp_short'])
            target_summaries.append(entry['target'])
            generated_summaries.append(pred['prediction'])
    
    score_dict = {}
    for metric_name in METRICS_TO_COMPUTE:
        if metric_name == 'rouge':
            scores = calculate_rouge(target_summaries, generated_summaries)
        elif metric_name == 'bertscore':
            scores = calculate_bertscore(target_summaries, generated_summaries)
        elif metric_name == 'ei_divergence':
            # TODO: fix
            scores = calculate_evidence_inference_divergence(target_summaries, generated_summaries, target_summaries)
        elif metric_name == 'nli':
            scores = calculate_sts('nli', target_summaries, generated_summaries, 'nli-roberta-base-v2')
        elif metric_name == 'sts':
            scores = calculate_sts('sts', target_summaries, generated_summaries, 'stsb-roberta-base-v2')
        elif metric_name == 'claimver':
            # scores = calculate_scientific_claim_verification(target_summaries, generated_summaries)
            scores = calculate_sts('claimver', target_summaries, generated_summaries, 'pritamdeka/S-PubMedBert-MS-MARCO-SCIFACT')
        else:
            raise NotImplementedError("Unknown metric!")
        score_dict[metric_name] = scores
        
    # add metric to data
    metric_list = [{} for i in range(len(generated_summaries))]
    for metric_name, scores in score_dict.items():
        for key, scores in scores.items():
            for i, score in enumerate(scores):
                metric_list[i][key] = score
    
    # insert metrics into main data dicts
    index = 0
    for entry in data:
        for pred in entry['predictions']:
            if pred.get('prediction'):
                pred['scores'] = metric_list[index]
                index += 1
       
    # write to file         
    with open('data/processed_data_w_metrics.json', 'w') as outf:
        for entry in data:
            json.dump(entry, outf)
            outf.write('\n')
            
    print('done.')
        