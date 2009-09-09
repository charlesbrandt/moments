from moments.log import Log as MomentLog
from node import File

class Log(File):
    """
    2008.12.10 17:05:55
    should we just use a standard log?
    is the wrapper needed?
    
    a Node based wrapper for the MomentLog Log Object
    """
    def __init__(self, path):
        File.__init__(self, path)
        self.log = MomentLog(path)
        self.log.from_file()

    
