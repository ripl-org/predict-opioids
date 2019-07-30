import pandas as pd
import sys
from riipl import Connection

panel, claims, outfile = sys.argv[1:]

sql = """
      SELECT p.riipl_id,
             COUNT(DISTINCT c.claim_dt) / p.months AS visits
        FROM {panel} p
   LEFT JOIN {claims} c
          ON p.riipl_id = c.riipl_id
    GROUP BY p.riipl_id, p.months
      """.format(**globals())

with Connection() as cxn:
    pd.read_sql(sql, cxn._connection, index_col="RIIPL_ID").to_csv(outfile)

# vim: expandtab sw=4 ts=4
