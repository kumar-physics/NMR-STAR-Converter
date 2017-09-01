'''
Created on Mar 15, 2017

@author: kumaran
'''
import pynmrstar,csv,copy,datetime
from datetime import date
from string import atoi

class NMRSTAR(object):
    '''
    classdocs
    '''


    def __init__(self,filename):
        '''
        Constructor
        '''
        self.inFile = filename
        self.outfile = '/home/kumaran/git/NMR-STAR-Converter/output.str'
        self.newSchema = pynmrstar.Schema('/home/kumaran/git/nmr-star-dictionary/bmrb_only_files/adit_input/xlschem_ann.csv')
        self.oldSchema = pynmrstar.Schema('/home/kumaran/git/nmr-star-dictionary/bmrb_star_v3_files/adit_input/xlschem_ann.csv')
        self.today = datetime.date.today()
    
    def Convert(self):
        self.inputStar = pynmrstar.Entry.from_database(self.inFile)
        #pynmrstar.validate(self.oldStar,self.newSchema)
        #self.newStar = pynmrstar.Entry.from_file('/home/kumaran/nmrstar/adit_input/nmrstar32.str')
        #self.ReadMapFile()
        self.outputStar = pynmrstar.Entry.from_scratch(self.inputStar.entry_id)
        for saveframe in self.inputStar:
            if saveframe.category == "entry_information":
                outSaveframe = copy.deepcopy(saveframe)
                outSaveframe["Format_name"]= 'NMR-STAR v3.2'
                outSaveframe["NMR_STAR_version"] = '3.2.0.9'
                #outSaveframe["Source_data_format"] = 'NMR-STAR v3.1'
                #outSaveframe["Source_data_format_version"] = saveframe["NMR_STAR_version"][0]
                #outSaveframe["Generated_software_name"] = 'yet to be decided'
                #outSaveframe["Generated_software_version"] = "yet to be decided"
                #outSaveframe["Generated_date"] = self.today
                self.loop_category = [loop.category for loop in saveframe]
                if "_Release" in self.loop_category:
                    release = saveframe.get_loop_by_category("_Release")
                    dat=[]
                    for col_name in release.columns:
                        if col_name == "Release_number":
                            dat.append(atoi(release.data[-1][release.columns.index(col_name)])+1)
                        elif col_name == "Format_type":
                            dat.append("NMR-STAR")
                        elif col_name == "Format_version":
                            dat.append("3.2.0.9")
                        elif col_name == "Date":
                            dat.append(self.today)
                        elif col_name == "Type":
                            dat.append("original")
                        elif col_name == "Author":
                            dat.append("BMRB")
                        elif col_name == "Detail":
                            dat.append("Format conversion from 3.1 to 3.2")
                        elif col_name == "Entry_ID":
                            dat.append(self.inputStar.entry_id)
                        else:
                            dat.append(".")
                    outSaveframe.get_loop_by_category("_Release").add_data(dat)
                else:
                    release = pynmrstar.Loop.from_scratch("_Release")
                    columns = ["Release_number","Format_type","Format_version","Date","Submission_date","Type","Author","Detail","Entry_ID"]
                    for col_name in columns:
                        release.add_column(col_name)
                    release.add_data([1,"NMR-STAR","3.2.0.9",self.today,".","original","BMRB","Format conversion from 3.1 to 3.2",self.inputStar.entry_id])
                    outSaveframe.add_loop(release)
                self.outputStar.add_saveframe(outSaveframe)
                
                #print outSaveframe
            elif saveframe.category == "spectral_peak_list":
                outSaveframe = pynmrstar.Saveframe.from_scratch("%s_v3.2"%(saveframe.name), saveframe.tag_prefix)
                for tag in saveframe.tags:
                    if tag[0] == "Sf_framecode":
                        outSaveframe.add_tag(tag[0],"%s_v3.2"%(saveframe.name))
                    else:
                        outSaveframe.add_tag(tag[0],tag[1])
                outSaveframe["Text_data_format"]='.'
                self.dim = atoi(saveframe["Number_of_spectral_dimensions"][0]) 
                self.loop_category = [loop.category for loop in saveframe]
                peak = copy.deepcopy(saveframe.get_loop_by_category("_Peak"))
                spect_dim = saveframe.get_loop_by_category("_Spectral_dim")
                outSaveframe.add_loop(spect_dim)
                if "_Peak_general_char" in self.loop_category:
                    peak_gen_char = saveframe.get_loop_by_category("_Peak_general_char")
                    #print len(peak_gen_char.get_data_by_tag("Measurement_method"))
                    if "height" in peak_gen_char.get_data_by_tag("Measurement_method")[0]:
                        peak.add_column("Height")
                        peak.add_column("Height_uncertainty")
                    if "volume" in peak_gen_char.get_data_by_tag("Measurement_method")[0]:
                        peak.add_column("Volume")
                        peak.add_column("Volume_uncertainty")
                    measurement = {}
                    measurement_err ={}
                    for dat in peak_gen_char.data:
                        measurement[(dat[peak_gen_char.columns.index("Peak_ID")],dat[peak_gen_char.columns.index("Measurement_method")])] = dat[peak_gen_char.columns.index("Intensity_val")]
                        measurement_err[(dat[peak_gen_char.columns.index("Peak_ID")],dat[peak_gen_char.columns.index("Measurement_method")])] = dat[peak_gen_char.columns.index("Intensity_val_err")]
                if "_Peak_char" in self.loop_category:
                    peak_char = saveframe.get_loop_by_category("_Peak_char")
                    for i in range(self.dim):
                        peak.add_column("Position_%d"%(i+1))
                        peak.add_column("Position_uncertainity_%d"%(i+1))
                    position = {}
                    position_err = {}
                    for dat in peak_char.data:
                        position[(dat[peak_char.columns.index("Peak_ID")],dat[peak_char.columns.index("Spectral_dim_ID")])] = dat[peak_char.columns.index("Chem_shift_val")]
                        position_err[(dat[peak_char.columns.index("Peak_ID")],dat[peak_char.columns.index("Spectral_dim_ID")])] = dat[peak_char.columns.index("Chem_shift_val_err")]
                        
                if "_Assigned_peak_chem_shift" in self.loop_category:
                    assigned_peak = saveframe.get_loop_by_category("_Assigned_peak_chem_shift")
                    if "Entity_assembly_ID" in assigned_peak.columns:
                        for i in range(self.dim):
                            peak.add_column("Entity_assembly_ID_%d"%(i+1))
                    if "Entity_ID" in assigned_peak.columns:
                        for i in range(self.dim):
                            peak.add_column("Entity_ID_%d"%(i+1))
                    if "Comp_ID" in assigned_peak.columns:
                        for i in range(self.dim):
                            peak.add_column("Comp_ID_%d"%(i+1))
                    if "Comp_index_ID" in assigned_peak.columns:
                        for i in range(self.dim):
                            peak.add_column("Comp_index_ID_%d"%(i+1))
                    if "Atom_ID" in assigned_peak.columns:
                        for i in range(self.dim):
                            peak.add_column("Atom_ID_%d"%(i+1))
                    if "Auth_entity_ID" in assigned_peak.columns:
                        for i in range(self.dim):
                            peak.add_column("Auth_entity_ID_%d"%(i+1))
                    if "Auth_comp_ID" in assigned_peak.columns:
                        for i in range(self.dim):
                            peak.add_column("Auth_comp_ID_%d"%(i+1))
                    if "Auth_seq_ID" in assigned_peak.columns:
                        for i in range(self.dim):
                            peak.add_column("Auth_seq_ID_%d"%(i+1))
                    if "Auth_atom_ID" in assigned_peak.columns:
                        for i in range(self.dim):
                            peak.add_column("Auth_atom_ID_%d"%(i+1))
                    
                    ent_asm_id = {}
                    ent_id = {}
                    com_id = {}
                    com_ind_id = {}
                    atm_id = {}
                    aut_ent_id = {}
                    aut_com_id = {}
                    aut_seq_id = {}
                    aut_atm_id = {}
                    for dat in assigned_peak.data:
                        ent_asm_id[(dat[assigned_peak.columns.index("Peak_ID")],dat[assigned_peak.columns.index("Spectral_dim_ID")])]= dat[assigned_peak.columns.index("Entity_assembly_ID")]
                        ent_id[(dat[assigned_peak.columns.index("Peak_ID")],dat[assigned_peak.columns.index("Spectral_dim_ID")])]= dat[assigned_peak.columns.index("Entity_ID")]
                        com_id[(dat[assigned_peak.columns.index("Peak_ID")],dat[assigned_peak.columns.index("Spectral_dim_ID")])]= dat[assigned_peak.columns.index("Comp_ID")] 
                        com_ind_id[(dat[assigned_peak.columns.index("Peak_ID")],dat[assigned_peak.columns.index("Spectral_dim_ID")])]= dat[assigned_peak.columns.index("Comp_index_ID")]
                        atm_id[(dat[assigned_peak.columns.index("Peak_ID")],dat[assigned_peak.columns.index("Spectral_dim_ID")])]= dat[assigned_peak.columns.index("Atom_ID")]
                        aut_ent_id[(dat[assigned_peak.columns.index("Peak_ID")],dat[assigned_peak.columns.index("Spectral_dim_ID")])]= dat[assigned_peak.columns.index("Auth_entity_ID")]
                        aut_com_id[(dat[assigned_peak.columns.index("Peak_ID")],dat[assigned_peak.columns.index("Spectral_dim_ID")])]= dat[assigned_peak.columns.index("Auth_comp_ID")]
                        aut_seq_id[(dat[assigned_peak.columns.index("Peak_ID")],dat[assigned_peak.columns.index("Spectral_dim_ID")])]= dat[assigned_peak.columns.index("Auth_seq_ID")]
                        aut_atm_id[(dat[assigned_peak.columns.index("Peak_ID")],dat[assigned_peak.columns.index("Spectral_dim_ID")])]= dat[assigned_peak.columns.index("Auth_atom_ID")]   
                new_peak_loop = pynmrstar.Loop.from_scratch(peak.category)   
                for col_name in peak.columns:
                    new_peak_loop.add_column(col_name)
                for dat in peak.data:
                    new_dat = copy.deepcopy(dat)
                    try:
                        new_dat.append(measurement[(dat[peak.columns.index("ID")],"height")])
                    except KeyError:
                        new_dat.append(".")
                    try:
                        new_dat.append(measurement_err[(dat[peak.columns.index("ID")],"height")])
                    except KeyError:
                        new_dat.append(".")
                    try:
                        new_dat.append(measurement[(dat[peak.columns.index("ID")],"volume")])
                    except KeyError:
                        new_dat.append(".")
                    try:
                        new_dat.append(measurement_err[(dat[peak.columns.index("ID")],"volume")])
                    except KeyError:
                        new_dat.append(".")
                    for d in range(self.dim):
                        try:
                            new_dat.append(position[(dat[peak.columns.index("ID")],"%d"%(d+1))])
                        except KeyError:
                            new_dat.append(".")
                    for d in range(self.dim):
                        try:
                            new_dat.append(position_err[(dat[peak.columns.index("ID")],"%d"%(d+1))])
                        except KeyError:
                            new_dat.append(".")
                    for d in range(self.dim):
                        try:
                            new_dat.append(ent_asm_id[(dat[peak.columns.index("ID")],"%d"%(d+1))])
                        except KeyError:
                            new_dat.append(".")
                    for d in range(self.dim):
                        try:
                            new_dat.append(ent_id[(dat[peak.columns.index("ID")],"%d"%(d+1))])
                        except KeyError:
                            new_dat.append(".")
                    for d in range(self.dim):
                        try:
                            new_dat.append(com_id[(dat[peak.columns.index("ID")],"%d"%(d+1))])
                        except KeyError:
                            new_dat.append(".")
                    for d in range(self.dim):
                        try:
                            new_dat.append(com_ind_id[(dat[peak.columns.index("ID")],"%d"%(d+1))])
                        except KeyError:
                            new_dat.append(".")
                    for d in range(self.dim):
                        try:
                            new_dat.append(atm_id[(dat[peak.columns.index("ID")],"%d"%(d+1))])
                        except KeyError:
                            new_dat.append(".")
                    for d in range(self.dim):
                        try:
                            new_dat.append(aut_ent_id[(dat[peak.columns.index("ID")],"%d"%(d+1))])
                        except KeyError:
                            new_dat.append(".")
                    for d in range(self.dim):
                        try:
                            new_dat.append(aut_com_id[(dat[peak.columns.index("ID")],"%d"%(d+1))])
                        except KeyError:
                            new_dat.append(".")
                    for d in range(self.dim):
                        try:
                            new_dat.append(aut_seq_id[(dat[peak.columns.index("ID")],"%d"%(d+1))])
                        except KeyError:
                            new_dat.append(".")
                    for d in range(self.dim):
                        try:
                            new_dat.append(aut_atm_id[(dat[peak.columns.index("ID")],"%d"%(d+1))])
                        except KeyError:
                            new_dat.append(".")
                    #print new_peak_loop.columns
                    #print new_dat   
                    new_peak_loop.add_data(new_dat)
                outSaveframe.add_loop(new_peak_loop)
                self.outputStar.add_saveframe(outSaveframe)
                self.outputStar.add_saveframe(saveframe)
            else:
                self.outputStar.add_saveframe(saveframe)
        #print self.outputStar
        #pynmrstar.Entry.normalize(self.outputStar, schema = self.newSchema)
        #self.outputStar.normalize()
        with open(self.outfile,'w') as wstarfile:
            wstarfile.write(str(self.outputStar))
        
                
                
           
            #print saveframe.name,saveframe.category
            
if __name__=="__main__":
    #p = NMRSTAR('/home/kumaran/git/nmr-star-dictionary/bmrb_star_v3_files/adit_input/nmrstar3_fake.txt')
    #p = NMRSTAR('/home/kumaran/git/nmr-star-dictionary/bmrb_only_files/adit_input/nmrstar3_fake.txt')
    p=NMRSTAR('26860')
    p.Convert()
    
      