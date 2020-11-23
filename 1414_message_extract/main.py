import cv2
import os
import re
import string
import pytesseract

import numpy as np

from unidecode import unidecode
from datetime import datetime


regex = {
    "id_card": r"([\s:]\d{9}[,;.])|([\s:]\d{12}[,;.])",
    "date": r"\d{1,2}/\d{2}/\d{4}",
    "fullname": [r"\s*Ho\sten: [AĂÂÁẮẤÀẰẦẢẲẨÃẴẪẠẶẬĐEÊÉẾÈỀẺỂẼỄẸỆIÍÌỈĨỊOÔƠÓỐỚÒỒỜỎỔỞÕỖỠỌỘỢUƯÚỨÙỪỦỬŨỮỤỰYÝỲỶỸỴ"
                 r"aăâáắấàằầảẳẩãẵẫạặậđeêéếèềẻểẽễẹệiíìỉĩịoôơóốớòồờỏổởõỗỡọộợuưúứùừủửũữụựyýỳỷỹỵA-Zaa-z\s]+[,.;]{0,1}\s",
                 r"\s*Họ\sten: [AĂÂÁẮẤÀẰẦẢẲẨÃẴẪẠẶẬĐEÊÉẾÈỀẺỂẼỄẸỆIÍÌỈĨỊOÔƠÓỐỚÒỒỜỎỔỞÕỖỠỌỘỢUƯÚỨÙỪỦỬŨỮỤỰYÝỲỶỸỴ"
                 r"aăâáắấàằầảẳẩãẵẫạặậđeêéếèềẻểẽễẹệiíìỉĩịoôơóốớòồờỏổởõỗỡọộợuưúứùừủửũữụựyýỳỷỹỵA-Zaa-z\s]+[,.;]{0,1}\s",
                 r"\s*Ho\sva\sten: [AĂÂÁẮẤÀẰẦẢẲẨÃẴẪẠẶẬĐEÊÉẾÈỀẺỂẼỄẸỆIÍÌỈĨỊOÔƠÓỐỚÒỒỜỎỔỞÕỖỠỌỘỢUƯÚỨÙỪỦỬŨỮỤỰYÝỲỶỸỴ"
                 r"aăâáắấàằầảẳẩãẵẫạặậđeêéếèềẻểẽễẹệiíìỉĩịoôơóốớòồờỏổởõỗỡọộợuưúứùừủửũữụựyýỳỷỹỵA-Zaa-z\s]+[,.;]{0,1}\s"]
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


def pre_process(im):
    gray = cv2.cvtColor(im, cv2.COLOR_RGB2GRAY)
    im = cv2.GaussianBlur(gray, (1, 1), 0)
    (thresh, im) = cv2.threshold(im, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY)
    # im = cv2.adaptiveThreshold(im, maxValue=255, adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    #                            thresholdType=cv2.THRESH_BINARY, blockSize=25, C=20)
    im = rotate_img(im)

    return im


def extract_text(im):
    # im = pre_process(im)
    text_preprocessed = pytesseract.image_to_string(im, lang='vie', config='--oem 3 --psm 1')
    final_text_preprocessed = [line for line in text_preprocessed.split('\n') if line.strip() != '']

    return final_text_preprocessed


def extract_full_name(extracted_text):
    text = " ".join(extracted_text)

    for re_fullname in regex['fullname']:
        fullname_string = re.findall(re_fullname, text)
        if len(fullname_string) == 0:
            continue
        fullname = fullname_string[-1].split(":")[1].strip().title()
        fullname = unidecode(fullname).translate(str.maketrans('', '', string.punctuation))
        return fullname
    return ""


def extract_date_new(extracted_text):
    final_dates = []
    extracted_text = " ".join(extracted_text)
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
    extracted_text = " ".join(extracted_text)
    id_numbers = re.findall(regex['id_card'], extracted_text)
    print(id_numbers)

    if len(id_numbers) == 0:
        return ""
    else:
        id_number = [_ for _ in id_numbers[-1] if len(_) > 0][0]
        id_number = id_number.translate(str.maketrans('', '', string.punctuation)).replace(" ", "")
        return id_number


def extract_id_card(extracted_text):
    for line in extracted_text:
        id_number = re.findall(regex['id_card'], line)

        if len(id_number) > 0:
            id_number = [_ for _ in id_number[0] if len(_) > 0][0]
            id_number = id_number.translate(str.maketrans('', '', string.punctuation)).replace(" ", "")
            return id_number
    return ""


def main(im):
    extracted_text = extract_text(im)
    print(extracted_text)
    fullname = extract_full_name(extracted_text)
    extracted_dates = extract_date(extracted_text)
    dob = extracted_dates[0]
    issue_date = extracted_dates[1]
    id_card = extract_id_card(extracted_text)

    return {
        "fullname": fullname,
        "id_number": id_card,
        "dob": dob,
        "issue_date": issue_date
    }


if __name__ == '__main__':

    folder_path = "/home/trungtq/Documents/automatic_disbursement/images/other/1414_message"
    file_paths = [os.path.join(folder_path, file_path) for file_path in os.listdir(folder_path)]

    for file_path in file_paths:
        image = cv2.imread("/home/trungtq/Documents/automatic_disbursement/images/other/1414_message/"
                           "7a0a1612-9d65-498a-bd4a-0938533bd882.jpeg")
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        print(os.path.basename(file_path))

        extracted_text = extract_text(image)
        print(" ".join(extracted_text))
        print(extract_id_card_new(extracted_text))

        print("======")
        break
