import os
import random
import logging

import pandas as pd

import parser


logging.basicConfig(level=logging.DEBUG)

SAMPLES = 5
ITER_DEPTH = 1
INPUT_FILE_BASENAME = 'url_search_06-02-2019_cleaned.csv'
OUTPUT_COLUMNS = [
    'Name',
    'URL',
    'Query_Depth',
    'Matching_Keyword',
    'Matching_Text',
]
SEARCH_TERMS = [
    'learning',
    'university',
    'smart',
    'diversity',
]


def generate_name_and_url(file_basename=INPUT_FILE_BASENAME):
    data_path = os.path.join(
        os.path.dirname(__file__),
        'data',
        'url_cache',
        file_basename,
    )

    df = pd.read_csv(data_path)
    for name, url in zip(df['name'], df['url1']):
        yield name, url


if __name__ == '__main__':
    master_df = pd.DataFrame(
        columns=OUTPUT_COLUMNS
    )

    roots = list(generate_name_and_url())
    random_samples = random.sample(roots, SAMPLES)

    for name, url in random_samples:
        nested_search = parser.NestedSearch(url)
        nested_search.search(SEARCH_TERMS, max_depth=ITER_DEPTH, n_char_buffer=100)
        search_df = nested_search.get_results_as_dataframe()
        search_df['Name'] = name
        master_df = master_df.append(
            search_df,
        )

    print(master_df)

    master_df = master_df[OUTPUT_COLUMNS]  # Realign columns for readability
    master_df.to_csv(
        os.path.join(
            os.path.dirname(__file__),
            'output',
            'master_df.csv',
        ),
        index=False
    )
