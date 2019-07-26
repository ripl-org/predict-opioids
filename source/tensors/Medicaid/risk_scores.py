import cx_Oracle
import pandas as pd
import os, sys, time
from riipl import SaveTensor

population, lookback, medicaid_enrollment, dim_date, diag_cde, proc_cde, ccs, cci, out = sys.argv[1:]

def main():

    index = ["RIIPL_ID", "TIMESTAMP"]

    sql = """
          SELECT pop.riipl_id,
                 lb.timestep,
                 COUNT(DISTINCT c.disease) AS value
            FROM {population} pop
       LEFT JOIN {lookback} lb
              ON pop.riipl_id = lb.riipl_id
      INNER JOIN {medicaid_enrollment} me
              ON lb.riipl_id = me.riipl_id AND
                 lb.yrmo = me.yrmo
       LEFT JOIN {dim_date} dd
              ON me.yrmo = dd.yrmo
       LEFT JOIN {diag_cde} d
              ON pop.riipl_id = d.riipl_id AND
                 dd.date_dt = d.claim_dt
       LEFT JOIN {ccs} c
              ON d.diag_cde = c.diag_cde
        GROUP BY pop.riipl_id, lb.timestep
          """.format(**globals())

    with cx_Oracle.connect("/") as cxn:
        values = pd.read_sql(sql, cxn)

    tensor = {"MEDICAID_DISEASE_SCORE": values.fillna(0)}

    sql = """
          SELECT pop.riipl_id,
                 lb.timestep,
                 COUNT(DISTINCT c.chronic) AS value
            FROM {population} pop
       LEFT JOIN {lookback} lb
              ON pop.riipl_id = lb.riipl_id
      INNER JOIN {medicaid_enrollment} me
              ON lb.riipl_id = me.riipl_id AND
                 lb.yrmo = me.yrmo
       LEFT JOIN {dim_date} dd
              ON me.yrmo = dd.yrmo
       LEFT JOIN {diag_cde} d
              ON pop.riipl_id = d.riipl_id AND
                 dd.date_dt = d.claim_dt
       LEFT JOIN {cci} c
              ON d.diag_cde = c.diag_cde
        GROUP BY pop.riipl_id, lb.timestep
          """.format(**globals())

    with cx_Oracle.connect("/") as cxn:
        values = pd.read_sql(sql, cxn)

    tensor["MEDICAID_CHRONIC_SCORE"] = values.fillna(0)

    sql = """
          SELECT pop.riipl_id,
                 lb.timestep,
                 COUNT(DISTINCT p.proc_cde) AS value
            FROM {population} pop
       LEFT JOIN {lookback} lb
              ON pop.riipl_id = lb.riipl_id
      INNER JOIN {medicaid_enrollment} me
              ON lb.riipl_id = me.riipl_id AND
                 lb.yrmo = me.yrmo
       LEFT JOIN {dim_date} dd
              ON me.yrmo = dd.yrmo
       LEFT JOIN {proc_cde} p
              ON pop.riipl_id = p.riipl_id AND
                 dd.date_dt = p.claim_dt
        GROUP BY pop.riipl_id, lb.timestep
          """.format(**globals())

    with cx_Oracle.connect("/") as cxn:
        values = pd.read_sql(sql, cxn)

    tensor["MEDICAID_PROCEDURES"] = values.fillna(0)

    # Add squared terms
    for x in ["MEDICAID_DISEASE_SCORE", "MEDICAID_CHRONIC_SCORE", "MEDICAID_PROCEDURES"]:
        values = tensor[x].copy()
        values["VALUE"] *= values["VALUE"]
        tensor["{}_SQ".format(x)] = values

    labels = {
        "MEDICAID_DISEASE_SCORE"    : "Number of AHRQ CCS diseases",
        "MEDICAID_CHRONIC_SCORE"    : "Number of AHRQ CCI chronic conditions",
        "MEDICAID_PROCEDURES"       : "Number of distinct procedures",
        "MEDICAID_DISEASE_SCORE_SQ" : "Squared number of AHRQ CCS diseases",
        "MEDICAID_CHRONIC_SCORE_SQ" : "Squared number of AHRQ CCI chronic conditions",
        "MEDICAID_PROCEDURES_SQ"    : "Squared number of distinct procedures"
    }

    fill_values = dict((feature, "mean") for feature in labels)

    SaveTensor(tensor, labels, fill_values, (population, "RIIPL_ID"), out)


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
