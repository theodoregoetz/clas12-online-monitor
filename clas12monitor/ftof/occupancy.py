import numpy as np

from clas12monitor.data import EvioReader

def ftof_occupancy(evio_source):
    ftofocc = np.zeros((6,90))
    for evt in EvioReader(evio_source):
        ftofhits = evt['FTOFRec::ftofhits']
        npaddles = [0,23,23+62]
        if ftofhits is not None:
            paddle_ids = np.array([pad + npaddles[pan] for pan,pad in zip(ftofhits.panel_id,ftofhits.paddle_id)])
            hit_data = np.vstack([ftofhits.sector, paddle_ids]).T - 1
            for panel_id in hit_data:
                ftofocc[tuple(panel_id)] += 1
    return ftofocc

if __name__ == "__main__" :
    import sys
    ftofocc = ftof_occupancy(sys.argv[1])
    print(ftofocc)

