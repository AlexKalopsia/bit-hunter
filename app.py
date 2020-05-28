from PIL import Image
from PIL import ImageDraw
from bs4 import BeautifulSoup
from io import BytesIO
import requests
import sys

# Trophies scraping
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0"}

URL = "https://psnprofiles.com/trophies/10903-atomicrops"
page = requests.get(URL, headers=headers)
soup = BeautifulSoup(page.content, 'html.parser')
images = soup.find_all("picture", class_="trophy")

urlImages = []

for image in images:
    info = str(image)
    urlStart = info.find('<img src="')+10
    url_1 = info[urlStart:]
    urlEnd = url_1.find('"')
    #urlEnd = info.find('"></img></picture>')
    urlImage = url_1[:urlEnd]

    print(urlImage)
    urlImages.append(urlImage)

for urlImage in urlImages:
    response = requests.get(urlImage)

# Image processing


def ProcessImage(_image):
    imgFrame = Image.open('./images/frame.png')
    imgFrame_size = imgFrame.size

    imgTrophy = Image.open('./images/trophy.png')
    imgTrophy_size = imgTrophy.size

    imgTrophy_s = imgTrophy.resize((210, 210))

    imgFinal = Image.new('RGB', imgFrame_size, color='#fff')
    imgFinal.paste(imgFrame)
    imgFinal.paste(imgTrophy_s, (15, 15))

    # imgFinal.show()
    #final = imgFinal.save('.images/')
