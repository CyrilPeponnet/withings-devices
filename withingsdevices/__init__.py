# -*- coding: utf-8 -*-
#
# withings-scale.py
#
# Copyright (C) 2014 Cyril Peponnet <cyril@peponnet.fr>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import requests, re, datetime

AUTH_URL     = "https://account.withings.com/connectionuser/account_login?r=https%3A%2F%2Fhealthmate.withings.com%2Fhome"
DEVICES_URL  = "https://healthmate.withings.com/index/service/association"
MEASURES_URL = "https://healthmate.withings.com/index/service/v2/measure"
TYPE_TEMPERATURE = 12
TYPE_CO2         = 35

class WithingsDevices(object):
    """
    Simple class object to retrieve devices informations not available throught official API
    This will use email/password and it's kind of hacky but it works
    """
    def __init__(self, email, password):
        """
        Init a WithingsDevices object
        @type email: string
        @params email : email used to connect to your withings account
        @type password: string
        @params password: the password to use
        """
        self._email = email
        self._password = password
        self._session = requests.Session()
        self.devices = {}

    def _post(self, url, params):
        """
        Make the post request
        @type url: string
        @params url: the url
        @type params: dict
        @params params: the parametters to post
        """
        result = self._session.post(url, params)
        if not result.status_code == 200:
            print "Request failed :\n%s" % result.text
            return None
        else:
            try:
                return result.json()
            except:
                return result.content

    def _login(self):
        """
        Perform the authentication to withings services
        Will populate required vars
        """
        page = self._post(AUTH_URL, {'email': self._email, 'is_admin': None, 'password': self._password, 'use_authy': None})
        if page:
            vars     = {item.split('=')[0].strip():item.split('=')[1].strip().replace("\"","") for item in re.findall(r'(\S+\s*=\s*"\S+")', page)}
            session  = {item.split(':')[0].strip().lower():item.split(':')[1].strip().replace("\"","") for item in re.findall(r'(\S+Id\s*:\s*"\S+")', page)}
            self.app = {'appname':vars[u"WS_APP_NAME"], 'appliver':vars[u"REV"], 'apppfm':vars[u"WS_APP_PFM"]}
            self.sessionid = session['sessionid']
            self.accountid = session['accountid']
            del vars
            del session
            return True
        return False

    def _get_devices(self):
        """
        Retrieves the devices linked to the account id
        """
        devices = self._post(DEVICES_URL, dict({'sessionid': self.sessionid, 'accountid':self.accountid, 'type':-1, 'enrich':'t', 'action':'getbyaccountid'}.items() + self.app.items()))
        if devices and isinstance(devices, dict):
            for device in devices['body']['associations']:
                if device['deviceid'] in self.devices.keys():
                    self.devices[device['deviceid']].update({'name':device['devicename'], 'batt_lvl':device['deviceproperties']['batterylvl'], 'lastseen':device['deviceproperties']['lastweighindate']})
                else:
                    self.devices.update({device['deviceid']:{'name':device['devicename'], 'batt_lvl':device['deviceproperties']['batterylvl'], 'lastseen':device['deviceproperties']['lastweighindate']}})

    def _retrieve_data(self, device=None, startdate=None, enddate=None):
        """
        Retrieve data for devices if startdate / enddate is not specified this will return
        only the last entry.
        @type device: int
        @params device: the deviceid to filter
        @type startdate: int
        @params startdate: the unixtime start date
        @type enddate: int
        @params enddate : the unixtime end date
        """
        for deviceid, device_attr in self.devices.iteritems():
            if device and not deviceid == device:
                continue
            period = {}
            if startdate and enddate:
                period = {'startdate':startdate, 'enddate':enddate}
            params = dict({'sessionid': self.sessionid, 'deviceid':deviceid, 'meastype':'%i,%i' % (TYPE_TEMPERATURE,TYPE_CO2), 'action':'getmeashf'}.items() + self.app.items() + period.items())
            results = self._post(MEASURES_URL, params)
            if results:
                data = {}
                for serie in results['body']['series']:
                    if serie['type'] == TYPE_TEMPERATURE:
                        data['temperature'] = serie['data']
                    elif serie['type'] == TYPE_CO2:
                        data['co2'] = serie['data']
            self.devices[deviceid].update({'data':data})

    def fetch_devices(self):
        """
        Return the list of devices
        """
        self._login()
        self._get_devices()

    def fetch_data(self, deviceid=None, last_days=None):
        """
        Return data for a given device or all if None for last_days or the last measure.
        @type deviceid: int
        @params deviceid: the device id
        @type last_days: int
        @params last_days: the number of days you want your data retrieves
        """
        self._login()
        self._get_devices()
        startdate=None
        enddate=None
        if last_days:
            now = datetime.datetime.now()
            enddate = now.strftime("%s")
            startdate = (now - datetime.timedelta(last_days)).strftime("%s")
        self._retrieve_data(deviceid,startdate, enddate)
