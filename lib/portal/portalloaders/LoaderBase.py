from JumpScale import j

class LoaderBase(object):
    """
    is loader for all objects e.g. for all actors or spaces
    """

    def __init__(self, type, objectClass):
        """
        """
        self.id2object = {}
        self.__dict__["%ss" % type] = self.id2object
        self.type = type
        self._objectClass = objectClass

    def getLoaderFromId(self, id):
        id = id.lower()
        if id in self.id2object:
            return self.id2object[id]
        else:
            raise RuntimeError("Could not find loader with id %s" % id)

    def removeLoader(self, id):
        id = id.lower()
        if id in self.id2object:
            self.id2object.pop(id)
            loader = self.__dict__["%ss" % self.type]
            if id in loader:
                loader.pop(id)

    # def _getSystemLoaderForUsersGroups(self):
    #     lba = LoaderBaseObject("")
    #     userspath = j.system.fs.joinPaths(j.core.portal.active.cfgdir, 'users.cfg')
    #     if not j.system.fs.exists(userspath):
    #         ini = j.config.getInifile(userspath)
    #         ini.addSection('admin')
    #         ini.addParam('admin', 'passwd', 'admin')
    #         ini.addParam('admin', 'groups', 'admin')
    #         ini.addParam('admin', 'reset', '1')
    #         ini.addSection('guest')
    #         ini.addParam('guest', 'passwd', '')
    #         ini.addParam('guest', 'groups', 'guest')
    #         ini.addParam('guest', 'reset', '1')

    #     lba.processUsers(j.core.portal.active.cfgdir)

    def scan(self, path, reset=False):
        """
        path can be 1 path or list of paths
        """
        paths = path
        if isinstance(path, basestring):
            paths = [path]

        for path in paths:
            items = [j.system.fs.pathNormalize(item.replace(".%s" % self.type, "") + "/") for
                     item in j.system.fs.listDirsInDir(path, True, False, True)
                     if j.system.fs.getDirName(item + "/", True) == ".%s" % self.type]

            #find objects like spaces,actors,...
            for path in items:
                object = self._objectClass()
                result = object.loadFromDisk(path, reset)
                if result != False:
                    print("load %s %s" % (self.type,path))
                    self.id2object[object.model.id.lower()] = object

class Model():
    pass

class LoaderBaseObject():
    """
    is loader for 1 object
    """

    def __init__(self, type):
        self.model=Model()
        if type=="actor":
            self.model.application=""
            self.model.actor=""
        self.model.id=""
        self.model.path=""
        self.model.acl={} #dict with key the group or username; and the value is a string
        self.type = type

    def _createDefaults(self, path):
        src = j.system.fs.joinPaths(j.core.portalloader.getTemplatesPath(), "%s" % self.type)
        dest = j.system.fs.joinPaths(path)
        j.system.fs.copyDirTree(src, dest, keepsymlinks=False, eraseDestination=False, skipProtectedDirs=False, overwriteFiles=False)        

    def _loadFromDisk(self, path, reset=False):
        # path=path.replace("\\","/")
        # print "loadfromdisk:%s" % path

        # remove old cfg and write new one with only id
        cfgpath = j.system.fs.joinPaths(path, ".%s" % self.type, "main.cfg")

        if not j.system.fs.exists(cfgpath):
            self.createDefaults(path)

        if j.system.fs.exists(cfgpath):
            ini=j.tools.inifile.open(cfgpath)
        else:
            ini = j.tools.inifile.new(cfgpath)
        ini.addSection("main")
        name=j.system.fs.getDirName(path, True)
        ini.setParam("main", "id", name)
        ini.write()

        self.model.id = name
        if ini.checkParam('main', 'name'):
            self.model.name = ini.getValue('main', 'name')
        else:
            self.model.name = name
        self.model.path=path
        self.processAcl()

    def processAcl(self, cfgdir=""):
        # populate acl
        if cfgdir == "":
            cfgfile = j.system.fs.joinPaths(self.model.path, ".%s" % self.type, "acl.cfg")
        else:
            cfgfile = j.system.fs.joinPaths(cfgdir, "acl.cfg")

        lines = j.system.fs.fileGetContents(cfgfile).split("\n")
        for line in lines:
            line = line.strip()
            if line.strip() == "" or line[0] == "#":
                continue
            for separator in ["=", ":"]:
                if line.find(separator) != -1:
                    name, rights = line.split(separator)
                    name = name.lower().strip()
                    rights = str(rights.lower().strip())
                    self.model.acl[name] = rights
                    # print "ACE:%s %s"%(name,rights)

    def deleteOnDisk(self):
        j.system.fs.removeDirTree(self.model.path)

    def reset(self):
        self.loadFromDisk(self.model.path, reset=True)


