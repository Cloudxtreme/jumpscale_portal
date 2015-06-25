from JumpScale import j

class system_usermanager(j.code.classGetBase()):
    """
    register a user (can be done by user itself, no existing key or login/passwd is needed)
    """
    def __init__(self):
        pass
        
        self._te={}
        self.actorname="usermanager"
        self.appname="system"
        #system_usermanager_osis.__init__(self)


    def authenticate(self, name, secret, **kwargs):
        """
        authenticate and return False if not successfull
        otherwise return secret for api
        param:name name
        param:secret md5 or passwd
        result str
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method authenticate")

    def create(self, username, password, groups, emails, domain, **kwargs):
        """
        create a user
        param:username name of user
        param:password passwd
        param:groups comma separated list of groups this user belongs to
        param:emails comma separated list of email addresses
        param:domain domain of user
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method create")

    def delete(self, username, **kwargs):
        """
        Delete a user
        param:username name of the user
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method delete")

    def editUser(self, username, groups, password, emails, domain, **kwargs):
        """
        set Groups for a user
        param:username name of user
        param:groups name of groups
        param:password password for user
        param:emails comma seperated list of emails or list
        param:domain Domain of user
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method editUser")

    def groupcreate(self, name, groups, **kwargs):
        """
        create a group
        param:name name of group
        param:groups comma separated list of groups this group belongs to
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method groupcreate")

    def userexists(self, name, **kwargs):
        """
        param:name name
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method userexists")

    def userget(self, name, **kwargs):
        """
        get a user
        param:name name of user
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method userget")

    def usergroupsget(self, user, **kwargs):
        """
        return list of groups in which user is member of
        param:user name of user
        result list(str)
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method usergroupsget")

    def userregister(self, name, passwd, emails, config, reference="''", remarks="''", **kwargs):
        """
        param:name name of user
        param:passwd chosen passwd (will be stored hashed in DB)
        param:emails comma separated list of email addresses
        param:reference reference as used in other application using this API (optional) default=''
        param:remarks free to be used field by client default=''
        param:config free to be used field to store config information e.g. in json or xml format
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method userregister")

    def whoami(self, **kwargs):
        """
        return username
        result str
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method whoami")
