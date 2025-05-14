import numpy as np


class suio:
    
    """ Python I/O module for seismic dataset with Seismic Un*x format ( Copyright ⓒ 2025 Sumin Kim ) 

        Author       :  Dr. Sumin Kim
        Affiliation  :  National Korea Maritime and Ocean University
        E-mail       :  seisminic@gmail.com
        github       :  https://github.com/seismin91/



        Main functions
        --------------
        1.  read_su  : to load header and trace from seismic data with Seismic Un*x format
            returns  : dictionary

        2.  write_su : to save header and trace to file with Seismic Un*x format
            returns  : None 
            
        Examples
        --------
        1. read_su

        * Implementation
        ----------------
        
        >>> from suio import suio
        >>> filename = "test_read.su"
        >>> suio = suio()
        >>> result_read = suio.read_su(filename)
        >>> result_read.keys()
        dict_keys(['tracl', 'tracr', 'fldr', 'tracf', 'ep', 'cdp', 'cdpt', 'offset', 'swdep', 'gwdep', 'sx', 'sy', 'gx', 'gy', 'cdpx', 'cdpy', 'trace'])

        >>> tracl  =  result_read[ 'tracl' ].copy()
        >>> ...

        2. write_su
        
        *Pre-requisite
        --------------
        trace        : 2D array (nt, nshot * nrcv)
              nt     : number of time samples
              nshot  : number of shots
              nrcv   : number of receivers

        headers      : dictionary
            ex) headers = {
                            'tracl' : tracl_array,
                            'fldr'  : fldr_array
                          }

        * Implementation
        ----------------
        
        >>> from suio import suio
        >>> filename = "test_write.su"
        >>> suio = suio()
        >>> suio.write_su(filename, trace, headers)

    """

    def __init__(self):
        
        print (" ***  Successfully imported I/O module for seismic Un*x format  *** \n ")
        print ("      For detail usage of this module, please refer to '?suio'      \n ")
        
        self.i4 = np.int32
        self.i2 = np.int16
        self.r4 = np.float32

        self.i4_size = self.i4().itemsize
        self.i2_size = self.i2().itemsize
        self.r4_size = self.r4().itemsize
        
        self.hdrbyte = 240
        self.nhdr_i2 = int(self.hdrbyte / self.i2_size)
        self.nhdr_i4 = int(self.hdrbyte / self.i4_size)
        self.nhdr_r4 = int(self.hdrbyte / self.r4_size)

        self.n_search_max = np.iinfo(np.int32).max
    
    def read_su(self,
                fname):
        
        self.flush_hdrs_arr()
        
        dm_i2 = np.fromfile(fname,
                            self.i2,
                            count = self.nhdr_i2,
                            offset = 0).byteswap()
        self.ns = dm_i2[57]
        self.dt = dm_i2[58]
        self.scalel = dm_i2[34]
        self.scalco = dm_i2[35]
        self.fldr_b = 0

        for idx in range(self.n_search_max):
            ioffset = (self.hdrbyte + self.r4_size * self.ns) * idx
            dm_i4 = np.fromfile(fname,
                                self.i4,
                                count = self.nhdr_i4,
                                offset = ioffset).byteswap()
            dm_r4 = np.fromfile(fname,
                                self.r4,
                                count = self.ns,
                                offset = self.hdrbyte + (self.hdrbyte + self.r4_size * self.ns) * idx).byteswap()
            if len(dm_i4) == 0:
                print (" *** Finished reading the data with Seismic Un*x format *** \n")
                print (f" Number of time samples   : {self.ns} ")
                print (f" Number of total traces   : {idx}  \n ")
                break
                
            else:
                
                self.gather_chn_hdrs(dm_i4)
                self.gather_chn_trc(dm_r4)
                
        self.trans_to_numarr()
        return self.output
        

    def write_su(self, 
                 filename,
                 seis, 
                 headers):
        
        self.file_open(filename)
        ns, nr = seis.shape
        
        for idx in range(nr):
            self.write_su_single(idx, 
                                 seis[:, idx], 
                                 headers)
        self.file_close()


    def write_su_single(self,
                        idx,
                        trc, 
                        headers):

        a_i4 = np.zeros((self.nhdr_i4), dtype = self.i4)
        a_i2 = np.zeros((self.nhdr_i2), dtype = self.i2)

        ns = trc.size
        a_i2[57] = ns

        for keyword, value in headers.items():
            if keyword == "tracl":  a_i4[ 0] = value[idx]
            if keyword == "tracr":  a_i4[ 1] = value[idx]
            if keyword == "fldr":   a_i4[ 2] = value[idx]
            if keyword == "tracf":  a_i4[ 3] = value[idx]
            if keyword == "ep":     a_i4[ 4] = value[idx]
            if keyword == "cdp":    a_i4[ 5] = value[idx]
            if keyword == "cdpt":   a_i4[ 6] = value[idx]
            if keyword == "offset": a_i4[ 9] = value[idx]
            if keyword == "swdep":  a_i4[15] = value[idx]
            if keyword == "gwdep":  a_i4[16] = value[idx]
            if keyword == "sx":     a_i4[18] = value[idx]
            if keyword == "sy":     a_i4[19] = value[idx]
            if keyword == "gx":     a_i4[20] = value[idx]
            if keyword == "gy":     a_i4[21] = value[idx]
            if keyword == "dt":     a_i2[58] = value[idx]

        self.f.seek(idx * (self.i4_size * a_i2[57] + self.hdrbyte), 0)
        self.f.write(a_i4.byteswap())
        self.f.seek(114 + idx * (self.i4_size * a_i2[57] + self.hdrbyte) ,0)
        self.f.write(a_i2[57:59].byteswap())
        self.f.seek(self.hdrbyte + idx * (self.r4_size * a_i2[57] + self.hdrbyte), 0)
        self.f.write(trc.byteswap())


    def flush_hdrs_arr(self):
        
        self.ns      = None
        self.dt      = None
        self.scalel  = None
        self.scalco  = None
        self.fldr_b  = 0
        self.tracl   = []
        self.tracr   = []
        self.fldr    = []
        self.tracf   = []
        self.ep      = []
        self.cdp     = []
        self.cdpt    = []
        self.offset  = []
        self.swdep   = []
        self.gwdep   = []
        self.sx      = []
        self.sy      = []
        self.gx      = []
        self.gy      = []
        self.cdpx    = []
        self.cdpy    = []
        self.trc     = []
        
    def gather_chn_trc(self,
                     arr):
        
        self.trc.append(arr)

    def gather_chn_hdrs(self,
                        arr):

        self.fldr_b = np.copy( arr[ 2] )
        
        self.tracl.append(     arr[ 0] )
        self.tracr.append(     arr[ 1] )
        self.fldr.append(      arr[ 2] )
        self.tracf.append(     arr[ 3] )
        self.ep.append(        arr[ 4] )
        self.cdp.append(       arr[ 5] )
        self.cdpt.append(      arr[ 6] )
        self.offset.append(    arr[ 9] )
        self.swdep.append(     arr[15] )
        self.gwdep.append(     arr[16] )
        self.sx.append(        arr[18] )
        self.sy.append(        arr[19] )
        self.gx.append(        arr[20] )
        self.gy.append(        arr[21] )
        self.cdpx.append(      arr[14] )
        self.cdpy.append(      arr[13] )
        
      
        
    def trans_to_numarr(self):

        self.tracl    = np.array( self.tracl )
        self.tracr    = np.array( self.tracr )
        self.fldr     = np.array( self.fldr )
        self.tracf    = np.array( self.tracf )
        self.ep       = np.array( self.ep )
        self.cdp      = np.array( self.cdp )
        self.cdpt     = np.array( self.cdpt )
        self.offset   = np.array( self.offset )
        self.swde     = np.array( self.swdep )
        self.gwdep    = np.array( self.gwdep )
        self.sx       = np.array( self.sx )
        self.sy       = np.array( self.sy )
        self.gx       = np.array( self.gx )
        self.gy       = np.array( self.gy )
        self.cdpx     = np.array( self.cdpx )
        self.cdpy     = np.array( self.cdpy )
        self.trc      = np.array( self.trc )

        self.output = {
            "tracl"  :  self.tracl,
            "tracr"  :  self.tracr,
            "fldr"   :  self.fldr,
            "tracf"  :  self.tracf,
            "ep"     :  self.ep,
            "cdp"    :  self.cdp,
            "cdpt"   :  self.cdpt,
            "offset" :  self.offset,
            "swdep"  :  self.swdep,
            "gwdep"  :  self.gwdep,
            "sx"     :  self.sx,
            "sy"     :  self.sy,
            "gx"     :  self.gx,
            "gy"     :  self.gy,
            "cdpx"   :  self.cdpx,
            "cdpy"   :  self.cdpy,
            "trace"  : self.trc
        }
        


            
    def file_open(self,
                  filename):
        self.f = open(filename,'wb')
        
    def file_close(self):
        self.f.close()
























