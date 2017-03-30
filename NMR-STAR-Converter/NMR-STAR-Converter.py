'''
Created on Mar 15, 2017

@author: kumaran
'''
import pynmrstar

class NMRSTAR(object):
    '''
    classdocs
    '''


    def __init__(self,filename):
        '''
        Constructor
        '''
        self.inFile = filename
        self.oldSchema = pynmrstar.Schema('/home/kumaran/nmrstar/adit_input/xlschem_ann.csv')
        self.newSchema = pynmrstar.Schema()
        
    
    def Convert(self):
        self.oldStar = pynmrstar.Entry.from_file('/home/kumaran/nmrstar/adit_input/nmrstar31.str')
        self.newStar = pynmrstar.Entry.from_file('/home/kumaran/nmrstar/adit_input/nmrstar32.str')
        self.oldTags = []
        self.newTags = []
        l1 = str(self.oldSchema).split("\n")
        p=""
        for x in l1:
            if len(x)>0:
                if x[0] == "_":
                    p=x
                else:
                    self.oldTags.append("%s.%s"%(p.strip(),x.strip().split(" ")[0]))
        l1 = str(self.newSchema).split("\n")
        p=""
        for x in l1:
            if len(x)>0:
                if x[0] == "_":
                    p=x
                else:
                    self.newTags.append("%s.%s"%(p.strip(),x.strip().split(" ")[0]))
        self.oldSet=set(self.oldTags)
        self.newSet=set(self.newTags)
        for x in self.newSet-self.oldSet:
            print x
if __name__=="__main__":
    p = NMRSTAR('/home/kumaran/nmrstar/adit_input/nmrstar31.str')
    p.Convert()
    
      