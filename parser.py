import logging
import re

import requests
import lxml.etree
import lxml.html
import pandas as pd


def main():
    logging.basicConfig(level=logging.INFO)

    url = 'https://www.espn.com/'
    nested_search = NestedSearch(url)
    nested_search.search(
        search_terms=['soccer', 'futbol'],
        max_depth=2
    )

    df = nested_search.get_results_as_dataframe()
    print(df.tail())

    print(
        '\n', 'pages parsed:', nested_search.webpages_parsed,
        '\n', 'text matched:', nested_search.match_count,
    )

    return nested_search


class WebpageParser(object):
    def __init__(self, url):
        self.url = url
        self.text = self._get_html()
        self.root = self._parse_html()
        self.links = self._generate_links()

    def string_count_in_text(self, string, case_sensitive=False):
        """Counts number of string occurences in HTML text

        Args:
            string (str): Target string to search for in text.
            case_sensitive (bool): Flag for case sensitivity in search.

        Returns:
            (int) Number of occurrences of string in text.
        """
        string = string if case_sensitive else string.lower()
        text = self.text if case_sensitive else self.text.lower()

        count = text.count(string)
        return count

    def generate_match_surrounding_text(self, string, n_char_buffer=15, case_sensitive=False):
        """Generates text surrounding string matches in HTML text

        Args:
            string (str): Target string to search for in text.
            n_char_buffer (int): Number of characters to return on either side of string match in text.
            case_sensitive (bool): Flag for case sensitivity in search.

        Returns:
            Generator (str) of string matches in HTML text.
        """
        match_length = len(string)
        starting_locations = self._find_string_start_locations(
            string,
            case_sensitive=case_sensitive
        )
        for start_index in starting_locations:
            yield self.text[start_index - n_char_buffer:start_index + match_length + n_char_buffer]

    def generate_linked_webpages(self):
        """Generates WebpageParser objects for valid links in current WebpageParser object

        Returns:
            Generator (obj) of WebpageParser instances for linked URLs
        """
        for link in self.links:
            try:
                yield WebpageParser(link)
            except lxml.etree.ParserError:
                logging.warning('can not parse webpage: %s', link)
                continue
            except requests.exceptions.SSLError:
                logging.warning('can not verify certs for webpage: %s', link)
                continue

    def _generate_links(self):
        """Generate properly resolved links from anchor elements from root HTML.

        Returns:
            Generator (str) for linked URL strings.
        """
        for anchor in self._get_anchor_elements():
            try:
                href = anchor.attrib['href']
                if href.startswith('http'):
                    yield href
                else:
                    yield self.url + href
            except KeyError:
                logging.debug('no href, skipping anchor element ... ')

    def _get_html(self):
        """Returns HTML as text"""
        response = requests.get(self.url)
        return response.text

    def _parse_html(self):
        """Returns lxml HTML root"""
        return lxml.html.fromstring(self.text)

    def _get_anchor_elements(self, link_css='a'):
        """Returns the anchor link HTML elements"""
        for element in self.root.cssselect(link_css):
            yield element

    def _find_string_start_locations(self, string, case_sensitive=False):
        """returns start index integer list"""
        string = string if case_sensitive else string.lower()
        text = self.text if case_sensitive else self.text.lower()

        find = [x.start() for x in re.finditer(string, text)]
        return find

    def __repr__(self):
        return f'<WebpageParser for [{self.url}]>'


class NestedSearch(object):
    def __init__(self, root_url):
        """Nested Search Manager

        Args:
            root_url (str): URL to begin nested query.

        Attributes:

        """
        self.root_webpage = WebpageParser(root_url)
        self.current_webpage = self.root_webpage
        self.current_depth = 1
        self.max_depth = 1

        self._search_result_urls = []
        self._search_result_matches = []
        self._search_result_depths = []

        self.webpages_parsed = 0

    @property
    def results(self):
        return zip(
            self._search_result_urls,
            self._search_result_depths,
            self._search_result_matches,
        )

    @property
    def match_count(self):
        return len(self._search_result_matches)

    def search(self, search_terms, n_char_buffer=25, max_depth=None, _current_depth=1):
        """

        Args:
            search_terms (str|list): Search term or terms for matching in target HTML.
            n_char_buffer (int): Number of characters to return on either side of string match in text.  Defaults to
                25 characters.
            max_depth (int): Maximum number of levels for recursion while following HTML links.  Defaults to None which
                will trigger the use the default class attribute value.
            _current_depth (int): By convention, a private parameter.  Used in recursive search pattern.

        Returns:
            None.  Results can be viewed with the results property, or get_results_as_dataframe method.
        """
        self.current_depth = _current_depth

        if self.current_depth == 1:
            self._reset_search()

        if max_depth:
            self._set_max_depth(max_depth)

        self._register_text_matches(search_terms, n_char_buffer)
        self.webpages_parsed += 1

        next_depth = _current_depth + 1
        if next_depth > self.max_depth:
            return

        for child_webpage in self.current_webpage.generate_linked_webpages():
            self._change_current_webpage(child_webpage)
            self.search(search_terms, _current_depth=next_depth)

        self._change_current_webpage(self.root_webpage)

    def get_results_as_dataframe(self):
        """Gets you the class attribute results as a pandas DataFrame object

        Returns:
            pd.DataFrame of class search results.
        """
        return pd.DataFrame(self.results, columns=['URL', 'Query_Depth', 'Matching_Text'])

    def _register_text_matches(self, search_terms, n_char_buffer):
        """Saves matches for all search terms to class """
        search_terms = search_terms if isinstance(search_terms, list) else [search_terms]
        for search_term in search_terms:
            for match in self.current_webpage.generate_match_surrounding_text(search_term, n_char_buffer=n_char_buffer):
                self._save_match(match)

    def _save_match(self, match):
        """Helper class to update global class attributes"""
        self._search_result_urls.append(self.current_webpage.url)
        self._search_result_depths.append(self.current_depth)
        self._search_result_matches.append(match)

    def _set_max_depth(self, new_max_depth):
        """Sets the max depth for recursion with class attribute across instances"""
        self.max_depth = new_max_depth

    def _change_current_webpage(self, webpage):
        """Updates WebpageParser object under query"""
        self.current_webpage = webpage

    def _reset_search(self):
        """Clears old results from search"""
        self._search_result_depths = []
        self._search_result_urls = []
        self._search_result_matches = []
        self.webpages_parsed = 0


if __name__ == '__main__':
    nested_search = main()
