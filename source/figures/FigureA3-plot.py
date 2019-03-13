import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import sys

csv_file, out_file = sys.argv[1:]

data = pd.read_csv(csv_file)

data = pd.melt(data, id_vars=["Years"], value_name="Percent of adverse outcomes", var_name="Outcome type")\
         .rename(columns={"Years": "Years from initial opioid prescription"})
print(data.head())

sns.lineplot(x="Years from initial opioid prescription",
             y="Percent of adverse outcomes",
             hue="Outcome type",
             data=data, markers=True, estimator=None)
plt.tight_layout()
plt.savefig(out_file)
