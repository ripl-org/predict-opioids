import csv
import numpy as np
import pandas as pd
import pickle
import sys
from collections import namedtuple
from riipl import PopulationSizes

nsteps       = int(sys.argv[1])
population   = sys.argv[2]
tensorfiles  = sys.argv[3:-2]
outfile      = sys.argv[-2]
manifestfile = sys.argv[-1]

index = ["RIIPL_ID"]
nsamples = PopulationSizes(population, index)

# Load and combine tensors

manifest = []
fill_values = []
tensors = [[], [], []]
nfeatures = 0

for tensorfile in tensorfiles:
    print("Adding tensor file", tensorfile)
    with open(tensorfile, "rb") as f:
        tensor = pickle.load(f)
    for feature, values in tensor["values"].items():
        values["FEATURE"] = nfeatures
        manifest.append((nfeatures, feature, tensor["labels"][feature]))
        fill_values.append(tensor["fill_values"][feature])
        for i in (0, 1, 2):
            tensors[i].append(values.loc[values.SUBSET == i, ["SAMPLE", "TIMESTEP", "FEATURE", "VALUE"]])
        nfeatures += 1

# Convert to final sparse representation
SparseTensor = namedtuple("SparseTensor", "nsamples nsteps nfeatures index values fill_values")
fill_values = np.array(fill_values)
results = []
for i in (0, 1, 2):
    tensor = pd.concat(tensors[i], ignore_index=True)
    # Flatten 2D (step, feature) coordinates to 1D index
    tensor["INDEX"] = tensor.TIMESTEP * nfeatures + tensor.FEATURE
    samples = tensor.groupby("SAMPLE")
    index = [None] * nsamples[i]
    values = [None] * nsamples[i]
    for j in samples.groups:
        index[j] = samples["INDEX"].get_group(j).values
        values[j] = samples["VALUE"].get_group(j).values
    results.append(SparseTensor(nsamples[i], nsteps, nfeatures, index, values, fill_values))

with open(outfile, "wb") as f:
    pickle.dump(results, f)

# Manifest
with open(manifestfile, "w") as f:
    writer = csv.writer(f)
    writer.writerow(("INDEX", "FEATURE", "DESCRIPTION"))
    writer.writerows(manifest)

# vim: expandtab sw=4 ts=4
