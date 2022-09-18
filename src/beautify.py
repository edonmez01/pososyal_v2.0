from bs4 import BeautifulSoup


def make_table_sortable():
    soup = BeautifulSoup(open("out.html").read(), "html.parser")
    script_tag = soup.new_tag('script')
    script_tag['src'] = "https://www.kryogenix.org/code/browser/sorttable/sorttable.js"
    soup.append(script_tag)
    soup.find('table')['class'] = 'sortable'

    with open("out.html", "w", encoding='utf-8') as out_file:
        out_file.write(str(soup))


def run():
    make_table_sortable()
