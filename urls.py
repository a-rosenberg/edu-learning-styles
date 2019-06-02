import os
import logging
import datetime

import pandas as pd
import googlesearch


def main():
    logging.basicConfig(level=logging.INFO)

    urls = get_university_tuples()

    names = [x[0] for x in urls]
    url_1 = [x[1][0] for x in urls]
    url_2 = [x[1][1] for x in urls]
    url_3 = [x[1][2] for x in urls]

    df = pd.DataFrame({'name': names, 'url1': url_1, 'url2': url_2, 'url3': url_3, })
    today = datetime.datetime.now().strftime('%m-%d-%Y')
    output_path = os.path.join(os.path.dirname(__file__), 'data', 'url_cache', 'url_search_' + today + '.csv')
    df.to_csv(output_path, index=False)


def get_university_tuples():
    """Procedural glue for URL scraping exercise

    Returns:
        List of tuples containing the institution query phrase and a list of URLs most highly matched in order.
    """
    logging.basicConfig(level=logging.INFO)

    names = get_university_names()
    url_tuples = list(get_n_matching_google_result(names))
    return url_tuples


def get_university_names(basename='cc_download.csv'):
    """Returns list of names in CSV from data directory"""
    data_path = os.path.join(os.path.dirname(__file__), 'data', basename)
    df = pd.read_csv(data_path)
    return list(df['name'])


def get_n_matching_google_result(names, n=3, pause=2.0):
    """Yields list of n results for search names

    Args:
        names (list; str):  University names for Google query.
        n (int):  Number of top results from Google query.
        pause:  Wait time between queries to prevent 429 response code (aka please slow down server response).

    Returns:
        list of tuples containing
    """
    query_count = len(names)

    if pause <= 1.0:
        raise ResourceWarning("Google's going to block your IP if you don't slow down")

    counter = 0
    for name in names:
        counter += 1
        logging.info(f'Google query ({counter}/{query_count}): "{name}"')
        results = googlesearch.search(name, tld='com', lang='en', num=n, stop=n, pause=pause)
        yield (name, list(results))


if __name__ == '__main__':
    main()
