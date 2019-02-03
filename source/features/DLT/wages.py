import cx_Oracle
import pandas as pd
import os, sys, time
from riipl import CachePopulation, SaveFeatures

population, lookback, dlt_wage, out, manifest = sys.argv[1:]

def main():
    """
    Summary of income and employers from DLT wages
    """

    index = ["RIIPL_ID"]
    features = CachePopulation(population, index).set_index(index)

    sql = """
          SELECT pop.riipl_id,
                 AVG(dw.wages)     AS wages_avg,
                 AVG(dw.employers) AS wages_avg_employers,
                 AVG(dw.hours)     AS wages_avg_hours,
                 STDDEV(dw.wages)  AS wages_var
            FROM {population} pop
       LEFT JOIN (
                  SELECT DISTINCT
                         riipl_id,
                         yyq
                    FROM {lookback}
                 ) lb
              ON pop.riipl_id = lb.riipl_id
      INNER JOIN (
                  SELECT riipl_id,
                         yyq,
                         SUM(wages)          AS wages,
                         SUM(hrs_worked)     AS hours,
                         COUNT(DISTINCT ern) AS employers
                    FROM {dlt_wage}
                GROUP BY riipl_id, yyq
                 ) dw
              ON pop.riipl_id = dw.riipl_id AND
                 lb.yyq = dw.yyq
        GROUP BY pop.riipl_id
          """.format(**globals())

    with cx_Oracle.connect("/") as cxn:
        features = features.join(pd.read_sql(sql, cxn).set_index(index))

    features = features.fillna(0)

    labels = {
        "WAGES_AVG": "average quarterly wage across jobs worked in 4 quarters before index date",
        "WAGES_AVG_EMPLOYERS": "average quarterly number of employers in the 4 quarters before index date",
        "WAGES_AVG_HOURS": "average quarterly hours worked (for hourly wages) in the 4 quarters before index date",
        "WAGES_VAR": "standard deviation of quarterly wage from each job worked in 4 quarters before index date"
    }

    SaveFeatures(features, out, manifest, population, labels)


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
