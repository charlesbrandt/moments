class Data:
    """
    Object to abstract the data field of an Entry
    
    typically a string works fine
    unless you want to do some parsing on the data itself
    """

    def __init__(self, data=u''):
        self.data = data
        self.template = []
        self.dictionary = {}
        
    def to_dict(self, template=''):
        if template:
            self.template = []
            for line in template.splitlines():
                self.template.append(line)
                
        ct = 0
        for line in self.data.splitlines():
            if line and self.template:
                self.dictionary[self.template[ct]] = line
            elif not self.template:
                print "ERROR: No template"
            else:
                #blankline
                pass
            
            ct += 1
            
        
