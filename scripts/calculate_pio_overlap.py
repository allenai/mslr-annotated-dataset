import pandas as pd 
from rapidfuzz import fuzz


data = pd.read_json('../data/processed_data_w_metrics_w_anns_pico.json', lines = True)

mapping = {'PAR': 'population', 'INT': 'intervention', 'OUT': 'outcome'}

def exact_match(str1, str2):
    if str1==str2:
        return 1
    return 0

def substring(str1, str2):
    if str1 in str2 or str2 in str1:
        return 1
    return 0

def close_match(str1, str2, cutoff=0.5):
    sim = fuzz.ratio(str1,str2)
    print(str1 +' - ' + str2, sim)
    return sim/100
    # if sim >= cutoff:
    #     return 1
    # return 0    

def overlap_score(targets,predictions, sim_function):
    threshold = 0.6
    scores = {'PAR':0,'INT':0,'OUT':0}
    number_of_ent_target = {'PAR':0,'INT':0,'OUT':0}
    for ent_t in targets:
        number_of_ent_target[ent_t[1]] +=1
        for ent_p in predictions:
            if ent_t[1] == ent_p[1]:
                score = sim_function(ent_t[0],ent_p[0])
                if score >= threshold:
                    # scores[ent_p[1]] += score
                    scores[ent_p[1]] += 1
                    break
    for key,value in scores.items():
        if number_of_ent_target[key]:
            scores[key] = value/number_of_ent_target[key]
    
    return scores


def compare_set(targets, predictions, strategy):
    if strategy == 'exact_match':
        scores = overlap_score(targets, predictions, exact_match)
    elif strategy == 'substring':
        scores = overlap_score(targets, predictions, substring)

    elif strategy == 'close_match':
        scores = overlap_score(targets, predictions, close_match)
    return scores


def calculate_overlap_item(item, strategy):
    target_ents = item['target_entities']
    # print(item['predictions'])
    for i,prediction in enumerate(item['predictions']):
        # print(prediction)
        if item['predictions'][i].get('overlap_scores') == None:
            item['predictions'][i]['overlap_scores'] = {}
        prediction_ents = prediction['entities']
        overlap_scores = compare_set(target_ents, prediction_ents, strategy)
        item['predictions'][i]['overlap_scores'][strategy] = overlap_scores
    return item

def calculate_overlap_corpus(corpus, strategy):
    items = []
    for i, row in corpus.iterrows():
        item = calculate_overlap_item(row, strategy)
        items.append(item)
    df = pd.DataFrame(data = items)
    df.to_json('data_with_overlap_scores.json', orient = 'records', lines = True)

if __name__ == "__main__":
    corpus = pd.read_json('processed_data_w_metrics_w_anns_pico.json', lines = True)
    strategy = 'exact_match'
    calculate_overlap_corpus(corpus, strategy)
    strategy = 'close_match'
    calculate_overlap_corpus(corpus, strategy)
    strategy = 'substring'
    calculate_overlap_corpus(corpus, strategy)