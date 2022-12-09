# MSLR annotation results

## Submissions

All submission files to the shared task are in `submissions/` split by subtask. The names of files are the system identifiers assigned by AI2 leaderboard. The last 6 digits are used to identify the systems in the processed data files. 

Metadata about submissions are available in `submissions/mslr-public-submissions.csv`

## Data

### Main annotation

From the Cochrane test split, we sampled 100 instances for 5 top-performing models and 1 baseline. Overlap occurs for 40(need to confirm) instances to assess IAA.

The pilot was conducted on MS^2, and is between the two baseline models.

### Annotation results

Annotations for MSLR shared task: `data/Annotations/`

Annotations for MSLR pilot: `data/Pilot/`

### Data preprocessing

All test entries, annotations, and automated metrics are combined into a single file: `data/processed_data_w_metrics.json`. The scripts for creating this file are in `scripts/`.

`0_download_submissions.py` is used to download submission data from Beaker.

`1_reorg_data.py` reorganizes all data and appends submissions and annotations. This outputs `data/processed_data.json`.

`2_add_metrics.py` adds automated mtrics to the processed data file. This outputs `data/processed_data_w_metrics.json`.

The current metrics are:

- rouge (R1, R2, RL, RLsum and P, R, F associated with each)
- bertscore (P, R, F)
- ei_divergence
- nli (cosine similarity from SBERT); model: `nli-roberta-base-v2`
- sts (cosine similarity from SBERT); model: `stsb-roberta-base-v2`
- claimver (cosine similarity from SBERT); model: `pritamdeka/S-PubMedBert-MS-MARCO-SCIFACT` (Note: this isn't the SciFact MultiVers model, that might be better...)

## Analysis

TBD; some starter notebooks in `notebooks`