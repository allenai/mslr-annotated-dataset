# MSLR annotation results

## Submissions

All submission files to the shared task are in `submissions/` split by subtask. The names of files are the system identifiers assigned by AI2 leaderboard. The last 6 digits are used to identify the systems in the processed data files. 

Metadata about submissions are available in `submissions/mslr-public-submissions.csv`

## Data

### Main annotation

From the Cochrane test split, we sampled 100 instances for 5 top-performing models and 1 baseline. Overlap occurs for 40(need to confirm) instances to assess IAA.

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

TBD; some starter notebooks in `notebooks`
