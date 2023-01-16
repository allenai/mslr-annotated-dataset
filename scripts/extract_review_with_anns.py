import json
import pandas as pd
import copy

df = pd.read_json('../data/processed_data_w_metrics.json',lines = True)

# df_with_ann = df[df['predictions'][0]['annotations']]
# df_with_ann = copy.deepcopy(df)
rows_with_ann = []
for i, row in df.iterrows():
    preds = row['predictions']
    if any(prediction['annotations'] for prediction in preds):
    # if len(preds[0]['annotations']):
        rows_with_ann.append(row)
        # print(preds)


df_with_ann = pd.DataFrame(data = rows_with_ann)
print(df_with_ann.head())

df_with_ann.to_json('processed_data_w_metrics_w_anns.json', orient = 'records', lines= True)