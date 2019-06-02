import lxml.html as lh
import requests


def get_html(url):
    response = requests.get(url)
    return response.text


def parse_html(html):
    """Returns lxml HTML root"""
    return lh.fromstring(html)

def find_links(url, link_css='a'):
    html = get_html(url)
    root = parse_html(html)
    elements = root.cssselect(link_css)
    return elements


if __name__ == '__main__':
    url = 'http://www.espn.com/'
    links = find_links(url)
