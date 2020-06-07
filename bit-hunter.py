#!/usr/bin/env python
# Bit-Hunter by Alex Camilleri.

from io import BytesIO
import json
import os
import sys

from PIL import Image, ImageDraw
from bs4 import BeautifulSoup
from pathlib import Path
import requests
import csv
import re

from errors import GameNotFoundError, InputError


def check_folders():
    """Creates image folders if any is missing"""
    folders = ('/consume', '/originals', '/processed')
    mkdir = False
    for i, path in enumerate(folders):
        if (os.path.exists('.'+path)):
            pass
        else:
            mkdir = True
            os.makedirs('.'+path)
            print("Generating "+path+" folder...")
        if (i == len(folders)-1) and mkdir:
            print("-------------------------------")


def load_config():
    """Loads config file or creates a new one
    if none can be found"""

    data = {}

    try:
        with open('config.json') as json_data_file:
            data = json.load(json_data_file)
    except FileNotFoundError:
        print("Could not find config.json. Generating one with default values...")
        data = {
            'exportTrophyInfo': True,
            'storeOriginals': False,
            'processOriginals': True,
            'acceptedTypes': ['.PNG', '.JPG', '.JPEG'],
            'frameThickness': 15,
            'exportSizes': [240],
            'exportTypes': ['.PNG'],
            'imageNameRoot': '',
            'imageNameEnd': ''
        }
        with open('config.json', 'w') as outfile:
            json.dump(data, outfile, indent=4)
    return data


check_folders()
config = load_config()
exportTrophyInfo = config.get('exportTrophyInfo')
storeOriginals = config.get('storeOriginals')
processOriginals = config.get('processOriginals')
acceptedTypes = config.get('acceptedTypes')
frameThickness = config.get('frameThickness')
exportSizes = config.get('exportSizes')
exportTypes = config.get('exportTypes')
imageNameRoot = config.get('imageNameRoot')
imageNameEnd = config.get('imageNameEnd')


class Game:

    def __init__(self, _id):
        self.id, self.name, self.platform = _id, None, None
        self.trophies = []

    def get_soup(self):
        """Pulls HTML data from game page"""

        URL = "https://psnprofiles.com/trophies/"+str(self.id)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0"}
        page = requests.get(URL, headers=headers)
        return BeautifulSoup(page.content, 'html.parser')

    def get_name(self, _soup):
        titles = _soup.findAll("div", class_="title flex v-align center")
        if titles == []:
            raise GameNotFoundError(self.id)
        for title in titles:
            info = str(title)
            self.name = info[info.find(
                '<h3>')+4:info.find(" Trophies")].replace('&amp;', '&')
            break

    def get_all_trophies(self, _soup):
        """Stores information of every trophy"""

        tables = _soup.find_all(
            'table', class_='zebra')
        for table in tables:
            rows = table.find_all('tr', class_='')
            for row in rows:
                columns = row.find_all('td')
                if len(columns) == 6:
                    name = columns[1].find('a').get_text().strip()
                    desc = columns[1].get_text()[len(name)+1:].strip()
                    URL = "https://psnprofiles.com" + \
                        columns[1].find('a').get('href')
                    type_ = columns[5].find('img').get('title')
                    trophy = Trophy(name, desc, type_, URL)
                    self.trophies.append(trophy)

    def export_data_to_csv(self):
        """Exports trophy list to csv file"""
        filename = str(self.id)+'-'+slugify(self.name)+'.csv'
        with (open(filename, 'w', newline='')) as f:
            writer = csv.writer(f)
            writer.writerow(['Name', 'Description', 'Type'])
            for trophy in self.trophies:
                writer.writerow([trophy.name, trophy.desc, trophy.type])
            print("Game trophies info exported to " + filename)

    def process_all_trophies(self):
        """Scrapes image and apply frame to every image"""

        for trophy in self.trophies:
            if trophy.scrape():
                if storeOriginals:
                    store_remote_image(trophy.imageURL)
                if processOriginals:
                    process_image(trophy.imageURL, False,
                                  self.name, trophy.name)


class Trophy:

    def __init__(self, _name='', _desc='', _type='', _url=''):
        self.name, self.desc, self.type, self.URL = _name, _desc, _type, _url
        self.imageURL = None

    def scrape(self):
        """Scrapes URL of HD trophy image"""

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0"}
        try:
            page = requests.get(self.URL, headers=headers)
        except requests.exceptions.RequestException as e:
            print("Invalid get request for "+self.URL+"\n")
            return False
        soup = BeautifulSoup(page.content, 'html.parser')
        blocks = soup.find_all('td')
        block = str(blocks[0])
        snippet = block[block.find('href="')+6:]
        self.imageURL = snippet[:snippet.find('"')]
        print("\nTrophy:\n"+self.name+" ("+self.type+")\n"+self.desc)
        return True


def consume_images():
    """
    Chews images from the /consume folder.
    Only chews accepted filetypes defined in config file
    """

    for r, d, f in os.walk('./consume/'):
        for file in f:
            filename, file_extension = os.path.splitext(file)
            canChew = any(s in file_extension.upper()
                          for s in acceptedTypes)
            if canChew:
                path = os.path.join(r, file)
                process_image(path, True)


def slugify(value):
    """Removes invalid characters from string"""
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_').replace('.', '')


def store_remote_image(_imageURL):
    """Store image from URL"""
    URL = _imageURL
    filename = URL.split('/')[-1]
    response = requests.get(URL)
    with open(os.path.join('./originals/', filename), 'wb') as f:
        f.write(response.content)


def process_image(_imageURL='', _local=False, _game='', _trophy=''):
    """Add frame to images"""

    print("Processing "+_imageURL+"...")
    try:
        imgFrame = Image.open('./frame.png')
    except IOError:
        print("Could not find frame image. Using default one.")
        imgFrame = Image.new('RGB', (240, 240), color='#fff')
    URL = _imageURL

    if (_local):
        img = URL
    else:
        response = requests.get(URL, headers={'Cache-Control': 'no-cache'})
        img = BytesIO(response.content)

    imgTrophy = Image.open(img)
    imgTrophy_w = int(min(imgTrophy.width, imgFrame.width))
    imgTrophy_h = int(min(imgTrophy.height, imgFrame.height))
    imgTrophyResized_size = (
        imgTrophy_w-(frameThickness*2), imgTrophy_h-(frameThickness*2))
    imgTrophyResized = imgTrophy.resize(imgTrophyResized_size)

    imgFinal = Image.new('RGB', imgFrame.size, color='#fff')
    imgFinal.paste(imgFrame)
    imgFinal.paste(imgTrophyResized, (frameThickness, frameThickness))

    for i, size in enumerate(exportSizes):
        imgResized = imgFinal.resize((size, size))
        for exportType in exportTypes:
            filename = URL.split('/')[-1]
            name, extension = os.path.splitext(filename)
            name = slugify(name)
            trophy = slugify(_trophy)
            game = slugify(_game)
            root = imageNameRoot.replace(
                '@g', game).replace('@t', trophy).replace('@s', str(size))
            if root != '':
                root = root+'-'
            name = root+name
            end = imageNameEnd.replace(
                '@g', game).replace('@t', trophy).replace('@s', str(size))
            if end != '':
                end = '-'+end
            filename = name+end+exportType.lower()
            try:
                final = imgResized.save(
                    './processed/'+filename, exportType[1:])
            except KeyError:
                if exportType == ".JPG":
                    if ".JPEG" in exportTypes:
                        print("Cannot export "+filename+" to JPG.")
                    else:
                        print("Cannot export "+filename +
                              "to JPG. Exporting to JPEG.")
                        final = imgResized.save(
                            './processed/'+filename, 'JPEG')
                else:
                    print("File format "+exportType+" not supported.")


intro = """
-----------------------
__________________       ______  __             _____             
___  __ )__(_)_  /_      ___  / / /___  __________  /_____________
__  __  |_  /_  __/________  /_/ /_  / / /_  __ \  __/  _ \_  ___/
_  /_/ /_  / / /_ _/_____/  __  / / /_/ /_  / / / /_ /  __/  /    
/_____/ /_/  \__/        /_/ /_/  \__,_/ /_/ /_/\__/ \___//_/                                   
                                                              
-----------------------
"""

prompt = """
Input Game ID or type 0 to consume local images:
"""


def check_input(input):
    if input.isdigit() == False:
        if (user_input == 'exit' or user_input == 'q'):
            sys.exit()
        else:
            raise InputError()


print(intro)
while True:
    user_input = input(prompt)

    try:
        check_input(user_input)
    except InputError:
        pass
    else:
        gameID = user_input
        if (gameID == 0):
            consume_images()
            print("\nAll the trophy images have been processed!\n\n")
        else:
            game = Game(gameID)
            soup = game.get_soup()
            try:
                game.get_name(soup)
            except GameNotFoundError:
                pass
            else:
                print("\nGame Title: "+game.name+"\n")
                game.get_all_trophies(soup)
                if (exportTrophyInfo):
                    game.export_data_to_csv()
                game.process_all_trophies()
                print("\n\nAll the trophy images for " +
                      game.name+" have been processed!\n\n")
