from node import File

class Sound(File):
    """
    object to hold sound/music specific meta data for local sound file

    """
    def __init__(self, path):
        File.__init__(self, path)

