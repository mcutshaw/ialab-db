#!/usr/bin/python3.6

import sys
import configparser
import time

from db import ialab_db
from ldap_class import ldapConnection

from lxml import *
from pyvcloud.vcd.client import BasicLoginCredentials
from pyvcloud.vcd.client import Client
from pyvcloud.vcd.client import EntityType
from pyvcloud.vcd.org import Org
from pyvcloud.vcd.vdc import VDC
from pyvcloud.vcd.vapp import VApp

#from pyvcloud.vcd.exceptions import *
import requests

def login(user, org, password):
    requests.packages.urllib3.disable_warnings()
    client = Client(host,
                api_version='29.0',
                verify_ssl_certs=False,
                log_file='pyvcloud.log',
                log_requests=True,
                log_headers=True,
                log_bodies=True)
    client.set_credentials(BasicLoginCredentials(user, org, password))
    return client

CONF_PATH = 'ialab-db.conf'
#Read in config variables
config = configparser.ConfigParser()
config.read(CONF_PATH)

host = config['Main']['Host']
org = config['Main']['Org']
user = config['Main']['User']
password = config['Main']['Password']
vdc = config['Main']['Vdc']

db = ialab_db(config)
ldap = ldapConnection(config)
client = login(user, org, password)

org_resource = client.get_org()
org = Org(client, resource=org_resource)

vdc_resource = org.get_vdc(vdc)
vdc = VDC(client, resource=vdc_resource)

users = org.list_users()
for user in users:
    name = user.attrib['name']
    fullName = user.attrib['fullName']
    href = user.attrib['href']

    if db.checkIalabUserExistsByID(href) == False:
        print(name)
        db.insertIalabUser(name, href, fullName)
        ldapUsers = ldap.getUser(name)
        for ldapUser in ldapUsers:
            ldap_username = ldapUser[0]
            for email in ldapUser[1]:
                print(email)
                db.insertLdapUser(ldap_username, email)
    elif db.checkIalabUserExistsByID(href) == False:
        ldapUsers = ldap.getUser(name)
        for ldapUser in ldapUsers:
            ldap_username = ldapUser[0]
            for email in ldapUser[1]:
                print(email)
                db.insertLdapUser(ldap_username, email)
            

    name += ":" + fullName + ':'+  href + '\n'


