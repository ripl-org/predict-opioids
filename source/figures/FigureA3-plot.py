import matplotlib.pyplot as plt
import pandas as pd
import sys
from matplotlib.ticker import StrMethodFormatter

csv_file, out_file = sys.argv[1:]

data = pd.read_csv(csv_file, index_col="Years")

data.plot(style=".-")
plt.xlabel("Years from initial opioid prescription")
plt.ylabel("Percent of adverse outcomes")
plt.xticks(data.index)
plt.gca().yaxis.set_major_formatter(StrMethodFormatter("{x:.0f}%"))
plt.tight_layout()
plt.savefig(out_file)
