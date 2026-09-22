from pathlib import Path


# Project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Dataset directory
DATASET_DIR = BASE_DIR / "dataset"

# Dataset files
SALES_DATA_PATH = DATASET_DIR / "sales_data.csv"
TARGETS_DATA_PATH = DATASET_DIR / "targets.csv"
DATA_DICTIONARY_PATH = DATASET_DIR / "data_dictionary.json"
NL_QUERIES_PATH = DATASET_DIR / "nl_queries.json"