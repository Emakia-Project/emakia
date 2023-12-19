from evaluate_model_02_first_script import extract_tweet_content
from evaluate_model_02_second_script import evaluate

THRESHOLDS = [0.600, 0.750, 0.775, 0.800, 0.825, 0.850, 0.900]
input_jsonl_file = 'mie_all_prediction.jsonl'
tweet_content_file = 'tweet_contents.csv'

for t in THRESHOLDS:
    # TODO: pass a file object instead of a path
    extract_tweet_content(input_jsonl_file, tweet_content_file, t)
    evaluate(tweet_content_file, t)
    
    print(f"Validation completed for threshold {t}.")