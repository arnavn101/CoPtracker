from database import SQL_Server
from apscheduler.schedulers.blocking import BlockingScheduler
from gmail import GMail, Message
import configparser


class Manager:
    def __init__(self):
        self.sql_server = SQL_Server()
        self.config = configparser.ConfigParser()
        self.config.read('config.cfg')
        self.DISTANCE_BETWEEN = int(self.config.get('ConfigInfo', 'DISTANCE_BETWEEN'))
        self.HOURS_DELETE = int(self.config.get('ConfigInfo', 'HOURS_DELETE'))
        self.INTERVAL_WAIT = float(self.config.get('ConfigInfo', 'INTERVAL_WAIT'))
        self.EMAIL_USERNAME = str(self.config.get('ConfigInfo', 'EMAIL_USERNAME'))
        self.EMAIL_PASSWORD = str(self.config.get('ConfigInfo', 'EMAIL_PASSWORD'))

    def sendEmail(self, email_recipient, subjectEmail, messageEmail):
        gmail_server = GMail(self.EMAIL_USERNAME, self.EMAIL_PASSWORD)
        email_content = Message(subjectEmail, to=email_recipient, text=messageEmail)
        gmail_server.send(email_content)

    def notifyBreach(self, individual_identifier, dateBreach):
        patient_id, _ = self.sql_server.returnPatientId(individual_identifier)
        contact_info, _ = self.sql_server.returnContactInformation(individual_identifier)
        self.sendEmail(contact_info, f'Patient {patient_id} Alert', f'The Patient {patient_id}'
                                                                    f' left their home at {dateBreach}')

    def notifyIrregularity(self, individual_identifier, dateBreach):
        patient_id, _ = self.sql_server.returnPatientId(individual_identifier)
        contact_info, _ = self.sql_server.returnContactInformation(individual_identifier)
        self.sendEmail(contact_info, f'Patient {patient_id} Alert', f'The Patient {patient_id} deleted the app '
                                                                    f'or turned off their phone around {dateBreach}')

    def identifyNewPossibleBreach(self, individual_identifier):
        breach_status, date = self.sql_server.breachStatus(individual_identifier)
        if breach_status:
            return False, False, False
        breach_status, date = self.ensureHomeProximity(individual_identifier)
        if breach_status:
            self.sql_server.insertBreachStatus(individual_identifier, True, date)
            return True, date, "Breach"
        irregular_status, date1, date2 = self.checkIrregularRequests(individual_identifier)
        if irregular_status:
            self.sql_server.insertBreachStatus(individual_identifier, True, date2)
            return True, date, "Irregular"
        return False, False, False

    def checkIrregularRequests(self, individual_identifier):
        listInformation = self.sql_server.view_information_user(individual_identifier)
        for index in range(len(listInformation) - 1):
            if listInformation[index]['location'] and listInformation[index + 1]['location']:
                diff_dates = self.sql_server.differenceBetweenDates(listInformation[index]['current_date'],
                                                                    listInformation[index + 1]['current_date'])
                if diff_dates > self.HOURS_DELETE:
                    return True, listInformation[index]['current_date'], listInformation[index + 1]['current_date']
        return False, False, False

    def ensureHomeProximity(self, individual_identifier):
        listLocations = self.sql_server.returnAllLocations(individual_identifier)
        home_location, _ = self.sql_server.returnHomeLocation(individual_identifier)
        if home_location and len(listLocations) != 0:
            for this_location in listLocations:
                calculated_distance = self.sql_server.locations_distance(home_location, this_location[0])
                if calculated_distance > self.DISTANCE_BETWEEN:
                    return True, this_location[1]
        return False, False

    def automate_manager(self):
        print("\nDatabase Manager has started\n")
        for individual in self.sql_server.return_allUsers():
            breach_status, dateBreach, breachType = self.identifyNewPossibleBreach(individual)
            if breach_status:
                print(individual)
                if breachType == 'Breach':
                    self.notifyBreach(individual, dateBreach)
                elif breachType == 'Irregular':
                    self.notifyIrregularity(individual, dateBreach)
        print("\nDatabase Manager has ended\n")


manager = Manager()
manager.automate_manager()
scheduler = BlockingScheduler()
scheduler.add_job(manager.automate_manager, 'interval', hours=manager.INTERVAL_WAIT)
scheduler.start()
