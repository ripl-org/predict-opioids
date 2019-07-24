import pandas as pd
import sys
from functools import reduce
from riipl import SaveFeatures

population, set1, set2, manifest_file = sys.argv[1:5]
feature_files = sys.argv[5:-2]
out, out_manifest = sys.argv[-2:]

set1 = set1.split(",")
set2 = set2.split(",")

index = ["RIIPL_ID"]

# Load features

features = reduce(lambda x,y: x.join(y), [pd.read_csv(feature_file, index_col=index)
                                          for feature_file in feature_files])

# Load manifest

manifest = pd.read_csv(manifest_file, sep="\t", names=["var", "desc"], index_col="var")["desc"].to_dict()

# Create pairwise interactions

interactions = pd.DataFrame(index=features.index)
labels = {}

for var1 in set1:
    for var2 in set2:
        varx = "{}_X_{}".format(var1, var2)
        interactions[varx] = features[var1] * features[var2]
        labels[varx] = "'{}' X '{}'".format(manifest[var1], manifest[var2])

SaveFeatures(interactions, out, out_manifest, population, labels)

# vim: expandtab sw=4 ts=4
