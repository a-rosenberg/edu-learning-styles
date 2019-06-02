import os
import random

import pandas as pd

import parser

search_terms = [
    'learning style',
    'admissions',
    'students',
]


def generate_name_and_url():
    data_path = os.path.join(os.path.dirname(__file__), 'data', 'url_cache', 'url_search_06-02-2019.csv')
    df = pd.read_csv(data_path)
    for name, url in zip(df['name'], df['url1']):
        yield name, url


if __name__ == '__main__':
    roots = list(generate_name_and_url())
    random_samples = random.sample(roots, 5)
    for name, url in random_samples:
        print(name)
        nested_search = parser.NestedSearch(url)
        nested_search.search(search_terms, max_depth=1, n_char_buffer=25)
        print(nested_search.get_results_as_dataframe().head())
        print()