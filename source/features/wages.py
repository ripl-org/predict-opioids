import cx_Oracle
import pandas as pd
import os, sys, time
from riipl.model import SaveFeatures

population, dlt_wage, dim_date, outfile, manifest = sys.argv[1:]

def main():
    sql = """
          SELECT                          pop.riipl_id,
                 COUNT(DISTINCT w.ern) AS wages_employers,
                 SUM(w.hrs_worked)     AS wages_hours,
                 STDDEV(w.wages)       AS wages_var,
                 AVG(w.wages)          AS wages_avg,
                 SUM(w.wages)          AS wages_sum
            FROM {population} pop
       LEFT JOIN (
                  SELECT riipl_id,
                         dd.date_dt,
                         dw.wages,
                         dw.ern,
                         dw.hrs_worked
                    FROM {dlt_wage} dw
                    JOIN {dim_date} dd
                      ON dw.yyq = dd.yyq AND
                         dd.date_dt = dd.qtr_st_dt
                 ) w
              ON pop.riipl_id = w.riipl_id            AND
                 w.date_dt < pop.initial_rx_dt        AND
                 pop.initial_rx_dt - w.date_dt <= 365
        GROUP BY pop.riipl_id
        ORDER BY pop.riipl_id
          """.format(**globals())

    with cx_Oracle.connect("/") as cxn:
        features = pd.read_sql(sql, cxn, index_col="RIIPL_ID")

    labels = {
        "WAGES_EMPLOYERS": "Number of distinct employers in the 4 quarters before prescription",
        "WAGES_HOURS": "Total hours worked (for hourly wages) in the 4 quarters before prescription",
        "WAGES_VAR": "Standard deviation of quarterly wage from each job worked in 4 quarters before prescription",
        "WAGES_AVG": "Average quarterly wage across jobs worked in 4 quarters before prescription",
        "WAGES_SUM": "Sum of wages across jobs worked in 4 quarters before prescription"
    }

    SaveFeatures(features, outfile, manifest, population, labels)


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
