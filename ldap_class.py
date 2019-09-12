from ldap3 import Server, Connection, ALL
import configparser

class ldapConnection:

    def __init__(self,config):

        self.config = configparser.ConfigParser()
        self.server = config['LDAP']['Server']
        self.username = config['LDAP']['Username']
        self.password = config['LDAP']['Password']
        self.baseDN = config['LDAP']['BaseDN']
        filters = config.items('SearchDN')
        self.filterList = []
        for item in filters:
            self.filterList.append(item[1])

        self.s = Server(self.server, get_info=ALL)  
        self.c = Connection(self.s, user='CN='+self.username+','+self.baseDN, password=self.password)

        if not self.c.bind():
            print('error in bind', self.c.result)
        self.c.start_tls()

    def getUsernameFilter(self,usernames):
        searchFilter = '(|'
        if type(usernames) == list:
            for username in usernames:
                searchFilter+='(sAMAccountName=' + username + ')'
            searchFilter+=')'
            return searchFilter
        elif type(usernames) == str:
            searchFilter+='(sAMAccountName=' + usernames + ')'
            searchFilter+=')'
            return searchFilter

    def getEmailFilter(self,emails):
        searchFilter = '(|'
        if type(emails) == list:
            for email in emails:
                searchFilter+='(proxyAddresses=*' + email + '*)'
            searchFilter+=')'
            return searchFilter
        elif type(emails) == str:
            searchFilter+='(proxyAddresses=*' + emails + '*)'
            searchFilter+=')'
            return searchFilter

    def getUserByUsername(self, username):
        searchFilter = self.getUsernameFilter(username)
        users = []
        for item in self.filterList:
            self.c.search(item,searchFilter,attributes=['cn', 'proxyAddresses', 'sAMAccountName'])
            for entry in self.c.entries:
                accountUsername = entry['sAMAccountName']
                proxyAddresses = entry['proxyAddresses']
                accountUsername = str(accountUsername).replace('sAMAccountName: ','')
                emails = []
                for email in proxyAddresses:
                    if 'smtp' in email.lower():
                        emails.append(email.lower().replace('smtp:',''))
                users.append((accountUsername, emails))
        return users

    def getUserByUsernameByEmail(self, email):
        searchFilter = self.getEmailFilter(email)
        users = []

        for item in self.filterList:
            self.c.search(item,searchFilter,attributes=['cn', 'proxyAddresses', 'sAMAccountName'])
            for entry in self.c.entries:
                accountUsername = entry['sAMAccountName']
                proxyAddresses = entry['proxyAddresses']
                accountUsername = str(accountUsername).replace('sAMAccountName: ','')
                emails = []
                for email in proxyAddresses:
                    if 'smtp' in email.lower():
                        emails.append(email.lower().replace('smtp:',''))
                users.append((accountUsername, emails))
        return users
