from JumpScale import j

class system_gridmanager(j.code.classGetBase()):
    """
    gateway to grid
    """
    def __init__(self):
        pass
        
        self._te={}
        self.actorname="gridmanager"
        self.appname="system"


    def getAgentControllerActiveJobs(self, **kwargs):
        """
        calls internally the agentcontroller
        list jobs now running on agentcontroller
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getAgentControllerActiveJobs")

    def getAgentControllerSessions(self, roles, nid, active, **kwargs):
        """
        calls internally the agentcontroller
        param:roles match on comma separated list of roles (subsets also ok e.g. kvm.  would match all roles starting with kvm.)
        param:nid find for specified node (on which agents are running which have sessions with the agentcontroller)
        param:active is session active or not
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getAgentControllerSessions")

    def getAlerts(self, id, level, descr, descrpub, nid, gid, category, tags, state, from_inittime, to_inittime, from_lasttime, to_lasttime, from_closetime, to_closetime, nrerrorconditions, errorcondition, **kwargs):
        """
        interface to get alert (is optionally the result of an eco)
        param:id only find 1 alert entry
        param:level level between 1 & 3; all levels underneath are found e.g. level 3 means all levels, 1:critical, 2:warning, 3:info
        param:descr match on text in descr
        param:descrpub match on text in descrpub
        param:nid find alerts for specified node
        param:gid find alerts for specified grid
        param:category match on multiple categories; are comma separated
        param:tags comma separted list of tags/labels
        param:state NEW ALERT CLOSED
        param:from_inittime -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find alerts from date specified when they happened first (-4d means 4 days ago)
        param:to_inittime -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find alerts to date specified when they happened first
        param:from_lasttime -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find alerts from date specified when they happened last  (-4d means 4 days ago)
        param:to_lasttime -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find alerts to date specified when they happened last
        param:from_closetime -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find alerts from date specified when they were closed  (-4d means 4 days ago)
        param:to_closetime -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find alerts to date specified when they were closed
        param:nrerrorconditions nr of times errorcondition happened
        param:errorcondition errorcondition(s) which caused this alert
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getAlerts")

    def getDisks(self, id, guid, gid, nid, fs, sizeFrom, sizeTo, freeFrom, freeTo, mounted, ssd, path, model, description, mountpoint, type, active, lastcheckFrom, lastcheckTo, **kwargs):
        """
        list found disks (are really partitions) (comes from ros)
        param:id find based on id
        param:guid find based on guid
        param:gid find disks for specified grid
        param:nid find disks for specified node
        param:fs ext4;xfs;...
        param:sizeFrom in MB
        param:sizeTo in MB
        param:freeFrom in MB
        param:freeTo in MB
        param:mounted is disk mounted
        param:ssd is disk an ssd
        param:path match on part of path e.g. /dev/sda
        param:model match on part of model
        param:description match on part of description
        param:mountpoint match on part of mountpoint
        param:type type e.g. BOOT DATA CACHE
        param:active True,is the disk still active
        param:lastcheckFrom -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find disks with lastcheckFrom  (-4d means 4 days ago)
        param:lastcheckTo -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find disk with lastcheckTo  (-4d means 4 days ago)
        result list(list)
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getDisks")

    def getErrorconditions(self, id, level, descr, descrpub, from_, to, nid, gid, category, tags, type, jid, jidparent, jsorganization, jsname, **kwargs):
        """
        interface to get errorcondition information (eco)
        param:id only find 1 eco entry
        param:level level between 1 & 3; all levels underneath are found e.g. level 3 means all levels
        param:descr match on text in descr
        param:descrpub match on text in descrpub
        param:from_ -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find ecos from date specified  (-4d means 4 days ago)
        param:to -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find ecos to date specified
        param:nid find ecos for specified node
        param:gid find ecos for specified grid
        param:category match on multiple categories; are comma separated
        param:tags comma separted list of tags/labels
        param:type optional unique type id for eco
        param:jid find ecos for specified job
        param:jidparent find ecos which are children of specified parent job
        param:jsorganization find ecos coming from scripts from this org
        param:jsname find ecos coming from scripts with this name
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getErrorconditions")

    def getGrids(self, **kwargs):
        """
        list grids
        result list(list)
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getGrids")

    def getJob(self, id, guid, includeloginfo, includechildren, **kwargs):
        """
        gets relevant info of job (also logs)
        can be used toreal time return job info
        param:id obliged id of job
        param:guid find based on guid
        param:includeloginfo True,if true fetch all logs of job & return as well
        param:includechildren True,if true look for jobs which are children & return that info as well
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getJob")

    def getJobs(self, id, guid, from_, to, nid, gid, parent, roles, state, organization, name, description, category, source, **kwargs):
        """
        interface to get job information
        param:id only find 1 job entry
        param:guid find based on guid
        param:from_ -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find jobs from date specified  (-4d means 4 days ago)
        param:to -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find jobs to date specified
        param:nid find jobs for specified node
        param:gid find jobs for specified grid
        param:parent find jobs which are children of specified parent
        param:roles match on comma separated list of roles (subsets also ok e.g. kvm.  would match all roles starting with kvm.)
        param:state OK;ERROR;...
        param:organization 
        param:name 
        param:description any description when asked for the job
        param:category category in dot notation
        param:source who asked for the job is free text
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getJobs")

    def getJumpscript(self, organization, name, **kwargs):
        """
        calls internally the agentcontroller to fetch detail for 1 jumpscript
        param:organization 
        param:name 
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getJumpscript")

    def getJumpscripts(self, organization, active, **kwargs):
        """
        calls internally the agentcontroller
        return: lists the jumpscripts with main fields (organization, name, category, descr)
        param:organization find jumpscripts
        param:active is session active or not
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getJumpscripts")

    def getLogs(self, id, level, category, text, to, jid, nid, gid, pid, tags, from_='-1h', **kwargs):
        """
        interface to get log information
        param:id only find 1 log entry
        param:level level between 1 & 9; all levels underneath are found e.g. level 9 means all levels
        param:category match on multiple categories; are comma separated
        param:text match on text in body
        param:from_ -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find logs from date specified  (-4d means 4 days ago) default=-1h
        param:to -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find logs to date specified
        param:jid find logs for specified jobid
        param:nid find logs for specified node
        param:gid find logs for specified grid
        param:pid find logs for specified process (on grid level)
        param:tags comma separted list of tags/labels
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getLogs")

    def getMachines(self, id, guid, otherid, gid, nid, name, description, state, roles, ipaddr, macaddr, active, cpucore, mem, type, lastcheckFrom, lastcheckTo, **kwargs):
        """
        list found machines (comes from ros)
        param:id find based on id
        param:guid find based on guid
        param:otherid find based on 2nd id
        param:gid find nodes for specified grid
        param:nid find nodes for specified node
        param:name match on text in name
        param:description match on text in name
        param:state STARTED,STOPPED,RUNNING,FROZEN,CONFIGURED,DELETED
        param:roles match on comma separated list of roles (subsets also ok e.g. kvm.  would match all roles starting with kvm.)
        param:ipaddr comma separated list of ip addr to match against
        param:macaddr comma separated list of mac addr to match against
        param:active True,is the machine still active
        param:cpucore find based on nr cpucore
        param:mem find based on mem in MB
        param:type KVM or LXC
        param:lastcheckFrom -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find machines with lastcheckFrom  (-4d means 4 days ago)
        param:lastcheckTo -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find machines with lastcheckTo  (-4d means 4 days ago)
        result list(list)
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getMachines")

    def getNodeSystemStats(self, nid, **kwargs):
        """
        ask the right processmanager on right node to get the information about node system
        param:nid id of node
        result json
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getNodeSystemStats")

    def getNodes(self, id, guid, gid, name, roles, ipaddr, macaddr, active, peer_stats, peer_log, peer_backup, lastcheckFrom, lastcheckTo, **kwargs):
        """
        list found nodes (comes from ros)
        param:id find specific id
        param:guid find based on guid
        param:gid find nodes for specified grid
        param:name match on text in name
        param:roles match on comma separated list of roles (subsets also ok e.g. kvm.  would match all roles starting with kvm.)
        param:ipaddr comma separated list of ip addr to match against
        param:macaddr comma separated list of mac addr to match against
        param:active True,is the node still active
        param:peer_stats id of node which has stats for this node
        param:peer_log id of node which has logs (e.g. transactionlogs) for this node
        param:peer_backup id of node which has backups for this node
        param:lastcheckFrom -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find nodes with lastcheckFrom  (-4d means 4 days ago)
        param:lastcheckTo -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find nodes with lastcheckTo  (-4d means 4 days ago)
        result list(list)
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getNodes")

    def getProcessStats(self, nid, domain, name, **kwargs):
        """
        ask the right processmanager on right node to get the information
        param:nid id of node
        param:domain optional domain name for process
        param:name optional name for process
        result json
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getProcessStats")

    def getProcesses(self, id, guid, name, nid, gid, from_, to, active, jpdomain, jpname, instance, systempid, lastcheckFrom, lastcheckTo, **kwargs):
        """
        list processes (comes from ros), are the grid unique processes (not integrated with processmanager yet)
        param:id only find 1 process entry
        param:guid find based on guid
        param:name match on text in name
        param:nid find logs for specified node
        param:gid find logs for specified grid
        param:from_ -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find processes from date specified  (-4d means 4 days ago)
        param:to -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find processes to date specified
        param:active True,is the process still active
        param:jpdomain JPackage domain of process
        param:jpname JPackage name of process
        param:instance instance of process
        param:systempid pid on the system of process
        param:lastcheckFrom -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find processes with lastcheckFrom  (-4d means 4 days ago)
        param:lastcheckTo -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find processes with lastcheckTo  (-4d means 4 days ago)
        result list(list)
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getProcesses")

    def getProcessesActive(self, nid, name, domain, **kwargs):
        """
        ask the right processmanager on right node to get the info (this comes not from ros)
        output all relevant info (no stat info for that we have getProcessStats)
        param:nid id of node (if not specified goes to all nodes and aggregates)
        param:name optional name for process name (part of process name)
        param:domain optional name for process domain (part of process domain)
        result json
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getProcessesActive")

    def getStatImage(self, statKey, width, height, **kwargs):
        """
        get png image as binary format
        comes from right processmanager
        param:statKey e.g. n1.disk.mbytes.read.sda1.last
        param:width 500,
        param:height 200,
        result binary
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getStatImage")

    def getVDisks(self, id, machineid, guid, gid, nid, disk_id, fs, sizeFrom, sizeTo, freeFrom, freeTo, sizeondiskFrom, sizeondiskTo, mounted, path, description, mountpoint, role, type, order, devicename, backup, backuplocation, backuptime, backupexpiration, active, lastcheckFrom, lastcheckTo, **kwargs):
        """
        list found vdisks (virtual disks like qcow2 or sections on fs as used by a container or virtual machine) (comes from ros)
        param:id find based on id
        param:machineid to which machine is the vdisk attached
        param:guid find based on guid
        param:gid find vdisks for specified grid
        param:nid find vdisks for specified node
        param:disk_id find disk which hosts this disk
        param:fs ext4;xfs;...
        param:sizeFrom in MB
        param:sizeTo in MB
        param:freeFrom in MB
        param:freeTo in MB
        param:sizeondiskFrom in MB
        param:sizeondiskTo in MB
        param:mounted is disk mounted
        param:path match on part of path e.g. /dev/sda
        param:description match on part of description
        param:mountpoint match on part of mountpoint
        param:role type e.g. BOOT DATA CACHE
        param:type type e.g. QCOW2 FS
        param:order when more vdisks linked to a vmachine order of linkage
        param:devicename if known device name in vmachine
        param:backup is this a backup image
        param:backuplocation where is backup stored (tag based notation)
        param:backuptime epoch when was backup taken
        param:backupexpiration when does backup needs to expire
        param:active True,is the disk still active
        param:lastcheckFrom -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find vdisks with lastcheckFrom  (-4d means 4 days ago)
        param:lastcheckTo -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find vdisks with lastcheckTo  (-4d means 4 days ago)
        result list(list)
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getVDisks")
