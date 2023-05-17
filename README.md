# MSLR annotated dataset for metric evaluations

This repo contains the dataset and analysis code for the ACL 2023 paper "Automated Metrics for Medical Multi-Document Summarization Disagree with Human Evaluations." As a follow up to the [MSLR shared task](https://github.com/allenai/mslr-shared-task) on multi-document summarization for literature review, we sampled six submissions to the MSLR-Cochrane subtask, and provide human judgments of summary quality for the submitted summaries. Two types of human judgments are provided, facet-based quality annotations, as well as pairwise judgments.

## Submissions

All submission files to the [MSLR shared task](https://github.com/allenai/mslr-shared-task) are in `submissions/` split by subtask. The names of files are the system identifiers assigned by AI2 leaderboard. The last 6 digits are used to identify the systems in the processed data files. 

Metadata about submissions are available in `submissions/mslr-public-submissions.csv`

## Data

***TL;DR* The final dataset is `data/data_with_overlap_scores.json`**

An example entry looks like the following:

```json
{
  "subtask": "Cochrane",
  "review_id": "CD000220",
  "target": "Metronidazole, given as a single dose, is likely to provide parasitological cure for trichomoniasis, but it is not known whether this treatment will have any effect on pregnancy outcomes. The cure rate could probably be higher if more partners used the treatment.",
  "predictions": [
    ...
  ]
}
```

Where predictions contains a list of model predictions of the following format:

```json
{
    "exp_short": "SPNXTA",
    "prediction": "Treatment of asymptomatic trichomoniasis with metronidazole 48 hours or 48 hours apart does not prevent preterm birth in women with trichomiasis. However, it does reduce the risk of caesarean section and the time of birth. [Note: The four citations in the awaiting classification section may alter the conclusions of the review once assessed.]",
    "annotations": [
        {
            "annot_id": 0,
            "annot_task": "main",
            "fluency": 1,
            "population": 2,
            "intervention": 2,
            "outcome": 1,
            "ed_target": 2,
            "ed_generated": 2,
            "strength_target": 2,
            "strength_generated": 2,
            "ed_agree": true,
            "strength_agree": true
        }
    ],
    "scores": {
        "bertscore_p": 0.8111618161,
        "bertscore_r": 0.8303713202,
        "bertscore_f": 0.8206541538,
        "rouge1_p": 0.2553191489,
        "rouge1_r": 0.375,
        "rouge1_f": 0.3037974684,
        "rouge2_p": 0,
        "rouge2_r": 0,
        "rouge2_f": 0,
        "rougeL_p": 0.1063829787,
        "rougeL_r": 0.15625,
        "rougeL_f": 0.1265822785,
        "rougeLsum_p": 0.1063829787,
        "rougeLsum_r": 0.15625,
        "rougeLsum_f": 0.1265822785,
        "ei_score": 0.54884296,
        "claimver": 0.3884240389,
        "sts": 0.3086568713,
        "nli": 0.481220901
    },
    "entities": [
        [
            "birth",
            "OUT"
        ],
        ...
    ],
    "overlap_scores": {
        "exact_match": {
            "PAR": 0,
            "INT": 1,
            "OUT": 0
        },
        "close_match": {
            "PAR": 0,
            "INT": 1,
            "OUT": 0
        },
        "substring": {
            "PAR": 0,
            "INT": 1,
            "OUT": 0
        }
    }
}
```

In each prediction entry:

- `exp_short` is the system ID
- `prediction` is the generated summary
- `annotations` is a list that includes facet annotations, usually with a single annotation entry but sometimes 2 or more if labeled by more than one annotator
- `scores` is a list of all automated metrics except PIO-Overlap
- `overlap_scores` contains the PIO-Overlap scores when computed using using different matching rules
- `entities` contains the list of PIO entities tagged in the summary

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

Facet annotations for MSLR Cochrane: `data/Annotations/`

Pairwise annotations for MSLR Cochrane: `data/Pairwise/`

Facet annotations for MSLR MS^2 pilot: `data/Pilot/`

### Data preprocessing

All test entries, annotations, and automated metrics are combined into a single file: `data/data_with_overlap_scores.json`. The scripts for creating this file can be found in `scripts/`.

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
        -1: [
            'N/A: no effect direction is specified in the target summary',
            'N/A: no effect direction is specified in the generated summary'
        ]
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

The metrics computed for each summary are:

- ROUGE (R1, R2, RL, RLsum and P, R, F associated with each)
- BERTScore (P, R, F)
- Delta-EI
- NLI (cosine similarity from SBERT); model: `nli-roberta-base-v2`
- STS (cosine similarity from SBERT); model: `stsb-roberta-base-v2`
- ClaimVer (cosine similarity from SBERT); model: `pritamdeka/S-PubMedBert-MS-MARCO-SCIFACT`
- PIO-Overlap (exact match, close match, substring)

## Analysis

Analysis included in the published manuscript are in `notebooks/mslr_annotation_analysis.ipynb`

To set up an environment, please follow the instructions provided [here](https://github.com/allenai/mslr-shared-task).

## Citation

If using this work, please cite:

```
@inproceedings{wang-etal-2023-automated,
    title = "Automated Metrics for Medical Multi-Document Summarization Disagree with Human Evaluations",
    author = "Wang, Lucy Lu  and
      Otmakhova, Yulia  and
      DeYoung, Jay  and
      Truong, Thinh Hung  and
      Kuehl, Bailey E  and
      Bransom, Erin  and
      Wallace, Byron C",
    booktitle = "Proceedings of the 61th Annual Meeting of the Association for Computational Linguistics (Long Papers)",
    month = july,
    year = "2023",
    address = "Toronto, Canada",
    publisher = "Association for Computational Linguistics",
    abstract = "Evaluating multi-document summarization (MDS) quality is difficult. This is especially true in the case of MDS for biomedical literature reviews, where models must synthesize contradicting evidence reported across different documents. Prior work has shown that rather than performing the task, models may exploit shortcuts that are difficult to detect using standard n-gram similarity metrics such as ROUGE. Better automated evaluation metrics are needed, but few resources exist to assess metrics when they are proposed. Therefore, we introduce a dataset of human-assessed summary quality facets and pairwise preferences to encourage and support the development of better automated evaluation methods for literature review MDS. We take advantage of community submissions to the Multi-document Summarization for Literature Review (MSLR) shared task to compile a diverse and representative sample of generated summaries. We analyze how automated summarization evaluation metrics correlate with lexical features of generated summaries, to other automated metrics including several we propose in this work, and to aspects of human-assessed summary quality. We find that not only do automated metrics fail to capture aspects of quality as assessed by humans, in many cases the system rankings produced by these metrics are anti-correlated with rankings according to human annotators."
}
```
