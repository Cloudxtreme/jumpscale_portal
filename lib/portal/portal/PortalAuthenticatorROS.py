from JumpScale import j
import time

class PortalAuthenticatorROS(object):

    def __init__(self, ros):
        self.ros = ros.system.user
        self.rosgroups = ros.system.group
        self.key2user={user['authkey']:user['id'] for user in self.ros.search({}, nativequery={'authkey':{'$ne': ''}})}
    
    def getUserFromKey(self,key):
        if not key in self.key2user:
            return "guest"
        return self.key2user[key]

    def _getkey(self, username, ros):
        results = ros.search({'id': username})
        if results:
            return results[0]['guid']
        else:
            return "%s_%s" % (j.application.whoAmI.gid, username)

    def getUserInfo(self, user):
        return self.ros.get(self._getkey(user, self.ros))

    def getGroupInfo(self, groupname):
        return self.rosgroups.get(self._getkey(groupname, self.rosgroups))

    def userExists(self, user):
        return self.ros.exists(self._getkey(user, self.ros))

    def createUser(self, username, password, email, groups, domain):
        user = self.ros.new()
        user.id=username
        if isinstance(groups, basestring):
            groups = [groups]
        user.groups=groups
        if isinstance(email, basestring):
            email = [email]
        user.emails=email
        user.domain=domain
        user.passwd=j.tools.hash.md5_string(password)
        self.ros.set(user)

    def listUsers(self):
        return self.ros.search({})

    def listGroups(self):
        return self.rosgroups.search({})

    def getGroups(self,user):
        try:
            userinfo = self.getUserInfo(user).__dict__
            return userinfo['groups'] + ["all"]
        except:
            return ["guest","guests"]

    def loadFromLocalConfig(self):
        #@tddo load from users.cfg & populate in ros
        #see jsuser for example
        pass

    def authenticate(self,login,passwd):
        """
        """
        login = login[0] if isinstance(login, list) else login
        passwd = passwd[0] if isinstance(passwd, list) else passwd
        result=self.ros.authenticate(name=login,passwd=passwd)
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
        return [ x.model.id.lower() for x in  spaceloader.spaces.values()]
