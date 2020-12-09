import pyodbc
import requests
import os
import editdistance

import pandas as pd
from unidecode import unidecode
from datetime import datetime
from lunarcalendar import Converter, Solar, Lunar, DateNotExist
from pprint import pprint

id_card_9_ = {'01': ['Hà Nội'],
                 '02': ['Hồ Chí Minh'],
                 '03': ['Hải Phòng'],
                 '04': ['Điện Biên', 'Lai Châu'],
                 '05': ['Sơn La'],
                 '06': ['Lào Cai', 'Yên Bái'],
                 '07': ['Hà Giang', 'Tuyên Quang'],
                 '08': ['Lạng Sơn'],
                 '090': ['Thái Nguyên'],
                 '091': ['Thái Nguyên'],
                 '10': ['Quảng Ninh'],
                 '11': ['Hà Tây Cũ', 'Hòa Bình'],
                 '12': ['Bắc Giang', 'Bắc Ninh'],
                 '13': ['Phú Thọ', 'Vĩnh Phúc'],
                 '14': ['Hải Dương'],
                 '15': ['Thái Bình'],
                 '16': ['Nam Định', 'Hà Nam'],
                 '17': ['Thanh Hóa'],
                 '18': ['Nghệ An', 'Hà Tĩnh'],
                 '19': ['Quảng Bình', 'Quảng Trị', 'Thừa Thiên Huế'],
                 '20': ['Quảng Nam', 'Đà Nẵng'],
                 '21': ['Quảng Ngãi', 'Bình Định'],
                 '22': ['Khánh Hòa', 'Phú Yên'],
                 '23': ['Kon Tum'],
                 '230': ['Gia Lai'],
                 '231': ['Gia Lai'],
                 '24': ['Đắk Lắk'],
                 '245': ['Đắk Nông'],
                 '25': ['Lâm Đồng'],
                 '26': ['Ninh Thuận', 'Bình Thuận'],
                 '27': ['Đồng Nai', 'Bà Rịa - Vũng Tàu'],
                 '280': ['Bình Dương'],
                 '281': ['Bình Dương'],
                 '285': ['Bình Phước'],
                 '29': ['Tây Ninh'],
                 '30': ['Long An'],
                 '31': ['Tiền Giang'],
                 '32': ['Bến Tre'],
                 '33': ['Vĩnh Long', 'Trà Vinh'],
                 '34': ['Đồng Tháp'],
                 '35': ['An Giang'],
                 '36': ['Cần Thơ', 'Hậu Giang', 'Sóc Trăng'],
                 '37': ['Kiên Giang'],
                 '38': ['Cà Mau', 'Bạc Liêu'],
                 '095': ['Bắc Kan']}

id_card_12_ = {'001': ['Hà Nội'],
                 '002': ['Hà Giang'],
                 '004': ['Cao Bằng'],
                 '006': ['Bắc Kan'],
                 '008': ['Tuyên Quang'],
                 '010': ['Lào Cai'],
                 '011': ['Điện Biên'],
                 '012': ['Lai Châu'],
                 '014': ['Sơn La'],
                 '015': ['Yên Bái'],
                 '017': ['Hòa Bình'],
                 '019': ['Thái Nguyên'],
                 '020': ['Lạng Sơn'],
                 '022': ['Quảng Ninh'],
                 '024': ['Bắc Giang'],
                 '025': ['Phú Thọ'],
                 '026': ['Vĩnh Phúc'],
                 '027': ['Bắc Ninh'],
                 '030': ['Hải Dương'],
                 '031': ['Hải Phòng'],
                 '033': ['Hưng Yên'],
                 '034': ['Thái Bình'],
                 '035': ['Hà Nam'],
                 '036': ['Nam Định'],
                 '037': ['Ninh Bình'],
                 '038': ['Thanh Hóa'],
                 '040': ['Nghệ An'],
                 '042': ['Hà Tĩnh'],
                 '044': ['Quảng Bình'],
                 '045': ['Quảng Trị'],
                 '046': ['Thừa Thiên Huế'],
                 '048': ['Đà Nẵng'],
                 '049': ['Quảng Nam'],
                 '051': ['Quảng Ngãi'],
                 '052': ['Bình Định'],
                 '054': ['Phú Yên'],
                 '056': ['Khánh Hòa'],
                 '058': ['Ninh Thuận'],
                 '060': ['Bình Thuận'],
                 '062': ['Kon Tum'],
                 '064': ['Gia Lai'],
                 '066': ['Đắk Lắk'],
                 '067': ['Đăk Nông'],
                 '068': ['Lâm Đồng'],
                 '070': ['Bình Phước'],
                 '072': ['Tây Ninh'],
                 '074': ['Bình Dương'],
                 '075': ['Đồng Nai'],
                 '077': ['Bà Rịa - Vũng Tàu'],
                 '079': ['Hồ Chí Minh'],
                 '080': ['Long An'],
                 '082': ['Tiền Giang'],
                 '083': ['Bến Tre'],
                 '084': ['Trà Vinh'],
                 '086': ['Vĩnh Long'],
                 '087': ['Đồng Tháp'],
                 '089': ['An Giang'],
                 '091': ['Kiên Giang'],
                 '092': ['Cần Thơ'],
                 '093': ['Hậu Giang'],
                 '094': ['Sóc Trăng'],
                 '095': ['Bạc Liêu'],
                 '096': ['Cà Mau']}


def connect_los_sql_db():

    conn = pyodbc.connect("Driver={ODBC Driver 17 for SQL Server};"
                          "Server=188.166.250.12,1533;"
                          "Database={los};"
                          "UID={datlt};"
                          "PWD={0123456a@}")
    return conn


def connect_mecash_sql_db():

    conn = pyodbc.connect("Driver={ODBC Driver 17 for SQL Server};"
                          "Server=42.112.23.25;"
                          "Database=Mecash;"
                          "UID=BigData;"
                          "PWD={-bZW[Bh*wdQ#>5('Nw;CL9h[9W\\qf\\y\"}")
    return conn


def query(conn, query):
    return pd.read_sql(query, conn)


def get_url(path: str, s3_status: int, mecash_id: int = None):
    if path.startswith("http"):
        return path
    if path and len(path) <= 1:
        return
    prefix = "http://file.tima.vn"
    if pd.isna(mecash_id) or mecash_id is None:
        prefix = "https://los-space.sgp1.digitaloceanspaces.com"
    elif s3_status == 0:
        prefix = "https://img.tima.vn"

    url = prefix + path
    return url


def download_img_by_url(image_url,
                        folder_path=os.path.join(os.path.dirname(__file__),
                                                 "images/id_card")):
    img_data = requests.get(image_url).content
    img_name = image_url.split("/")[-1]
    with open(os.path.join(folder_path, img_name), 'wb') as handler:
        handler.write(img_data)


def get_info_id_extract(images):
    host = "http://172.16.10.111:15004/image/ocr/id"
    headers = {
        'Content-Type': 'application/json'
    }
    params = {
        "image": images
    }

    res = requests.post(host, json=params, headers=headers)
    return res.json()


def get_province_from_id(id_number):
    id_number = str(id_number)

    if len(id_number) == 9:
        try:
            province_list = id_card_9_[id_number[0:3]]
            return {
                "category": "9-digit",
                "province_list": province_list,
                "message": "province from 9-digit card, 3 first numbers"
            }
        except KeyError:
            try:
                province_list = id_card_9_[id_number[0:2]]
                return {
                    "category": "9-digit",
                    "province_list": province_list,
                    "message": "province from 9-digit card, 2 first numbers"
                }
            except KeyError:
                return {
                    "category": None,
                    "province_list": [],
                    "message": "no province from 9-digit card"
                }
    elif len(id_number) == 12:
        try:
            province_list = id_card_12_[id_number[0:3]]
            gender_code = id_number[3]
            year_of_birth = id_number[4:6]
            if gender_code in ["0", "2"]:
                gender = "Male"
            elif gender_code in ["1", "3"]:
                gender = "Female"
            else:
                gender = None
            return {
                "category": "12-digit",
                "province_list": province_list,
                "message": "province from 12-digit card, 3 first numbers",
                "gender": gender,
                "year_of_brith": year_of_birth
            }
        except KeyError:
            return {
                "category": None,
                "province_list": [],
                "message": "no province from 9-digit card"
            }
    else:
        print("id number non-verified")
        return None


ID_PROVINCE = 0
ID_DISTRICT = 1
ID_WARD = 2


def check_household_address(id_card_address, inserted_address):
    province = inserted_address[ID_PROVINCE]
    district = inserted_address[ID_DISTRICT]
    ward = inserted_address[ID_WARD]

    check_result = []
    try:
        if province in id_card_address:
            check_result.append(True)
        elif unidecode(province) in unidecode(id_card_address):
            check_result.append(True)
        else:
            check_result.append(False)

        if district in id_card_address:
            check_result.append(True)
        elif unidecode(district) in unidecode(id_card_address):
            check_result.append(True)
        else:
            check_result.append(False)

        if ward in id_card_address:
            check_result.append(True)
        elif unidecode(ward) in unidecode(id_card_address):
            check_result.append(True)
        else:
            check_result.append(False)

        return check_result

    except TypeError:
        print("NO address detected")
        return [False, False, False]


def correct_id_card_address(id_card_address):
    return id_card_address


def check_national_id_card_num(id_num_from_card, id_num_inserted):
    return {
        "is_match": id_num_from_card == id_num_inserted,
        "edit_distance": editdistance.eval(id_num_from_card, id_num_inserted)
    }


def convert_date_to_weekday(date_str):
    try:
        date_ = datetime.strptime(date_str, "%d-%m-%Y")
        return date_.weekday()
    except:
        try:
            date_ = datetime.strptime(date_str, "%d/%m/%Y")
            return date_.weekday()
        except:
            return None


def check_province_from_id_number(id_number, inserted_province):
    provinces_from_id_res = get_province_from_id(id_number)
    if provinces_from_id_res is None or len(provinces_from_id_res) == 0:
        return None
    provinces_from_id = provinces_from_id_res['province_list']
    return {
        "is_match": inserted_province in provinces_from_id,
        "edit_distance": [editdistance.eval(province, inserted_province) for province in provinces_from_id],
        "province_from_id": provinces_from_id
    }


def check_issue_date(date_str):
    all_check_issue_date = []
    weekday = convert_date_to_weekday(date_str)
    if weekday is not None:
        if weekday not in [5, 6]:
            all_check_issue_date.append(False)
        else:
            all_check_issue_date.append(True)
    else:
        return None


if __name__ == '__main__':

    id_card_types = (1, 11, 19, 46, 55, 58, 69, 75, 77, 83, 92, 94, 96, 98, 100, 102, 104, 106, 108, 110,
                     111, 112, 113, 114, 115, 134)
    other_types = (23, 126, 127, 128, 129, 130, 131, 132, 142, 143, 144, 145, 146)
    vr = (12, 35, 70)
    vehicle_types = 141
    conn_los = connect_los_sql_db()

    id_card_query = "select loan.LoanBriefId as loan_id, " \
                    "loan_file.FilePath as file_path, " \
                    "loan_file.S3Status as s3_status, loan_file.MecashId as mecash_id, loan_file.TypeId as type_id " \
                    "from  (select * " \
                    "from LoanBrief " \
                    "where FromDate > '2020-09-01') loan " \
                    "inner join (select * from LoanBriefFiles " \
                    "where Status != 0 " \
                    "and IsDeleted = 0 " \
                    "and CreateAt > '2020-09-01' " \
                    "and CreateAt < '2020-12-01' " \
                    f"and  TypeId in {id_card_types}) loan_file " \
                    "on loan.LoanBriefId = loan_file.LoanBriefId " \
                    "order by  loan.LoanBriefId desc" \

    df = query(conn_los, id_card_query)
    print(df)

    for i, row in df.iterrows():
        file_path = row['file_path']
        s3_status = row['s3_status']
        mecash_id = row['mecash_id']

        image_url = get_url(file_path, s3_status, mecash_id)
        print(image_url)
        # download_img_by_url(image_url, "/home/trungtq/Documents/automatic_disbursement/images/vehicle_registration")


