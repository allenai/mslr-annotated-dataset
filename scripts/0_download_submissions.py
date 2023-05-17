"""
This script downloads all public submissions to the MSLR leaderboards 
It requires Beaker access for the specific task
"""

import os
import csv
import subprocess
import shutil
import yaml

SUBMISSIONS_FILE = 'submissions/mslr-public-submissions.csv'
OUTPUT_DIR = 'submissions'

if __name__ == '__main__':
    subtasks = ['MS2', 'Cochrane']
    for subtask in subtasks:
        output_subdir = os.path.join(OUTPUT_DIR, subtask)
        os.makedirs(output_subdir, exist_ok=True)

    submissions = []
    with open(SUBMISSIONS_FILE, 'r') as f:
        reader = csv.DictReader(f, delimiter=',')
        for line in reader:
            submissions.append(line)

    for row in submissions:
        exp_id = row['Beaker experiment ID']
        task_name = row['Task']

        fetch_dataset = subprocess.run([
            "beaker", "experiment", "spec", exp_id
        ], capture_output=True)

        spec_yaml = yaml.load(fetch_dataset.stdout, Loader=yaml.FullLoader)
        ds_id = spec_yaml['tasks'][0]['datasets'][0]['source']['beaker']

        print(f'Downloading {ds_id}')
        download_dataset = subprocess.run([
            "beaker", "dataset", "fetch", "-o", os.path.join(OUTPUT_DIR, task_name, exp_id), ds_id
        ])
        source_dir = os.path.join(OUTPUT_DIR, task_name, exp_id)
        source_loc = os.path.join(OUTPUT_DIR, task_name, exp_id, 'predictions.csv')
        target_loc = os.path.join(OUTPUT_DIR, task_name, f'{exp_id}.csv')
        shutil.move(source_loc, target_loc)
        shutil.rmtree(source_dir)

    print('done.')

