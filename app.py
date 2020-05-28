from PIL import Image
from PIL import ImageDraw

imgFrame = Image.open('./images/frame.png')
imgFrame_size = imgFrame.size


imgTrophy = Image.open('./images/trophy.png')
imgTrophy_size = imgTrophy.size

imgTrophy_s = imgTrophy.resize((210, 210))

imgFinal = Image.new('RGB', imgFrame_size, color='#fff')
imgFinal.paste(imgFrame)
imgFinal.paste(imgTrophy_s, (15, 15))

imgFinal.show()
#final = imgFinal.save('.images/')
