import numpy as np
import pandas as pd
import sys

outcomes_file, out_file = sys.argv[1:]

years = 5

# Measure by quarters
years = np.arange(0, years+0.25, 0.25)

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

data = {"Years": years}
for var, label in labels.items():
    data[label] = []
    for x in years:
        data[label].append(100 * (outcomes["{}_DAYS".format(var)] <= (x*365)).sum() / n)

pd.DataFrame(data).to_csv(out_file, index=False, float_format="%.2f")
