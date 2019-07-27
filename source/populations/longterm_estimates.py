import pandas as pd
import sys
from riipl import Connection

panel, outcomes_file, rx_file, out_file = sys.argv[1:]

MAX_DT = 99999999

with Connection() as cxn:
    panel = pd.read_sql("SELECT * FROM {}".format(panel), cxn._connection)

panel = panel.merge(pd.read_csv(outcomes_file, usecols=["RIIPL_ID", "OUTCOME_ANY"]),
                    how="left",
                    on="RIIPL_ID")

panel = panel.merge(pd.read_csv(rx_file, usecols=["RIIPL_ID", "INITIAL_RX_DT"]),
                    how="left",
                    on="RIIPL_ID")

with open(out_file, "w") as f:

    print("panel size:", len(panel), file=f)
    print("months enrolled:", file=f)
    print("----------------", file=f)
    print(panel.MONTHS.describe(), file=f)
    print("----------------", file=f)

    adverse = panel.OUTCOME_ANY.fillna(MAX_DT) < MAX_DT

    n_adverse = adverse.sum()
    print("adverse outcomes: {} ({:.1f}%)".format(n_adverse, 100.0 * n_adverse / len(panel)), file=f)

    n_without_rx = panel[adverse].INITIAL_RX_DT.isnull().sum()
    print("adverse outcomes without rx: {} ({:.1f}%)".format(n_without_rx, 100.0 * n_without_rx / n_adverse), file=f)

    rx = panel.INITIAL_RX_DT.notnull()

    n_rx = rx.sum()
    print("rx: {} ({:.1f}%)".format(n_rx, 100.0 * n_rx / len(panel)), file=f)

    n_without_adverse = (panel[rx].OUTCOME_ANY.fillna(MAX_DT) == MAX_DT).sum()
    print("rx without adverse outcomes: {} ({:.1f}%)".format(n_without_adverse, 100.0 * n_without_adverse / n_rx), file=f)


# vim: syntax=python expandtab sw=4 ts=4
