import pandas as pd
import sys

manifest_file = sys.argv[1]
coef_files    = sys.argv[2:-2]
freq_file     = sys.argv[-2]
selected_file = sys.argv[-1]

# Load manifest
manifest = pd.read_csv(manifest_file, sep="\t", names=["var", "desc"], index_col="var")

# Load coefficients and calculate non-zero frequency
var = pd.read_csv(coef_files[0], index_col="var")
var["freq"] = (var.coef != 0).astype(int)
for coef_file in coef_files[1:]:
    var["freq"] += (pd.read_csv(coef_file, index_col="var").coef != 0).astype(int)
var["freq"] /= len(coef_files)

var.drop("intercept", inplace=True)
del var["coef"]

var.join(manifest).sort_values("freq", ascending=False).to_csv(freq_file)

# Select variables with >= 0.9 frequency
selected = set(var[var.freq >= 0.9].index)

# Make sure base variables are present for any selected interaction
for name in list(selected):
    if "_X_" in name:
        var1, _, var2 = name.partition("_X_")
        selected.add(var1)
        selected.add(var2)

with open(selected_file, "w") as f:
    print("var", file=f)
    print("\n".join(sorted(selected)), file=f)

# vim: expandtab sw=4 ts=4
