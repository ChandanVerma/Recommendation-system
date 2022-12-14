import yaml

def load_config(file_path):
    with open(file_path, 'r') as f:
        cfg = yaml.safe_load(f)
    return cfg
