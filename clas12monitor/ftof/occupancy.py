import numpy as np

from clas12monitor.data import EvioReader

def ftof_wire_occupancy(evio_source):
    ftofocc = np.zeros((6,60))
    for evt in EvioReader(evio_source):
        ftofhits = evt['FTOFRec::rawhits']
        if ftofhits is not None:
            hit_data = np.vstack([
                ftofhits.sector    ,
                ftofhits.panel_id,]).T - 1
            for panel_id in hit_data:
                ftofocc[tuple(panel_id)] += 1
    return ftofocc

if __name__ == "__main__" :
    import sys
    ftof_wire_occupancy(sys.argv[1])
