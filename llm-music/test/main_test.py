import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.run_query import run_query_loop
from scripts.process_user_data import reformat_spotify_data
from scripts.make_haystack_docs import convert_to_haystack_docs

if __name__ == "__main__":
    reformat_spotify_data()
    convert_to_haystack_docs()
    print(run_query_loop("sad breakup music"))

