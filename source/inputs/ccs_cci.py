import pandas as pd
import os, sys, time
from riipl import Connection

ccs_file, cci_file, ccs_table, cci_table = sys.argv[1:]

ccs = pd.read_csv(ccs_file,
                  usecols=[0, 1],
                  quotechar="'",
                  skiprows=3,
                  names=["DIAG_CDE", "DISEASE"])
ccs["DIAG_CDE"] = ccs.DIAG_CDE.str.strip()

cci = pd.read_csv(cci_file,
                  usecols=[0, 2],
                  quotechar="'",
                  skiprows=2,
                  names=["DIAG_CDE", "CHRONIC"])
cci = cci[cci.CHRONIC == 1]
cci["DIAG_CDE"] = cci.DIAG_CDE.str.strip()

with Connection() as cxn:
    cxn.read_dataframe(ccs, ccs_table)
    cxn.save_table(ccs_table, "DIAG_CDE", checksum=False)
    cxn.read_dataframe(cci, cci_table)
    cxn.save_table(cci_table, "DIAG_CDE", checksum=False)

# vim: expandtab sw=4 ts=4
