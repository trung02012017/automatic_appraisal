import os
import requests
import cv2
import shutil
import logging

import numpy as np

from flask import Flask, jsonify, render_template, request, url_for
from flask_eureka import Eureka, eureka_bp

from main import YOLOV3PlateModelRecognition

debug = False
detector = YOLOV3PlateModelRecognition("./model/config/yolov3.cfg",
                                       "./model/weights/yolov3.weights",
                                       "./classes/coco.names",
                                       debug=debug)
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


def main_detect(image_urls):
    image_paths = [download_img(img_url) for img_url in image_urls]
    detect_results = []

    for path in image_paths:
        image = cv2.imread(path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        detect_result = detector.predict(image)
        detect_result = [label for label in detect_result if label == "motorbike"]
        detect_results.append(len(detect_result))

    print(detect_results)
    detect_results = np.array(detect_results)
    detect_results = [r for r in detect_results if r > 0]

    if len(detect_results) >= 2:
        return True
    else:
        return False


@app.route('/motor_recognition', methods=['POST'])
def get_label_loan():
    try:
        if request.method == 'POST':
            data = request.get_json()
            img_urls = data["image_urls"]

            if len(img_urls) < 3:
                logger.error(f'{str(data)} - {str({"status_code": 400, "message": "bad request"})}')
                print("BAD REQUEST")
                return {
                    "motor_detected": None,
                    "status": "400",
                    "add_message": "Bad Request",
                }

            try:
                result_check_motor = main_detect(img_urls)
                return {
                    "motor_detected": result_check_motor,
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