import requests
import shutil
import os


prefix = 'https://nlp-suite.oss-cn-beijing.aliyuncs.com/'
dir_path = os.path.dirname(os.path.realpath(__file__))


def download_file(url, file_name):
    local_path = dir_path + '/' + file_name
    with requests.get(url, stream=True) as r:
        with open(local_path, 'wb') as f:
            shutil.copyfileobj(r.raw, f)


def download_jars():
    names = ['Lucene.jar','WordNet_Search_DOWN.jar', 'WordNet_Search_UP.jar']
    for name in names:
        full_url = prefix + name
        print(f'Downloading {name}...')
        download_file(full_url, name)
        print(f'Successfully downloaded {name}')


if __name__ == '__main__':
    download_jars()