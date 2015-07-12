from JumpScale import j

class system_packagemanager(j.code.classGetBase()):
    """
    gateway to grid
    """
    def __init__(self):
        pass
        
        self._te={}
        self.actorname="packagemanager"
        self.appname="system"


    def action(self, nid, domain, pname, action, **kwargs):
        """
        use agentcontroller to execute action on a jpackage
        give good category for job so its easy to fetch info later
        return jobid
        param:nid id of node
        param:domain domain name for jpackage
        param:pname name for jpackage
        param:action action to be executed on jpackage
        result str
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method action")

    def getJPackageFilesInfo(self, nid, domain, pname, **kwargs):
        """
        ask the right processmanager on right node to get the information (will query jpackages underneath)
        returns all relevant info about files of jpackage
        param:nid id of node
        param:domain domain name for jpackage
        param:pname name for jpackage
        result json
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getJPackageFilesInfo")

    def getJPackageInfo(self, nid, domain, pname, **kwargs):
        """
        ask the right processmanager on right node to get the information (will query jpackages underneath)
        returns all relevant info about 1 jpackage
        param:nid id of node
        param:domain domain name for jpackage
        param:pname name for jpackage
        result json
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getJPackageInfo")

    def getJPackages(self, nid, domain, **kwargs):
        """
        ask the right processmanager on right node to get the information (will query jpackages underneath)
        lists installed, name, domain, version
        param:nid id of node
        param:domain optional domain name for jpackage
        result json
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getJPackages")
