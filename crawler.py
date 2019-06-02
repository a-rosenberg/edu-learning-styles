import logging

import lxml.html as lh
import requests


def main():
    url = 'http://www.espn.com/'
    anchors = get_anchor_elements(url)
    resolved_urls = generate_links(url, anchors)
    print(list(resolved_urls))


def get_html(url):
    response = requests.get(url)
    return response.text


def parse_html(html):
    """Returns lxml HTML root"""
    return lh.fromstring(html)


def get_anchor_elements(url, link_css='a'):
    html = get_html(url)
    root = parse_html(html)
    for element in root.cssselect(link_css):
        yield element


def generate_links(url, anchors):
        for anchor in anchors:
            try:
                href = anchor.attrib['href']
                if href.startswith('http'):
                    yield href
                else:
                    yield url + href
            except KeyError:
                logging.debug('no href, skipping anchor element ... ')


if __name__ == '__main__':
    main()
