# import the necessary packages
from PIL import Image
import re
import csv
import io
from io import BytesIO
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PIL import ImageFont
from PIL import ImageDraw
import requests
import pytesseract
import argparse
import cv2
import os




script_dir = os.path.dirname(__file__)
rel_path = "Original_Images"
dg = "Digits"
np = os.path.join(script_dir, dg)
rel_path = "Output_preprocess"
Gry_Img_Path = os.path.join(script_dir, rel_path)


subscription_key = "59cb1f192b514ad89972e7861d74a216"
assert subscription_key
vision_base_url = "https://southeastasia.api.cognitive.microsoft.com/vision/v2.0/"
ocr_url = vision_base_url + "ocr"

# Read the image into a byte array
headers = {'Ocp-Apim-Subscription-Key': subscription_key, 'Content-Type': 'application/octet-stream'}
params = {'language': 'unk', 'detectOrientation': 'true'}

fnames = os.listdir("Digits")
fnames2 = os.path.join(script_dir, rel_path)

for Org_Img_Path in fnames:
        if os.path.isdir(os.path.join(os.path.abspath("Digits"), Org_Img_Path)):
            print("Starting with: "+Org_Img_Path)
            Gry_Img_Path = os.path.join(fnames2, Org_Img_Path)
            os.makedirs(Gry_Img_Path)
            print("created a folder: " + Gry_Img_Path)
            with open(os.path.join(Gry_Img_Path, Gry_Img_Path+".csv"), mode='w') as reading_file:
                reading_writer = csv.writer(reading_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                reading_writer.writerow(["Image Name", "Reading"])
                for file in os.listdir(os.path.join(np, Org_Img_Path)):
                    filename = os.fsdecode(file)
                    if filename.endswith(".jpg") or filename.endswith(".jpeg"):
                        abs_file_path = os.path.join(os.path.join(np, Org_Img_Path), filename)
                        Gry_Img_Path = os.path.join(os.path.join(fnames2, Org_Img_Path), filename)
                        image_data = open(abs_file_path, "rb").read()

                        basewidth = 1000
                        img = cv2.imread(abs_file_path)
                        gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                        gray_image = cv2.medianBlur(gray_image, 3)
                        gray_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
                        cv2.imwrite(abs_file_path, gray_image)
                        img = Image.open(abs_file_path)

                        wpercent = (basewidth / float(img.size[0]))
                        hsize = int((float(img.size[1]) * float(wpercent)))
                        img = img.resize((basewidth, hsize), Image.ANTIALIAS)

                        imgByteArr = io.BytesIO()
                        img.save(imgByteArr, format='jpeg')
                        image_data = imgByteArr.getvalue()

                        response = requests.post(ocr_url, headers=headers, params=params, data=image_data)
                        try:
                            response.raise_for_status()
                        except requests.exceptions.HTTPError:
                            print("Error reading file")
                            continue
                        analysis = response.json()

                        # Extract the word bounding boxes and text.
                        line_infos = [region["lines"] for region in analysis["regions"]]
                        word_infos = []
                        for line in line_infos:
                            for word_metadata in line:
                                for word_info in word_metadata["words"]:
                                    word_infos.append(word_info)
                        word_infos

                        # Display the image and overlay it with the extracted text.
                        result = ""
                        for word in word_infos:
                            #bbox = [int(num) for num in word["boundingBox"].split(",")]
                            text = word["text"]
                            if re.findall(r"[-+]?\d*\.\d+|\d+", text):
                                result = result + re.findall(r"[-+]?\d*\.\d+|\d+", text)[0]
                        plt.axis("off")

                        image = img #Image.open(abs_file_path)
                        draw = ImageDraw.Draw(image)
                        fontsize = 1  # starting font size

                        # portion of image width you want text width to be
                        img_fraction = 0.40

                        font = ImageFont.truetype("arial.ttf", fontsize)
                        # while font.getsize(result)[0] < img_fraction * image.size[0]:
                        #     # iterate until the text size is just larger than the criteria
                        #     print("IN font loop")
                        #     fontsize += 1
                        #     font = ImageFont.truetype("arial.ttf", fontsize)

                        # optionally de-increment to be sure it is less than criteria
                        fontsize = 21
                        font = ImageFont.truetype("arial.ttf", fontsize)

                        # print
                        # 'final font size', fontsize
                        draw.text((0, 0), result, font=font)  # put the text on the image
                        abs_file_path = os.path.join(Gry_Img_Path, filename)
                        image.save(Gry_Img_Path)  # save it

                        print(result + " : " + Gry_Img_Path)
                        try:
                            reading_writer.writerow([filename.rstrip(), result.rstrip()])
                        except UnicodeEncodeError:
                            print("Unicode conversion error")
                            continue

                    # for file in os.listdir(Org_Img_Path):
                    #     filename = os.fsdecode(file)
                    #     if filename.endswith(".jpg") or filename.endswith(".jpeg"):
                    #         abs_file_path = os.path.join(Org_Img_Path, filename)
                    #         image = cv2.imread(abs_file_path)
                    #         gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    #
                    #         gray_image = cv2.medianBlur(gray_image, 3)
                    #         gray_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
                    #
                    #         abs_file_path = os.path.join(Gry_Img_Path, filename)
                    #         cv2.imwrite(abs_file_path, gray_image)
                    #         print("Innfor loop")
                    #         config = '-l eng --oem 1 --psm 3'
                    #         text = pytesseract.image_to_string(Image.open(abs_file_path), config=config)
                    #         #os.remove(filename)
                    #         print(text)
                    #
                    #         #cv2.imshow('color_image', image)
                    #         #cv2.imshow('gray_image', gray_image)
                    #         #cv2.waitKey(0)  # Waits forever for user to press any key
                    #         cv2.destroyAllWindows()
                    #         continue
                    #     else:
                    #         continue

                    #image = cv2.imread(abs_file_path)
                    #gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    #dst = cv2.fastNlMeansDenoisingColored(gray_image, None, 10, 10, 7, 21)
                    #cv2.imwrite('gray_image.png', gray_image)
                    #cv2.imshow('color_image', image)
                    #cv2.imshow('gray_image', gray_image)
                    cv2.waitKey(0)  # Waits forever for user to press any key
                    cv2.destroyAllWindows()  # Closes displayed windows
# End of Code