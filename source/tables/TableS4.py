import pandas as pd
import os
import sys
from sklearn.metrics import roc_auc_score

seed        = int(sys.argv[1])
n_bootstrap = int(sys.argv[2])
outcomes    = sys.argv[3].split(",")
tensors     = sys.argv[4].split(",")
infiles     = sys.argv[5:-1]
outfile     = sys.argv[-1]

def bootstrap(data, N, statistic, seed):
    replicates = sorted(statistic(data.sample(n=len(data),
                                              replace=True,
                                              random_state=seed+i))
                        for i in range(N))
    ci_lower = replicates[int(0.025 * N)]
    ci_upper = replicates[int(0.975 * N)]
    return statistic(data), ci_lower, ci_upper

cells = []
for y_pred_file in infiles:
    auc, ci_lower, ci_upper = bootstrap(pd.read_csv(y_pred_file),
                                        n_bootstrap,
                                        lambda df: roc_auc_score(df.y_test, df.y_pred),
                                        seed)
    cells.append("{:.3f} ({:.3f}-{:.3f})".format(auc, ci_lower, ci_upper))

N = len(outcomes)
with open(outfile, "w") as f:
    print("\t".join(["Agencies/Programs"] + outcomes), file=f)
    for i, tensor in enumerate(tensors):
        print("\t".join([tensor] + cells[i*N:(i+1)*N]), file=f)

# vim: syntax=python expandtab sw=4 ts=4
