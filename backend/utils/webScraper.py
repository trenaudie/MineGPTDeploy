import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def download_file(url, folder_path):
    response = requests.get(url, stream=True)
    local_filename = url.split('/')[-1]

    with open(os.path.join(folder_path, local_filename), 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)


def scrape_and_download_documents(url, folder_path, cookies, extension='.pdf'):
    response = requests.get(url, cookies=cookies)
    soup = BeautifulSoup(response.content, 'html.parser')

    for link in soup.find_all('a'):
        href = link.get('href')
        if href and href.endswith(extension):
            document_url = urljoin(url, href)
            print(f'Downloading {document_url}')
            download_file(document_url, folder_path)


if __name__ == '__main__':
    # Replace with the URL of the webpage you want to scrape
    url = 'https://oasis.mines-paristech.fr/prod/bo/?targetProject=oasis_ensmp#uid=COURSE6436c2ce04e2f&code=ECUE61.1&num=22&COURSE_TYPE=TC&type=DETAIL&name=COURSE&mainTab=COURSEdocuments'
    # Replace with the desired folder path to save the documents
    folder_path = '../Backend/database/'

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    scrape_and_download_documents(url, folder_path)
