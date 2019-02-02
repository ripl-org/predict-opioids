import h5py
import numpy as np
import pandas as pd
import sys

infile  = sys.argv[1]
columns = list(map(int, sys.argv[2].split(",")))
dtypes  = sys.argv[3].split(",")

f = h5py.File(sys.argv[4], "w")

for i, dtype in zip(columns, dtypes):
    d = pd.read_csv(infile, usecols=[i], sep="|")
    print(d.head())
    print(d.dtypes)
    name = d.columns[0]
    f.create_dataset(name, (len(d),), data=np.array(d[name], dtype=dtype), compression="lzf")

f.close()
