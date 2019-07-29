import cx_Oracle
import pandas as pd
import os
import sys
from riipl import *

def lookback(population, months, table):
    """
    Create a table with the lookback months before each index month.
    """
    months = int(months)

    sql = """
          SELECT riipl_id,
                 TO_CHAR(initial_dt, 'YYYYMM') AS initial_mo
            FROM {population}
        ORDER BY riipl_id
          """.format(**locals())
    with cx_Oracle.connect("/") as cxn:
        population = pd.read_sql(sql, cxn, index_col="RIIPL_ID")

    # Construct columns
    riipl_ids = []
    timestep = []
    yrmo = []
    yyq = []

    for riipl_id, initial_mo in population.itertuples():
        year = int(initial_mo[:4])
        month = int(initial_mo[4:])
        for t in range(months):
            month = month - 1
            if month == 0:
                year = year - 1
                month = 12
            riipl_ids.append(riipl_id)
            timestep.append(months - t - 1)
            yrmo.append("{}{:02d}".format(year, month))
            q = int((month - 1) / 3) + 1
            yyq.append("{}{}".format(str(year)[2:], q))

    df = pd.DataFrame({"riipl_id": riipl_ids, "timestep": timestep, "yrmo": yrmo, "yyq": yyq})

    with Connection() as cxn:
        cxn.clear_tables(table)
        cxn.read_dataframe(df, table)


if __name__ == "__main__": lookback(*sys.argv[1:])

# vim: expandtab sw=4 ts=4
