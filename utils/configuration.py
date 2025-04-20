import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# print(f"Base directory: {BASE_DIR}")
DATA_DIR = os.path.join(BASE_DIR, "data")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
RIFE_DIR = os.path.join(BASE_DIR, "ECCV2022-RIFE")
