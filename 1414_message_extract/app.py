import os
import requests
import cv2
import shutil
import logging
import editdistance

import numpy as np

from unidecode import unidecode
from flask import Flask, jsonify, render_template, request, url_for
from flask_eureka import Eureka, eureka_bp

from main import main

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

file_handler = logging.FileHandler('log/api.log')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def download_img(image_url):
    img_name = image_url.split("/")[-1]
    img_data = requests.get(image_url).content
    img_path = os.path.join(os.path.dirname(__file__), f"tmp/{img_name}")
    with open(img_path, 'wb') as handler:
        handler.write(img_data)
    return img_path


def delete_all_folder_files(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def main_compare(image_url, inserted_fullname, inserted_id_number, inserted_dob):
    compare_results = []
    image_path = download_img(image_url)

    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    extract_results = main(image)
    print(extract_results)
    fullname = extract_results['fullname']
    id_number = extract_results['id_number']
    dob = extract_results['dob']
    issue_date = extract_results['issue_date']

    if all(info == '' for info in [fullname, id_number, dob, issue_date]):
        return compare_results, False

    # compare fullname
    inserted_fullname = unidecode(inserted_fullname).strip().title()
    if editdistance.eval(inserted_fullname, fullname) <= 2:
        compare_results.append(True)
    else:
        compare_results.append(False)

    # compare id number
    if str(inserted_id_number) == id_number:
        compare_results.append(True)
    else:
        compare_results.append(False)

    # compare date of birth
    if editdistance.eval(inserted_dob, dob) <= 2:
        compare_results.append(True)
    else:
        compare_results.append(False)

    if all(compare is True for compare in compare_results):
        return compare_results, True
    else:
        return compare_results, None


@app.route('/check_info_message', methods=['POST'])
def get_label_loan():
    try:
        if request.method == 'POST':
            data = request.get_json()
            img_url = data["image_url"]
            inserted_fullname = data['fullname']
            inserted_id_number = data['id_number']
            inserted_dob = data['date_of_birth']

            try:
                result_check_message = main_compare(img_url,
                                                    inserted_fullname,
                                                    inserted_id_number,
                                                    inserted_dob)
                print(result_check_message)
                return {
                    "info_check_result": result_check_message[1],
                    "status": "200",
                    "add_message": "Success",
                }
            except:
                logger.error(f'{str(data)} - {str({"status_code": 500, "message": "Server Error"})}')
                print("SERVER ERROR")
                return jsonify({
                    "status_code": 500,
                    "message": "Server Error"
                })
    except:
        logger.error(f'{str({"status_code": 400, "message": "Bad Request"})}')
        print("BAD REQUEST")
        return jsonify({
            "status_code": 400,
            "message": "Bad Request"
        })
    finally:
        delete_all_folder_files("./tmp")


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=11006, debug=True, threaded=False)