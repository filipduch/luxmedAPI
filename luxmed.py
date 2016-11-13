import httplib
import urllib
import time
import hashlib
import json

API_SECRET = "{A130BFEE-EEF0-4733-9064-17FAFC341F26}"
API_HOST = "m.grupaluxmed.pl"
API_BASE_URL = "/PatientPortalProxyBE/api/"

# x-api request headers
X_API_VERSION = "2"
X_API_CLIENT = "client_android"
X_API_LANG = "pl"

class Luxmed:

    def __init__(self, username, password):
        self._userHash = None  # GUID will be obtained after successful login
        self._login(username, password)

        # get cities and languages
        response, request_data = self._sendRequest("reservationFilter", {"isFromReservation": "true"})
        self._validateResponse(response)
        self._cities = request_data["Cities"]
        self._languages = request_data["Languages"]
        self._services = list()
        self._clinics = list()
        self._cityId = None

    def _sendRequest(self, action, data):
        """ sends request to server """
        data = urllib.urlencode(data)
        headers = self._getHeaders()

        conn = httplib.HTTPSConnection(API_HOST)
        conn.request("POST", API_BASE_URL + action, data, headers)
        response = conn.getresponse()

        if response.status != httplib.OK:
            request_data = None
        else:
            request_data = json.loads(response.read())

        conn.close()

        return response, request_data

    def _getHeaders(self):
        """ creates necessary headers which every request must include """
        timestamp = str(int(time.time())) + "000"
        string_to_hash = API_SECRET + "::" + X_API_VERSION + "::" + X_API_CLIENT + "::" + timestamp

        # add userHash param if user is already logged-in
        if self._userHash is not None:
            string_to_hash = string_to_hash + "::" + self._userHash

        md5 = hashlib.md5()
        md5.update(string_to_hash)
        api_signature = md5.hexdigest()

        headers = {
            "x-api-signature": api_signature,
            "x-api-timestamp": timestamp,
            "x-api-client-identifier": X_API_CLIENT,
            "x-api-version": X_API_VERSION,
            "x-api-lang": X_API_LANG,
            "Content-type": "application/x-www-form-urlencoded",
            "Connection": "Keep-Alive",
            "User-Agent": "Apache-HttpClient/UNAVAILABLE (java 1.4)"
        }

        if self._userHash is not None:
            headers["x-api-user-hash"] = self._userHash

        return headers

    def _validateResponse(self, response):
        if response.status != httplib.OK:
            raise Exception(str(response.status) + " " + response.reason)

    def _login(self, username, password):
        """ performs user login """
        data = {
            "login": username,
            "password": password
        }

        response, request_data = self._sendRequest("login", data)
        self._validateResponse(response)
        self._userHash = request_data["UserHash"]

    def getCities(self):
        """ returns list of cities and their id's """
        """ keys: CityId, Name, Type """
        return self._cities

    def getLanguages(self):
        """ returns list of languages and their id's """
        """ keys: LanguageId, Name, Type """
        return self._languages

    def selectCityById(self, city_id):
        """ gets services and clinics """
        data = {
            "isFromReservation": "true",
            "cityId": city_id
        }

        response, request_data = self._sendRequest("reservationFilter", data)
        self._validateResponse(response)
        self._clinics = request_data["Clinics"]
        self._services = request_data["Services"]
        self._cityId = city_id

    def selectCityByName(self, city_name):
        """ finds cityId by city name """
        for city in self._cities:
            if city_name == city["Name"]:
                self.selectCityById(city["CityId"])
                return

        raise Exception("City '%s' not found!" % city_name)

    def getClinics(self):
        """ returns list of available clinics """
        """ keys: ClinicId, Name, Type and others but empty """
        return self._clinics

    def getServices(self):
        """ returns list of available services """
        """ keys: ServiceId, Name, Type """
        return self._services

    def findVisits(self, clinic_id, service_id, date_from, date_to):
        """ finds visits """
        """ date_from and date_to must be formatted: YYYY-mm-dd """
        if self._cityId is None:
            raise Exception("Error: select city first, use selectCityById or selectCityByName")

        data = {
            "cityId": self._cityId,
            "clinicId": clinic_id,
            "serviceId": service_id,
            "termDateFrom": date_from,
            "termDateTo": date_to,
            "showOnlyFree": "true",
            "ResultOnPage": 100,  # max number of results
            "page": 1
        }

        response, request_data = self._sendRequest("visits", data)

        if response.status == httplib.OK:
            return request_data

        elif response.status == httplib.NOT_FOUND:
            return []

        else:
            # throw an exception
            self._validateResponse(response)
