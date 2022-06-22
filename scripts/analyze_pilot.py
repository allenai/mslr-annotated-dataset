import os
import csv
import pandas as pd
import seaborn as sns
import simpledorff
from collections import defaultdict, Counter

"""COLUMNS
['docid',
 'model',
 'Background',
 'Target Summary',
 'Generated Summary',
 'Is the generated summary fluent?',
 'Is the *population* in the generated summary the same as the population in '
 'the target summary?',
 'Is the *intervention* in the generated summary the same as the intervention '
 'in the target summary?',
 'Is the *outcome* in the generated summary the same as the outcome in the '
 'target summary?',
 'Comments about PIO agreement (optional)',
 'What is the effect direction in the *target* summary?',
 'What is the effect direction in the *generated* summary?',
 'Comments about effect directions (optional)',
 'What is the strength of the claim made in the *target* summary?',
 'What is the strength of the claim made in the *generated* summary?',
 'Comments about strength of claim (optional)',
 '',
 'annotator']
"""

BASE_DIR = 'data/'
DATA_FILES = os.listdir(BASE_DIR)
ANNOTATOR_ORDER = ['Bailey', 'Erin', 'Madeleine']

ANNOT_KEYS = [
 'Is the generated summary fluent?',
 'Is the *population* in the generated summary the same as the population in '
 'the target summary?',
 'Is the *intervention* in the generated summary the same as the intervention '
 'in the target summary?',
 'Is the *outcome* in the generated summary the same as the outcome in the '
 'target summary?',
 'What is the effect direction in the *target* summary?',
 'What is the effect direction in the *generated* summary?',
 'What is the strength of the claim made in the *target* summary?',
 'What is the strength of the claim made in the *generated* summary?',
]


def df_to_experiment_annotator_table(df, experiment_col, annotator_col, class_col):
    return df.pivot_table(
        index=annotator_col, columns=experiment_col, values=class_col, aggfunc="first"
    )


all_data = []
for fname in DATA_FILES:
    annotator = fname.split('-')[-1].strip()[:-4]
    print(fname)
    with open(os.path.join(BASE_DIR, fname), 'r') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')
        for row in reader:
            if not row['Is the generated summary fluent?']:
                continue
            row['annotator'] = annotator
            row['docid_model'] = f"{row['docid']}_{row['model']}"
            all_data.append(row)

all_data.sort(key=lambda x: ANNOTATOR_ORDER.index(x['annotator']))

df = pd.DataFrame(all_data)

# Krippendorff's alpha
alphas = dict()
krippendorff_tables = dict()
for question in ANNOT_KEYS:
    alpha = simpledorff.calculate_krippendorffs_alpha_for_df(
        df,
        experiment_col='docid_model',
        annotator_col='annotator',
        class_col=question
    )
    alphas[question] = alpha
    table = df_to_experiment_annotator_table(df, 'docid_model', 'annotator', question)
    krippendorff_tables[question] = table

# Agreement
by_docid = defaultdict(list)
for entry in all_data:
    by_docid[(entry['docid'], entry['model'])].append(entry)

# IAA
num_errors = 0
agreement_per_question = defaultdict(list)
split_by_model = {
    'bart_predictions': defaultdict(list),
    'longformer_predictions': defaultdict(list)
}
for (docid, model), entries in by_docid.items():
    for question in ANNOT_KEYS:
        answers = [entry[question] for entry in entries]
        if len(answers) > 2:
            print('warning: error! >2')
            agreement_per_question[question].append(answers)
            split_by_model[model][question].append(answers)
            continue
        elif len(answers) == 2:
            agreement_per_question[question].append(answers)
            split_by_model[model][question].append(answers)
        else:
            print('error! <2')
            num_errors += 1
            continue

agreements = dict()
ns = dict()
for question, answers in agreement_per_question.items():
    agrees = [a[0] == a[1] for a in answers]
    perc_agree = sum(agrees) / len(agrees)
    agreements[question] = perc_agree
    ns[question] = len(agrees)

manual_alphas = dict()
for question, answers in agreement_per_question.items():
    entries = []
    for i, aaa in enumerate(answers):
        a0 = aaa[0]
        a1 = aaa[1]
        entries.append((i, a0, 'A'))
        entries.append((i, a1, 'B'))
    df = pd.DataFrame(entries, columns=['exp', 'class', 'ann'])
    alpha = simpledorff.calculate_krippendorffs_alpha_for_df(
        df,
        experiment_col='exp',
        annotator_col='ann',
        class_col='class'
    )
    manual_alphas[question] = alpha


print('model\tquestion\tsplit')
results_by_model = []
for model, splits in split_by_model.items():
    for question, answers in splits.items():
        use_answers = [a[0] for a in answers]
        ans_count = Counter(use_answers)
        results_by_model.append([model, question, ans_count])

results_by_model.sort(key=lambda x: ANNOT_KEYS.index(x[1]))
for model, question, ans_count in results_by_model:
    print(model, '\t', question, '\t', ans_count)




