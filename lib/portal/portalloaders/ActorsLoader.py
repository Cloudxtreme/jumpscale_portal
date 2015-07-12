from JumpScale import j
from .LoaderBase import LoaderBase, LoaderBaseObject

from JumpScale.core.extensions.PMExtensionsGroup import PMExtensionsGroup
from JumpScale.core.extensions.PMExtensions import PMExtensions
import JumpScale.baselib.tags


class ActorExtensionsGroup(PMExtensionsGroup):

    """
    ActorExtensionsGroup
    """

    def __init__(self, path):
        """
        ActorExtensionsGroup constructor
        """

        PMExtensionsGroup.__init__(self)

        self.pm_name = "a"
        self.pm_location = "a"

        extensionLoader = PMExtensions(self, 'a.')

        extensionLoader.load(path, True)

        self._activate()

    def _activate(self):
        """
        Activates all extensions in the extention group
        """
        for extensionName in list(self.pm_extensions.keys()):
            extension = self.pm_extensions[extensionName]
            extension.activate()

class Class():
    pass

class GroupAppsClass(object):
    def __init__(self, actorsloader):
        self.actorsloader = actorsloader

    def __getattr__(self, appname):
        app = AppClass(appname)
        setattr(self, appname, app)
        return app

class AppClass(object):
    def __init__(self, appname):
        self._appname = appname

    def __getattr__(self, actorname):
        if actorname in ('__members__', '__methods__', 'trait_names', '_getAttributeNames'):
            return object.__getattr__(self, actorname)
        actor = j.apps.actorsloader.getActor(self._appname, actorname)
        setattr(self, actorname, actor)
        return actor


class ActorsLoader(LoaderBase):
    """
    loader for all actors
    """

    def __init__(self):
        """
        """
        LoaderBase.__init__(self, "actor", ActorLoader)
        self.actorIdToActorLoader = self.id2object
        self.getActorLoaderFromId = self.getLoaderFromId
        self.roscl = None

    def reset(self):
        j.apps = GroupAppsClass(self)
        j.core.specparser.app_actornames = {}
        j.core.specparser.actornames = []
        j.core.specparser.appnames = []
        j.core.specparser.modelnames = {}
        j.core.specparser.roles = {}
        j.core.specparser.specs = {}
        j.core.codegenerator.classes = {}
        # j.core.portal.active._init()

    def getApps(self):
        result = {}
        for item in list(self.id2object.keys()):
            if item.find("__") != -1:
                app = item.split("__")[0]
                result[app] = 1
        return list(result.keys())

    def getAppActors(self):
        result = []
        for item in list(self.id2object.keys()):
            if item.find("__") != -1:
                app, actor = item.split("__", 2)
                result.append([app, actor])
        return result

    def getActor(self, appname, actorname):

        key = "%s__%s" % (appname.lower(), actorname.lower())

        if key in j.core.portal.active.actors:
            return j.core.portal.active.actors[key]

        print("get actor cache miss for %s %s" % (appname, actorname))

        if key in self.actorIdToActorLoader:
            loader = self.actorIdToActorLoader[key]
            aobj = loader.activate()
            j.core.portal.active.actors[key] = aobj
            return j.core.portal.active.actors[key]
        else:
            raise RuntimeError("Cannot find actor from app %s with name %s" % (appname, actorname))

    def existsActorLoader(self, appname, actorname):
        key = "%s__%s" % (appname.lower(), actorname.lower())
        return key in self.id2object

    def existsActor(self, appname, actorname):
        key = "%s__%s" % (appname.lower(), actorname.lower())
        return key in j.core.portal.active.actors

    def scan(self, path, reset=False):
        paths = path
        if isinstance(paths, basestring):
            paths = [paths]

        for path in paths:
            jsonfiles = j.system.fs.listFilesInDir(path, filter='*.json')
            for jsonfile in jsonfiles:
                j.tools.swaggerGen.loadSpecFromFile(jsonfile)
                j.tools.swaggerGen.generateActors(path)

        return super(ActorsLoader, self).scan(paths, reset)

    def loadOsisTasklets(self, actorobject, actorpath, modelname):
        path = j.system.fs.joinPaths(actorpath, "ros", modelname)
        if j.system.fs.exists(path):
            for method in ["set", "get", "delete", "list", "find", "datatables"]:
                path2 = j.system.fs.joinPaths(path, "method_%s" % method)
                actorobject._te["model_%s_%s" % (modelname, method)] = j.core.taskletengine.get(path2)

class ActorLoader(LoaderBaseObject):

    def __init__(self):
        LoaderBaseObject.__init__(self, "actor")
        self.roscl = None

    def createDefaults(self, path):
        base = j.system.fs.joinPaths(j.core.portalloader.getTemplatesPath(), "%s" % self.type)
        j.system.fs.copyDirTree(base, path, overwriteFiles=False)

    def raiseError(self, msg, path=None):
        raise RuntimeError("%s\npath was:%s"%(msg,path))

    def loadFromDisk(self, path, reset=False):
        # the name is $appname__actorname all in lowercase
        name = j.system.fs.getDirName(path, True)
        # print "load actor dir:%s"%path
        if name.find("__") != -1:
            app, actor = name.split("__", 1)
        else:
            return self.raiseError("Cannot create actor, name of directory needs to be $appname__$actorname", path=path)
        self._loadFromDisk(path, reset=False)
        self.model.application = app
        self.model.actor = actor

    def _removeFromMem(self):
        print("remove actor %s from memory" % self.model.id)
        j.core.specparser.removeSpecsForActor(self.model.application, self.model.actor)
        j.core.codegenerator.removeFromMem(self.model.application, self.model.actor)
        j.core.portal.active.unloadActorFromRoutes(self.model.application, self.model.actor)
        key = "%s_%s" % (self.model.application.lower(), self.model.actor.lower())
        if key in j.core.portal.active.actors:
            j.core.portal.active.actors.pop(key)

    def reset(self):
        self._removeFromMem()
        self.loadFromDisk(self.model.path, reset=True)
        j.core.portal.active.actorsloader.getActor(self.model.application, self.model.actor)

    def _descrTo1Line(self, descr):
        if descr == "":
            return descr
        descr = descr.strip()
        descr = descr.replace("\n", "\\n")
        # descr=descr.replace("'n","")
        return descr


    def activate(self):
        print("activate actor: %s %s" % (self.model.application, self.model.actor))

        appname=self.model.application
        actorname=self.model.actor
        actorpath=self.model.path
        # parse the specs
        j.core.specparser.parseSpecs("%s/specs" % actorpath, appname=appname, actorname=actorname)

        # retrieve the just parsed spec
        spec = j.core.specparser.getActorSpec(appname, actorname, raiseError=False)
        if spec == None:
            return None

        if spec.tags == None:
            spec.tags = ""
        tags = j.core.tags.getObject(spec.tags)

        spec.hasTasklets = tags.labelExists("tasklets")

        # generate the tasklets for the methods of the actor
        # j.core.codegenerator.generate(spec,"tasklet",codepath=actorpath)

        # generate the class for the methods of the actor
        args = {}
        args["tags"] = tags
        classpath = j.system.fs.joinPaths(actorpath, "methodclass", "%s_%s.py" % (spec.appname, spec.actorname))
        modelNames = j.core.specparser.getModelNames(appname, actorname)

        actorobject = j.core.codegenerator.generate(spec, "actorclass", codepath=actorpath, classpath=classpath,
                                                    args=args, makeCopy=True)()

        if len(modelNames) > 0:
            actorobject.models = Class()

            for modelName in modelNames:
                modelspec = j.core.specparser.getModelSpec(appname, actorname, modelName)
                modeltags = j.core.tags.getObject(modelspec.tags)

                # will generate the tasklets
                modelHasTasklets = modeltags.labelExists("tasklets")
                if modelHasTasklets:
                    j.core.codegenerator.generate(modelspec, "ros", codepath=actorpath, returnClass=False, args=args)

                if spec.hasTasklets:
                    self.loadOsisTasklets(actorobject, actorpath, modelname=modelspec.name)

                classs = j.core.codegenerator.getClassJSModel(appname, actorname, modelName, codepath=actorpath)
                if modelspec.tags == None:
                    modelspec.tags = ""
                index = j.core.tags.getObject(modelspec.tags).labelExists("index")
                tags = j.core.tags.getObject(modelspec.tags)

        # add routes to webserver
        for methodspec in spec.methods:
            # make sure tasklets are loaded

            methodtags = j.core.tags.getObject(methodspec.tags)
            methodspec.hasTasklets = methodtags.labelExists("tasklets")

            if methodspec.hasTasklets or spec.hasTasklets:
                taskletpath = j.system.fs.joinPaths(actorpath, "methodtasklets", "method_%s" % methodspec.name)
                if not j.system.fs.exists(taskletpath):
                    j.system.fs.createDir(taskletpath)
                    taskletContent = """
def main(j, args, params, actor, tags, tasklet):
    return params

def match(j, args, params, actor, tags, tasklet):
    return True
                    """
                    methodtasklet = j.system.fs.joinPaths(taskletpath, "5_%s.py" % methodspec.name)
                    j.system.fs.writeFile(methodtasklet, taskletContent)
                actorobject._te[methodspec.name] = j.core.taskletengine.get(taskletpath)

            if j.core.portal.active != None:

                params = {}
                for var in methodspec.vars:
                    param = {'optional': False, 'description': '', 'default': None, 'type': None}
                    tags = j.core.tags.getObject(var.tags)
                    if tags.labelExists("optional"):
                        param['optional'] = True
                        descr = var.description + " (optional)"
                    else:
                        descr = var.description
                    param['description'] = descr
                    param['type'] = var.ttype
                    if var.defaultvalue:
                        param['default'] = var.defaultvalue
                    params[var.name] = param

                tags = j.core.tags.getObject(methodspec.tags)
                if tags.tagExists("returnformat"):
                    returnformat = tags.tagGet("returnformat")
                else:
                    returnformat = None

                auth = not tags.labelExists("noauth")
                methodcall = getattr(actorobject, methodspec.name)
                j.core.portal.active.addRoute(methodcall, appname, actorname, methodspec.name, params=params,
                                              description=methodspec.description, auth=auth, returnformat=returnformat)

        # load taskletengines if they do exist
        tepath = j.system.fs.joinPaths(actorpath, "taskletengines")
        if j.system.fs.exists(tepath):
            if "taskletengines" not in actorobject.__dict__:
                actorobject.taskletengines = Class()
            tepaths = j.system.fs.listDirsInDir(tepath)
            for tepath in tepaths:
                actorobject.taskletengines.__dict__[j.system.fs.getBaseName(tepath)] = j.core.taskletengine.get(tepath)

        # LOAD actorobject to qbase tree
        if appname not in j.apps.__dict__:
            j.apps.__dict__[appname] = AppClass(appname)

        if actorname not in j.apps.__dict__[appname].__dict__:
            j.apps.__dict__[appname].__dict__[actorname] = actorobject

        if "runningAppserver" in j.core.portal.__dict__:
            key = "%s_%s" % (spec.appname.lower(), spec.actorname.lower())
            j.core.portal.active.actors[key] = actorobject

        # load extensions
        actorobject.__dict__['extensions'] = ActorExtensionsGroup(j.system.fs.joinPaths(actorpath, "extensions"))

        return actorobject
