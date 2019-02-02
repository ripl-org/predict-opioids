import cx_Oracle
import pandas as pd
import os, sys, time
from riipl import SaveTensor

population, lookback, dlt_wage, out = sys.argv[1:]

def main():
    sql = """
          SELECT pop.riipl_id,
                 lb.timestep,
                 COUNT(DISTINCT dw.ern) AS wage_employers,
                 SUM(dw.hrs_worked)     AS wage_hours,
                 SUM(dw.wages)          AS wages
            FROM {population} pop
       LEFT JOIN {lookback} lb
              ON pop.riipl_id = lb.riipl_id
      INNER JOIN {dlt_wage} dw
              ON lb.riipl_id = dw.riipl_id AND
                 lb.yyq = dw.yyq
        GROUP BY pop.riipl_id, lb.timestep
          """.format(**globals())

    with cx_Oracle.connect("/") as cxn:
        values = pd.read_sql(sql, cxn)

    labels = {
        "WAGE_EMPLOYERS" : "number of distinct employers",
        "WAGE_HOURS"     : "total quarterly hours worked (for hourly wages)",
        "WAGES"          : "total quarterly wages"
    }

    tensor = {}
    for feature in labels:
        tensor[feature] = values[["RIIPL_ID", "TIMESTEP", feature]].fillna(0).rename(columns={feature: "VALUE"})

    fill_values = dict((feature, "mean") for feature in tensor)

    SaveTensor(tensor, labels, fill_values, (population, "RIIPL_ID"), out)


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
