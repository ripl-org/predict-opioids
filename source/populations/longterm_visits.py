import pandas as pd
import sys
from riipl import Connection

panel, claims, outfile = sys.argv[1:]

sql = """
      SELECT DISTINCT
             p.riipl_id,
             TO_CHAR(c.claim_dt, 'YYYYMMDD') AS claim_dt,
             1 AS visits
        FROM {panel} p
   LEFT JOIN {claims} c
          ON p.riipl_id = c.riipl_id
       WHERE c.claim_dt BETWEEN '01-Jan-07' AND '31-Dec-11'
      """.format(**globals())

with Connection() as cxn:
    pd.read_sql(sql, cxn._connection, index_col="RIIPL_ID").to_csv(outfile)

# vim: expandtab sw=4 ts=4
