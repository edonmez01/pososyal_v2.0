from bs4 import BeautifulSoup


def make_table_sortable():
    soup = BeautifulSoup(open("out.html").read(), "html.parser")
    head = soup.head
    if head is None:
        head = soup.new_tag("head")
        soup.html.insert(0, head)
    style_tag = soup.new_tag('style')
    style_tag.string = """
    th {
        position: sticky;
        top: 0;
        background-color: #fff;
    }
    """
    head.append(style_tag)
    script_tag = soup.new_tag('script')
    script_tag['src'] = "https://www.kryogenix.org/code/browser/sorttable/sorttable.js"
    soup.append(script_tag)
    soup.find('table')['class'] = 'sortable'

    with open("out.html", "w", encoding='utf-8') as out_file:
        out_file.write(str(soup))


def run():
    make_table_sortable()
