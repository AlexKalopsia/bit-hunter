from PIL import Image
from PIL import ImageDraw
from bs4 import BeautifulSoup
from io import BytesIO
import time
import urllib.request
import requests
import sys
import os
import config

# Trophies scraping

urlImages = []
urlImagesHD = []


def GetTrophies(_url):

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
    filename = URL.split('/')[-1]
    urllib.request.urlretrieve(
        URL, "./images/originals/"+filename)


def ConsumeImages():
    for r, d, f in os.walk('./images/consume/'):
        for file in f:
            filename, file_extension = os.path.splitext(file)
            canChew = any(s in file_extension.upper()
                          for s in config.fileTypes)
            if canChew:
                path = os.path.join(r, file)
                ProcessImage(path, True)


def ProcessImage(_imageURL='', _local=False):
    imgFrame = Image.open('./images/frame.png')
    imgFrame_size = imgFrame.size
    URL = _imageURL
    filename = URL.split('/')[-1]

    if (_local):
        img = URL
    else:
        response = requests.get(URL, headers={'Cache-Control': 'no-cache'})
        img = BytesIO(response.content)

        if (config.storeOriginals):
            SaveImagesFromURL(URL)

    imgTrophy = Image.open(img)
    imgTrophy_size = imgTrophy.size
    imgTrophy_s = imgTrophy.resize((210, 210))

    imgFinal = Image.new('RGB', imgFrame_size, color='#fff')
    imgFinal.paste(imgFrame)
    imgFinal.paste(imgTrophy_s, (15, 15))

    # imgFinal.show()
    print(os.getcwd())
    final = imgFinal.save(
        './images/processed/'+filename, 'PNG')


ConsumeImages()

# GetTrophiesHD(10904)
# for urlImage in urlImagesHD:
#    ProcessImage(urlImage)
