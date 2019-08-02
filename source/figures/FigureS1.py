import numpy as np
import pandas as pd
import sys

outcomes_file, out_file = sys.argv[1:]

years = np.arange(0, 6)

labels = {
    "OUTCOME_PROCEDURE": "Treatment",
    "OUTCOME_POISONING_HEROIN": "Heroin poisoning",
    "OUTCOME_POISONING_RX": "Prescription-opioid poisoning",
    "OUTCOME_ABUSE": "Opioid abuse",
    "OUTCOME_DEPENDENCE": "Opioid dependence",
    "OUTCOME_ANY": "Any adverse outcome"
}

outcomes = pd.read_csv(outcomes_file, index_col="RIIPL_ID")
n = len(outcomes)

with open(out_file, "w") as f:
    print("Years", "Outcome", "Fraction", sep=",", file=f)
    for yr in years:
        for var, label in labels.items():
            print(yr, label, (outcomes["{}_DAYS".format(var)] <= (yr*365)).sum() / n, sep=",", file=f)

