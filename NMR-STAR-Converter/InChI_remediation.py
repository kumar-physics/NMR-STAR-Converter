'''
Created on Sep 6, 2017

@author: kumaran
'''

import pynmrstar,csv,copy,datetime,urllib2,json
from datetime import date
from string import atoi

class InChI(object):
    '''
    classdocs
    '''


    def __init__(self, bmrbid):
        '''
        Constructor
        '''
        self.bmrbid = bmrbid
        self.alatis_url = "http://alatis.nmrfam.wisc.edu/examples/BMRB/%s/map.txt"%(self.bmrbid)
        self.get_map()
        self.today = datetime.date.today()
        self.outfile = '/home/kumaran/git/NMR-STAR-Converter/InChIOutput/%s.str'%(self.bmrbid)

    def convert(self):
        try:
            self.inStar = pynmrstar.Entry.from_database(self.bmrbid)
        except ValueError:
            print self.bmrbid
            exit(1)
        
        for saveframe in self.inStar:
            self.loop_category = [loop.category for loop in saveframe]
            if saveframe.category == "entry_information":
                if "_Release" in self.loop_category:
                    release = saveframe.get_loop_by_category("_Release")
                    dat=[]
                    for col_name in release.columns:
                        if col_name == "Release_number":
                            dat.append(atoi(release.data[-1][release.columns.index(col_name)])+1)
                        #elif col_name == "Format_type":
                        #    dat.append("NMR-STAR")
                        #elif col_name == "Format_version":
                        #    dat.append("3.2.0.9")
                        elif col_name == "Date":
                            dat.append(self.today)
                        elif col_name == "Submission_date":
                            dat.append(release.data[-1][release.columns.index(col_name)])
                        elif col_name == "Type":
                            dat.append("update")
                        elif col_name == "Author":
                            dat.append("BMRB")
                        elif col_name == "Detail":
                            dat.append("InChI numbering updated according to ALATIS")
                        elif col_name == "Entry_ID":
                            dat.append(self.inStar.entry_id)
                        else:
                                dat.append(".")
                    saveframe.get_loop_by_category("_Release").add_data(dat)
                else:
                    release = pynmrstar.Loop.from_scratch("_Release")
                    columns = ["Release_number","Date","Submission_date","Type","Author","Detail","Entry_ID"]
                    for col_name in columns:
                        release.add_column(col_name)
                    release.add_data([1,self.today,".","update","BMRB","InChI numbering updated according to ALATIS",self.inStar.entry_id])
                    saveframe.add_loop(release)
            for loop in saveframe:
                if loop.category == "_Atom_nomenclature":
                    for data in loop.data:
                        data[loop.columns.index("Atom_ID")] = self.map[data[loop.columns.index("Atom_ID")]]
                        data[loop.columns.index("Naming_system")] = "BMRB"
                    data_copy = copy.deepcopy(loop.data)
                    for dat in data_copy:
                        try:
                            dat[loop.columns.index("Atom_name")] = self.map[dat[loop.columns.index("Atom_name")]]
                            dat[loop.columns.index("Naming_system")] = "ALATIS" 
                            loop.add_data(dat)
                        except KeyError:
                            print self.inStar.entry_id,saveframe.name, loop.category,self.map
                            exit(10)
                else:
                    if "Atom_ID" in loop.columns:
                        for data in loop.data:
                            try:
                                data[loop.columns.index("Atom_ID")] = self.map[data[loop.columns.index("Atom_ID")]]
                            except KeyError:
                                if data[loop.columns.index("Atom_ID")] == "?":
                                    data[loop.columns.index("Atom_ID")] = "?"
                                else:
                                    print self.inStar.entry_id,saveframe.name, loop.category,self.map
                                    exit(1)
                                
                    if "Atom_ID_1" in loop.columns:
                        for data in loop.data:
                            data[loop.columns.index("Atom_ID_1")] = self.map[data[loop.columns.index("Atom_ID_1")]]
                    if "Atom_ID_2" in loop.columns:
                        for data in loop.data:
                            data[loop.columns.index("Atom_ID_2")] = self.map[data[loop.columns.index("Atom_ID_2")]]
                    
        #self.inStar.normalize()            
        with open(self.outfile,'w') as wstarfile:
            wstarfile.write(str(self.inStar))
        
            
        #print self.inStar
    def get_map(self):
        try:
            data = [d.split("\t") for d in urllib2.urlopen(self.alatis_url).read().split("\n")]
            self.map = {}
            for i in range(1,len(data)):
                if len(data[i])>1: self.map[data[i][1]+data[i][2]]=data[i][1]+data[i][0]
        except urllib2.HTTPError:
            print self.bmrbid
            self.map={}
        
           
if __name__ == "__main__":
    res = urllib2.urlopen('http://webapi.bmrb.wisc.edu/v2/list_entries?database=metabolomics')
    idlist = json.loads(res.read())
    for j in range(len(idlist)):
        #print bmrbid
        bmrbid = idlist[j]
        p = InChI(bmrbid)
        if len(p.map)>0 and bmrbid not in [ 'bmse001024','bmse000134','bmse000400','bmse000471','bmse000644','bmse000717','bmse000720','bmse000735','bmse000762']:
            p.convert()