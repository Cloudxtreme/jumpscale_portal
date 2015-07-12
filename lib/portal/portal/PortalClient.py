
#from ActorLoaderRemote import ActorLoaderRemote
#from Portal6Process import Portal6Process

from .PortalClientWS import PortalClientWS

from JumpScale import j


class PortalProcess():
    pass


class ModelsClass():
    pass


class GroupAppsClass(object):
    def __init__(self, client):
        self._client = client

    def __getattr__(self, appname):
        app = AppClass(self._client, appname)
        setattr(self, appname, app)
        return app

class AppClass(object):
    def __init__(self, client, appname, actors=None):
        self._appname = appname
        self._client = client
        if actors:
            for actor in actors:
                setattr(self, actor, None)


    def __getattribute__(self, actorname):
        if actorname in ('__class__', '__members__', '__methods__', '__dict__', 'trait_names', '_getAttributeNames'):
            return object.__getattribute__(self, actorname)
        attr = self.__dict__.get(actorname)
        if attr:
            return attr

        actor = self._client.getActor(self._appname, actorname)
        setattr(self, actorname, actor)
        return actor

class PortalClient():

    """
    client to appserver 6 running out of process
    """

    def __init__(self, ip, port, secret):
        """
        connect to Portal6
        """
        
        self.wsclient = PortalClientWS(ip, port, secret=secret)
        self.ip = ip
        self.port = port
        self._actormap = dict()


        if not hasattr(j, 'apps'):
            j.apps = GroupAppsClass(self)
        if isinstance(j.apps, GroupAppsClass):
            self.actors = j.apps
        else:
            self.actors = GroupAppsClass(self)

    # def _loadSpaces(self):
    #     spaces = dict()
    #     for actor in j.apps.system.contentmanager.getActors():
    #         space, actor = actor.split('__')
    #         spaceactors = spaces.setdefault(space, list())
    #         spaceactors.append(actor)
    #     for space, actors in spaces.iteritems():
    #         setattr(j.apps, space, AppClass(self, space, actors))


    def getActor(self, appname, actorname, instance=0, redis=False, refresh=False):
        if appname.lower() == "system" and actorname == "manage":
            raise RuntimeError("Cannot open actor connection to system actor, use directly the wsclient with callwebservice method.")

        key = "%s_%s" % (appname.lower(), actorname.lower())
        if refresh == False and key in self._actormap:
            return self._actormap[key]

        result = self.wsclient.callWebService("system", "contentmanager", "prepareActorSpecs", app=appname, actor=actorname)
        if result[1] != None and "error" in result[1]:
            error = result[1]["error"]
            raise RuntimeError(error)

        # there is now a tgz specfile ready
        # now we should download
        scheme = "http" if self.port != 443 else "https"
        url = "%s://%s:%s/files/specs/%s_%s.tgz" % (scheme, self.ip, self.port, appname, actorname)  # @todo use gridmap
        downloadpathdir = j.system.fs.joinPaths(j.dirs.varDir, "downloadedactorspecs")
        j.system.fs.createDir(downloadpathdir)
        downloadpath = j.system.fs.joinPaths(downloadpathdir, "%s_%s.tgz" % (appname, actorname))
        http = j.clients.http.getConnection()
        http.download(url, downloadpath)
        destinationdir = j.system.fs.joinPaths(downloadpathdir, appname, actorname)
        j.system.fs.removeDirTree(destinationdir)
        j.system.fs.targzUncompress(downloadpath, destinationdir, removeDestinationdir=True)

        codepath = j.system.fs.joinPaths(j.dirs.varDir, "code4appclient", appname, actorname)
        j.core.specparser.parseSpecs(destinationdir, appname=appname, actorname=actorname)

        classs = j.core.codegenerator.getClassActorRemote(appname, actorname, instance=instance, redis=redis, wsclient=self.wsclient, codepath=codepath)
        actorobject = classs()
        self._actormap[key] = actorobject

        apphook = getattr(self.actors, appname, None)
        if not apphook:
            apphook = AppClass(self, appname)
            setattr(self.actors, appname, apphook)
        if not hasattr(apphook, actorname):
            setattr(apphook, actorname, actorobject)

        return actorobject
