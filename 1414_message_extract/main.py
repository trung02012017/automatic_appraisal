import cv2
import pytesseract

import numpy as np

from PIL import Image
from datetime import datetime
from components import MessageExtractor, InfoExtractor


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


def pre_process_1(im):
    im = cv2.cvtColor(im, cv2.COLOR_RGB2GRAY)
    # im = cv2.GaussianBlur(im, (1, 1), 0)
    # (thresh, im) = cv2.threshold(im, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY)
    im = cv2.adaptiveThreshold(im, maxValue=255, adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                               thresholdType=cv2.THRESH_BINARY, blockSize=25, C=20)
    # im = rotate_img(im)

    return im


def pre_process_2(im):
    return im


def extract_text(im):
    # im = pre_process_1(im)
    try:
        text_preprocessed = pytesseract.image_to_string(im, lang='vie', config='--oem 3 --psm 3')
        final_text_preprocessed = [line for line in text_preprocessed.split('\n') if line.strip() != '']
        return final_text_preprocessed, im
    except pytesseract.pytesseract.TesseractError as e:
        print(e)
        return "", im


def main(im: np.ndarray, image_url: str, message_extractor: MessageExtractor, info_extractor: InfoExtractor):

    start_time = datetime.now()
    boxes = message_extractor.main_extract(image_url)
    extract_box_time = datetime.now() - start_time
    print(f">>>>>>>>>>>>>> Extract box time is {extract_box_time} s <<<<<<<<<<<<<<<<<<<<")

    for i, box in enumerate(boxes):
        # preprocess 1
        box_im = im[box[1]:box[3], box[0]:box[2], :]
        start_time = datetime.now()
        extracted_text_1, im_1 = extract_text(box_im)
        extract_text_time = datetime.now() - start_time
        print(f">>>>>>>>>>>>>> Extract text time is {extract_text_time} s <<<<<<<<<<<<<<<<<<<<")
        fullname_1 = info_extractor.extract_full_name(extracted_text_1)
        extracted_dates_1 = info_extractor.extract_date_new(extracted_text_1)
        dob_1 = extracted_dates_1[0]
        issue_date_1 = extracted_dates_1[1]
        id_card_1 = info_extractor.extract_id_card_new(extracted_text_1)

        if all([element == "" for element in [fullname_1, dob_1, issue_date_1, id_card_1]]):
            continue

        return {
            "fullname": fullname_1,
            "id_number": id_card_1,
            "dob": dob_1,
            "issue_date": issue_date_1
        }

    return {
        "fullname": "",
        "id_number": "",
        "dob": "",
        "issue_date": ""
    }

        # preprocess 2
        # extracted_text_2, im_2 = extract_text_2(im)
        # fullname_2 = extract_full_name(extracted_text_2)
        # extracted_dates_2 = extract_date_new(extracted_text_2)
        # dob_2 = extracted_dates_2[0]
        # issue_date_2 = extracted_dates_2[1]
        # id_card_2 = extract_id_card_new(extracted_text_2)
        #
        # print(extracted_text_1)
        # print(extracted_text_2)

        # return {
        #     "fullname": fullname_1 if len(fullname_1) >= len(fullname_2) else fullname_2,
        #     "id_number": id_card_1 if len(id_card_1) >= len(id_card_2) else id_card_2,
        #     "dob": dob_1 if len(dob_1) >= len(dob_2) else dob_2,
        #     "issue_date": issue_date_1 if len(issue_date_1) >= len(issue_date_2) else issue_date_2
        # }


if __name__ == '__main__':
    im = cv2.imread("/home/trungtq/Desktop/failed_images/f83f4db6-d9b2-4ffd-9c85-50baea703cf6.jpg")
    angle = pytesseract.image_to_string(im, config='--psm 0')

    print(angle)