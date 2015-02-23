from JumpScale import j
import JumpScale.baselib.gitlab
import gitlab3
import time

class PortalAuthenticatorGitlab(object):
    """
    Main functionality is to provide authenticate() function and other helper functions
    Those functions are all added to client
    """

    def __init__(self, instance='main'):
        self.client = j.clients.gitlab.get(instance=instance)
    
    def authenticate(self, login, password):
        return self.client.authenticate(login, password)
    
    def getGroups(self,username):
        return self.client.getGroups(username)

    def getUserFromKey(self,key):
        new_client = gitlab3.GitLab(self.client.addr, token=key)
        
        try:
            return new_client.current_user().username
        except gitlab3.exceptions.UnauthorizedRequest:
            return "guest"