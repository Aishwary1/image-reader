from flask import Flask, request
import easyocr
import os
import difflib
import cv2
import numpy as np
import urllib

app = Flask(__name__)

@app.route('/')
def hello_geek():
    return '<h1>Hello from Flask & Docker</h2>'

@app.route('/test', methods=['POST'])
def hello_test():
    data = request.get_json()
    print(data)
    file_name = data['filename']
    print(file_name)
    return file_name

#file_name = r"C:\Users\Rahul Krishna\Desktop\AIM\Images4Xtrct\Fertilizers.jpg"


def getScore(query_string, main_string):
    p1 = 0
    p2 = 0
    p3 = 0
    p4 = 0
    p5 = 0
    d_ratio = 0

    main_string_lower = [item.lower() for item in main_string]
    query_string_lower = str.lower(query_string)

    close_matches = difflib.get_close_matches(query_string_lower, main_string_lower)
    print("close matches are", close_matches)

    if len(close_matches) > 0:
        for items in close_matches:
            if query_string_lower in items:
                p1 = 1
            else:
                d_ratio = d_ratio + difflib.SequenceMatcher(None, items, query_string_lower).ratio()
                print(items, d_ratio)
        p2 = d_ratio / len(close_matches)

    else:
        p3 = 0

    # p4= getSmallScore(query_string_lower,main_string_lower)
    # print("small score is", p4)

    score = max(p1, p2, p3)
    return score


@app.route('/image', methods=['POST'])
def image_reader():
    data = request.get_json()
    print(data)
    file_name = data['filename']
    print(file_name)
    reader = easyocr.Reader(['en'], gpu=False)
    #image1 = cv2.imread(file_name)
    #read for URL
    #req = urllib.urlopen('http://answers.opencv.org/upfiles/logo_2.png')
    req = urllib.urlopen(file_name)
    arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
    image1 = cv2.imdecode(arr, -1)  # 'Load it as it is'
    image = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    print(image.shape, image.size, image.size.bit_length)
    # text_list=reader.readtext(image,detail=0)
    text_list = reader.readtext(image, add_margin=0.45, width_ths=0.8, link_threshold=0.9, decoder='beamsearch',
                                blocklist='=-', detail=0)
    print(text_list)

    query_name = str(input("Enter Name exactly as mentioned in your Document"))
    print(" you want to search for", query_name)
    score_name = getScore(query_name, text_list)
    print("score_name is", score_name)

    query_ID = str(input("Enter Document ID exactly as mentioned in your Document"))
    print(" you want to search for", query_ID)
    score_ID = getScore(query_ID, text_list)
    print("score_ID is", score_ID)

    final_score = round((score_name + score_ID) / 2, 2)

    if final_score > 0.80:
        print("Your details match by", final_score * 100, "%, Please proceed to next step")
    else:
        print("We are sorry, but your details match only by", final_score * 100,
              "% , the possible causes of low matching score may be: \n",
              "i] The text size is very small, uploaded Document Image should be larger \n"
              "ii] Name or Document ID entered by you and available in your uploaded document are different \n"
              "iii] You may have uploaded a skewed or tilted image/photo of your Document \n"
              "If you have committed any of these mistakes, please retry and proceed to next step")

    return final_score

if __name__ == "__main__":
    app.run(debug=False)
