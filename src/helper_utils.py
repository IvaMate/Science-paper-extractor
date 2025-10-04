from pathlib import Path
import yaml

CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"

def load_config(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)