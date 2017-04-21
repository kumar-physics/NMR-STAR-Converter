'''
Created on Mar 15, 2017

@author: kumaran
'''
import pynmrstar,csv

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
        self.mapFile = '/home/kumaran/git/NMR-STAR-Converter/NMR-STAR-Converter/tag_mapping.txt'
        self.newstarFile = '/home/kumaran/nmrstar/adit_input/converted.str'
    
    def Convert(self):
        self.oldStar = pynmrstar.Entry.from_file('/home/kumaran/nmrstar/adit_input/nmrstar31.str')
        #self.newStar = pynmrstar.Entry.from_file('/home/kumaran/nmrstar/adit_input/nmrstar32.str')
        self.ReadMapFile()
        self.newStar = pynmrstar.Entry.from_scratch(self.oldStar.entry_id)
        for saveframe in self.oldStar:
            sf = pynmrstar.Saveframe.from_scratch(saveframe.name)
            for tag in saveframe.tags:
                old_tag = "%s.%s"%(saveframe.tag_prefix,tag[0])
                new_tag = self.tagMap[1][self.tagMap[0].index(old_tag)]
                sf.add_tag(new_tag,tag[1])
            for loop in saveframe:
                lp = pynmrstar.Loop.from_scratch()
                for coln in loop.columns:
                    old_tag = "%s.%s"%(loop.category,coln)
                    new_tag = self.tagMap[1][self.tagMap[0].index(old_tag)]
                    #print old_tag,new_tag,lp.category,lp.columns
                    lp.add_column(new_tag)
                for dat in loop.data:
                    lp.add_data(dat[:])
                try:
                    sf.add_loop(lp)
                except ValueError:
                    for coln in lp.columns:
                        #print "%s.%s"%(lp.category,coln),sf.get_loop_by_category(lp.category).category
                        sf.get_loop_by_category(lp.category).add_column("%s.%s"%(lp.category,coln))
                    for i in range(len(sf.get_loop_by_category(lp.category).data)):
                        sf.get_loop_by_category(lp.category).data[i]=sf.get_loop_by_category(lp.category).data[i]+lp.data[i]
            if saveframe.category ==  "spectral_peak_list":
                print saveframe       
            self.newStar.add_saveframe(sf)
         
        #print self.newStar
        self.newStar.normalize()
        with open(self.newstarFile,'w') as wstarfile:
            wstarfile.write(str(self.newStar))
       
#         self.oldTags = []
#         self.newTags = []
#         l1 = str(self.oldSchema).split("\n")
#         p=""
#         for x in l1:
#             if len(x)>0:
#                 if x[0] == "_":
#                     p=x
#                 else:
#                     self.oldTags.append("%s.%s"%(p.strip(),x.strip().split(" ")[0]))
#         l1 = str(self.newSchema).split("\n")
#         p=""
#         for x in l1:
#             if len(x)>0:
#                 if x[0] == "_":
#                     p=x
#                 else:
#                     self.newTags.append("%s.%s"%(p.strip(),x.strip().split(" ")[0]))
#         self.oldSet=set(self.oldTags)
#         self.newSet=set(self.newTags)
#         self.ReadMapFile()
#         print len(self.tagMap)
#         for tag in self.oldTags:
#             if tag not in self.newTags:
#                 print "%s,%s"%(tag,"????")
#                 print self.tagMap[1][self.tagMap[0].index(tag)]
#     
    def ReadMapFile(self):
        '''Reads the NEF_NMRSTAR_equivalence.csv file and create a mapping as a list'''
        with open(self.mapFile,'rb') as csvfile:
            spamreader = csv.reader(csvfile,delimiter=',')
            map_dat=[]
            for r in spamreader:
                #print r
                if r[0][0]!='#':
                    map_dat.append(r)
        self.tagMap=map(list,zip(*map_dat))                
if __name__=="__main__":
    p = NMRSTAR('/home/kumaran/nmrstar/adit_input/nmrstar31.str')
    p.Convert()
    
      