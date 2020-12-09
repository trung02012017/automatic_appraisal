import requests


def get_result_motor_api(req):
    try:
        url = "http://172.16.10.111:15004/image/motor/check"

        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, json={"image": req})

        return response.json()
    except Exception as e:
        print(e)
        return None


def process_response(res):
    if res is None:
        return None
    else:
        count_moto, count_plate = 0, 0
        plates = []
        results = res['results']
        for r in results:
            if r['has_motor'] is True:
                count_moto += 1
            if r['plate'] is not None:
                count_plate += 1
                plates.append(r['plate'])

        if count_moto >= 2:
            return True, plates, res
        else:
            return False, plates, res
