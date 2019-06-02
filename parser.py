import logging
import requests
import re
import lxml.html as lh


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

    def _get_html(self):
        """Returns HTML as text"""
        response = requests.get(self.url)
        return response.text

    def _parse_html(self):
        """Returns lxml HTML root"""
        return lh.fromstring(self.text)

    def _get_anchor_elements(self, link_css='a'):
        """Returns the anchor link HTML elements"""
        for element in self.root.cssselect(link_css):
            yield element

    def _generate_links(self):
        """Generate properly resolved links from anchor elements"""
        for anchor in self._get_anchor_elements():
            try:
                href = anchor.attrib['href']
                if href.startswith('http'):
                    yield href
                else:
                    yield self + href
            except KeyError:
                logging.debug('no href, skipping anchor element ... ')

    def _find_string_start_locations(self, string, case_sensitive=False):
        """returns start index integer list"""
        string = string if case_sensitive else string.lower()
        text = self.text if case_sensitive else self.text.lower()

        find = [x.start() for x in re.finditer(string, text)]
        return find

    def __repr__(self):
        return f'<WebpageParser for [{self.url}]>'



if __name__ == '__main__':
    url = 'http://www.espn.com/'
    parser = WebpageParser(url)

    search_phrase = 'Soccer'

    print('search phrase:', search_phrase )
    print('count:', parser.string_count_in_text('Soccer'))

    for match_string in parser.generate_match_surrounding_text('Soccer', n_char_buffer=50):
        print(match_string)
        break