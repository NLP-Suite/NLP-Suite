import sys
import GUI_util
import IO_libraries_util

# if IO_libraries_util.install_all_Python_packages(GUI_util.window,"POTUS_webscraper.py",['beautifulsoup4'])==False:
#     sys.exit(0)

import tkinter as tk
import requests
# conda install -c anaconda beautifulsoup4
from bs4 import BeautifulSoup
import os
import shutil

base_url = "https://www.presidency.ucsb.edu/" # base website url for link redirects
out_path = tk.filedialog.askdirectory(title='Select a directory where to save the scraped POTUS files. The fiiles will be saved in a subdirectory "\data" of the selected directory.\n Press Esc or Cancel to exit.')

out_path = out_path # folder for output saving
if out_path=='':
    sys.exit(0)
else:
    out_path = out_path + os.sep + "POTUS_data/"
if not os.path.exists(out_path):
    os.mkdir(out_path)
else:
    # remove/delete and recreate directory
    shutil.rmtree(out_path)
    os.mkdir(out_path)

# Base link for inaugural address speeches
ina_base = "https://www.presidency.ucsb.edu/advanced-search?field-keywords=&field-keywords2=&field-keywords3=&from%5Bdate%5D=&to%5Bdate%5D=&person2=&category2%5B%5D=46&items_per_page=100"

# Base link for State Of the Union Speeches
sotu_base = "https://www.presidency.ucsb.edu/advanced-search?field-keywords=&field-keywords2=&field-keywords3=&from%5Bdate%5D=&to%5Bdate%5D=&person2=&category2%5B%5D=45&category2%5B%5D=400&items_per_page=100"

"""
    Speech stores data about an individual speech
"""
class Speech():
    """
    Store data about each individual speech with functionality to write to a file

    link: str
        The URL Link for each speech
    date: str
        The raw date parsed from the html page
    president: str
        The raw president name parsed from the html page
    text: str
        The raw speech contents parsed from the html page
    """
    def __init__(self, link: str, date: str, president: str, text: str):
        self.link = link
        self.date = date
        self.president = president
        self.text = text


    """
    Writes the speech text to a file with the format:
        ./out_path/prefix_president_date.txt

    prefix: str
        The prefix that goes before the file name
    """
    def writeToFile(self, prefix: str):
        date = self.date.lower().split(" ")
        # Get rid of the date formatting and comma
        date = date[0] + "_" + date[1][:-1] + "_" + date[2]
        # Get rid of any punctuation in the name
        name = self.president.replace(".", "").lower().split(" ")
        name = "_".join(name)

        try:
            with open(f'./{out_path + prefix}_{name}_{date}.txt', "x") as f:
                f.write(self.text)
        except Exception:
            print(f"got duplicate speech {self.link}")


"""
    Get speeches from a base URL

    base: str
        The base URL to start recursively web crawling

    returns: list
        A list of Speech objects
"""
def getSpeeches(base: str) -> list:
    resp = requests.get(base)
    soup = BeautifulSoup(resp.content, "html.parser")

    odd_data = soup.find_all("tr", class_="odd")
    even_data = soup.find_all("tr", class_="even")

    data = even_data + odd_data
    speeches = []

    for item in data:
        metadata = item.find_all("td", class_="views-field")
        link = base_url + metadata[2].find("a")['href']
        date = metadata[0].text.strip().lower()
        president = metadata[1].text.strip().lower()
        speeches.append(getSpeech(link, date, president))

    nextLink = soup.find("li", class_="next")
    if nextLink is not None:
        speeches += getSpeeches(base_url + nextLink.find("a")["href"])

    print(f'{base} got {len(speeches)} speeches')
    return speeches


"""
    Get the speech contents from a speech URL

    link: str
        The URL to the speech
    date: str
        The raw date parsed from the parent HTML page
    president: str
        The raw president name parsed from the parent HTML page

    returns: Speech
        The Speech object created from the parsed data
"""
def getSpeech(link: str, date: str, president: str) -> Speech:
    resp = requests.get(link)
    soup = BeautifulSoup(resp.content, "html.parser")
    speech = soup.find_all("div", class_="field-docs-content")
    if speech is None or len(speech) < 1:
        print(f"[WARNING] {link} may be corrupt...")

    text = []
    for p in speech:
        text.append(p.text)

    return Speech(link, date, president, "\n".join(text))


if __name__ == "__main__":
    # Get the inaugural speeches
    for speech in getSpeeches(ina_base):
        speech.writeToFile("ina")

    # Get the State of the Union Speeches
    for speech in getSpeeches(sotu_base):
        speech.writeToFile("sotu")