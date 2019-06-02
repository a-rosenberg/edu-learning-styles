import os

import pandas as pd

search_terms = [
    'learning style',
    'learning styles',
    'learning strategy',
    'learning strategies',
    'visual learner',
]


def generate_name_and_url():
    data_path = os.path.join(os.path.dirname(__file__), 'data', 'url_cache', 'url_search_06-02-2019.csv')
    df = pd.read_csv(data_path)
    for name, url in zip(df['name'], df['url1']):
        yield name, url


if __name__ == '__main__':
    roots = generate_name_and_url()
    for name, url in roots:
        print(name, url)