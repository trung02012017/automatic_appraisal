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
app.register_blueprint(eureka_bp)
app.config["SERVICE_NAME"] = "1414_MESSAGE_VALIDATE"
app.config["EUREKA_SERVICE_URL"] = "http://172.16.10.111:8761"
app.config["EUREKA_INSTANCE_PORT"] = 10200
app.config["EUREKA_INSTANCE_HOSTNAME"] = "172.16.10.111"
app.config["EUREKA_HEARTBEAT"] = 60
eureka = Eureka(app)
eureka.register_service(name="1414_MESSAGE_VALIDATE", vip_address="1414_MESSAGE_VALIDATE")

logging.basicConfig(level=logging.INFO)
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
        return compare_results, False, {'fullname': '', 'id_number': '', 'dob': '', 'issue_date': ''}

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
        returned_compare_results = {
            "same_fullname": compare_results[0],
            "same_id_number": compare_results[1],
            "same_dob": compare_results[2]
        }
        return returned_compare_results, True, extract_results
    else:
        returned_compare_results = {
            "same_fullname": compare_results[0],
            "same_id_number": compare_results[1],
            "same_dob": compare_results[2]
        }
        return returned_compare_results, None, extract_results


@app.route('/health_check')
def health_check():
    return str(0)


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
                result = {
                    "info_check_result": result_check_message[1],
                    "compare_results": result_check_message[0],
                    "extracted_info": result_check_message[2],
                    "response_code": 200,
                    "mess": "Success",
                }
                logger.info(f'{str(data)} - {str(result)}')
                return result
            except Exception as e:
                print(e)
                logger.error(f'{str(data)} - {str({"response_code_code": 500, "mess": "Server Error"})}')
                print("SERVER ERROR")
                return jsonify({
                    "response_code": 500,
                    "mess": "Server Error"
                })
    except:
        logger.error(f'{str({"status_code": 400, "message": "Bad Request"})}')
        print("BAD REQUEST")
        return jsonify({
            "response_code": 400,
            "mess": "Bad Request"
        })
    finally:
        delete_all_folder_files("./tmp")


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10200, debug=True, threaded=False)