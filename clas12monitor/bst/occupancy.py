import numpy as np

from clas12monitor.data import EvioReader

def bst_occupancy(evio_source):
    bstocc = np.zeros((4,24,2,256))
    for evt in EvioReader(evio_source):

        bsthits = evt['BSTRec::Hits']
        if bsthits is not None:

            region = bsthits.layer // 2
            layer = bsthits.layer % 2

            hit_data = np.vstack([
                region,
                bsthits.sector,
                layer,
                bsthits.strip]).T - 1

            for hit_id in hit_data:
                bstocc[tuple(hit_id)] += 1

    return bstocc

def bst_occupancy2(evio_source):
    bstocc = [
        np.zeros((10*2,256)),
        np.zeros((14*2,256)),
        np.zeros((18*2,256)),
        np.zeros((24*2,256)) ]
    for evt in EvioReader(evio_source):

        bsthits = evt['BSTRec::Hits']
        if bsthits is not None:

            region = bsthits.layer // 2
            layer = bsthits.layer % 2

            for reg in range(3):
                sel = (region == reg)

                hit_data = np.vstack([
                    bsthits.sector[sel] + layer[sel],
                    bsthits.strip[sel]]).T - 1

                for hit_id in hit_data:
                    bstocc[reg][tuple(hit_id)] += 1

    return bstocc

if __name__ == "__main__" :
    # run with this command:
    # python3 -m clas12monitor.bst.occupancy exim1690.0001.recon
    import sys
    bstocc = bst_occupancy2(sys.argv[1])
    print(bstocc)


