from JumpScale import j
from JumpScale.portal.portal import exceptions
from JumpScale.portal.portal.auth import auth

class system_usermanager(j.code.classGetBase()):

    """
    register a user (can be done by user itself, no existing key or login/passwd is needed)

    """

    def __init__(self):

        self._te = {}
        self.actorname = "usermanager"
        self.appname = "system"
        self.ros = j.clients.ros.get()
        self.modelUser = self.ros.system.user
        self.modelGroup = self.ros.system.group

    def authenticate(self, name, secret, **kwargs):
        """
        The function evaluates the provided username and password and returns a session key.
        The session key can be used for doing api requests. E.g this is the authkey parameter in every actor request.
        A session key is only vallid for a limited time.
        param:username username to validate
        param:password password to validate
        result str,,session
        """
        ctx = kwargs['ctx']
        if j.core.portal.active.auth.authenticate(name, secret):
            session = ctx.env['beaker.get_session']()  # create new session
            session['user'] = name
            session.save()
            return session.id
        raise exceptions.Unauthorized("Unauthorized")

    @auth(['admin'])
    def userget(self, name, **kwargs):
        """
        get a user
        param:name name of user
        """
        return self.modelUser.get("%s_%s"%(j.application.whoAmI.gid,name))

    def usergroupsget(self, user, **args):
        """
        return list of groups in which user is member of
        param:user name of user
        result list(str)

        """
        raise NotImplementedError("not implemented method getusergroups")
        user = self._userGet(user)

        if user == None:
            # did not find user
            result = []
        else:
            # print "usergroups:%s" % user.groups
            result = user.groups

        return result

    def _getUser(self, user):
        users = self.modelUser.search({'id': user})[1:]
        if not users:
            return None
        return self.modelUser.get(users[0]['guid'])

    @auth(['admin'])
    def editUser(self, username, groups, emails, domain, password, **kwargs):
        ctx = kwargs['ctx']
        user = self._getUser(username)
        if not user:
            ctx.start_response('404 Not Found', [('Content-Type', 'text/plain')])
            return "User %s not found" % username
        if groups:
            if isinstance(groups, basestring):
                groups = [x.strip() for x in groups.split(',')]
            elif not isinstance(groups, list):
                ctx.start_response('400 Bad Request', [('Content-Type', 'text/plain')])
                return "Groups paramter should be a list or string"
        else:
            groups = []
        if emails:
            if isinstance(emails, basestring):
                emails = [x.strip() for x in emails.split(',')]
            elif not isinstance(emails, list):
                ctx.start_resonpnse('400 Bad Request', [('Content-Type', 'text/plain')])
                return "Emails should be a list or a comma seperated string"
            user.emails = emails
        if domain:
            user.domain = domain
        if password:
            user.passwd = j.tools.hash.md5_string(password)

        user.groups = groups
        self.modelUser.set(user)
        return True

    @auth(['admin'])
    def delete(self, username, **kwargs):
        self.modelUser.delete(username)
        return True

    @auth(['admin'])
    def deleteGroup(self, id, **kwargs):
        self.modelGroup.delete(id)

    @auth(['admin'])
    def createGroup(self, name, domain, description, **args):
        """
        create a group
        param:name name of group
        param:domain of group
        param:description of group
        result bool

        """
        if self.modelGroup.search({'id': name})[1:]:
            raise exceptions.Conflict("Group with name %s already exists" % name)
        group = self.modelGroup.new()
        group.id = name
        group.domain = domain
        group.description = description
        self.modelGroup.set(group)
        return True

    @auth(['admin'])
    def editGroup(self, name, domain, description, users, **args):
        """
        edit a group
        param:name name of group
        param:domain of group
        param:description of group
        result bool

        """
        groups = self.modelGroup.search({'id': name})[1:]
        if not groups:
            raise exceptions.NotFound("Group with name %s does not exists" % name)
        else:
            group = groups[0]
        if users and isinstance(users, basestring):
            users = users.split(',')
        group['id'] = name
        group['domain'] = domain
        group['description'] = description
        group['users'] = users
        self.modelGroup.set(group)
        return True

    @auth(['admin'])
    def create(self, username, emails, password, groups, domain, **kwargs):
        ctx = kwargs['ctx']
        headers = [('Content-Type', 'text/plain'), ]
        check, result = self._checkUser(username)
        if check:
            ctx.start_response('409', headers)
            return "Username %s already exists" % username
        groups = groups or []
        return j.core.portal.active.auth.createUser(username, password, emails, groups, None)

    def _checkUser(self, username):
        users = self.modelUser.search({'id': username})[1:]
        if not users:
            return False, 'User %s does not exist' % username
        return True, users[0]

    def userexists(self, name, **args):
        """
        param:name name
        result bool

        """
        return self.modelUser.exists("%s_%s"%(j.application.whoAmI.gid,name))

    def whoami(self, **kwargs):
        """
        result current user
        """
        ctx = kwargs["ctx"]
        return str(ctx.env['beaker.session']["user"])


    def userregister(self, name, passwd, emails, reference, remarks, config, **args):
        """
        param:name name of user
        param:passwd chosen passwd (will be stored hashed in DB)
        param:emails comma separated list of email addresses
        param:reference reference as used in other application using this API (optional)
        param:remarks free to be used field by client
        param:config free to be used field to store config information e.g. in json or xml format
        result bool

        """
        # put your code here to implement this method
        raise NotImplementedError("not implemented method userregister")
