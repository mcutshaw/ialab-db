#!/usr/bin/python3.6

import sys
import configparser
import time
from db import ialab_db
from lxml import *
from ldap_class import ldapConnection
from pyvcloud.vcd.client import BasicLoginCredentials
from pyvcloud.vcd.client import Client
from pyvcloud.vcd.client import EntityType
from pyvcloud.vcd.org import Org
from pyvcloud.vcd.vdc import VDC
from pyvcloud.vcd.vapp import VApp
from pyvcloud.vcd.exceptions import EntityNotFoundException
import requests

class vcloud:
    def __init__(self,config):

        self.host = config['Main']['Host']
        self.org = config['Main']['Org']
        self.user = config['Main']['User']
        self.password = config['Main']['Password']
        self.vdc = config['Main']['Vdc']

        self.client = self.login()

        self.org_resource = self.client.get_org()
        self.org = Org(self.client, resource=self.org_resource)

        self.vdc_resource = self.org.get_vdc(self.vdc)
        self.vdc = VDC(self.client, resource=self.vdc_resource)


    def login(self):
        requests.packages.urllib3.disable_warnings()
        client = Client(self.host,
                    api_version='29.0',
                    verify_ssl_certs=False,
                    log_file='pyvcloud.log',
                    log_requests=True,
                    log_headers=True,
                    log_bodies=True)
        client.set_credentials(BasicLoginCredentials(self.user, self.org, self.password))
        return client

    def _getvapp(self, name):
        vapp = self.vdc.get_vapp(name)
        vapp = VApp(self.client, resource=vapp)
        return vapp
    
    def addUsersToVapp(self, vapp, memberList):
        dicts = []
        access_level='ReadOnly'
        user_type='user'
        for member in memberList:
            print(member)
            dicts.append({'type':user_type,'name':member,'access_level':access_level})
        vapp.add_access_settings(dicts)

    def addUserToVapp(self, vapp, member):
        dicts = []
        access_level='ReadOnly'
        user_type='user'
        dicts.append({'type':user_type,'name':member,'access_level':access_level})
        try:
            vapp.add_access_settings(dicts)
        except EntityNotFoundException:
            print('User: {user} failed'.format(user=member))

