import pandas as pd
import sys
from riipl import Connection

panel, mega, outfile = sys.argv[1:]

sql = """
      SELECT p.riipl_id,
             m.age,
             m.race,
             m.sex,
             m.bmi
        FROM {panel} p
   LEFT JOIN {mega} m
          ON p.riipl_id = m.riipl_id
       WHERE m.month = '200701'
      """

with Conection as cxn:
    pd.read_sql(sql, cxn._connection, index_col="RIIPL_ID").to_csv(outfile)

# vim: expandtab sw=4 ts=4
