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
        self.userHash = None

    def sendRequest(self, action, data):
        data = urllib.urlencode(data)
        headers = self.getHeaders()

        conn = httplib.HTTPSConnection(API_HOST)
        conn.request("POST", API_BASE_URL + action, data, headers)
        response = conn.getresponse()

        if response.status != httplib.OK:
            raise Exception(str(response.status) + " " + response.reason)

        reply = json.loads(response.read())
        conn.close()

        return reply

    def getHeaders(self):
        return {}
