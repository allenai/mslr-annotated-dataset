import os
import json
import csv
from collections import defaultdict, Counter
import itertools
from pprint import pprint
import random

OUTPUT_DIR = '../data/Pairwise/'

if __name__ == '__main__':
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # read data
    data = []
    with open('../data/processed_data.json', 'r') as f:
        for line in f:
            data.append(json.loads(line))
            
    with open('../data/submission_info.json', 'r') as f:
        submissions = json.load(f)

    # extract entries
    predictions = []
    for d in data:
        if d['subtask'] != 'Cochrane':
            continue
        for pred in d['predictions']:
            entry = {
                'review_id': d['review_id'],
                'target': d['target'],
                'exp_id': pred['exp_short'],
                'generated': pred['prediction'],
                'annotators': [annot['annot_id'] for annot in pred['annotations']]
            }
            predictions.append(entry)
            
    # keep just the systems included in faceted annotation (5 models + 1 baseline on cochrane subtask)
    keep_systems = set([entry['exp_id'] for entry in predictions if entry['annotators']])
    predictions = [entry for entry in predictions if entry['exp_id'] in keep_systems]     
                
    # lookup dict by review_id
    by_rev_id = defaultdict(list)
    for entry in predictions:
        by_rev_id[entry['review_id']].append({
            'exp_id': entry['exp_id'],
            'target': entry['target'],
            'generated': entry['generated'],
            'annotators': entry['annotators']
        })
        
    # number of annotations
    print('Number of annotations per review_id')
    num_annots = Counter([sum([bool(v['annotators']) for v in val]) for val in by_rev_id.values()])
    print(num_annots.most_common())
        
    # create all possible pairwise comparisons
    pop_to_sample = []
    for rev_id, entries in by_rev_id.items():
        for e1, e2 in itertools.combinations(entries, 2):
            if e1['target'] != e2['target']:
                print('Target mismatch!')
                break
            pop_to_sample.append({
                'review_id': rev_id,
                'target': e1['target'],
                'exp_pair': list(sorted([e1['exp_id'], e2['exp_id']])),
                'exp1': e1['exp_id'],
                'exp1_generated': e1['generated'],
                'exp2': e2['exp_id'],
                'exp2_generated': e2['generated'],
                'both_annotated': bool(e1['annotators']) and bool(e2['annotators'])
            })
            
    print('Number of pairwise comparisons: ', len(pop_to_sample))
    print()
    
    print('Distribution of annotations: ') 
    distro_annotation = Counter([inst['both_annotated'] for inst in pop_to_sample])
    print(distro_annotation)
    print()

    print('Distribution by experiment pair:')
    pair_annotation = Counter([(
        inst['exp_pair'][0], inst['exp_pair'][1], inst['both_annotated']
        ) for inst in pop_to_sample
    ])
    pprint(pair_annotation.most_common())
    print()

    # stratified sampling
    full_sample = []
    target_n = 30
    for e1, e2, annot_true in pair_annotation.keys():
        matches = [
            pair for pair in pop_to_sample 
            if pair['exp_pair'] == [e1, e2]
            and pair['both_annotated'] == annot_true
        ] 
        samp = random.sample(matches, min(target_n, len(matches)))
        for s in samp:
            coin_toss = random.randint(0, 1)
            if coin_toss == 0:
                full_sample.append(s)
            else:
                # swap order
                full_sample.append({
                    'review_id': s['review_id'],
                    'target': s['target'],
                    'exp_pair': [s['exp2'], s['exp1']],
                    'exp1': s['exp2'],
                    'exp1_generated': s['exp2_generated'],
                    'exp2': s['exp1'],
                    'exp2_generated': s['exp1_generated'],
                    'both_annotated': s['both_annotated']
                })
                
    print('Number of sampled comparisons: ', len(full_sample))
    print()
    
    print('Distribution of annotations: ') 
    distro_annotation = Counter([inst['both_annotated'] for inst in full_sample])
    print(distro_annotation)
    print()

    print('Distribution by experiment pair:')
    pair_annotation = Counter([f"{inst['exp1']}_{inst['exp2']}" for inst in full_sample])
    pprint(pair_annotation)
    print()

    # randomly shuffle and write to file
    random.shuffle(full_sample)
    num_annotators = 8
    
    target_per_annotator = 200
    header_keys = ['review_id', 'target', 'exp1', 'exp1_generated', 'exp2', 'exp2_generated']
    header_names = ['review_id', 'target', 'sys_a', 'A', 'sys_b', 'B']
    samp_distros = []
    for i in range(num_annotators):
        print(f'Sampling for annot {i}')
        samp_to_file = random.sample(full_sample, target_per_annotator)
        samp_distro_annot = Counter([inst['both_annotated'] for inst in samp_to_file])
        samp_pair_annot = Counter([f"{'_'.join(sorted([inst['exp1'], inst['exp2']]))}" for inst in samp_to_file])
        samp_distros.append([samp_distro_annot, samp_pair_annot])
        with open(os.path.join(OUTPUT_DIR, f'sample{i}.csv'), 'w') as outf:
            writer = csv.writer(outf, delimiter=',', quotechar='"')
            writer.writerow(header_names)
            for row in samp_to_file:
                writer.writerow([row[k] for k in header_keys])
    print()
    
    distro_annots = [d[0] for d in samp_distros]
    keys = distro_annots[0].keys()
    print('key' + '\t' + '\t'.join([str(i) for i in range(num_annotators)]))
    print('-'*70)
    for k in keys:
        print(str(k) + '\t' + '\t'.join([str(d[k]) for d in distro_annots]))
    print()
    
    pair_annots = [d[1] for d in samp_distros]
    keys = pair_annots[0].keys()
    print('key' + '\t\t' + '\t'.join([str(i) for i in range(num_annotators)]))
    print('-'*80)
    for k in keys:
        print(str(k) + '\t' + '\t'.join([str(p[k]) for p in pair_annots]))
    
    print('done.')