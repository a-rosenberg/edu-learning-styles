import crawler


def main():
    url = 'http://www.espn.com/'
    test_data = crawler.get_html(url)
    print(count_string_in_text('soccer', test_data))


def count_string_in_text(target_string, text, case_sensitive=False):
    """"""
    if not case_sensitive:
        target_string = target_string.lower()
        text = text.lower()

    count = text.count(target_string)
    return count


if __name__ == '__main__':
    main()