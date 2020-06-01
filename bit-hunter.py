#!/usr/bin/env python
# Copyright 2020 by Alex Camilleri.
# All rights reserved.

from io import BytesIO
import json
import os
import sys

from PIL import Image
from PIL import ImageDraw
from bs4 import BeautifulSoup
from pathlib import Path
import requests
import urllib.request
import time
import re


def CheckFolders():
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


def LoadConfig():
    """Loads config file or creates a new one
    if none can be found"""

    try:
        with open('config.json') as json_data_file:
            data = json.load(json_data_file)
    except FileNotFoundError:
        print("Could not find config.json. Generating one with default values...")
        data = {
            'storeOriginals': False,
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


CheckFolders()
config = LoadConfig()
storeOriginals = config.get('storeOriginals')
acceptedTypes = config.get('acceptedTypes')
frameThickness = config.get('frameThickness')
exportSizes = config.get('exportSizes')
exportTypes = config.get('exportTypes')
imageNameRoot = config.get('imageNameRoot')
imageNameEnd = config.get('imageNameEnd')


class Trophy:

    def __init__(self, _name='', _desc='', _url=''):
        self.name, self.desc, self.URL = _name, _desc, _url
        self.imageURL = None

    def Scrape(self):
        """Scrapes URL of HD trophy image"""

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0"}
        print(self)
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
        print("Trophy: "+self.name)
        return True


class Game:

    def __init__(self, _id):
        self.id, self.name, self.platform = _id, None, None
        self.trophies = []

    def GetSoup(self):
        """Pulls HTML data from game page"""

        URL = "https://psnprofiles.com/trophies/"+str(self.id)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0"}
        page = requests.get(URL, headers=headers)
        return BeautifulSoup(page.content, 'html.parser')

    def GetName(self, _soup):
        titles = _soup.findAll("div", class_="title flex v-align center")
        for title in titles:
            info = str(title)
            self.name = info[info.find(
                '<h3>')+4:info.find(" Trophies")].replace('&amp;', '&')
            break

    def GetAllTrophies(self, _soup):
        """Stores information of every trophy"""

        blocks = _soup.find_all('td', style="width: 100%;")
        for block in blocks:
            data = str(block)
            snippet = data[data.find('href="')+6:]

            title = snippet[snippet.find('">')+2:snippet.find('</a>')]
            URL = "https://psnprofiles.com"+snippet[:snippet.find('"')]
            desc = snippet[snippet.find('<br/>')+5:snippet.find('</td>')]

            trophy = Trophy(title, desc, URL)
            self.trophies.append(trophy)

    def ProcessAllTrophies(self):
        """Scrapes image and apply frame to every image"""

        for trophy in self.trophies:
            if trophy.Scrape():
                print(self.name)
                ProcessImage(trophy.imageURL, False, self.name, trophy.name)


def SaveImagesFromURL(_imageURL):

    URL = _imageURL
    filename = URL.split('/')[-1]
    urllib.request.urlretrieve(
        URL, "./originals/"+filename)


def ConsumeImages():
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
                ProcessImage(path, True)


def Slugify(value):
    """Removes invalid characters from string"""
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_').replace('.', '')


def ProcessImage(_imageURL='', _local=False, _game='', _trophy=''):
    """Add frame to images"""

    print("Processing "+_imageURL+"...\n")
    try:
        imgFrame = Image.open('./frame.png')
    except IOError:
        print("Could not find frame image. Using default one.")
        imgFrame = Image.new('RGB', (240, 240), color='#fff')
    imgFrame_size = imgFrame.size
    URL = _imageURL

    if (_local):
        img = URL
    else:
        response = requests.get(URL, headers={'Cache-Control': 'no-cache'})
        img = BytesIO(response.content)

        if (storeOriginals):
            SaveImagesFromURL(URL)

    imgTrophy = Image.open(img)
    imgTrophy_w = int(imgTrophy.width)
    imgTrophy_h = int(imgTrophy.height)
    imgTrophyResized_size = (
        imgTrophy_w-(frameThickness*2), imgTrophy_h-(frameThickness*2))
    imgTrophyResized = imgTrophy.resize(imgTrophyResized_size)

    imgFinal = Image.new('RGB', imgFrame_size, color='#fff')
    imgFinal.paste(imgFrame)
    imgFinal.paste(imgTrophyResized, (frameThickness, frameThickness))

    for i, size in enumerate(exportSizes):
        imgResized = imgFinal.resize((size, size))
        for exportType in exportTypes:
            filename = URL.split('/')[-1]
            name, extension = os.path.splitext(filename)
            name = Slugify(name)
            trophy = Slugify(_trophy)
            game = Slugify(_game)
            root = imageNameRoot.replace(
                '@g', game).replace('@t', trophy).replace('@s', str(size))
            if root != '':
                root = root+'-'
            name = root+name
            end = imageNameEnd.replace(
                '@g', game).replace('@t', trophy).replace('@s', str(size))
            if end != '':
                end = '-'+end
            filename = name+'-'+imageNameEnd+exportType.lower()
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
BitHunter - Kalopsia © 2020
-----------------------
"""

prompt = """
Input Game ID or type 0 to consume local images:
"""

print(intro)
while True:
    user_input = input(prompt)
    if (user_input == 'exit' or user_input == 'q'):
        break
    else:
        try:
            gameID = int(user_input)
            if (int(gameID) == 0):
                ConsumeImages()
                print("\nAll the trophy images have been processed!\n\n")
            else:
                game = Game(int(gameID))
                soup = game.GetSoup()
                game.GetName(soup)
                print("Game Title: "+game.name+"\n")
                time.sleep(0.5)
                game.GetAllTrophies(soup)
                game.ProcessAllTrophies()
                print("\n\nAll the trophy images for " +
                      game.name+" have been processed!\n\n")

        except ValueError:
            print('Please enter a valid GameID or type `exit` to quit')
