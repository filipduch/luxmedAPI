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
        self.userHash = None  # GUID will be obtained after successful login

    def _sendRequest(self, action, data):
        """ sends request to server """
        data = urllib.urlencode(data)
        headers = self._getHeaders()

        conn = httplib.HTTPSConnection(API_HOST)
        conn.request("POST", API_BASE_URL + action, data, headers)
        response = conn.getresponse()

        if response.status != httplib.OK:
            raise Exception(str(response.status) + " " + response.reason)

        reply = json.loads(response.read())
        conn.close()

        return reply

    def _getHeaders(self):
        """ creates necessary headers every request must include """
        timestamp = str(int(time.time())) + "000"
        string_to_hash = API_SECRET + "::" + X_API_VERSION + "::" + X_API_CLIENT + "::" + timestamp

        # add another param if user is already logged-in
        if self.userHash is not None:
            string_to_hash = string_to_hash + "::" + self.userHash

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

        return headers

