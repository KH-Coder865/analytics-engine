from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


DATASET_DIR = BASE_DIR / "dataset"

SALES_DATA_PATH = DATASET_DIR / "sales_data.csv"
TARGETS_DATA_PATH = DATASET_DIR / "targets.csv"
DATA_DICTIONARY_PATH = DATASET_DIR / "data_dictionary.json"
NL_QUERIES_PATH = DATASET_DIR / "nl_queries.json"