# MSLR annotation results

## Submissions

All submission files to the shared task are in `submissions/` split by subtask. The names of files are the system identifiers assigned by AI2 leaderboard. The last 6 digits are used to identify the systems in the processed data files. 

Metadata about submissions are available in `submissions/mslr-public-submissions.csv`

## Data

### Main annotation

From the Cochrane test split, we sampled 100 instances for 5 top-performing models and 1 baseline. Overlap occurs for 50 instances to assess IAA.

The models annotated were:

```
'SciSpace'
'led-base-16384-cochrane'
'bart-large-finetuned'
'ittc1'
'ittc2'
'AI2/BART/train Cochrane/decode Cochrane' (baseline)
```

The pilot was conducted on MS^2, and is between the two baseline models.

### Annotation results

Annotations for MSLR shared task: `data/Annotations/`

Annotations for MSLR pilot: `data/Pilot/`

### Data preprocessing

All test entries, annotations, and automated metrics are combined into a single file: `data/processed_data_w_metrics.json`. The scripts for creating this file are in `scripts/`.

#### `0_download_submissions.py` is used to download submission data from Beaker.

#### `1_reorg_data.py` reorganizes all data and appends submissions and annotations. This outputs `data/processed_data.json`.

Here is the annotation key:

```python
ANSWER_KEYS = {
    'Is the generated summary fluent?': {
        2: ['2: Yes--there are no errors that impact comprehension of the summary'],
        1: ['1: Somewhat--there are some grammatical or lexical errors but I can understand the meaning'],
        0: ['0: No--there are major grammatical or lexical errors that impact comprehension']
    },
    'Is the *population* in the generated summary the same as the population in the target summary?': {
        0: ['0: No'],
        1: ['1: Partially'],
        2: ['2: Yes']
    },
    'Is the *intervention* in the generated summary the same as the intervention in the target summary?': {
        0: ['0: No'],
        1: ['1: Partially'],
        2: ['2: Yes']
    },
    'Is the *outcome* in the generated summary the same as the outcome in the target summary?': {
        0: ['0: No'],
        1: ['1: Partially'],
        2: ['2: Yes']
    },
    'What is the effect direction in the *target* summary?': {
        2: ['(+1): Positive effect'],
        1: ['0: No effect'],
        0: ['(-1): Negative effect'],
        -1: ['N/A: no effect direction is specified in the target summary']
    },
    'What is the effect direction in the *generated* summary?': {
        2: ['(+1): Positive effect'],
        1: ['0: No effect'],
        0: ['(-1): Negative effect'],
        -1: ['N/A: no effect direction is specified in the generated summary']
    },
    'What is the strength of the claim made in the *target* summary?': {
        3: ['3: Strong claim'],
        2: ['2: Moderate claim'],
        1: ['1: Weak claim'],
        0: ['0: Not enough evidence (there is insufficient evidence to draw a conclusion)']
    },
    'What is the strength of the claim made in the *generated* summary?': {
        3: ['3: Strong claim'],
        2: ['2: Moderate claim'],
        1: ['1: Weak claim'],
        0: ['0: Not enough evidence (there is insufficient evidence to draw a conclusion)']
    }
}
```

These correspond to `fluency`, `population`, `intervention`, `outcome`, `ed_target`, `ed_generated`, `strength_target`, and `strength_generated` in the output annotation dicts, as in:

```python
ANNOT_KEYS = {
    'fluency': 'Is the generated summary fluent?',
    'population': 'Is the *population* in the generated summary the same as the population in the target summary?',
    'intervention': 'Is the *intervention* in the generated summary the same as the intervention in the target summary?',
    'outcome': 'Is the *outcome* in the generated summary the same as the outcome in the target summary?',
    'ed_target': 'What is the effect direction in the *target* summary?',
    'ed_generated': 'What is the effect direction in the *generated* summary?',
    'strength_target': 'What is the strength of the claim made in the *target* summary?',
    'strength_generated': 'What is the strength of the claim made in the *generated* summary?',
}
```


#### `2_add_metrics.py` adds automated mtrics to the processed data file. This outputs `data/processed_data_w_metrics.json`.

The current metrics are:

- rouge (R1, R2, RL, RLsum and P, R, F associated with each)
- bertscore (P, R, F)
- ei_divergence
- nli (cosine similarity from SBERT); model: `nli-roberta-base-v2`
- sts (cosine similarity from SBERT); model: `stsb-roberta-base-v2`
- claimver (cosine similarity from SBERT); model: `pritamdeka/S-PubMedBert-MS-MARCO-SCIFACT` (Note: this isn't the SciFact MultiVers model, that might be better...)

## Analysis

The dataset you should use is `data/processed_data_w_metrics.json`. Each line of this file is an entry like follows:

```python
{'subtask': 'Cochrane',
 'review_id': 'CD000220',
 'target': 'Metronidazole, given as a single dose, is likely to provide parasitological cure for trichomoniasis, but it is not known whether this treatment will have any effect on pregnancy outcomes. The cure rate could probably be higher if more partners used the treatment.',
 'predictions': [{'exp_short': 'SPNXTA',
   'prediction': 'Treatment of asymptomatic trichomoniasis with metronidazole 48 hours or 48 hours apart does not prevent preterm birth in women with trichomiasis. However, it does reduce the risk of caesarean section and the time of birth. [Note: The four citations in the awaiting classification section may alter the conclusions of the review once assessed.]',
   'annotations': [{'annot_id': 0,
     'annot_task': 'main',
     'fluency': 1,
     'population': 2,
     'intervention': 2,
     'outcome': 1,
     'ed_target': 2,
     'ed_generated': 2,
     'strength_target': 2,
     'strength_generated': 2,
     'ed_agree': True,
     'strength_agree': True}],
   'scores': {'bertscore_p': 0.8111618161201477,
    'bertscore_r': 0.8303713202476501,
    'bertscore_f': 0.8206541538238525,
    'rouge1_p': 0.2553191489361702,
    'rouge1_r': 0.375,
    'rouge1_f': 0.3037974683544304,
    'rouge2_p': 0.0,
    'rouge2_r': 0.0,
    'rouge2_f': 0.0,
    'rougeL_p': 0.10638297872340426,
    'rougeL_r': 0.15625,
    'rougeL_f': 0.12658227848101267,
    'rougeLsum_p': 0.10638297872340426,
    'rougeLsum_r': 0.15625,
    'rougeLsum_f': 0.12658227848101267,
    'ei_score': 0.5488429600021912,
    'claimver': 0.3884240388870239,
    'sts': 0.30865687131881714,
    'nli': 0.48122090101242065}},
  {'exp_short': '6GBRY0',
   'prediction': 'Routine screening and treatment of asymptomatic pregnant women for this condition cannot be recommended. The birth weights and gestational age at delivery were similar in all three groups.',
   'annotations': [],
   'scores': {'bertscore_p': 0.8368433713912964,
    'bertscore_r': 0.8643536567687988,
    'bertscore_f': 0.8503761291503906,
    'rouge1_p': 0.1320754716981132,
    'rouge1_r': 0.16666666666666666,
    'rouge1_f': 0.14736842105263157,
    'rouge2_p': 0.0,
    'rouge2_r': 0.0,
    'rouge2_f': 0.0,
    'rougeL_p': 0.07547169811320754,
    'rougeL_r': 0.09523809523809523,
    'rougeL_f': 0.08421052631578949,
    'rougeLsum_p': 0.07547169811320754,
    'rougeLsum_r': 0.09523809523809523,
    'rougeLsum_f': 0.08421052631578949,
    'ei_score': 0.37089626717063295,
    'claimver': 0.6722995638847351,
    'sts': 0.6493898034095764,
    'nli': 0.7216427326202393}}]}
```

All model predictions are available under the `predictions` key. If annotations are available, they are under the `annotations` key associated with each prediction. Same for scores (which should be available for every prediction).

TBD; some starter notebooks in `notebooks`
