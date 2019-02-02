import cx_Oracle
import pandas as pd
import os, sys, time
from riipl import SaveFeatures

population, mega, incomepath, povertypath, outfile, manifest = sys.argv[1:]

def main():
    """
    This code generates the following features based on someone's home census block group:
    * Median income
    * Share below the federal povery line
    """

    income = pd.read_csv(incomepath, skiprows=1, na_values=["-", "**"], index_col="Id2",
                         usecols=["Id2", "Estimate; Median household income in the past 12 months (in 2015 Inflation-adjusted dollars)"])
    income.index.name = "GEO_ID"
    income.columns = ["BLKGRP_MEDIANINCOME"]

    fpl = pd.read_csv(povertypath, skiprows=1, na_values=["-", "**"], index_col="Id2",
                      usecols=["Id2", "Estimate; Total:", "Estimate; Income in the past 12 months below poverty level:"])
    fpl.index.name = "GEO_ID"
    fpl.columns = ["TOTAL", "FPL"]
    fpl["BLKGRP_BELOWFPL"] = fpl.FPL / fpl.TOTAL
    fpl = fpl[["BLKGRP_BELOWFPL"]]

    sql = """
          SELECT pop.riipl_id,
                 TO_NUMBER(m.address_state || m.address_county || m.address_trct || m.address_blkgrp) AS geo_id
            FROM {population} pop
       LEFT JOIN {mega} m
              ON pop.riipl_id = m.riipl_id AND
                 TO_CHAR(pop.initial_rx_dt, 'YYYYMM') = m.month
          """.format(**globals())

    with cx_Oracle.connect("/") as cxn:
        features = pd.read_sql(sql, cxn, index_col="GEO_ID").join(income).join(fpl)

    features = features.sort_values("RIIPL_ID").set_index("RIIPL_ID")

    # Check that no columns are below 0
    for feature in ["BLKGRP_MEDIANINCOME", "BLKGRP_BELOWFPL"]:
        assert (features[feature].isna() | (features[feature] >= 0)).all(), "{} contains negative values".format(feature)
    
    labels = {
        "BLKGRP_MEDIANINCOME" : "Block group's median annual household income (2015 dollars)",
        "BLKGRP_BELOWFPL"     : "Share of block group's residents with annual income below poverty level"
    }

    SaveFeatures(features, outfile, manifest, population, labels)


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
