import pandas as pd

results_path = '/Users/aaron.rosenberg/Projects/edu-learning-styles/data/url_cache/url_search_06-02-2019.csv'
metadata_path = '/Users/aaron.rosenberg/Projects/edu-learning-styles/data/cc_download.csv'

df = pd.read_csv(metadata_path)
df = df.merge(
    pd.read_csv(results_path),
    on='name',
)

df = df.loc[
    (df.level == '4-year or above') & (df.control == 'Public'),
    ['name', 'url1', 'url2', 'url3']
    ]

df.to_csv('/Users/aaron.rosenberg/Projects/edu-learning-styles/data/url_cache/url_search_06-02-2019_cleaned.csv')