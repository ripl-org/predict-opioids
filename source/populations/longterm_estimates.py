import numpy as np
import pandas as pd
import sys
from riipl import Connection

panel, outcomes_file, rx_file, proc_file, demo_file, out_file, csv_file = sys.argv[1:]

MAX_DT = 99999999

with Connection() as cxn:
    panel = pd.read_sql("SELECT * FROM {}".format(panel), cxn._connection)

panel = panel.merge(pd.read_csv(outcomes_file),
                    how="left",
                    on="RIIPL_ID")

panel = panel.merge(pd.read_csv(rx_file, usecols=["RIIPL_ID", "INITIAL_RX_DT"]),
                    how="left",
                    on="RIIPL_ID")

panel = panel.merge(pd.read_csv(proc_file, usecols=["RIIPL_ID", "INITIAL_INJECTION_DT"]),
                    how="left",
                    on="RIIPL_ID")

panel = panel.merge(pd.read_csv(demo_file),
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

with open(csv_file, "w") as f:

    proc = panel.INITIAL_INJECTION_DT.notnull()
    both = rx & proc
    none = (~rx) & (~proc)

    panel["INITIAL_DT"] = panel[["INITIAL_RX_DT", "INITIAL_INJECTION_DT"]].min(axis=1)

    perc = lambda val, n: "{} ({:.1f}%)".format(val, 100.0*val/n)

    subsets = [rx, proc, both, none]

    outcomes = {
        "OUTCOME_DEPENDENCE": "Dependence",
        "OUTCOME_ABUSE": "Abuse",
        "OUTCOME_POISONING_RX": "Rx Poisoning",
        "OUTCOME_POISONING_HEROIN": "Heroin Poisoning",
        "OUTCOME_PROCEDURE": "Treatment",
        "OUTCOME_ANY": "Any Outcome"
    }

    print("", "All", "Opioid Rx", "Opioid Injection", "Both", "Neither", sep=",", file=f)
    print("N", len(panel), *[s.sum() for s in subsets], sep=",", file=f)

    for outcome, desc in outcomes.items():
        print(desc,
              perc((panel[outcome] < MAX_DT).sum(), len(panel)),
              perc((panel.loc[rx, outcome] < panel.loc[rx, "INITIAL_RX_DT"]).sum(), rx.sum()),
              perc((panel.loc[proc, outcome] < panel.loc[proc, "INITIAL_INJECTION_DT"]).sum(), proc.sum()),
              perc((panel.loc[both, outcome] < panel.loc[both, "INITIAL_DT"]).sum(), both.sum()),
              perc((panel.loc[none, outcome] < MAX_DT).sum(), none.sum()),
              sep=",",
              file=f)

    for q in [0.25, 0.5, 0.75]:
        print("Age ({:.0f}th Percentile)".format(100*q),
              "{:.1f}".format(panel["AGE"].quantile(q)),
              *["{:.1f}".format(panel.loc[s, "AGE"].quantile(q)) for s in subsets],
              sep=",",
              file=f)

    for race in ["White", "Black", "Hispanic"]:
        print(race,
              perc((panel["RACE"] == race).sum(), len(panel)),
              *[perc((panel.loc[s, "RACE"] == race).sum(), s.sum()) for s in subsets],
              sep=",",
              file=f)

    print("BMI (Median)",
          "{:.1f}".format(panel["BMI"].quantile(0.5)),
          *["{:.1f}".format(panel.loc[s, "BMI"].quantile(0.5)) for s in subsets],
          sep=",",
          file=f)


# vim: syntax=python expandtab sw=4 ts=4
