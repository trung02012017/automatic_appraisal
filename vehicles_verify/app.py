import logging

from flask import Flask, jsonify, render_template, request, url_for
from flask_eureka import Eureka, eureka_bp

from main import process_response, get_result_motor_api

app = Flask(__name__)
app.register_blueprint(eureka_bp)
app.config["SERVICE_NAME"] = "motor_detection"
app.config["EUREKA_SERVICE_URL"] = "http://172.16.10.111:8761"
app.config["EUREKA_INSTANCE_PORT"] = 10201
app.config["EUREKA_INSTANCE_HOSTNAME"] = "172.16.10.111"
app.config["EUREKA_HEARTBEAT"] = 60
eureka = Eureka(app)
eureka.register_service(name="motor_detection", vip_address="motor_detection")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

file_handler = logging.FileHandler('log/api.log')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


@app.route('/health_check')
def health_check():
    return str(0)


@app.route('/detect_motor', methods=['POST'])
def get_label_loan():
    try:
        if request.method == 'POST':
            data = request.get_json()

            try:
                req = data['image']
                result_check_motor, plates, source_result = process_response(get_result_motor_api(req))
                result = {
                    "info_check_motor": {
                        "have_motor": result_check_motor,
                        "plates": plates
                    },
                    "response_code": "200",
                    "mess": "Success",
                    "result_check_from_source": source_result
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
    except Exception as e:
        print(e)
        logger.error(f'{str({"status_code": 400, "message": "Bad Request"})}')
        print("BAD REQUEST")
        return jsonify({
            "response_code": 400,
            "mess": "Bad Request"
        })


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10201, debug=True, threaded=False)