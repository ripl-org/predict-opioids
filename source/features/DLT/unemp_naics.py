import numpy as np
import pandas as pd
import os, sys, time
from riipl import Connection, SaveFeatures

population, lookback, dlt_wage, unemp_file, out, manifest = sys.argv[1:]

def main():
    """
    Nationwide unemployment rate by NAICS code at a yearly level from Bureau of Labor and Statistics
    """
    index = ["RIIPL_ID"]

    unemp = pd.read_csv(unemp_file)
    unemp["NAICS"] = unemp.NAICS.astype(str)

    # Calculate average unemployment by year
    unemp_avg = unemp.groupby("YR").mean().reset_index()
    print(unemp_avg)

    # Lookup all wage records in the lookback period, and order by
    # wages, to select the NAICS for the highest wage.
    sql = """
          SELECT DISTINCT
                 pop.riipl_id,
                 TO_CHAR(pop.initial_dt, 'YYYY') AS yr,
                 dw.wages,
                 SUBSTR(dw.naics4, 1, 2) AS naics
            FROM {population} pop
       LEFT JOIN {lookback} lb
              ON pop.riipl_id = lb.riipl_id
       LEFT JOIN {dlt_wage} dw
              ON pop.riipl_id = dw.riipl_id AND
                 lb.yyq = dw.yyq
        ORDER BY pop.riipl_id, dw.wages
           """.format(**globals())
 
    with Connection() as cxn:
        features = pd.read_sql(sql, cxn._connection).drop_duplicates(index, keep="last").set_index(index)

    # Use the previous year for joining the unemployment rate
    features["YR"] = features.YR.astype(int) - 1

    # Join NAICS unemployment, using avg unemployment when no NAICS is available
    naics = features.merge(unemp, how="left", on=["YR", "NAICS"]).NAICS_UNEMP_RATE

    avg = features.merge(unemp_avg, how="left", on="YR").NAICS_UNEMP_RATE

    features["UNEMP_NAICS"] = np.where(naics.notnull(), naics, avg)

    labels = {"UNEMP_NAICS": "unemployment rate by NAICS code at national level in year before index date"}

    SaveFeatures(features[["UNEMP_NAICS"]], out, manifest, population, labels)


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
