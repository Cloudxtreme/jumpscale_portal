from JumpScale import j
import os

class system_cpunode(j.code.classGetBase()):
    """
    API Actor api for managing cpu node creation and bootstraping
    """
    def __init__(self):
        self._te = {}
        self.actorname = "cpunode"
        self.appname = "system"

    def init(self, **kwargs):
        """
        return the init script for creating a new node
        result str
        """
        ctx = kwargs["ctx"]
        host = ctx.env['HTTP_HOST']
        authkey = ctx.params['authkey']

        script = """#!/bin/bash
apt-get install autossh -y
PRIVPATH="$HOME/.ssh/id_dsa"
PUBPATH="$PRIVPATH.pub"
if [ ! -e "$PUBPATH" ]
then
    ssh-keygen -t dsa -f "$PRIVPATH" -P ''
fi
PUBKEY=`cat $PUBPATH`

curl -L -X POST -F "pubkey=$PUBKEY" -F "login=$USER" -F "hostname=$HOSTNAME" https://%s/restmachine/system/cpunode/create?authkey=%s | bash""" % (host, authkey)
        headers = [('Content-Type', 'text/plain'), ]
        ctx.start_response("200", headers)
        return script

    def create(self, login, pubkey, hostname, **kwargs):
        """
        Create a new cpu node
        param:login login to connect to the node
        param:passwd password of the login given in argument
        param:pubkey public ssh key of the cpunode
        result str
        """
        sshkey = None
        loc = None
        ctx = kwargs["ctx"]
        headers = [('Content-Type', 'text/plain'), ]

        try:
            loc = j.atyourservice.get(name='location', instance='openvc_nodes')
        except RuntimeError as e:
            if e.message.find('cannot find service') == -1:
                ctx.start_response("500", headers)
                return "echo %s" % e.message

        if loc is None:
            loc = j.atyourservice.new(name='location', instance='openvc_nodes')
            loc.install()

        try:
            sshkey = j.atyourservice.get(name='sshkey', instance='openvc_nodes', parent=loc)
        except RuntimeError as e:
            if e.message.find('cannot find service') == -1:
                ctx.start_response("500", headers)
                return "echo %s" % e.message

        if sshkey is None:
            data = {'instance.key.priv': ''}  # emtpy trigger autogeneration
            sshkey = j.atyourservice.new(name='sshkey', instance='openvc_nodes', args=data, parent=loc)
            sshkey.install(deps=True)

        # remove service if already exists
        nodes = j.atyourservice.findServices(name='node.ssh', instance=hostname, parent=loc)
        for n in nodes:
            j.atyourservice.remove(n.domain, n.name, n.instance, n.parent)

        try:
            masterPort = self._findFreePort()
        except RuntimeError as e:
            ctx.start_response("500", headers)
            return "echo %s" % e.message

        # creation of the node.ssh service to connect to the node
        nodePort = 22
        masterLogin = os.environ['USER']
        host = ctx.env['HTTP_HOST']
        masterAddr = host.split(':')[0]
        data = {
            "instance.ip": "127.0.0.1",  # localhost cause we reverse ssh tunnel
            "instance.ssh.port": masterPort,
            'instance.sshkey': sshkey.instance,
            'instance.login': login,
            'instance.password': "",
            'instance.jumpscale': True,
            'instance.ssh.shell': '/bin/bash -l -c'
        }
        node = j.atyourservice.new(name='node.ssh', instance=hostname, args=data, parent=loc)
        node.hrd # force creation of service.hrd and action.py

        # todo handle exeption here
        # todo make sure the key is valid
        authorized_keys_path = j.system.fs.joinPaths(os.environ['HOME'], '.ssh/authorized_keys')
        j.system.fs.writeFile(authorized_keys_path, pubkey+"\n", append=True)

        # start jscript that will install the node
        self._scheduleInstall(node, masterAddr)

        script = """#!/bin/bash
echo '{key}' >> ~/.ssh/authorized_keys
tmux kill-session -t jumpscale
tmux new-session -d -s jumpscale -n autossh_{hostname} 'autossh -o StrictHostKeyChecking=no -NR {masterPort}:localhost:{nodePort} {masterLogin}@{masterAddr}'
""".format(
    key=sshkey.hrd.getStr('instance.key.pub'),
    masterPort=masterPort,
    nodePort=nodePort,
    masterLogin=masterLogin,
    masterAddr=masterAddr,
    hostname=hostname)

        ctx.start_response("201", headers)
        return script

    def _findFreePort(self):
        port_range = [i for i in xrange(2000, 2500)]
        nodes = j.atyourservice.findServices(name='node.ssh')
        taken_port = [n.hrd.get('instance.ssh.port') for n in nodes]
        free_port = [p for p in port_range if p not in taken_port]
        for p in sorted(free_port):
            if not j.system.net.checkListenPort(p):
                return p
        raise RuntimeError('no available port to connect to')

    def _scheduleInstall(self, node, masterAddr):
        args = {
            'node': str(node),
            'parent': str(node.parent),
            'masterAddr': str(masterAddr)
        }
        clients = j.atyourservice.findServices(name='agentcontroller_client')
        if len(clients) <= 0:
            raise RuntimeError('no agentcontroller client installed')
        cl = j.clients.agentcontroller.getByInstance(clients[0].instance)

        gid, nid, _ = j.application.whoAmI
        cl.executeJumpscript("jumpscale", "cpunode_install", nid=nid, args=args, all=False, timeout=300, wait=False, gid=gid, errorreport=True, transporttimeout=5)
