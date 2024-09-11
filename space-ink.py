
#!/usr/bin/python
# -*- coding:utf-8 -*-
import requests
import time
import pytz
import logging
import sys
import os
import glob
# Import date class from datetime module
from datetime import date, datetime

from lib.waveshare_epd import epd5in65f
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

def get_current_time_12hour():
    """Gets the current time in 12-hour format for the current timezone."""

    current_time = datetime.now(pytz.timezone('America/Chicago'))
    return current_time.strftime("%I:%M:%S %p")

def fetchImage() -> dict:

    # replace API_KEY with key from NASA API
    requestURL = 'https://api.nasa.gov/planetary/apod?api_key={API_KEY}'
    searchResponse = requests.get(requestURL)
    # extracting data in json format
    imageData = searchResponse.json()
    return imageData

def downloadImage(imageUrl, imagesDirectoryPath, titleFormatted):
    try:
        response = requests.get(imageUrl)
    except:
        print('Error fetching image')
        print(sys.exc_info()[0])
    else:
        if response.status_code == 200:
            with open(imagesDirectoryPath + titleFormatted + '.jpg', 'wb') as f:
                f.write(response.content)
    print('apod downloaded to local filesystem')

def addTextToImage(image_path, text, font_path, font_size, text_color=(0, 0, 0)):
    """
    Adds text to the bottom center of an image.

    Args:
        image_path: Path to the image.
        text: Text to be added.
        font_path: Path to the font file.
        font_size: Font size.
        text_color: Color of the text (default: black).
    """

    # Open the image
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)

    # Load the font
    font = ImageFont.truetype(font_path, font_size)
    smallFont =  ImageFont.truetype(font_path, 18)

    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Calculate the position
    x = (image.width - text_width) // 2
    y = image.height - text_height - 10  # 10 for a small padding from the bottom

    # Draw the text
    draw.text((x, y), text, font=font, fill=text_color)

    # add the date to the top middle of the frame
    today = date.today()

    # Calculate text position for top middle
    x = (image.width - text_width) // 2
    y = 0  # Adjust this for top margin

    # Draw the text
    draw.text((x, y), "Rendered at: " + today.strftime("%Y-%m-%d") + " " + get_current_time_12hour(), font=smallFont, fill=text_color)

    # Save the image
    image.save(image_path)
    print('added text to image')


def resizeImage(image, imagePath):
    # Resizing the image, given our display we want to ensure the photo fits well
    # resizing by this equation so the size is 15% smaller than max resolution of module
    img = image.resize((int(600 * 0.85), int(448 * 0.85)), Image.Resampling.LANCZOS)

    # raise saturation
    converter = ImageEnhance.Color(img)
    image = converter.enhance(2)

    # Create a new white background image
    background = Image.new("RGB", (600, 448), (255, 255, 255))

    # Paste the image onto the background
    background.paste(image, (50,24))

    # Saving the resized image with new background
    background.convert('RGB').save(imagePath)
    print('resized image')


def main():
    today = date.today()
    print('script started at ' + today.strftime("%Y-%m-%d") + " " + get_current_time_12hour())
    try:
        # fetch a dict of image data
        selectedImageData = fetchImage()
        # creating a list for the characters to be replaced
        char_remov = [" ", ",", ":", "(", ")", '"', "/", ";", "'"]

        originalTitle = selectedImageData['title']

        for char in char_remov:
            # remove potentially problematic chars from string we want to use in the filepath to avoid issues
            selectedImageData['title'] = selectedImageData['title'].replace(char, "_")

        titleFormatted = selectedImageData['title'].lower()

        imagesDirectoryPath = os.path.dirname(
        os.path.realpath(__file__)) + '/images/'

        fontsDirectoryPath = os.path.dirname(
        os.path.realpath(__file__)) + '/fonts/'

        # first off, to save space remove any lingering jpg files from old script runs
        removingJpgs = glob.glob(imagesDirectoryPath + '*.jpg')
        for i in removingJpgs:
            os.remove(i)

        # after we have our image URL, lets download it and save to directory
        downloadImage(selectedImageData['url'],
                imagesDirectoryPath, titleFormatted)

        # after downloaded, check if the dimensions need to be adjusted to fit onto the e-paper display
        filepath = imagesDirectoryPath + titleFormatted
        img = Image.open(filepath + '.jpg')

        # resize and place in white background
        resizeImage(img, filepath + ".jpg")

        # add title to image
        addTextToImage(filepath + ".jpg", originalTitle, fontsDirectoryPath + "Font.ttc", 30)

        img = Image.open(filepath + '.jpg')
        logging.basicConfig(level=logging.DEBUG)
        epd = epd5in65f.EPD()
        logging.info(epd)
        epd.init()
        epd.Clear()

        Himage = Image.new('RGB', (epd.height, epd.width),
                           0xffffff)  # 255: clear the frame
        draw = ImageDraw.Draw(Himage)
        epd.display(epd.getbuffer(Himage))
        time.sleep(3)
        epd.display(epd.getbuffer(img))
        time.sleep(3)
        print('displayed the photo' + filepath + '.jpg')
        quit()
    except IOError as e:
        print('something went wrong :(')
        print(e)
    except KeyboardInterrupt:
        logging.info("ctrl + c:")
        epd5in65f.epdconfig.module_exit()
        exit()

main()