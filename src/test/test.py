import sys, os
sys.path.append(os.path.abspath(os.path.join('..', 'api')))
import app
import unittest
from unittest.mock import MagicMock,Mock,patch
import sqlite3
import requests
from flask import Response
import json

#################################################################################################################
#                                                                                                               #
#                                             Time Series                                                       #
#                                                                                                               #
#################################################################################################################

# Test database connection
class TestConnection(unittest.TestCase):
    def test_sqlite3_connect_success(self):
        sqlite3.connect = MagicMock(return_value='connection succeeded')

        dbc = app.timeseries_connection()
        sqlite3.connect.assert_called_with("databases/timeseries.db")
        self.assertEqual(dbc, 'connection succeeded')

    def test_sqlite3_connect_fail(self):
        sqlite3.connect = MagicMock(return_value = 'connection failed')

        dbc = app.timeseries_connection()
        sqlite3.connect.assert_called_with("databases/timeseries.db")
        self.assertEqual(dbc, 'connection failed')

# Test time_series/header POST
url_header = "http://127.0.0.1:9803/time_series/header"
header = {"Success": "header is generated, can process to /time_series/input to input csv body['Province/State', 'Country/Region', 'Lat', 'Long', '01/22/2020', '01/23/2020', '01/24/2020', '01/25/2020', '01/26/2020', '01/27/2020', '01/28/2020', '01/29/2020', '01/30/2020', '01/31/2020', '02/01/2020', '02/02/2020', '02/03/2020', '02/04/2020', '02/05/2020']"}
class TestHeader(unittest.TestCase):
    def test_header_valid(self):
        info = {'header': "Province/State,Country/Region,Lat,Long,01/22/20,02/05/20", 'csv': ""}
        info = json.dumps(info)
        request_json = json.loads(info)
        resp = requests.post(url_header, json = request_json)
        response_json = json.loads(resp.text)
        exp = header
        exp = json.dumps(exp)
        exp_json = json.loads(exp)
        assert response_json == exp_json 
        assert resp.status_code == 200

    def test_header_valid_day_input(self):
        info = {'header': "Province/State,Country/Region,Lat,Long,1/30/20,2/5/20", 'csv': ""}
        info = json.dumps(info)
        request_json = json.loads(info)
        resp = requests.post(url_header, json = request_json)
        response_json = json.loads(resp.text)
        exp = header
        exp = json.dumps(exp)
        exp_json = json.loads(exp)
        assert response_json == exp_json 
        assert resp.status_code == 200

    def test_header_valid_month_input(self):
        info = {'header': "Province/State,Country/Region,Lat,Long,1/22/20,1/23/20", 'csv': ""}
        info = json.dumps(info)
        request_json = json.loads(info)
        resp = requests.post(url_header, json = request_json)
        response_json = json.loads(resp.text)
        exp = header
        exp = json.dumps(exp)
        exp_json = json.loads(exp)
        assert response_json == exp_json
        assert resp.status_code == 200

    def test_header_missing_province(self):
        info = {'header': "Country/Region,Lat,Long,01/22/20,01/23/20", 'csv': ""}
        info = json.dumps(info)
        request_json = json.loads(info)
        resp = requests.post(url_header, json = request_json)
        response_json = json.loads(resp.text)
        exp = {"valid": "Not valid header"}
        exp = json.dumps(exp)
        exp_json = json.loads(exp)
        assert response_json == exp_json 

    def test_header_invalid_date_format(self):
        info = {'header': "Province/State,Country/Region,Lat,Long,01-22-20,01-23-20", 'csv': ""}
        info = json.dumps(info)
        request_json = json.loads(info)
        resp = requests.post(url_header, json = request_json)
        assert resp.text == "Invalid input"
        assert resp.status_code == 400

    def test_header_invalid_year_input1(self):
        info = {'header': "Province/State,Country/Region,Lat,Long,01/22/19,01/23/19", 'csv': ""}
        info = json.dumps(info)
        request_json = json.loads(info)
        resp = requests.post(url_header, json = request_json)
        assert resp.text == "Invalid header, wrong date format in year"
        assert resp.status_code == 400

    def test_header_invalid_year_input2(self):
        info = {'header': "Province/State,Country/Region,Lat,Long,01/22/2020,01/23/2021", 'csv': ""}
        info = json.dumps(info)
        request_json = json.loads(info)
        resp = requests.post(url_header, json = request_json)
        assert resp.text == "Invalid header, wrong date format in year"
        assert resp.status_code == 400

    def test_header_invalid_month_input(self):
        info = {'header': "Province/State,Country/Region,Lat,Long,13/22/20,13/23/20", 'csv': ""}
        info = json.dumps(info)
        request_json = json.loads(info)
        resp = requests.post(url_header, json = request_json)
        assert resp.text == "Invalid header, wrong date format in month"
        assert resp.status_code == 400

    def test_header_invalid_day_input(self):
        info = {'header': "Province/State,Country/Region,Lat,Long,01/44/20,01/45/20", 'csv': ""}
        info = json.dumps(info)
        request_json = json.loads(info)
        resp = requests.post(url_header, json = request_json)
        assert resp.text == "Invalid header, wrong date format in day"
        assert resp.status_code == 400

# Test time_series/add_data POST
url_add_data = "http://127.0.0.1:9803/time_series/add_data"
url_view_data = "http://127.0.0.1:9803/time_series/view_data"
add_data = {"response": "update successfully"}
class TestAddData(unittest.TestCase):
    def setup_header(self):
        header = {'header': "Province/State,Country/Region,Lat,Long,01/22/20,02/05/20", 'csv': ""}
        header = json.dumps(header)
        request_json = json.loads(header)
        requests.post(url_header, json = request_json)

    def test_add_valid_data(self):
        self.setup_header()
        confirm = ",Afghanistan,33.93911,67.709953,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
        death = ",Afghanistan,33.93911,67.709953,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
        recover = ",Afghanistan,33.93911,67.709953,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
        info = {"confirmed": confirm, "death": death, "recovered": recover}
        info = json.dumps(info)
        request_json = json.loads(info)
        resp = requests.post(url_add_data, json = request_json)
        response_json = json.loads(resp.text)
        exp = add_data
        exp = json.dumps(exp)
        exp_json = json.loads(exp)
        assert response_json == exp_json 
        assert resp.status_code == 200

    def test_add_data_invalid_confirm(self):
        self.setup_header()
        confirm = ",Afghanistan,33.93911,67.709953,0,0,0,0,0,0,0,0,-1,0,0,0,0,0,0"
        death = ",Afghanistan,33.93911,67.709953,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
        recover = ",Afghanistan,33.93911,67.709953,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
        info = {"confirmed": confirm, "death": death, "recovered": recover}
        info = json.dumps(info)
        request_json = json.loads(info)
        resp = requests.post(url_add_data, json = request_json)
        exp = "Invalid data for confirmed"
        assert resp.text == exp 
        assert resp.status_code == 400

    def test_add_data_invalid_death(self):
        self.setup_header()
        confirm = ",Afghanistan,33.93911,67.709953,0,1,3,2,0,10,0,0,11,0,0,0,0,0,0"
        death = ",Afghanistan,33.93911,67.709953,0,1,0,0,-1,0,5,0,7,8,9,0,1,0,0"
        recover = ",Afghanistan,33.93911,67.709953,0,0,0,0,0,2,0,0,0,0,0,3,0,0,0"
        info = {"confirmed": confirm, "death": death, "recovered": recover}
        info = json.dumps(info)
        request_json = json.loads(info)
        resp = requests.post(url_add_data, json = request_json)
        exp = "Invalid data for death"
        assert resp.text == exp 
        assert resp.status_code == 400

    def test_add_data_invalid_recover(self):
        self.setup_header()
        confirm = ",Afghanistan,33.93911,67.709953,0,1,3,2,0,10,0,0,11,0,0,0,0,0,0"
        death = ",Afghanistan,33.93911,67.709953,0,1,0,0,0,0,5,0,7,8,9,0,1,0,0"
        recover = ",Afghanistan,33.93911,67.709953,0,0,0,0,0,2,0,0,-1,0,0,3,0,0,0"
        info = {"confirmed": confirm, "death": death, "recovered": recover}
        info = json.dumps(info)
        request_json = json.loads(info)
        resp = requests.post(url_add_data, json = request_json)
        exp = "Invalid data for recovered"
        assert resp.text == exp
        assert resp.status_code == 400

    def test_data_successfully_add_confirm(self):
        info = {"data": "confirmed", "csv": ""}
        info = json.dumps(info)
        request_json = json.loads(info)
        resp = requests.post(url_view_data, json = request_json)
        response_json = json.loads(resp.text)
        exp = {"confirmed": [["","Afghanistan",33.93911,67.709953,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]}
        assert response_json == exp 
        assert resp.status_code == 200





if __name__ == "__main__":
    unittest.main()