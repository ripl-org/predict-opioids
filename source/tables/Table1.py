import pandas as pd
import os
import sys
from sklearn.metrics import roc_auc_score

seed        = int(sys.argv[1])
n_bootstrap = int(sys.argv[2])
infiles     = sys.argv[3:-1]
outfile     = sys.argv[-1]

out = []

def bootstrap(data, N, statistic, seed):
    replicates = sorted(statistic(data.sample(n=len(data),
                                              replace=True,
                                              random_state=seed+i))
                        for i in range(N))
    ci_lower = replicates[int(0.025 * N)]
    ci_upper = replicates[int(0.975 * N)]
    return statistic(data), ci_lower, ci_upper

for y_pred_file in infiles:
    auc, ci_lower, ci_upper = bootstrap(pd.read_csv(y_pred_file),
                                        n_bootstrap,
                                        lambda df: roc_auc_score(df.y_test, df.y_pred),
                                        seed)
    out.append((os.path.basename(y_pred_file).split(".")[0],
                "{:.3f}".format(auc),
                "({:.3f}-{:.3f})".format(ci_lower, ci_upper)))

with open(outfile, "w") as f:
    print("\t".join(("Model", "AUC", "95% C.I.")), file=f)
    for row in out:
        print("\t".join(row), file=f)

# vim: syntax=python expandtab sw=4 ts=4
