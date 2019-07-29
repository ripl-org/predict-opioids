import pandas as pd
import sys
from riipl import Connection

panel, proc_cde, opioid_proc_cde, outfile = sys.argv[1:]

sql = """
      SELECT p.riipl_id,
             MIN(pc.claim_dt) AS initial_injection_dt
        FROM {panel} p
   LEFT JOIN {proc_cde} pc
          ON p.riipl_id = pc.riipl_id
  INNER JOIN {opioid_proc_cde} opc
          ON pc.proc_cde = opc.proc_cde
       WHERE pc.claim_dt BETWEEN '01-Jan-07' AND '31-Dec-11'
    GROUP BY p.riipl_id
      """.format(**globals())

with Connection() as cxn:
    pd.read_sql(sql, cxn._connection, index_col="RIIPL_ID").to_csv(outfile)

# vim: expandtab sw=4 ts=4
