import pandas as pd
import sys
from functools import reduce
from riipl import SaveFeatures

population, manifest_file, feature1_file = sys.argv[1:4]
feature_files = sys.argv[4:-2]
out, out_manifest = sys.argv[-2:]

index = ["RIIPL_ID"]

# Load features

features1 = pd.read_csv(feature1_file, index_col=index)
set1 = features1.columns

features2 = reduce(lambda x,y: x.join(y), [pd.read_csv(feature_file, index_col=index)
                                           for feature_file in feature_files])
set2 = features2.columns

# Load manifest

manifest = pd.read_csv(manifest_file, sep="\t", names=["var", "desc"], index_col="var")["desc"].to_dict()

# Create pairwise interactions

interactions = pd.DataFrame(index=features1.index)
labels = {}

for var1 in set1:
    for var2 in set2:
        varx = "{}_X_{}".format(var1, var2)
        interactions[varx] = features1[var1] * features2[var2]
        labels[varx] = "'{}' X '{}'".format(manifest[var1], manifest[var2])

SaveFeatures(interactions, out, out_manifest, population, labels)

# vim: expandtab sw=4 ts=4
