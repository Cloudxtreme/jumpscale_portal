from JumpScale import j
import os

from .LoaderBase import LoaderBase
from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler

addedspaces = []

class SpaceWatcher():

    def __init__(self, contentdir=''):
        """
        @param contentDirs are the dirs where we will load wiki files from & parse

        """
        self.file_observers = []
        self.spacehandler = SpaceHandler(self)
        self.contentdir = contentdir if contentdir.endswith('/') else '%s/' % contentdir
        
        if not j.system.fs.exists(contentdir):
            print("Contentdir %s was not found .. creating it." % contentdir)
            j.system.fs.createDir(contentdir)

        if contentdir.strip():
            # Watch the contentdir for changes
            observer = Observer()
            self.file_observers.append(observer)
            j.core.portal.active.watchedspaces.append(contentdir)
            print('Monitoring', contentdir)
            observer.schedule(self.spacehandler, contentdir, recursive=True)
            observer.start()

    def addSpace(self, spacename, spacepath):
        if spacename not in j.core.portal.active.spacesloader.spaces:
            print('Space %s added' % spacename)
            j.core.portal.active.spacesloader.scan(spacepath)


 
class SpaceHandler(FileSystemEventHandler):
    def __init__(self, spacewatcher):
        self.spacewatcher = spacewatcher


    def on_created(self, event):
        path = os.path.dirname(event.src_path)
        newspace = path.replace(self.spacewatcher.contentdir, '').split('/', 1)[0]
        newspacepath = j.system.fs.joinPaths(self.spacewatcher.contentdir, newspace)
        if newspace:
            self.spacewatcher.addSpace(newspace.lower(), newspacepath)

    on_moved = on_created

