import yaml
from datetime import datetime
import os

def load_config(file_path):
    with open(file_path, 'r') as f:
        cfg = yaml.safe_load(f)
    return cfg

config = load_config('config.yml')

def categorify(df, cat, freq_treshhold=20, unkown_id=1, lowfrequency_id=0):
    freq = df[cat].value_counts()
    freq = freq.reset_index()
    freq.columns = [cat, 'count']
    freq = freq.reset_index()
    freq.columns = [cat + '_Categorify', cat, 'count']
    freq[cat + '_Categorify'] = freq[cat + '_Categorify']+2
    freq.loc[freq['count']<freq_treshhold, cat + '_Categorify'] = lowfrequency_id
    freq = freq.drop('count', axis=1)
    df = df.merge(freq, how='left', on=cat)
    df[cat + '_Categorify'] = df[cat + '_Categorify'].fillna(unkown_id)
    return df

def save_preprocessed_data(df):
    now = datetime.now()
    dt_string = now.strftime("%d_%m_%Y_%H_%M_%S")
    df.to_parquet(os.path.join(f"preprocessed_data_{dt_string}.parquet"), index=False)


def convert_types(df):
    df[config["asset_feature_list"]] = df[config["asset_feature_list"]].astype(str)
    df[config["user_feature_list"]] = df[config["user_feature_list"]].astype(str)
    return df