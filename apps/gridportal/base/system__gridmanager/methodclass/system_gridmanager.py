from JumpScale import j
import JumpScale.grid.geventws
import JumpScale.grid.agentcontroller
import JumpScale.baselib.serializers

def mbToKB(value):
    if not value:
        return value
    return value * 1024

def getInt(val):
    if val is not None:
        return int(val)
    return val

class system_gridmanager(j.code.classGetBase()):
    """
    gateway to grid
    """
    def __init__(self):
        self._te={}
        self.actorname="gridmanager"
        self.appname="system"
        self.clients={}
        self._nodeMap = dict()
        self.clientsIp = dict()

        ros = j.clients.ros.get()
        self.ros_node = ros.system.node
        self.ros_job = ros.system.job
        self.ros_eco = ros.system.eco
        self.ros_process = ros.system.process
        self.ros_application = ros.system.applicationtype
        self.ros_grid = ros.system.grid
        self.ros_machine = ros.system.machine
        self.ros_disk = ros.system.disk
        self.ros_vdisk = ros.system.vdisk
        self.ros_alert = ros.system.alert
        self.ros_log = ros.system.log
        self.ros_nic = ros.system.nic
        self.ros_jumpscript = ros.system.jumpscript

    def getClient(self,nid,category):
        nid = int(nid)
        if nid not in self.clients:
            if nid not in self._nodeMap:
                self.getNodes()
            if nid not in self._nodeMap:
                raise RuntimeError('Could not get client for node %s!' % nid)
            for ip in self._nodeMap[nid]['ipaddr']:
                if j.system.net.tcpPortConnectionTest(ip, 4446):
                    user="root"#j.application.config.get('system.superadmin.login')
                    self.clients[nid] = j.servers.geventws.getClient(ip, 4446, org="myorg", user=user, passwd='fake',category=category)
                    self.clientsIp[nid] = ip
                    return self.clients[nid]
            raise RuntimeError('Could not get client for node %s!' % nid)

        return self.clients[nid]

    def getNodeSystemStats(self, nid, **kwargs):
        """
        ask the right processmanager on right node to get the information about node system
        param:nid id of node
        result json
        """
        nid = int(nid)
        client = self.getClient(nid, 'stats') 

        try:
            stats = client.listStatKeys('n%s.system.' % nid)
        except Exception,e:
            # from IPython import embed
            # print "DEBUG NOW getNodeSystemStats"
            # embed()
            pass
            

        cpupercent = [ stats['n%s.system.cpu.percent' % nid][-1] ]
        mempercent = [ stats['n%s.system.memory.percent' % nid][-1] ]
        netstat = [ stats['n%s.system.network.kbytes.recv' % nid][-1], stats['n%s.system.network.kbytes.send' % nid][-1] ]

        result = {'cpupercent': [cpupercent, {'series': [{'label': 'CPU PERCENTAGE'}]}], 
                  'mempercent': [mempercent, {'series': [{'label': 'MEMORY PERCENTAGE'}]}], 
                  'netstat': [netstat, {'series': [{'label': 'KBytes Recieved'}, {'label': 'KBytes Sent'}]}]}
        return result

    def _getNode(self, nid):
        node=self.ros_node.get(getInt(nid))
        r = dict()
        r["id"]=node.id
        r["roles"]=node.roles
        r["name"]=node.name
        r["ipaddr"]=node.ipaddr
        self._nodeMap[node.id] = r
        return r

    def getNodes(self, guid=None, gid=None, name=None, roles=None, ipaddr=None, macaddr=None, id=None, \
            active=None, peer_stats=None, peer_log=None, peer_backup=None, lastcheckFrom=None, lastcheckTo=None, **kwargs):
        """
        param:id int,,find specific id
        param:guid str,,find based on guid
        param:gid int,,find nodes for specified grid
        param:name str,,match on text in name
        param:roles str,,match on comma separated list of roles (subsets also ok e.g. kvm.  would match all roles starting with kvm.)
        param:ipaddr str,,comma separated list of ip addr to match against
        param:macaddr str,,comma separated list of mac addr to match against
        param:active bool,,True,is the node still active
        param:peer_stats int,,id of node which has stats for this node
        param:peer_log int,,id of node which has logs (e.g. transactionlogs) for this node
        param:peer_backup int,,id of node which has backups for this node
        param:lastcheckFrom str,-1h,-4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find nodes with lastcheckFrom  (-4d means 4 days ago)
        param:lastcheckTo str,-1h,-4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find nodes with lastcheckTo  (-4d means 4 days ago)
        result:list(list)
        """
        lastcheckFrom = self._getEpoch(lastcheckFrom)
        lastcheckTo = self._getEpoch(lastcheckTo)
        params = {'gid': getInt(gid),
                  'name': name,
                  'guid': guid,
                  'active': active,
                  'lastcheckFrom': {'name': 'lastcheck', 'value': lastcheckFrom, 'eq': 'gte'},
                  'lastcheckTo': {'name': 'lastcheck', 'value': lastcheckTo, 'eq': 'lte'},
                  'peer_stats': peer_stats,
                  'peer_log': peer_log,
                  'peer_backup': peer_backup,
                  'id': getInt(id),
                  }
        results = self.ros_node.search(params)
        def myfilter(node):
            self._nodeMap[node['id']] = node
            if roles and not set(roles).issubset(set(node['roles'])):
                return False
            if ipaddr and ipaddr not in node['ipaddr']:
                return False
            if macaddr and macaddr not in node['netaddr']:
                return False
            return True

        return filter(myfilter, results)

    def getProcessStats(self, nid, domain="", name="", **kwargs):
        """
        ask the right processmanager on right node to get the information
        param:nid id of node
        param:domain optional domain name for process
        param:name optional name for process
        result json
        """
        if domain=="*":
            domain=""
        if name=="*":
            name=""
        client=self.getClient(nid)
        return client.monitorProcess(domain=domain,name=name)

    def _showUnavailable(self, width, height, message="STATS UNAVAILABLE"):
        import PIL.Image as Image
        import PIL.ImageDraw as ImageDraw
        import StringIO

        size = (int(width), int(height))
        im = Image.new('RGB', size, 'white') 
        draw = ImageDraw.Draw(im)   
        red = (255,0,0)
        text_pos = (size[0]/2,size[1]/2)
        text = message
        draw.text(text_pos, text, fill=red)
        
        del draw 
        output = StringIO.StringIO()
        im.save(output, 'PNG')
        del im
        response = output.getvalue()
        output.close()
        return response

    def getStatImage(self, statKey, title=None, aliases={}, width=500, height=250, **kwargs):
        """
        @param statkey e.g. n1.disk.mbytes.read.sda1.last
        """
        import urllib
        query = list()
        ctx = kwargs['ctx']
        ctx.start_response('200', (('content-type', 'image/png'),))
        statKey=statKey.strip()

        for target in statKey.split(','):

            if target in aliases:
                target = "alias(%s, '%s')" % (target, aliases[target])
            query.append(('target', target))
        if title:
            query.append(('title', title))

        query.append(('height', height))
        query.append(('width', width))
        query.append(('lineWidth', '2'))
        query.append(('graphOnly', 'false'))
        query.append(('hidexAxes', 'false'))
        query.append(('hidexGrid', 'false'))
        query.append(('areaMode', 'none'))
        query.append(('tz', 'CET'))

        params = kwargs.copy()
        params.pop('ctx')
        for key, value in params.iteritems():
            query.append((key, value))

        querystr = urllib.urlencode(query)
        url="http://127.0.0.1:8081/render?%s"%(querystr)
        r = requests.get(url)
        try:
            result = r.send()
        except Exception:        
            return self._showUnavailable(width, height, "GRAPHITE UNAVAILABLE")
        return result.content

    def getProcessesActive(self, nid, name, domain, **kwargs):
        """
        ask the right processmanager on right node to get the info (this comes not from ros)
        output all relevant info (no stat info for that we have getProcessStats)
        param:nid id of node (if not specified goes to all nodes and aggregates)
        param:name optional name for process name (part of process name)
        param:domain optional name for process domain (part of process domain)
        result json
        """
        client = self.getClient(nid)
        return client.getProcessesActive(domain, name)

    def getJob(self, id, includeloginfo, includechildren, guid=None, **kwargs):
        """
        gets relevant info of job (also logs)
        can be used toreal time return job info
        param:id obliged id of job
        param:includeloginfo if true fetch all logs of job & return as well
        param:includechildren if true look for jobs which are children & return that info as well
        """
        # TODO include loginfo
        job = None
        if guid and not id:
            jobs = self.ros_job.search({'guid':guid})
            if jobs:
                id = jobs[0]['id']
        job = self.ros_job.get(id)
        return {'result': job}

    def getLogs(self, id=None, level=None, category=None, text=None, from_=None, to=None, jid=None, nid=None, gid=None, pid=None, tags=None, guid=None, **kwargs):
        """
        interface to get log information
        param:id only find 1 log entry
        param:level level between 1 & 9; all levels underneath are found e.g. level 9 means all levels
        param:category match on multiple categories; are comma separated
        param:text match on text in body
        param:from_ -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find logs from date specified  (-4d means 4 days ago)
        param:to -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find logs to date specified
        param:jid find logs for specified jobid
        param:nid find logs for specified node
        param:gid find logs for specified grid
        param:pid find logs for specified process (on grid level)
        param:tags comma separted list of tags/labels
        """
        from_ = self._getEpoch(from_)
        to = self._getEpoch(to)
        params = {'id': getInt(id),
                  'guid': guid,
                  'level': {'name': 'level', 'value': level, 'eq': 'lte'},
                  'category': category,
                  'text': text,
                  'from_': {'name': 'epoch', 'value': from_, 'eq': 'gte'},
                  'to': {'name': 'epoch', 'value': to, 'eq': 'lte'},
                  'jid': jid,
                  'nid': getInt(nid),
                  'gid': getInt(gid),
                  'pid': pid,
                  'tags': tags,
                  }
        return self.ros_log.search(params)

    def getJobs(self, id=None, guid=None, from_=None, to=None, nid=None, gid=None, parent=None, roles=None, state=None, organization=None, name=None, description=None, category=None, source=None, **kwargs):
        """
        interface to get job information
        param:id only find 1 job entry
        param:from_ -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find jobs from date specified  (-4d means 4 days ago)
        param:to -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find jobs to date specified
        param:nid find jobs for specified node
        param:gid find jobs for specified grid
        param:parent find jobs which are children of specified parent
        param:roles match on comma separated list of roles (subsets also ok e.g. kvm.  would match all roles starting with kvm.)
        param:state OK;ERROR;...
        param:jsorganization
        param:jsname
        param:description any description when asked for the job
        param:category category in dot notation
        param:source who asked for the job is free text
        """
        from_ = self._getEpoch(from_)
        to = self._getEpoch(to)
        params = {'ffrom': {'name': 'timeStart', 'value': from_, 'eq': 'gte'},
                  'to': {'name': 'timeStart', 'value': to, 'eq': 'lte'},
                  'nid': getInt(nid),
                  'gid': getInt(gid),
                  'id': id,
                  'guid': guid,
                  'description': description,
                  'category': category,
                  'source': source,
                  'parent': parent,
                  'state': state,
                  'category': organization,
                  'cmd': name}
        return self.ros_job.search(params)

    def getErrorconditions(self, id=None, level=None, descr=None, descrpub=None, from_=None, to=None, nid=None, gid=None, category=None, tags=None, type=None, jid=None, jidparent=None, jsorganization=None, jsname=None, **kwargs):
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
        param:type
        param:jid find ecos for specified job
        param:jidparent find ecos which are children of specified parent job
        param:jsorganization find ecos coming from scripts from this org
        param:jsname find ecos coming from scripts with this name
        """
        from_ = self._getEpoch(from_)
        to = self._getEpoch(to)
        params = {'ffrom': {'name': 'epoch', 'value': from_, 'eq': 'gte'},
                  'to': {'name':'epoch','value': to, 'eq': 'lte'},
                  'nid': getInt(nid),
                  'level': getInt(level),
                  'descr': descr,
                  'descrpub': descrpub,
                  'category': category,
                  'tags': tags,
                  'type': type,
                  'gid': getInt(gid),
                  'jid': jid,
                  'jidparent': jidparent,
                  'id': id,
                  'jsorganization': jsorganization,
                  'jsname': jsname}
        return self.ros_eco.search(params)


    def getProcesses(self, id=None, guid=None, name=None, nid=None, gid=None, from_=None, to=None, active=None, jpdomain=None, jpname=None, instance=None, systempid=None, lastcheckFrom=None, lastcheckTo=None, **kwargs):
        """
        list processes (comes from ros), are the grid unique processes (not integrated with processmanager yet)
        param:id only find 1 process entry
        param:name match on text in name
        param:nid find logs for specified node
        param:gid find logs for specified grid
        param:aid find logs for specified application type
        param:from_ -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find processes from date specified  (-4d means 4 days ago)
        param:to -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find processes to date specified
        param:jpdomain str.. JPackage domain of process
        param:jpname str.. JPackage name of process
        param:instance str.. instance of process
        param:systempid int.. pid on the system of process
        param:lastcheckFrom str,-1h,-4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find processes with lastcheckFrom  (-4d means 4 days ago)
        param:lastcheckTo str,-1h,-4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find processes with lastcheckTo  (-4d means 4 days ago)
        result list(list)
        """
        from_ = self._getEpoch(from_)
        to = self._getEpoch(to)
        lastcheckFrom = self._getEpoch(lastcheckFrom)
        lastcheckTo = self._getEpoch(lastcheckTo)
        params = {'ffrom': {'name': 'epochstart', 'value': from_, 'eq': 'gte'},
                  'to': {'name': 'epochstart', 'value': to, 'eq': 'lte'},
                  'lastcheckFrom': {'name': 'lastcheck', 'value': lastcheckFrom, 'eq': 'gte'},
                  'lastcheckTo': {'name': 'lastcheck', 'value': lastcheckTo, 'eq': 'lte'},
                  'nid': getInt(nid),
                  'gid': getInt(gid),
                  'active': active,
                  'id': id,
                  'systempid': systempid,
                  'jpdomain': jpdomain,
                  'jpname': jpname,
                  'instance': instance,
                  'guid': guid,
                  }

        return self.ros_process.search(params)

    def getGrids(self, **kwargs):
        """
        list grids
        result list(list)
        """
        return self.ros_grid.search({})

    def getJumpscript(self, organization, name, **kwargs):
        """
        calls internally the agentcontroller to fetch detail for 1 jumpscript
        param:jsorganization
        param:jsname
        """
        return self.ros_jumpscript.search({'organization': organization, 'name': name})[1]

    def getJumpscripts(self, organization=None, **kwargs):
        """
        calls internally the agentcontroller
        return: lists the jumpscripts with main fields (organization, name, category, descr)
        param:jsorganization find jumpscripts
        """
        res={}
        for js in self.ros_jumpscript.search({'organization': organization}):
            key="%s:%s"%(js["organization"],js["name"])
            if not res.has_key(key):
                res[key]=js
            if int(js["id"])>int(res[key]["id"]):
                res[key]=js

        res2=[]
        for key,val in res.iteritems():
            res2.append(val)

        return res2

    def getAgentControllerActiveJobs(self, **kwargs):
        """
        calls internally the agentcontroller
        list jobs now running on agentcontroller
        """
        return j.clients.agentcontroller.getActiveJobs()

    def getAgentControllerSessions(self, roles, nid, active, **kwargs):
        """
        calls internally the agentcontroller
        param:roles match on comma separated list of roles (subsets also ok e.g. kvm.  would match all roles starting with kvm.)
        param:nid find for specified node (on which agents are running which have sessions with the agentcontroller)
        param:active is session active or not
        """
        sessions = j.clients.agentcontroller.listSessions()
        def myfilter(session):
            if roles and not set(roles).issubset(set(session['roles'])):
                return False
            if active and not session['activejob']:
                return False
            # TODO nid?
            return True

        return filter(myfilter, sessions)

    def _getEpoch(self, time):
        if not time:
            return time
        if isinstance(time, int):
            return time
        if time.startswith('-'):
            return j.base.time.getEpochAgo(time)
        return j.base.time.getEpochFuture(time)

    def getAlerts(self, id=None, level=None, descr=None, descrpub=None, nid=None, gid=None, category=None, tags=None, state=None, from_inittime=None, to_inittime=None, from_lasttime=None, to_lasttime=None, from_closetime=None, to_closetime=None, nrerrorconditions=None, errorcondition=None, **kwargs):
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
        from_inittime = self._getEpoch(from_inittime)
        to_inittime = self._getEpoch(to_inittime)
        from_lasttime = self._getEpoch(from_lasttime)
        to_lasttime = self._getEpoch(to_lasttime)
        from_closetime = self._getEpoch(from_closetime)
        to_closetime = self._getEpoch(to_closetime)
        params = {'id': id,
                  'level': {'name': 'level', 'eq': 'lte', 'value': level},
                  'from_inittime': {'name': 'inittime', 'eq': 'lte', 'value': from_inittime},
                  'to_inittime': {'name': 'inittime', 'eq': 'gte', 'value': to_inittime},
                  'from_lasttime': {'name': 'lasttime', 'eq': 'lte', 'value': from_lasttime},
                  'to_lasttime': {'name': 'lasttime', 'eq': 'gte', 'value': to_lasttime},
                  'from_closetime': {'name': 'closetime', 'eq': 'lte', 'value': from_closetime},
                  'to_closetime': {'name': 'closetime', 'eq': 'gte', 'value': to_closetime},
                  'descrpub': descrpub,
                  'nid': getInt(nid),
                  'gid': getInt(gid),
                  'category': category,
                  'tags': tags,
                  'state': state,
                  'nrerrorconditions': nrerrorconditions,
                  'errorcondition': errorcondition,
                 }
        return self.ros_alert.search(params)

    def getVDisks(self, id=None, machineid=None, guid=None, gid=None, nid=None, disk_id=None, fs=None, sizeFrom=None, sizeTo=None, freeFrom=None, freeTo=None, sizeondiskFrom=None, sizeondiskTo=None, mounted=None, path=None, description=None, mountpoint=None, role=None, type=None, order=None, devicename=None, backup=None, backuplocation=None, backuptime=None, backupexpiration=None, active=None, lastcheckFrom=None, lastcheckTo=None, **kwargs):
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
        param:lastcheckFrom str,-1h,-4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find vdisks with lastcheckFrom  (-4d means 4 days ago)
        param:lastcheckTo str,-1h,-4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find vdisks with lastcheckTo  (-4d means 4 days ago)
        result list(list)
        """
        lastcheckFrom = self._getEpoch(lastcheckFrom)
        lastcheckTo = self._getEpoch(lastcheckTo)
        params = {'id': id,
                  'machineid': machineid,
                  'guid': guid,
                  'gid': getInt(gid),
                  'nid': getInt(nid),
                  'disk_id': disk_id,
                  'fs': fs,
                  'sizeFrom': {'name': 'size', 'eq': 'lte', 'value': mbToKB(sizeFrom)},
                  'sizeTo': {'name': 'size', 'eq': 'gte', 'value': mbToKB(sizeTo)},
                  'freeFrom': {'name': 'free', 'eq': 'lte', 'value': mbToKB(freeFrom)},
                  'freeTo': {'name': 'free', 'eq': 'gte', 'value': mbToKB(freeTo)},
                  'sizeondiskFrom': {'name': 'sizeondisk', 'eq': 'lte', 'value': mbToKB(sizeondiskFrom)},
                  'sizeondiskTo': {'name': 'sizeondisk', 'eq': 'gte', 'value': mbToKB(sizeondiskTo)},
                  'lastcheckFrom': {'name': 'lastcheck', 'value': lastcheckFrom, 'eq': 'gte'},
                  'lastcheckTo': {'name': 'lastcheck', 'value': lastcheckTo, 'eq': 'lte'},
                  'mounted': mounted,
                  'path': path,
                  'description': description,
                  'mountpoint': mountpoint,
                  'role': role,
                  'type': type,
                  'order': order,
                  'devicename': devicename,
                  'backup': backup,
                  'backuplocation': backuplocation,
                  'backupexpiration': backupexpiration,
                  'backuptime': backuptime,
                  'active': active,
                 }
        return self.ros_vdisk.search(params)

    def getMachines(self, id=None, guid=None, otherid=None, gid=None, nid=None, name=None, description=None, state=None, roles=None, ipaddr=None, macaddr=None, active=None, cpucore=None, mem=None, type=None, lastcheckFrom=None, lastcheckTo=None, **kwargs):
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
        param:lastcheckFrom str,-1h,-4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find machines with lastcheckFrom  (-4d means 4 days ago)
        param:lastcheckTo str,-1h,-4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find machines with lastcheckTo  (-4d means 4 days ago)
        result list(list)
        """
        lastcheckFrom = self._getEpoch(lastcheckFrom)
        lastcheckTo = self._getEpoch(lastcheckTo)
        params = {'id': id,
                  'guid': guid,
                  'otherid': otherid,
                  'gid': getInt(gid),
                  'nid': getInt(nid),
                  'lastcheckFrom': {'name': 'lastcheck', 'value': lastcheckFrom, 'eq': 'gte'},
                  'lastcheckTo': {'name': 'lastcheck', 'value': lastcheckTo, 'eq': 'lte'},
                  'name': name,
                  'description': description,
                  'state': state,
                  'active': active,
                  'cpucore': cpucore,
                  'mem': mem,
                  'type': type,}

        def myfilter(machine):
            if roles and not set(roles).issubset(set(machine['roles'])):
                return False
            if ipaddr and ipaddr not in machine['ipaddr']:
                return False
            if macaddr and macaddr not in machine['netaddr']:
                return False
            return True

        results = self.ros_machine.search(params)
        return filter(myfilter, results)

    def getDisks(self, id=None, guid=None, gid=None, nid=None, fs=None, sizeFrom=None, sizeTo=None, freeFrom=None, \
                 freeTo=None, mounted=None, ssd=None, path=None, model=None, description=None, mountpoint=None, \
                 type=None, active=None, lastcheckFrom=None, lastcheckTo=None, **kwargs):
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
        param:lastcheckFrom str,-1h,-4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find disks with lastcheckFrom  (-4d means 4 days ago)
        param:lastcheckTo str,-1h,-4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find disks with lastcheckTo  (-4d means 4 days ago)
        result list(list)
        """
        lastcheckFrom = self._getEpoch(lastcheckFrom)
        lastcheckTo = self._getEpoch(lastcheckTo)
        params = {'id': id,
                  'guid': guid,
                  'gid': getInt(gid),
                  'nid': getInt(nid),
                  'fs': fs,
                  'sizeFrom': {'name': 'size', 'eq': 'lte', 'value': mbToKB(sizeFrom)},
                  'sizeTo': {'name': 'size', 'eq': 'gte', 'value': mbToKB(sizeTo)},
                  'freeFrom': {'name': 'free', 'eq': 'lte', 'value': mbToKB(freeFrom)},
                  'freeTo': {'name': 'free', 'eq': 'gte', 'value': mbToKB(freeTo)},
                  'lastcheckFrom': {'name': 'lastcheck', 'value': lastcheckFrom, 'eq': 'gte'},
                  'lastcheckTo': {'name': 'lastcheck', 'value': lastcheckTo, 'eq': 'lte'},
                  'mounted': mounted,
                  'ssd': ssd,
                  'path': path,
                  'model': model,
                  'description': description,
                  'mountpoint': mountpoint,
                  'type': type,
                  'active': active,
                 }
        return self.ros_disk.search(params)


    def getNics(self, id=None, guid=None, gid=None, nid=None, active=None, ipaddr=None, lastcheck=None, mac=None, name=None, **kwargs):
        """
        list found disks (are really partitions) (comes from ros)
        param:id find based on id
        param:guid find based on guid
        param:gid find disks for specified grid
        param:nid find disks for specified node
        param:active
        param:ipaddr
        param:lastcheck
        param:mac
        param:name
        result list(list)
        """
        params = {'id': id,
                  'guid': guid,
                  'gid': getInt(gid),
                  'nid': getInt(nid),
                  'lastcheck': lastcheck,
                  'mac': mac,
                  'name': name,
                  'ipaddr': ipaddr,
                  'active': active
                 }
        return self.ros_nic.search(params)


