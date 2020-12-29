import cv2
import os
import re
import string
import requests
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


class MessageExtractor:
    def __init__(self, message_detect_url: str):
        self.message_detect_url = message_detect_url

    def get_coordinates_message(self, image_url: str):
        try:

            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("POST", self.message_detect_url, headers=headers, json={"image": image_url})
            return response.json()
        except Exception as e:
            print(f"Error {e}")
            print("MessageExtractorAPI")
            return None

    def pick_message_box(self, image: np.ndarray, coordinates: list):
        return image[coordinates[0]:coordinates[2], coordinates[1]:coordinates[3]]

    def compare_boxes(self, coordinates_1: list, coordinates_2: list):
        # True: box 2, False: boxes 1
        if coordinates_2[1] <= coordinates_1[3]:
            return True
        else:
            if coordinates_2[0] >= coordinates_1[2]:
                return True
            else:
                return False

    def sort_coordinates(self, coordinates: list):
        if len(coordinates) <= 1:
            return coordinates
        if len(coordinates) == 2:
            if self.compare_boxes(coordinates[0], coordinates[1]):
                return coordinates
            else:
                return [coordinates[1], coordinates[0]]

        for i in range(len(coordinates) - 1):
            for j in range(1, len(coordinates)):
                if self.compare_boxes(coordinates[i], coordinates[j]):
                    pass
                else:
                    tmp = coordinates[i]
                    coordinates[i] = coordinates[j]
                    coordinates[j] = tmp
        return reversed(coordinates)

    def main_extract(self, image_url: str):
        coordinates_result = self.get_coordinates_message(image_url)
        if coordinates_result is None:
            return coordinates_result
        else:
            print(coordinates_result)
            boxes = coordinates_result['results']['boxes']
            boxes = self.sort_coordinates(boxes)
            return boxes


class InfoExtractor:
    def __init__(self):
        pass

    def extract_full_name(self, extracted_text):
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
            return fullname.title()
        return ""

    def extract_date_new(self, extracted_text):
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

    def extract_date(self, extracted_text):
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

    def extract_id_card_new(self, extracted_text):
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

    def extract_id_card(self, extracted_text):
        for line in extracted_text:
            id_number = re.findall(regex['id_card'], line)

            if len(id_number) > 0:
                id_number = [_ for _ in id_number[0] if len(_) > 0][0]
                id_number = id_number.translate(str.maketrans('', '', string.punctuation)).replace(" ", "")
                id_number = "".join([c for c in id_number if not c.isalpha()])
                return id_number
        return ""