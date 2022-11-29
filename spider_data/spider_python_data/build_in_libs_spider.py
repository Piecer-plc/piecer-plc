from bs4 import BeautifulSoup
from utils import pypi_utils
from utils import files_utils


urls = ['https://docs.python.org/3.8/py-modindex.html',
        'https://docs.python.org/3.9/py-modindex.html',
        'https://docs.python.org/3.7/py-modindex.html',
        'https://docs.python.org/3.6/py-modindex.html',
        'https://docs.python.org/3.5/py-modindex.html',
        'https://docs.python.org/2.7/py-modindex.html'
        ]


def spider_build_in_models(url):
    date_html = pypi_utils.get_page(url)
    soup = BeautifulSoup(date_html, 'html.parser')
    build_in_models = soup.find_all('code', class_='xref')
    models = []
    for item in build_in_models:
        model = item.text
        models.append(model)
    return models


def get_all_build_in_models():
    build_in_models = []
    for url in urls:
        models = spider_build_in_models(url)
        for model in models:
            if model not in build_in_models:
                print(model)
                build_in_models.append(model)
    files_utils.txt_write_into(r'./build_in_models.txt', str(build_in_models))


if __name__ == '__main__':
    get_all_build_in_models()
