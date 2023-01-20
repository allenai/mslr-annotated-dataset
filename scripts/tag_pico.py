from tabnanny import check
from re import I
from transformers import AutoTokenizer, pipeline,  AutoModelForTokenClassification

import spacy
import pandas as pd
from tqdm import tqdm
nlp = spacy.load("en_core_web_sm")

import time


def init_pipeline(model_name):
	tokenizer = AutoTokenizer.from_pretrained(model_name, model_max_length=128)
	model = AutoModelForTokenClassification.from_pretrained(model_name)
	nerpipeline = pipeline('ner', model=model, tokenizer=tokenizer,ignore_labels = ['O'], device = 0)
	# nerpipeline = pipeline('ner', model=model, tokenizer=tokenizer,ignore_labels = [], device = 0)

	return nerpipeline


def tag_sentence(nerpipeline,sent):
    ret = nerpipeline(sent)
    ret = nerpipeline.group_entities(ret)
    # ret = normalize_span(ret)
    return ret

def normalize_span(ret):
    spans = []
    for span in ret:
        label = span['entity_group']
        text = span['word']
        text = text.strip('.')
        text = text.strip(',')
        if text == '':
            continue
        spans.append((text,label))

    spans = set(spans)
    return spans



def tag_document(nerpipeline,doc):
    doc = nlp(doc)
    sents = []
    for sent in doc.sents:
        spans = tag_sentence(nerpipeline, sent.text)
        # ret = prepare_input(text, spans)
        for span in spans:
            sents.append(span)
    sents = normalize_span(sents)
    return sents

def tag_corpus(nerpipeline,corpus_path):

    corpus = pd.read_json(corpus_path, lines= True)

    rows = []
    for i, row in corpus.iterrows():
        target_ents = tag_document(nerpipeline,row['target'])
        row['target_entities'] = target_ents
        # print(row['target'])
        # print(target_ents)
        for j,prediction in enumerate(row['predictions']):
            pred_ents = tag_document(nerpipeline,prediction['prediction'])
            row['predictions'][j]['entities'] = pred_ents
            # print(prediction['prediction'])
            # print(pred_ents)
        rows.append(row)
        # break
    df_with_ent = pd.DataFrame(data = rows)
    file_name = corpus_path.replace('.json','_pico.json')
    df_with_ent.to_json(file_name, orient = 'records', lines = True)


if __name__=='__main__':
	model_name = 'joey234/BioLinkBERT-base-EBMNLP'
	pipeline = init_pipeline(model_name)
	tag_corpus(pipeline,'../processed_data_w_metrics_w_anns.json')