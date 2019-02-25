import pandas as pd
import os
import sys

accuracy_files = sys.argv[1:4]
out_file       = sys.argv[4]

accuracy = pd.read_csv(accuracy_files[0], index_col="decile").rename(columns={"outcomes": "BOLASSO Logit"})
accuracy["BOLASSO Ensemble"] = pd.read_csv(accuracy_files[1], index_col="decile")["outcomes"]
accuracy["Neural Network"] = pd.read_csv(accuracy_files[2], index_col="decile")["outcomes"]

accuracy.to_csv(out_file)

# vim: syntax=python expandtab sw=4 ts=4
