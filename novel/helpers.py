from bs4 import BeautifulSoup


def text_to_html(text):
    array = text.split("\n")
    html = [f"<p>{s}</p>" for s in array]
    return "".join(html)


def html_to_text(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator="\n")
