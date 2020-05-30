from PIL import Image
from PIL import ImageDraw
from bs4 import BeautifulSoup
from io import BytesIO
import time
import urllib.request
import requests
import sys
import os
import json


def LoadConfig():
    """Loads config file or creates a new one
    if none can be found"""

    try:
        with open('config.json') as json_data_file:
            data = json.load(json_data_file)
    except FileNotFoundError:
        print("Could not find config.json. Generating one with default values.")
        data = {
            'storeOriginals': False,
            'acceptedTypes': ['.PNG', '.JPG', '.JPEG'],
            'frameWidth': 15,
            'exportSizes': [240],
            'exportTypes': ['.PNG']
        }
        with open('config.json', 'w') as outfile:
            json.dump(data, outfile, indent=4)
    return data


config = LoadConfig()
storeOriginals = config.get('storeOriginals')
acceptedTypes = config.get('acceptedTypes')
frameWidth = config.get('frameWidth')
exportSizes = config.get('exportSizes')
exportTypes = config.get('exportTypes')


urlImages = []
urlImagesHD = []


def GetTrophies(_url):
    """
    Scrapes all trophies SD images given a URL.\n
    This is a fast scrape, but not ideal
    """

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0"}

    URL = _url
    page = requests.get(URL, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    images = soup.find_all("picture", class_="trophy")

    for image in images:
        info = str(image)
        urlStart = info.find('<img src="')+10
        url_1 = info[urlStart:]
        urlEnd = url_1.find('"')
        urlImage = url_1[:urlEnd]
        urlImages.append(urlImage)


def GetTrophiesHD(_gameID):
    """
    Scrapes all trophies URLs given a game ID.\n
    Scrapes links to the single trophy pages
    """

    URL = "https://psnprofiles.com/trophies/"+str(_gameID)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0"}
    page = requests.get(URL, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    blocks = soup.find_all('td', style="width: 100%;")
    for block in blocks:
        fullSnippet = str(block)
        urlStart = fullSnippet.find('href="')+6
        url_1 = fullSnippet[urlStart:]
        urlEnd = url_1.find('"')
        urlTrophy = "https://psnprofiles.com"+url_1[:urlEnd]
        GetTrophyImage(urlTrophy)


def GetTrophyImage(_url):
    """
    Scrapes URL of HD trophies images
    """

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0"}
    URL = _url

    page = requests.get(URL, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    blocks = soup.find_all('td')
    block = str(blocks[0])

    urlStart = block.find('href="')+6
    url_1 = block[urlStart:]
    urlEnd = url_1.find('"')
    urlTrophyImage = url_1[:urlEnd]
    urlImagesHD.append(urlTrophyImage)


def SaveImagesFromURL(_imageURL):
    URL = _imageURL
    filename = URL.split('/')[-1]
    urllib.request.urlretrieve(
        URL, "./images/originals/"+filename)


def ConsumeImages():
    """
    Chews images from the /consume folder.
    Only chews accepted filetypes defined in config file
    """

    for r, d, f in os.walk('./images/consume/'):
        for file in f:
            filename, file_extension = os.path.splitext(file)
            canChew = any(s in file_extension.upper()
                          for s in acceptedTypes)
            if canChew:
                path = os.path.join(r, file)
                ProcessImage(path, True)


def ProcessImage(_imageURL='', _local=False):
    """Add frame to images"""

    imgFrame = Image.open('./images/frame.png')
    imgFrame_size = imgFrame.size
    URL = _imageURL
    filename = URL.split('/')[-1]

    if (_local):
        img = URL
    else:
        response = requests.get(URL, headers={'Cache-Control': 'no-cache'})
        img = BytesIO(response.content)

        if (storeOriginals):
            SaveImagesFromURL(URL)

    imgTrophy = Image.open(img)
    imgTrophy_width = imgTrophy.width
    imgTrophy_height = imgTrophy.height
    imgTrophyInFrame_size = (
        imgTrophy_width-(frameWidth*2), imgTrophy_width-(frameWidth*2))
    imgTrophy_s = imgTrophy.resize(imgTrophyInFrame_size)

    imgFinal = Image.new('RGB', imgFrame_size, color='#fff')
    imgFinal.paste(imgFrame)
    imgFinal.paste(imgTrophy_s, (frameWidth, frameWidth))

    for i, size in enumerate(exportSizes):
        imgResized = imgFinal.resize((size, size))
        name, extension = os.path.splitext(filename)
        for exportType in exportTypes:
            filename = name+"_"+str(size)+exportType.lower()
            final = imgResized.save(
                './images/processed/'+filename, exportType[1:])


intro = """"
-----------------------
BitImager - Kalopsia © 2020
-----------------------

Insert Game ID: """
gameID = int(input(intro))
if (gameID != 0):
    GetTrophiesHD(gameID)
else:
    ConsumeImages()
