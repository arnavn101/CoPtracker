from datetime import datetime
from math import radians, cos, sin, asin, sqrt

import dataset


class SQL_Server:

    def __init__(self):
        self.db = dataset.connect('sqlite:///pythonsqlite.db', )

    def close_database(self):
        self.db.close()

    def save_database(self):
        self.db.commit()

    def insert_LocInformation(self, unique_identifier, location, current_date):
        self.db[unique_identifier].insert(
            dict(location=location, contact_info=None, home_location=None, commitBreach=None,
                 patientId=None, current_date=current_date))

    def insert_HomeInformation(self, unique_identifier, homeLocation, current_date):
        self.db[unique_identifier].insert(
            dict(home_location=homeLocation, contact_info=None, patientId=None,
                 location=None, commitBreach=None, current_date=current_date))

    def insert_ContactInformation(self, unique_identifier, contactInfo, current_date):
        self.db[unique_identifier].insert(
            dict(contact_info=contactInfo, commitBreach=None, home_location=None, location=None,
                 patientId=None, current_date=current_date))

    def insert_PatientId(self, unique_identifier, patientId, current_date):
        self.db[unique_identifier].insert(
            dict(contact_info=None, commitBreach=None, home_location=None, location=None,
                 patientId=patientId, current_date=current_date))

    def insertBreachStatus(self, unique_identifier, breachStatus, current_date):
        self.db[unique_identifier].insert(dict(commitBreach=breachStatus, patientId=None,
                                               contact_info=None, home_location=None, location=None,
                                               current_date=current_date))

    def returnAllLocations(self, unique_identifier):
        possible_locations = []
        for row in self.db[unique_identifier]:
            if row['location'] is not None:
                possible_locations.append([row['location'], row['current_date']])
        return possible_locations

    def returnContactInformation(self, unique_identifier):
        for row in self.db[unique_identifier]:
            if row['contact_info'] is not None:
                return row['contact_info'], row['current_date']
        return False, False

    def returnPatientId(self, unique_identifier):
        for row in self.db[unique_identifier]:
            if row['patientId'] is not None:
                return row['patientId'], row['current_date']
        return False, False

    def returnHomeLocation(self, unique_identifier):
        for row in self.db[unique_identifier]:
            if row['home_location'] is not None:
                return row['home_location'], row['current_date']
        return False, False

    def breachStatus(self, unique_identifier):
        for row in self.db[unique_identifier]:
            if row['commitBreach'] is not None:
                return row['commitBreach'], row['current_date']
        return False, False

    @staticmethod
    def haversine(lon1, lat1, lon2, lat2):
        """
        Calculate the great circle distance between two points 
        on the earth (specified in decimal degrees)

        input : str(lat,lon)
        """
        # convert decimal degrees to radians 
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

        # haversine formula 
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        r = 6371  # Radius of earth in kilometers. Use 3956 for miles
        return (c * r) * 1000

    @staticmethod
    def locations_distance(location_1, location_2):
        location_1 = (location_1.split(","))
        location_2 = (location_2.split(","))
        return SQL_Server.haversine(float(location_1[0]), float(location_1[1]), float(location_2[0]),
                                    float(location_2[1]))

    @staticmethod
    def dateTimeToString(datetimeDate):
        return datetimeDate.strftime("%Y-%m-%d %H:%M:%S.%f")

    @staticmethod
    def stringToDatetime(stringDate):
        return datetime.strptime(stringDate, '%Y-%m-%d %H:%M:%S.%f')

    @staticmethod
    def differenceBetweenDates(d1, d2):
        diff = SQL_Server.stringToDatetime(d2) - SQL_Server.stringToDatetime(d1)
        days, seconds = diff.days, diff.seconds
        return days * 24 + seconds // 3600

    def view_information_user(self, unique_identifier):
        return list(self.db[unique_identifier].all())

    def return_allUsers(self):
        return self.db.tables
