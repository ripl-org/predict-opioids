import numpy as np
import pandas as pd
import sys
import h5py
from riipl.connection import Connection
from riipl.test import *


def _reformat_ndc(ndc):
    """
    Converts unpadded XXXXX-XXXX to 9-digit integer.
    """
    upper, _, lower = ndc.partition("-")
    return int(upper + "{:04d}".format(int(lower)))


def read_h5py(filename, usecols=None, index_col=None):
    f = h5py.File(filename, "r")
    datasets = list(f.keys())
    if usecols is not None:
        for col in usecols: assert col in datasets
        datasets = usecols
    n = len(f[datasets[0]])
    for d in datasets[1:]:
         assert n == len(f[d])
    data = {}
    for d in datasets:
        data[d] = np.array(f[d])
    df = pd.DataFrame.from_dict(data)
    if index_col is not None:
        return df.set_index(index_col)
    else:
        return df


def LoadRX(rxfile, start, end):
    """
    Load all Medicaid prescriptions in the time period.
    """
    rx = read_h5py(rxfile)

    # Select time period
    n = len(rx)
    rx = rx[(rx.DISPENSED_DT >= int(start)) & (rx.DISPENSED_DT < int(end))]
    print(len(rx), "of", n, "prescriptions in time period")

    # Zero RIIPL_IDs should be <1% (see OPIOID-31)
    TestValue(rx.RIIPL_ID, 0, 0.01)

    # No NDCs should be missing
    TestMissing(rx.NDC9_CODE, 0)

    # Zero NDCs should be <5%
    TestValue(rx.NDC9_CODE, 0, 0.05)

    # All 9s NDCs should be <1%
    TestValue(rx.NDC9_CODE, 999999999, 0.01)

    return rx


def ClassifyRX(rx, ndcfile):
    """
    Load classification of opioid drugs and join to prescriptions.
    """
    #ndc = pd.read_csv(ndcfile).rename(columns={"ndc": "NDC9_CODE"})
    ndc = pd.read_csv(ndcfile, sep="\t", usecols=["PRODUCTNDC"])
    ndc = pd.DataFrame(data={"NDC9_CODE": ndc["PRODUCTNDC"].apply(_reformat_ndc).unique()})
    ndc["opioid"] = 1
    ndc["recovery"] = 1

    rx_class = rx.merge(ndc, how="left", on="NDC9_CODE")#, validate="one_to_one")

    # Test percent missing
    TestMissing(rx_class.opioid, 1)

    return rx_class


if __name__ == "__main__":

    rxfile, start, end, ndcfile = sys.argv[1:5]
    ClassifyRX(LoadRX(rxfile, start, end), ndcfile)

# vim: expandtab sw=4 ts=4
