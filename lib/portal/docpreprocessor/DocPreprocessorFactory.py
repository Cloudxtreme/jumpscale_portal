from JumpScale import j
from .DocPreprocessor import *


class DocPreprocessorFactory():

    def get(self, contentDirs=[], varsPath="", spacename=""):
        """
        @param contentDirs are the dirs where we will load wiki files from & parse
        """
        if spacename=="":
            raise RuntimeError("spacename cannot be empty")
        return DocPreprocessor(contentDirs, varsPath, spacename)

    def _getMacroExecutor(self, paths):
        return MacroExecutor(paths)

    def generate(self, preprocessorobject, outpath="out", startDoc="Home", visibility=[], reset=True, outputdocname="", format="preprocess", deepcopy=False):
        raise RuntimeError("need to fix")
        if deepcopy:
            poogen = copy.copy(preprocessorobject)
        else:
            poogen = preprocessorobject

        docname = startDoc.name.lower().strip()
        if docname not in poogen.name2doc:
            raise RuntimeError("Cannot generate docs because could not find doc %s" % docname)
        if reset:
            try:
                j.system.fs.removeDirTree(outpath)
            except:
                print("COULD NOT REMOVE %s" % outpath)

        doc = poogen.name2doc[docname]
        doc.checkVisible(visibility)
        doc.preprocess()

        if outputdocname != "":
            doc.pagename = outputdocname

        if format == "preprocess":
            doc.generate2disk(outpath)
        elif format == "confluence":
            page = j.tools.docgenerator.pageNewConfluence(doc.name)
            for line in doc.content.split("\n"):
                macrostrs = poogen.macroexecutor.findMacros(line)
                if len(macrostrs) > 0:
                    for macrostr in macrostrs:
                        poogen.macroexecutor.executeMacroAdd2Page(macrostr, page, doc)
                else:
                    page.content += "%s\n" % line

                dirpath = j.system.fs.joinPaths(outpath, doc.name)
                filepath = j.system.fs.joinPaths(dirpath, "%s.txt" % doc.name)
                j.system.fs.createDir(dirpath)
                for image in doc.images:
                    if image in doc.preprocessor.images:
                        filename = "%s_%s" % (doc.name, image)
                        j.system.fs.copyFile(doc.preprocessor.images[image], j.system.fs.joinPaths(dirpath, filename))
                    page.content = page.content.replace("!%s" % image, "!%s" % filename)

                j.system.fs.writeFile(filepath, page.content)

        else:
            raise RuntimeError("formatter not understood, only supported now preprocess & confluence")

    def generateFromDir(self, path, macrosPaths=[], visibility=[], cacheDir=""):
        """
        @param path is starting point, will look for generate.cfg & params.cfg in this dir, input in these files will determine how preprocessor will work
        @param macrosPaths are dirs where macro's are they are in form of tasklets
        @param cacheDir if non std caching dir override here
        """

        if j.system.fs.isFile(path):
            path = j.system.fs.getDirName(path)

        varcfgpath = j.system.fs.joinPaths(path, "vars.cfg")
        cfgpath = j.system.fs.joinPaths(path, "generate.cfg")

        if j.system.fs.exists(cfgpath):
            inifile = j.tools.inifile.open(cfgpath)
            outpath = inifile.getValue("generate", "outpath")
            format = inifile.getValue("generate", "format")
        else:
            raise RuntimeError("could not find inifile %s" % cfgpath)

        if outpath.find("\\") == -1 and outpath.find("/") == -1:
            # is dirname only
            outpath = j.system.fs.joinPaths(path, outpath)

        preprocessor = DocPreprocessor([path], varcfgpath, macrosPaths, cacheDir=cacheDir)

        counter = 1
        while inifile.checkSection("include%s" % counter):
            path2 = inifile.getValue("include%s" % counter, "path")
            counter += 1
            if path2.find("..") == 0:
                path2 = j.system.fs.joinPaths(path, path2)
            # if path2.find("^")==0:
                # path2=j.system.fs.joinPaths(path,path2)
                # path2=path2[1:]

            preprocessor.scan(path2)

        j.system.fs.createDir(outpath)

        try:
            j.system.fs.removeDirTree(outpath)
        except:
            pass

        homepaths = j.system.fs.listFilesInDir(path, filter="*.wiki")
        for homedocPath in homepaths:
            homedoc = j.system.fs.getBaseName(homedocPath)
            homedoc = homedoc.replace(".wiki", "")
            outputdocname = homedoc
            doc = preprocessor.docGet(homedoc)
            doc.contenttype = "c"
            self.generate(preprocessor, outpath=outpath, startDoc=doc, visibility=visibility, reset=False, outputdocname=outputdocname, format="confluence")

        return preprocessor

    def getMacroPath(self):
        dirname = j.system.fs.getDirName(__file__)
        return j.system.fs.joinPaths(dirname, 'macros')
