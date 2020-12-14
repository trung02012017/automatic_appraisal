import cv2
import os
import re
import string
import pytesseract

import numpy as np

from unidecode import unidecode
from datetime import datetime


regex = {
    "date": r"\d{1,2}/\d{2}/\d{4}",
    "fullname": [r"[\s:]*Ho\sten[:]\s*['AĂÂÁẮẤÀẰẦẢẲẨÃẴẪẠẶẬĐEÊÉẾÈỀẺỂẼỄẸỆIÍÌỈĨỊOÔƠÓỐỚÒỒỜỎỔỞÕỖỠỌỘỢUƯÚỨÙỪỦỬŨỮỤỰYÝỲỶỸỴ"
                 r"aăâáắấàằầảẳẩãẵẫạặậđeêéếèềẻểẽễẹệiíìỉĩịoôơóốớòồờỏổởõỗỡọộợuưúứùừủửũữụựyýỳỷỹỵA-Zaa-z\s]+[,.;(]{0,1}\s*",
                 r"[\s:]*Ho\sva\sten[:]\s*['AĂÂÁẮẤÀẰẦẢẲẨÃẴẪẠẶẬĐEÊÉẾÈỀẺỂẼỄẸỆIÍÌỈĨỊOÔƠÓỐỚÒỒỜỎỔỞÕỖỠỌỘỢUƯÚỨÙỪỦỬŨỮỤỰYÝỲỶỸỴ"
                 r"aăâáắấàằầảẳẩãẵẫạặậđeêéếèềẻểẽễẹệiíìỉĩịoôơóốớòồờỏổởõỗỡọộợuưúứùừủửũữụựyýỳỷỹỵA-Zaa-z\s]+[,.;(]{0,1}\s*"]
}


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


def extract_text_1(im):
    im = pre_process_1(im)
    text_preprocessed = pytesseract.image_to_string(im, lang='vie', config='--oem 3 --psm 1')
    final_text_preprocessed = [line for line in text_preprocessed.split('\n') if line.strip() != '']

    return final_text_preprocessed, im


def extract_text_2(im):
    im = pre_process_2(im)
    text_preprocessed = pytesseract.image_to_string(im, lang='vie', config='--oem 3 --psm 1')
    final_text_preprocessed = [line for line in text_preprocessed.split('\n') if line.strip() != '']

    return final_text_preprocessed, im


def extract_full_name(extracted_text):
    text = unidecode(" ".join(extracted_text)).replace(";", ":")

    for re_fullname in regex['fullname']:
        fullname_string = re.findall(re_fullname, text)
        if len(fullname_string) == 0:
            continue
        fullname = fullname_string[-1].strip().split(":")[-1].strip()
        if len(fullname.strip()) == 0:
            continue
        fullname = " ".join([w for w in fullname.split(" ") if w[0].isupper()])
        fullname = unidecode(fullname).translate(str.maketrans('', '', string.punctuation))
        return fullname
    return ""


def extract_date_new(extracted_text):
    final_dates = []
    extracted_text = " ".join(extracted_text).replace(" ", "")
    extracted_dates = re.findall(regex['date'], extracted_text)
    extracted_dates = list(reversed(extracted_dates))

    for i, date_string in enumerate(extracted_dates):
        try:
            date_ = datetime.strptime(date_string, "%d/%m/%Y")
        except ValueError:
            continue
        if 18 <= datetime.now().year - date_.year <= 80:
            final_dates.append(date_string)
            if i - 1 >= 0:
                final_dates.append(extracted_dates[i - 1])
            else:
                final_dates.append("")
            return final_dates
        else:
            continue

    return ["", ""]


def extract_date(extracted_text):
    extracted_dates = []
    for line in extracted_text:
        found_dob = re.findall(regex['date'], line)
        if len(found_dob) == 0:
            continue
        date_string = found_dob[0]

        try:
            date_dob = datetime.strptime(date_string, "%d/%m/%Y")

            if len(extracted_dates) == 0:
                if 18 <= datetime.now().year - date_dob.year <= 80:
                    extracted_dates.append(date_string)
                else:
                    extracted_dates.append("")
            else:
                if 0 <= datetime.now().year - date_dob.year <= 15:
                    extracted_dates.append(date_string)
                else:
                    extracted_dates.append("")
        except ValueError:
            print(date_string)
            print("wrong format for date")
            extracted_dates.append("")

        if len(extracted_dates) == 2:
            return extracted_dates

    for _ in range(2):
        extracted_dates.append("")
        if len(extracted_dates) == 2:
            return extracted_dates


def extract_id_card_new(extracted_text):
    extracted_text = " ".join(extracted_text).replace("'", "")

    regex_1_id = r"(cuoc[:]*\d{12}[,;.]*)|(cuoc[:]*\d{9}[,;.]*)|(CMT[:]*\d{12}[,;.]*)" \
                 r"|(CMT[:]*\d{9}[,;.]*)|(to[:]*\d{12}[,;.]*)|(to[:]*\d{9}[,;.]*)"
    regex_2_id = r"([\s:o]\d{12}[,;.])|([\s:o]\d{9}[,;.])"
    id_numbers = re.findall(regex_1_id, extracted_text.replace(" ", ""))
    if len(id_numbers) == 0:
        id_numbers = re.findall(regex_2_id, extracted_text)
        if len(id_numbers) == 0:
            return ""
        else:
            id_number = [_ for _ in id_numbers[0] if len(_) > 0][0]
            id_number = id_number.translate(str.maketrans('', '', string.punctuation)).replace(" ", "")
            id_number = "".join([c for c in id_number if c.isdigit()])
            return id_number
    else:
        id_number = [_ for _ in id_numbers[-1] if len(_) > 0][0]
        id_number = id_number.translate(str.maketrans('', '', string.punctuation)).replace(" ", "")
        id_number = "".join([c for c in id_number if c.isdigit()])
        return id_number


def extract_id_card(extracted_text):
    for line in extracted_text:
        id_number = re.findall(regex['id_card'], line)

        if len(id_number) > 0:
            id_number = [_ for _ in id_number[0] if len(_) > 0][0]
            id_number = id_number.translate(str.maketrans('', '', string.punctuation)).replace(" ", "")
            id_number = "".join([c for c in id_number if not c.isalpha()])
            return id_number
    return ""


def main(im):

    # preprocess 1
    extracted_text_1, im_1 = extract_text_1(im)
    fullname_1 = extract_full_name(extracted_text_1)
    extracted_dates_1 = extract_date_new(extracted_text_1)
    dob_1 = extracted_dates_1[0]
    issue_date_1 = extracted_dates_1[1]
    id_card_1 = extract_id_card_new(extracted_text_1)

    # preprocess 2
    extracted_text_2, im_2 = extract_text_2(im)
    fullname_2 = extract_full_name(extracted_text_2)
    extracted_dates_2 = extract_date_new(extracted_text_2)
    dob_2 = extracted_dates_2[0]
    issue_date_2 = extracted_dates_2[1]
    id_card_2 = extract_id_card_new(extracted_text_2)

    print(extracted_text_1)
    print(extracted_text_2)

    return {
        "fullname": fullname_1 if len(fullname_1) >= len(fullname_2) else fullname_2,
        "id_number": id_card_1 if len(id_card_1) >= len(id_card_2) else id_card_2,
        "dob": dob_1 if len(dob_1) >= len(dob_2) else dob_2,
        "issue_date": issue_date_1 if len(issue_date_1) >= len(issue_date_2) else issue_date_2
    }


# if __name__ == '__main__':
#
#     from pprint import pprint
#
#     im = cv2.imread("/home/trungtq/Desktop/failed_images/9137b3b7-d75f-4c2a-9a51-6f95cc3b0cc6.jpg")
#     extracted_info, im = main(im)
#     pprint(extracted_info)
#     cv2.imshow("a", im)
#     cv2.waitKey(0)