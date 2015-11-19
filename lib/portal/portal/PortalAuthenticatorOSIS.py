from JumpScale import j
import time

class PortalAuthenticatorOSIS(object):

    def __init__(self, osis):
        self.osisuser = j.clients.osis.getCategory(osis, "system", "user")
        self.osisgroup = j.clients.osis.getCategory(osis, "system", "group")
        self.key2user = {user['authkey']: user['id'] for user in self.osisuser.simpleSearch({}, nativequery={'authkey': {'$ne': ''}})}

    def getUserFromKey(self,key):
        if not key in self.key2user:
            return "guest"
        return self.key2user[key]

    def _getkey(self, username, osis):
        results = osis.simpleSearch({'id': username}, withguid=True)
        if results:
            return results[0]['guid']
        else:
            return None

    def getUserInfo(self, user):
        key = self._getkey(user, self.osisuser)
        if not key:
            return None
        return self.osisuser.get(key)

    def getGroupInfo(self, groupname):
        key = self._getkey(groupname, self.osisgroup)
        if not key:
            return None
        return self.osisgroup.get(key)

    def userExists(self, user):
        return self._getkey(user, self.osisuser) is not None

    def createUser(self, username, password, email, groups, domain):
        user = self.osisuser.new()
        user.id = username
        if isinstance(groups, str):
            groups = [groups]
        user.groups = groups
        if isinstance(email, str):
            email = [email]
        user.emails = email
        user.domain = domain
        user.passwd = j.tools.hash.md5_string(password)
        return self.osisuser.set(user)


    def listUsers(self):
        return self.osisuser.simpleSearch({})

    def listGroups(self):
        return self.osisgroup.simpleSearch({})

    def getGroups(self,user):
        try:
            userinfo = self.getUserInfo(user).__dict__
            return userinfo['groups'] + ["all"]
        except:
            return ["guest","guests"]

    def loadFromLocalConfig(self):
        #@tddo load from users.cfg & populate in osis
        #see jsuser for example
        pass

    def authenticate(self,login,passwd):
        """
        """
        login = login[0] if isinstance(login, list) else login
        passwd = passwd[0] if isinstance(passwd, list) else passwd
        result=self.osisuser.authenticate(name=login, passwd=passwd)
        return result['authenticated']

    def getUserSpaceRights(self, username, space, **kwargs):
        spaceobject = kwargs['spaceobject']
        groupsusers = set(self.getGroups(username))

        for groupuser in groupsusers:
            if groupuser in spaceobject.model.acl:
                right = spaceobject.model.acl[groupuser]
                if right == "*":
                    return username, "rwa"
                return username, right

        # No rights .. check guest
        rights = spaceobject.model.acl.get('guest', '')
        return username, rights

    def getUserSpaces(self, username, **kwargs):
        spaceloader = kwargs['spaceloader']
        return [ x.model.id.lower() for x in  list(spaceloader.spaces.values())]
