import cx_Oracle
import pandas as pd
import os, sys, time
from riipl import *

population, lookback, dim_date, medicaid_pharmacy, ashp_path, out = sys.argv[1:]

def main():
    # Read in ASHP derived table
    ashp = pd.read_csv(ashp_path, dtype={"CLASS": str})
    ashp["FEATURE"] = ashp["CLASS"].apply(lambda x: "ASHP_{}".format(x))
    ashp_desc = ashp[["FEATURE", "DESC"]].drop_duplicates("FEATURE")

    # Load pharmacy claims
    sql = """ 
          SELECT pop.riipl_id,
                 lb.timestep,
                 mp.ndc9_code
            FROM {population} pop
       LEFT JOIN {lookback} lb
              ON pop.riipl_id = lb.riipl_id
       LEFT JOIN {dim_date} dd
              ON lb.yrmo = dd.yrmo
      INNER JOIN {medicaid_pharmacy} mp
              ON lb.riipl_id = mp.riipl_id AND
                 dd.date_dt = mp.dispensed_dt
          """.format(**globals())

    with cx_Oracle.connect("/") as cxn:
        values = pd.read_sql(sql, cxn)

    # Merge classes onto pharmacy claims
    values = values.merge(ashp, how="left", on="NDC9_CODE")

    # Missing classes should be <20%
    TestMissing(values.FEATURE, 0.2)
    values.loc[values.FEATURE.isnull(), "FEATURE"] = "ASHP_MISSING"

    # Pivot ASHP categories
    columns = ["RIIPL_ID", "TIMESTEP", "FEATURE"]
    grouped = values[columns].groupby(columns).size().reset_index().rename(columns={0: "VALUE"})

    labels = {"ASHP_MISSING": "No mapping from NDC code to ASHP classification"}
    for _, f, desc in ashp_desc.itertuples():
        if f.startswith("ASHP_99"):
            labels[f] = "Unknown"
        else:
            labels[f] = desc

    tensor = {}
    for feature in labels:
        tensor[feature] = grouped.loc[grouped.FEATURE == feature, ["RIIPL_ID", "TIMESTEP", "VALUE"]]

    fill_values = dict((feature, 0) for feature in labels)

    SaveTensor(tensor, labels, fill_values, (population, "RIIPL_ID"), out)


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
