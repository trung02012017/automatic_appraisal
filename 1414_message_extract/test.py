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


def test_api_extract_message(request):
    import requests

    url = "http://18.138.46.64:8082/message-validate/check_info_message"

    headers = {
        'Authorization': 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJhaS10ZXN0IiwiYXV0aG9yaXRpZXMiOlsiUk9MRV9DQUNfVE9PT'
                         'F9WRVJJRlkiLCJST0xFX0NPTVBVVEVSX1ZJU0lPTl9BRE1JTiIsIlJPTEVfQ09NUFVURVJfVklTSU9OX0VLWUNfVj'
                         'IiLCJST0xFX0NPTVBVVEVSX1ZJU0lPTl9OQVRfRVhUUkFDVE9SIiwiUk9MRV9DT05UUkFDVF9FWFRSQUNUX0FETUl'
                         'OIiwiUk9MRV9DUkFXTEVSX1RPT0xfQURNSU4iLCJST0xFX0NSRURJVF9TQ09SRV9BRE1JTiIsIlJPTEVfRkFDRUJP'
                         'T0tfSU5GT19BRE1JTiIsIlJPTEVfRkFDRUJPT0tfU0NPUkVfQURNSU4iLCJST0xFX0lERU5USUZZX1RPT0xfQURNS'
                         'U4iLCJST0xFX0xFQURfU0NPUkVfQURNSU4iLCJST0xFX01FU1NBR0VfVkFMSURBVEUiLCJST0xFX1BSRURJQ1RfUF'
                         'JJQ0VfQURNSU4iLCJST0xFX1BST0RVQ1RfSU5GT19BRE1JTiIsIlJPTEVfVEFYX1RPT0xfQURNSU4iLCJST0xFX1'
                         'RPUF9GUklFTkRfQURNSU4iLCJST0xFX1RSQUNLX0xPQ0FUSU9OX0FETUlOIiwiUk9MRV9VU0VSX0lOVEVSRVNUX'
                         '0FETUlOIiwiUk9MRV9WRUhJQ0xFX0RBVEFfQU1ESU4iXSwiaWF0IjoxNjA5MTQ0OTEzLCJleHAiOjE2MDkyMzEzM'
                         'TN9.Ih6BcmaB9ebzl_C5vwpx9svXqS5nnsWA2eNQA-xPbxkZuXD16L9gPbsm9dpkFVCHavn98tqvD27dtSnMe49eYw',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, json=request)

    return response.json()


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

        if elements[0].startswith('2020-12-28') and dict_response['info_check_result'] is True:
            new_response = test_api_extract_message(dict_request)
            print(dict_request['image_url'])
            if new_response['compare_results'] is None:
                print("New response fail")
                continue

            pprint(f"result_check_compare: {[dict_response['compare_results'][k] == new_response['compare_results'][k] for k in dict_response['compare_results'].keys()]}")
            print()
            pprint(f"old_result_extract: {dict_response['extracted_info']}")
            pprint(f"new_result_extract: {new_response['extracted_info']}")

            print("==========================")

    print(count_true_check)