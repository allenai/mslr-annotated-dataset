import os
import csv
import json
from collections import defaultdict


SUBMISSIONS_DIR = 'submissions/'
TARGET_DIR = 'submissions/targets/'
ANNOTATION_DATA_DIR = 'data/Annotations/'
PILOT_ANNOT_DATA_DIR = 'data/Pilot/'
OUTPUT_DATA_DIR = 'data/'

PUBLIC_SUBMISSIONS_FILE = os.path.join(SUBMISSIONS_DIR, 'mslr-public-submissions.csv')
ANNOTATION_FILE_TEMPLATE = 'Data for MSLR Annotation - Cochrane Subtask - {}.tsv'
PILOT_ANNOT_FILE_TEMPLATE = 'Data for MSLR Annotation - 100 instances - {}.tsv'

SUBTASKS = {'Cochrane', 'MS2'}
ANNOTATORS = {0: 'Bailey', 1: 'Erin', 2: 'Madeleine'}
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
REV_ANSWER_MAP = {
    question: {atext: num for num, atexts in answers.items() for atext in atexts} for question, answers in ANSWER_KEYS.items()
}
PILOT_MAP = {
    'bart_predictions': '01G4NE57VTEC7884D13JWHTYYD',
    'longformer_predictions': '01G4NHX1Z0SSHJBD8T5B8ZAR37'
}

SUBMISSION_OUTPUT_FILE = os.path.join(OUTPUT_DATA_DIR, 'submission_info.json')
DATA_OUTPUT_FILE = os.path.join(OUTPUT_DATA_DIR, 'processed_data.json')


if __name__ == '__main__':
    # Load submissions and write info to file
    submissions = []
    with open(PUBLIC_SUBMISSIONS_FILE, 'r') as f:
        reader = csv.DictReader(f, delimiter=',')
        for line in reader:
            submissions.append(line)

    submission_dict = dict()
    for row in submissions:
        exp_short = row['Beaker experiment ID'][-6:]
        submission_dict[exp_short] = {
            'exp_id': row['Beaker experiment ID'],
            'url': row['Leaderboard entry'],
            'name': row['Submission name'],
            # 'author': row['Author'],
            'type': row['Type'],
            'subtask': row['Task']
        }

    with open(SUBMISSION_OUTPUT_FILE, 'w') as outf:
        json.dump(submission_dict, outf, indent=True)

    # Load targets
    print('Reading targets...')
    targets = defaultdict(dict)
    for subtask in SUBTASKS:
        target_file = os.path.join(TARGET_DIR, f'{subtask.lower()}.csv')
        with open(target_file, 'r') as f:
            reader = csv.DictReader(f, delimiter=',')
            for row in reader:
                targets[subtask][row['ReviewID']] = row['Target']

    # Load available submissions
    print('Reading submissions...')
    predictions = defaultdict(lambda: defaultdict(dict))
    for exp_short, submission in submission_dict.items():
        prediction_file = os.path.join(SUBMISSIONS_DIR, submission['subtask'], f"{submission['exp_id']}.csv")
        if not os.path.exists(prediction_file):
            print(f'No submission file for {exp_short}: {submission["name"]}, skipping...')
            continue
        print(f'{submission["subtask"]} {exp_short}: {submission["name"]}')
        with open(prediction_file, 'r') as f:
            reader = csv.DictReader(f, delimiter=',')
            for row in reader:
                predictions[submission["subtask"]][exp_short][row["ReviewID"]] = row["Generated"]

    # Add annotations to submissions
    print('Reading annotations...')
    all_annot_files = []
    for annot_id, annotator in ANNOTATORS.items():
        # cochrane main annotation files
        annotation_file = os.path.join(ANNOTATION_DATA_DIR, ANNOTATION_FILE_TEMPLATE.format(annotator))
        if os.path.exists(annotation_file):
            all_annot_files.append([annot_id, 'Cochrane', 'main', annotation_file])
        # pilot annotation files
        pilot_annot_file = os.path.join(PILOT_ANNOT_DATA_DIR, PILOT_ANNOT_FILE_TEMPLATE.format(annotator))
        if os.path.exists(pilot_annot_file):
            all_annot_files.append([annot_id, 'MS2', 'pilot', pilot_annot_file])

    print(all_annot_files)

    # TODO: Current MS2 annotations are on the dev set while this loads the test set; there are no MS2 annotations in the resulting file
    annotations = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for annot_id, subtask, annot_task, annot_file in all_annot_files:
        with open(annot_file, 'r') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                exp_id = row.get('ExpID', row.get('model'))
                if annot_task == 'pilot' and exp_id in PILOT_MAP:
                    exp_id = PILOT_MAP[exp_id]
                exp_short = exp_id[-6:]
                review_id = row.get('ReviewID', row.get('docid'))
                if not exp_id or not review_id:
                    continue
                annotation_to_attach = {
                    'annot_id': annot_id,
                    'annot_task': annot_task
                }
                for annot_field, long_form in ANNOT_KEYS.items():
                    text_answer = row[long_form]
                    if text_answer:
                        int_answer = REV_ANSWER_MAP[long_form].get(text_answer)
                    else:
                        int_answer = None
                    annotation_to_attach[annot_field] = int_answer
                annot_values = [annotation_to_attach[annot_field] for annot_field in ANNOT_KEYS]
                if not any(annot_values):
                    continue
                if annotation_to_attach.get('ed_target') is None and annotation_to_attach.get('ed_generated') is None:
                    annotation_to_attach['ed_agree'] = None
                else:
                    annotation_to_attach['ed_agree'] = (annotation_to_attach['ed_target'] == annotation_to_attach['ed_generated'])
                if annotation_to_attach.get('strength_target') is None and annotation_to_attach.get('strength_generated') is None:
                    annotation_to_attach['strength_agree'] = None
                else:
                    annotation_to_attach['strength_agree'] = (annotation_to_attach['strength_target'] == annotation_to_attach['strength_generated'])
                annotations[subtask][exp_short][review_id].append(annotation_to_attach)

    # Combine targets, predictions, and annotations
    print('Combining targets and predictions...')
    mslr_data = []
    for subtask, target_summaries in targets.items():
        for review_id, target in target_summaries.items():
            predictions_for_review_id = []
            for exp_short, predicted_summaries in predictions[subtask].items():
                try:
                    predictions_for_review_id.append({
                        'exp_short': exp_short,
                        'prediction': predicted_summaries[review_id],
                        'annotations': annotations[subtask][exp_short][review_id],
                        'scores': {}
                    })
                except KeyError:
                    print(f'{review_id} missing in {exp_short} for {subtask}')
            mslr_data.append({
                'subtask': subtask,
                'review_id': review_id,
                'target': target,
                'predictions': predictions_for_review_id
            })

    has_annotations = [entry for entry in mslr_data if any([pred['annotations'] for pred in entry['predictions']])]

    with open(DATA_OUTPUT_FILE, 'w') as outf:
        for entry in mslr_data:
            json.dump(entry, outf)
            outf.write('\n')

    print('done.')
