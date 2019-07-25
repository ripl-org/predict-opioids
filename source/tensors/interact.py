import pickle
import sys

tensorfile   = sys.argv[1]
tensorfiles  = sys.argv[2:-1]
outfile      = sys.argv[-1]

labels = {}
keep = {}
fill_values = {}

with open(tensorfile, "rb") as f:
    tensor1 = pickle.load(f)

for tensorfile in tensorfiles:

    print("Adding tensor file", tensorfile)

    with open(tensorfile, "rb") as f:
        tensor2 = pickle.load(f)

    for var1 in tensor1.values:
        for var2 in tensor2.values:

            feature = "{}_X_{}".format(var1, var2)
            values = tensor1.values[var1].merge(tensor2.values[var2], on=["SUBSET", "SAMPLE", "TIMESTEP"], how="inner")
            train = values.SUBSET == 0

            if (len(values) > 0) & train.any():
                values["VALUE"] = values.VALUE_x * values.VALUE_y
                if len(values.loc[train, "VALUE"].unique()) <= 1:
                    print("dropping interaction with zero variance:", feature)
                    continue
                labels[feature] = "'{}' X '{}'".format(tensor1.labels[var1], tensor2.labels[var2])
                keep[feature] = values[["SUBSET", "SAMPLE", "TIMESTEP", "VALUE"]]
                fill_values[feature] = tensor1.fill_values[var1] * tensor2.fill_values[var2]

            else:
                print("dropping interaction missing from training data:", feature)

with open(outfile, "wb") as f:
    pickle.dump({"labels": labels, "values": keep, "fill_values": fill_values}, f)

# vim: expandtab sw=4 ts=4
