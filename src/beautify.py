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

    color_palette = soup.new_tag('div', id='colorPalette', style="position: fixed; bottom: 0; width: 100%; height: 20px;")

    colors = ['red', 'blue', 'green', 'yellow', 'purple', 'orange']
    for color in colors:
        color_div = soup.new_tag('div', style=f"background-color: {color}; width: 50px; height: 20px; display: inline-block;")
        color_palette.append(color_div)
    body = soup.body
    if body is None:
        body = soup.new_tag("body")
        soup.html.insert(1, body)
    soup.body.append(color_palette)

    for row in soup.find_all('tr'):
        row['onclick'] = "changeColor(this)"

    script_tag = soup.new_tag('script')
    script_tag.string = """
    var currentColor = 'red';
    document.getElementById('colorPalette').addEventListener('click', function(event) {
        currentColor = event.target.style.backgroundColor;
    });
    function changeColor(row) {
        if (row.style.backgroundColor == currentColor) {
            row.style.backgroundColor = '';
        } else {
            row.style.backgroundColor = currentColor;
        }
    }
    """
    soup.body.append(script_tag)

    with open("out.html", "w", encoding='utf-8') as out_file:
        out_file.write(str(soup))


def run():
    make_table_sortable()
