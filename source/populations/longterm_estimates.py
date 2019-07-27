import sys
from riipl import Connection

panel, out_file = sys.argv[1:]

with Connection() as cxn:
    panel = pd.read_sql("SELECT * FROM {}".format(panel), cxn._connection)

with open(out_file, "w") as f:
    print("panel size:", len(panel), file=f)
    print("median months enrolled:", panel.MONTHS.median(), file=f)

# vim: syntax=python expandtab sw=4 ts=4
