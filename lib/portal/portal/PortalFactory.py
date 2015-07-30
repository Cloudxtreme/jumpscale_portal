#from ActorsLoaderRemote import ActorsLoaderRemote
from .PortalServer import PortalServer
from .PortalClient import PortalClient
from .PortalClient2 import Resource
import time
#from ActorLoaderLocal import *

import JumpScale.baselib.redis

from JumpScale import j


class Group():
    pass

class PortalFactoryClient(object):
    def __init__(self):
        self._portalClients = {}

    def getByInstance(self, instance=None):
        if not instance:
            instance = j.application.hrdinstance.get('portal.connection')
        hrd = j.application.getAppInstanceHRD(name="portal_client",instance=instance)
        addr = hrd.get('instance.param.addr')
        port = hrd.getInt('instance.param.port')
        secret = hrd.getStr('instance.param.secret')
        return self.get(addr, port, secret)

    def get(self, ip="localhost", port=9900, secret=None):
        """
        return client to manipulate & access a running application server (out of process)
        caching is done so can call this as many times as required
        secret is normally configured from grid
        there is normally no need to use this method, use self.getActorClient in stead
        """

        if ip == "localhost":
            ip = "127.0.0.1"
        key = "%s_%s_%s" % (ip, port,secret)
        if key in self._portalClients:
            return self._portalClients[key]
        else:
            cl = PortalClient(ip, port, secret)
            self._portalClients[key] = cl
            # cl._loadSpaces()
            return cl

    def get2(self, ip="localhost", port=82, secret=None):
        return Resource(ip, port, secret, "/restmachine")

class PortalFactory():

    def __init__(self):
        # self._inited = False
        self.active = None
        self.inprocess = False

    def getServer(self):
        return PortalServer()

    def getPortalConfig(self, appname):
        cfg = j.system.fs.joinPaths(j.dirs.baseDir, 'apps', appname, 'cfg', 'portal')
        return j.config.getConfig(cfg)

    def loadActorsInProcess(self, name='main'):
        """
        make sure all actors are loaded on j.apps...
        """
        class FakeServer(object):
            def __init__(self):
                import JumpScale.grid
                self.actors = dict()
                self.ros = j.clients.ros.get()
                self.epoch = time.time()
                self.actorsloader = j.core.portalloader.getActorsLoader()
                self.spacesloader = j.core.portalloader.getSpacesLoader()

            def addRoute(self, *args, **kwargs):
                pass

            def addSchedule1MinPeriod(self, *args, **kwargs):
                pass

            addSchedule15MinPeriod = addSchedule1MinPeriod

        self.inprocess = True
        # self._inited = False
        j.apps = Group()
        basedir = j.system.fs.joinPaths(j.dirs.baseDir, 'apps', 'portals', name)
        ini = j.tools.inifile.open("%s/cfg/portal.cfg" % basedir)
        appdir = ini.getValue("main", "appdir")
        appdir=appdir.replace("$base",j.dirs.baseDir)
        j.system.fs.changeDir(appdir)
        server = FakeServer()
        j.core.portal.active = server
        server.actorsloader.scan(appdir)
        server.actorsloader.scan(basedir + "/base")

        for actor in list(server.actorsloader.actors.keys()):
            appname,actorname=actor.split("__",1)
            try:
                server.actorsloader.getActor(appname, actorname)
            except Exception as e:
                print("*ERROR*: Could not load actor %s %s:\n%s" % (appname,actorname, e))

