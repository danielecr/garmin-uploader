#! /usr/bin/python3

import requests
import re
import configparser

class GarminSignon:

    def __init__(self, email=None, password=None):
        print ("INIT")
        self.params = {
            "service": "http://connect.garmin.com/post-auth/login",
            "clientId": "GarminConnect",
            "consumeServiceTicket": "false",
        }
        self.data = {
            "username": email,
            "password": password,
            "_eventId": "submit",
            "embed": "true",
        }
        self.gcPreResp = requests.get("http://connect.garmin.com/", allow_redirects=False)

    def get_cookies(self):
        data = self.data
        params = self.params
        preResp = requests.get('https://sso.garmin.com/sso/login', params=params)
        print (preResp.status_code)
        self.data["lt"] = re.search("name=\"lt\"\s+value=\"([^\"]+)\"", preResp.text).groups(1)[0]
        self.preCookies = preResp.cookies
        return preResp.cookies

    def sso(self):
        ssoResp = requests.post('https://sso.garmin.com/sso/login',params=self.params,data=self.data, allow_redirects=False, cookies=self.preCookies)
        ticket_match = re.search("ticket=([^']+)'", ssoResp.text)
        print (ticket_match)
        self.ticket = ticket_match.groups(1)[0]
        return ssoResp;

    def ssoFin(self):
        gcPreResp = self.gcPreResp
        gcRedeemResp1 = requests.get("http://connect.garmin.com/post-auth/login", params={"ticket": self.ticket}, allow_redirects=False, cookies=gcPreResp.cookies)
        gcRedeemResp2 = requests.get(gcRedeemResp1.headers["location"], cookies=gcPreResp.cookies, allow_redirects=False)
        self.gcCookies = gcPreResp.cookies

    def getActivities(self):
        cookies = self.gcCookies
        res = requests.get("http://connect.garmin.com/proxy/activity-search-service-1.0/json/activities",params={"start":0,"limit":3},cookies=cookies);
        self.aText = res.text
        res = res.json()["results"];
        self.activities = res

    def printActivities(self):
        res = self.activities
        for act in res['activities']:
            act = act['activity']
            print (act);
            break

    def Upload(self,filename):
        cookies = self.gcCookies
        uploadurl = "http://connect.garmin.com/proxy/upload-service-1.1/json/upload/.fit";
        files = {'file':('2014-06-08-08-56-27.fit', open(filename,'rb'))}
        res = requests.post(uploadurl, files=files, cookies = cookies)
        print ( res.text)
        self.uploadResult = res.json()["detailedImportResult"]
        code =0
        self.uploadResult
        for failure in  self.uploadResult["failures"]:
            for message in failure['messages']:
                if message['code'] == 202:
                    code = 202
        if code == 202:
            self.duplicatedUpload = True
        else:
            self.duplicatedUpload = False
        pass

config = configparser.ConfigParser()
config.read('user.ini')
u = config['User']['username']
p = config['User']['password']

x = GarminSignon(u,p)
a = x.get_cookies()
print (a)
b = x.sso();
print (b.status_code)

ticket_match = re.search("ticket=([^']+)'", b.text)
print (ticket_match)
ticket = ticket_match.groups(1)[0]
print (ticket)
x.ssoFin();
x.getActivities()
x.printActivities()
print (x.aText)
filename = '2014-06-08-08-56-27.fit'
x.Upload(filename)

print ('is duplicated ' + str(x.duplicatedUpload))
str(x.duplicatedUpload)
