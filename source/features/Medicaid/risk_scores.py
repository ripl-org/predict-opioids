import pandas as pd
import os, sys, time
from riipl import CachePopulation, Connection, SaveFeatures

population, lookback, dim_date, diag_cde, proc_cde, ccs_file, cci_file, out, manifest = sys.argv[1:]

def main():

    ccs = pd.read_csv(ccs_file,
                      usecols=[0, 1],
                      quotechar="'",
                      skiprows=3,
                      names=["DIAG_CDE", "DISEASE"])
    ccs["DIAG_CDE"] = ccs.DIAG_CDE.str.strip()

    cci = pd.read_csv(cci_file,
                      usecols=[0, 2],
                      quotechar="'",
                      skiprows=2,
                      names=["DIAG_CDE", "CHRONIC"])
    cci = cci[cci.CHRONIC == 1]
    cci["DIAG_CDE"] = cci.DIAG_CDE.str.strip()

    index = ["RIIPL_ID"]
    features = CachePopulation(population, index).set_index(index)

    sql = """
          SELECT DISTINCT
                 pop.sample_id,
                 d.diag_cde
            FROM {population} pop
       LEFT JOIN {lookback} lb
              ON pop.riipl_id = lb.riipl_id
       LEFT JOIN {dim_date} dd
              ON lb.yrmo = dd.yrmo
      INNER JOIN {diag_cde} d
              ON pop.riipl_id = d.riipl_id AND
                 dd.date_dt = d.claim_dt
          """.format(**globals())

    with Connection() as cxn:
        diags = pd.read_sql(sql, cxn._connection)
    
    ndisease = diags.merge(ccs, how="inner", on="DIAG_CDE")[["RIIPL_ID", "DISEASE"]]\
                    .groupby("RIIPL_ID")\
                    .agg({"DISEASE": pd.Series.nunique})\
                    .rename(columns={"DISEASE": "MEDICAID_DISEASE_SCORE"})
    features = features.join(ndisease)

    nchronic = diags.merge(cci, how="inner", on="DIAG_CDE")[["RIIPL_ID", "CHRONIC"]]\
                    .groupby("RIIPL_ID")\
                    .sum()\
                    .rename(columns={"CHRONIC": "MEDICAID_CHRONIC_SCORE"})
    features = features.join(nchronic)

    sql = """
          SELECT pop.sample_id,
                 COUNT(DISTINCT p.proc_cde) AS medicaid_procedures
            FROM {population} pop
       LEFT JOIN {lookback} lb
              ON pop.riipl_id = lb.riipl_id
       LEFT JOIN {dim_date} dd
              ON lb.yrmo = dd.yrmo
      INNER JOIN {proc_cde} p
              ON pop.riipl_id = p.riipl_id AND
                 dd.date_dt = p.claim_dt
        GROUP BY pop.riipl_id
          """.format(**globals())

    with Connection() as cxn:
        nproc = pd.read_sql(sql, cxn._connection, index_col="SAMPLE_ID")

    features = features.join(nproc).fillna(0)

    # Add squared terms
    for x in ["MEDICAID_DISEASE_SCORE", "MEDICAID_CHRONIC_SCORE", "MEDICAID_PROCEDURES"]:
        features["{}_SQ".format(x)] = features[x] * features[x]

    labels = {
        "MEDICAID_DISEASE_SCORE"    : "Number of AHRQ CCS diseases",
        "MEDICAID_CHRONIC_SCORE"    : "Number of AHRQ CCI chronic conditions",
        "MEDICAID_PROCEDURES"       : "Number of distinct procedures",
        "MEDICAID_DISEASE_SCORE_SQ" : "Squared number of AHRQ CCS diseases",
        "MEDICAID_CHRONIC_SCORE_SQ" : "Squared number of AHRQ CCI chronic conditions",
        "MEDICAID_PROCEDURES_SQ"    : "Squared number of distinct procedures"
    }

    SaveFeatures(features, out, manifest, population, labels)


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
