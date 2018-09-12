#!/usr/bin/python3.6
import hashlib
import configparser
import pymysql

class ialab_db:

    def __init__(self,config):
        try:
            self.host = config['Database']['Host']
            self.user = config['Database']['User']
            self.database = config['Database']['DB']
            self.password = config['Database']['Password']

        except Exception as e:
            print("Config Error!")
            print(e)
            exit()
        try:    
            self.connect()
        except:
            print("Database Error!")
        tables = self.execute("show tables;")         
        if(('ialab',) not in tables): 

            self.execute('''CREATE TABLE ialab
                            (username VARCHAR(100) PRIMARY KEY,
                            href VARCHAR(100) NOT NULL,
                            full_name VARCHAR(100) NOT NULL);''')

        if(('ldap',) not in tables): 
            self.execute('''CREATE TABLE ldap
                            (username VARCHAR(100),
                            email VARCHAR(100),
                            FOREIGN KEY(username) REFERENCES ialab(username));''')

    def close(self):
        self.conn.close()

    def connect(self):
        self.conn = pymysql.connect(host=self.host, user=self.user, password=self.password, db=self.database)
        self.cur = self.conn.cursor()

    def execute(self,command):
        self.connect()
        self.cur.execute(command)
        self.conn.commit()
        text_return = self.cur.fetchall()
        self.close()
        return text_return

    def executevar(self,command,operands):
        self.connect()
        self.cur.execute(command,operands)
        self.conn.commit()
        text_return = self.cur.fetchall()
        self.close()
        return text_return

    def insertLdapUser(self,username, email):
        self.executevar('INSERT INTO `ldap` VALUES(%s,%s)', (username, email))

    def insertIalabUser(self,username,href,full_name):
        self.executevar('INSERT INTO `ialab` VALUES(%s,%s,%s)', (username, href, full_name))
    
    def checkIalabUserExists(self,username):
        print(username)
        count = self.executevar('SELECT COUNT(`username`) FROM `ialab` WHERE `username`=%s', (username,))
        if(int(count[0][0])) > 0:
            return True
        else:
            return False

    def checkIalabUserExistsByID(self,href):
        count = self.executevar('SELECT COUNT(`username`) FROM `ialab` WHERE `href`=%s', (href,))
        if(int(count[0][0])) > 0:
            return True
        else:
            return False
    
    def checkLdapUserExists(self,username):
        count = self.executevar('SELECT COUNT(`username`) FROM `ldap` WHERE `username`=%s', (username,))
        if(int(count[0][0])) > 0:
            return True
        else:
            return False
    
