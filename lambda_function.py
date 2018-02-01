#!/usr/bin/env python
#
# Source: https://github.com/Strosel/Carnet-alexa
# Huge thank you to https://github.com/reneboer/python-carnet-client/
#

import re
import json
import time

import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '/modules'))
import requests

from urlparse import urlsplit

class VWCarnet(object):
    def __init__(self, args):
        self.output = ""
        self.carnet_username = ""
        self.carnet_password = ""
        if args["httpMethod"] == "GET":
            self.carnet_task = args["queryStringParameters"]['task'].lower()
            self.action = args["queryStringParameters"]['action'].lower()
        else:
            self.carnet_task = "0"
            self.action = "0"

        # Fake the VW CarNet mobile app headers
        self.headers = { 'Accept': 'application/json, text/plain, */*', 'Content-Type': 'application/json;charset=UTF-8', 'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0.1; D5803 Build/23.5.A.1.291; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/63.0.3239.111 Mobile Safari/537.36' }
        self.session = requests.Session()

        try:
            self._carnet_logon()
        except:
            self.output += "Unable to log in at this time. Have you entered the correct credentials?"

    def _carnet_logon(self):
        AUTHHEADERS = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0.1; D5803 Build/23.5.A.1.291; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/63.0.3239.111 Mobile Safari/537.36'}

        auth_base = "https://security.volkswagen.com"
        base = "https://www.volkswagen-car-net.com"

        # Regular expressions to extract data
        csrf_re = re.compile('<meta name="_csrf" content="([^"]*)"/>')
        redurl_re = re.compile('<redirect url="([^"]*)"></redirect>')
        viewstate_re = re.compile('name="javax.faces.ViewState" id="j_id1:javax.faces.ViewState:0" value="([^"]*)"')
        authcode_re = re.compile('code=([^"]*)&')
        authstate_re = re.compile('state=([^"]*)')

        def extract_csrf(r):
            return csrf_re.search(r.text).group(1)

        def extract_redirect_url(r):
            return redurl_re.search(r.text).group(1)

        def extract_view_state(r):
            return viewstate_re.search(r.text).group(1)

        def extract_code(r):
            return authcode_re.search(r).group(1)

        def extract_state(r):
            return authstate_re.search(r).group(1)

        # Request landing page and get CSFR:
        r = self.session.get(base + '/portal/en_GB/web/guest/home')
        if r.status_code != 200:
            return ""
        csrf = extract_csrf(r)

        # Request login page and get CSRF
        AUTHHEADERS["Referer"] = base + '/portal'
        AUTHHEADERS["X-CSRF-Token"] = csrf
        r = self.session.post(base + '/portal/web/guest/home/-/csrftokenhandling/get-login-url', headers=AUTHHEADERS)
        if r.status_code != 200:
            return ""
        responseData = json.loads(r.content)
        lg_url = responseData.get("loginURL").get("path")

        # no redirect so we can get values we look for
        r = self.session.get(lg_url, allow_redirects=False, headers = AUTHHEADERS)
        if r.status_code != 302:
            return ""
        ref_url = r.headers.get("location")

        # now get actual login page and get session id and ViewState
        r = self.session.get(ref_url, headers = AUTHHEADERS)
        if r.status_code != 200:
            return ""
        view_state = extract_view_state(r)

        # Login with user details
        AUTHHEADERS["Faces-Request"] = "partial/ajax"
        AUTHHEADERS["Referer"] = ref_url
        AUTHHEADERS["X-CSRF-Token"] = ''

        post_data = {
            'loginForm': 'loginForm',
            'loginForm:email': self.carnet_username,
            'loginForm:password': self.carnet_password,
            'loginForm:j_idt19': '',
            'javax.faces.ViewState': view_state,
            'javax.faces.source': 'loginForm:submit',
            'javax.faces.partial.event': 'click',
            'javax.faces.partial.execute': 'loginForm:submit loginForm',
            'javax.faces.partial.render': 'loginForm',
            'javax.faces.behavior.event': 'action',
            'javax.faces.partial.ajax': 'true'
        }

        r = self.session.post(auth_base + '/ap-login/jsf/login.jsf', data=post_data, headers = AUTHHEADERS)
        if r.status_code != 200:
            return ""
        ref_url = extract_redirect_url(r).replace('&amp;', '&')

        # redirect to link from login and extract state and code values
        r = self.session.get(ref_url, allow_redirects=False, headers = AUTHHEADERS)
        if r.status_code != 302:
            return ""
        ref_url2 = r.headers.get("location")

        code = extract_code(ref_url2)
        state = extract_state(ref_url2)

        # load ref page
        r = self.session.get(ref_url2, headers = AUTHHEADERS)
        if r.status_code != 200:
            return ""

        AUTHHEADERS["Faces-Request"] = ""
        AUTHHEADERS["Referer"] = ref_url2
        post_data = {
            '_33_WAR_cored5portlet_code': code,
            '_33_WAR_cored5portlet_landingPageUrl': ''
        }
        r = self.session.post(base + urlsplit(
            ref_url2).path + '?p_auth=' + state + '&p_p_id=33_WAR_cored5portlet&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_count=1&_33_WAR_cored5portlet_javax.portlet.action=getLoginStatus',
                   data=post_data, allow_redirects=False, headers=AUTHHEADERS)
        if r.status_code != 302:
            return ""

        ref_url3 = r.headers.get("location")
        r = self.session.get(ref_url3, headers=AUTHHEADERS)

        # We have a new CSRF
        csrf = extract_csrf(r)

        # Update headers for requests
        self.headers["Referer"] = ref_url3
        self.headers["X-CSRF-Token"] = csrf
        self.url = ref_url3

    def _carnet_post(self, command):
        #print(command)
        r = self.session.post(self.url + command, headers = self.headers)
        return r.content

    def _carnet_post_action(self, command, data):
        #print(command)
        r = self.session.post(self.url + command, json=data, headers = self.headers)
        return r.content

    def _carnet_start_charge(self):
        post_data = {
            'triggerAction': True,
            'batteryPercent': '100'
        }
        return json.loads(self._carnet_post_action('/-/emanager/charge-battery', post_data))

    def _carnet_stop_charge(self):
        post_data = {
            'triggerAction': False,
            'batteryPercent': '99'
        }
        return json.loads(self._carnet_post_action('/-/emanager/charge-battery', post_data))


    def _carnet_start_climat(self):
        post_data = {
            'triggerAction': True,
            'electricClima': True
        }
        return json.loads(self._carnet_post_action('/-/emanager/trigger-climatisation', post_data))


    def _carnet_stop_climat(self):
        post_data = {
            'triggerAction': False,
            'electricClima': True
        }
        return json.loads(self._carnet_post_action('/-/emanager/trigger-climatisation', post_data))

    def _carnet_start_window_melt(self):
        post_data = {
            'triggerAction': True
        }
        return json.loads(self._carnet_post_action('/-/emanager/trigger-windowheating', post_data))

    def _carnet_stop_window_melt(self):
        post_data = {
            'triggerAction': False
        }
        return json.loads(self._carnet_post_action('/-/emanager/trigger-windowheating', post_data))

    def _carnet_print_action(self, resp):
        if not 'actionNotification' in resp:
            self.output = "Error. Command unavailable at the moment"
        else:
            if self.action == "start":
                self.output = "Started %s" % (self.carnet_task)
            elif self.action == "stop":
                self.output = "Stopped %s" % (self.carnet_task)

    def _carnet_do_action(self):
        if self.action == "start":
            if 'charg' in self.carnet_task:
                resp = self._carnet_start_charge()
                self._carnet_print_action(resp)
                return True

            elif 'climat' in self.carnet_task or ('heat' in self.carnet_task and 'window' not in self.carnet_task):
                resp = self._carnet_start_climat()
                self._carnet_print_action(resp)
                return True

            elif 'window' in self.carnet_task:
                resp = self._carnet_start_window_melt()
                self._carnet_print_action(resp)
                return True
            else:
                self.output = "Error! not a GET variable"
                return False
        elif self.action == "stop":
            if 'charg' in self.carnet_task:
                resp = self._carnet_stop_charge()
                self._carnet_print_action(resp)
                return True

            elif 'climat' in self.carnet_task or ('heat' in self.carnet_task and 'window' not in self.carnet_task):
                resp = self._carnet_stop_climat()
                self._carnet_print_action(resp)
                return True

            elif 'window' in self.carnet_task:
                resp = self._carnet_stop_window_melt()
                self._carnet_print_action(resp)
                return True
            else:
                self.output = "Error! not a GET variable"
                return False
        else:
            self.output = "Error! not a GET variable"
            return False

def main(event, context):

    vw = VWCarnet(event)
    if vw.output == "":
        vw._carnet_do_action()
    return {
        "isBase64Encoded": False,
        "statusCode": 200,
        "headers": {},
        "body": vw.output
    }
    return response
