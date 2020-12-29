import cv2
import os
import re
import string
import scipy
import requests
import pytesseract

import numpy as np

from unidecode import unidecode
from datetime import datetime


def rotate_img(im):
    coords = np.column_stack(np.where(im < 1))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    (h, w) = im.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(im, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    return rotated


def pre_process(im):
    im = cv2.cvtColor(im, cv2.COLOR_RGB2GRAY)
    # im = cv2.GaussianBlur(im, (1, 1), 0)
    # (thresh, im) = cv2.threshold(im, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY)
    im = cv2.adaptiveThreshold(im, maxValue=255, adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                               thresholdType=cv2.THRESH_BINARY, blockSize=25, C=20)
    # im = rotate_img(im)

    return im


def extract_text(im):
    # im = pre_process(im)
    text_preprocessed = pytesseract.image_to_string(im, lang='vie', config='--oem 3 --psm 1')
    final_text_preprocessed = [line for line in text_preprocessed.split('\n') if line.strip() != '']

    return final_text_preprocessed


if __name__ == '__main__':
    import ast
    from pprint import pprint
    file_path = "/home/trungtq/Desktop/failed_images/api.log"
    log_requests = open(file_path).read().split("\n")

    count_true_check = 0
    for i, log_line in enumerate(reversed(log_requests)):
        elements = log_line.split(" - ")

        if elements[2] == "ERROR":
            continue

        request = elements[3]
        response = elements[4]

        dict_request = ast.literal_eval(request)
        dict_response = ast.literal_eval(response)

        if elements[0].startswith('2020-12-28') and dict_response['info_check_result'] is False:
            pprint(dict_request)
            print("==========================")

    print(count_true_check)