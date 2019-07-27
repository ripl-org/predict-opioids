import pandas as pd
import os, sys, time
from riipl import Connection

csv_file, pk, table = sys.argv[1:]

df = pd.read_csv(csv_file)

with Connection() as cxn:
    cxn.read_dataframe(df, table)
    cxn.save_table(table, pk.split(","), checksum=False)

# vim: expandtab sw=4 ts=4
