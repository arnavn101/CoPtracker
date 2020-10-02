import configparser
import os
from datetime import datetime, timedelta
from json import dumps

from flask import Flask, request, abort, Response
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource, Api

from database import SQL_Server
import geocoder

app = Flask(__name__)
api = Api(app, prefix="/api/v1")

auth = HTTPBasicAuth()
config = configparser.ConfigParser()
config.read('config.cfg')

TIME_REQUESTS = float(config.get('ConfigInfo', 'TIME_REQUESTS'))
MAP_QUEST_KEY = str(config.get('ConfigInfo', 'MAP_QUEST_KEY'))
PORT = str(config.get('ConfigInfo', 'PORT'))
USERNAME = str(config.get('ConfigInfo', 'USERNAME'))
PASSWORD = str(config.get('ConfigInfo', 'PASSWORD'))

USER_DATA = {
    USERNAME: PASSWORD
}

""" 
Curl Requests to simulate calls

Insert User Location: 
curl -X GET "http://localhost:5000/api/v1/user_Location?user=User&location=400,-700" \
            --user admin:SuperSecretPwd
            
Insert User Home Location: 
curl -X GET "http://localhost:5000/api/v1/home_Location?user=User&home_location=400,-740" \
            --user admin:SuperSecretPwd

Insert User Contact Information: 
curl -X GET "http://localhost:5000/api/v1/user_Contact?user=User&contact_information=random@gmail.com" \
            --user admin:SuperSecretPwd
"""


# App Verification Method
@auth.verify_password
def verify(username, password):
    if not (username and password):
        return False
    return USER_DATA.get(username) == password


# decorator to limit flask requests
def limit_requests(function):
    def wrapper(self):
        user = request.args.get('user')
        filename = f'dates-{user}.txt'
        first_request = False
        if not os.path.exists(filename):
            datesFile = open(filename, "w+")
        else:
            datesFile = open(filename, "r")

        if os.stat(filename).st_size == 0:
            previous_date = datetime.now()
            first_request = True
        else:
            previous_date = SQL_Server.stringToDatetime(datesFile.read())

        diff_times = (datetime.now() - previous_date)

        if diff_times > timedelta(minutes=TIME_REQUESTS) or first_request:
            datesFile = open(filename, "w+")
            datesFile.write(str(datetime.now()))
            return function(self)
        else:
            error_message = dumps({'Message': 'Too Many Requests'})
            abort(Response(error_message, 401))

    return wrapper


# Get User's Current location
class user_Location(Resource):
    @auth.login_required
    @limit_requests
    def get(self):
        sql_server = SQL_Server()
        params = request.args.get('user')
        params2 = (request.args.get('location')).replace(" ", "")
        if params != 'null':
            sql_server.insert_LocInformation(params, params2, SQL_Server.dateTimeToString(datetime.now()))
            sql_server.save_database()
            sql_server.close_database()
        return "Current Location data added to User's table"


# user location api endpoint
api.add_resource(user_Location, '/user_Location')


# Get User's Home location & Contact Information
class contact_Form(Resource):
    @auth.login_required
    def get(self):
        sql_server = SQL_Server()
        params0 = request.args.get('patient_id')
        params = request.args.get('user')
        params2 = (request.args.get('home_location'))
        geocoded_location = geocoder.mapquest(params2, key=MAP_QUEST_KEY)
        params2 = f"{geocoded_location.lat},{geocoded_location.lng}"
        params3 = request.args.get('email_information')
        if params != 'null':
            sql_server.insert_PatientId(params, params0, SQL_Server.dateTimeToString(datetime.now()))
            sql_server.insert_HomeInformation(params, params2, SQL_Server.dateTimeToString(datetime.now()))
            sql_server.insert_ContactInformation(params, params3, SQL_Server.dateTimeToString(datetime.now()))
            sql_server.save_database()
            sql_server.close_database()
        return "Home Location and Contact Information data added to User's table"


# user location api endpoint
api.add_resource(contact_Form, '/contact_Form')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)
