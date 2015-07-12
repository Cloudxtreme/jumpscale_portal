from JumpScale import j

class system_logs(j.code.classGetBase()):
    """
    Gets jobs that match criteria
    """
    def __init__(self):
        pass
        
        self._te={}
        self.actorname="logs"
        self.appname="system"


    def listECOs(self, nid, **kwargs):
        """
        Gets ECOs for node
        param:nid 
        result dict
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method listECOs")

    def listJobs(self, ffrom, to, nid, gid, parent, state, jsorganization, jsname, nip, roles, **kwargs):
        """
        param:ffrom format -4h, -3d, etc
        param:to format -4h, -3d, etc
        param:nid 
        param:gid 
        param:parent 
        param:state 
        param:jsorganization 
        param:jsname 
        param:nip 
        param:roles 
        result dict
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method listJobs")

    def listLogs(self, nid, **kwargs):
        """
        Gets logs (for node)
        param:nid 
        result dict
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method listLogs")

    def listNodes(self, **kwargs):
        """
        Gets nodes for grid
        result dict
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method listNodes")
