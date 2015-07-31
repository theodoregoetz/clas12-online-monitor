import numpy as np

from clas12monitor.data import EvioReader

def dc_wire_occupancy(evio_source):
    dcocc = np.zeros((6,6,6,112))
    for evt in EvioReader(evio_source):
        dchits = evt.bank('HitBasedTrkg::HBHits')
        if dchits is not None:
            hit_data = np.vstack([
                dchits.sector    ,
                dchits.superlayer,
                dchits.layer     ,
                dchits.wire      ]).T - 1
            for wire_id in hit_data:
                dcocc[tuple(wire_id)] += 1
    return dcocc
