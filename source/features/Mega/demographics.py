import pandas as pd
import os, sys, time
from riipl import CachePopulation, Connection, SaveFeatures

population, lookback, mega, out, manifest = sys.argv[1:]

def main():
    """
    Demographics variables from MEGA table
    """

    sql = """
          SELECT pop.riipl_id,
                 MAX(m.age)                                                  AS age,
                 MAX(m.bmi)                                                  AS bmi,
                 MAX(m.marital_status)                                       AS married,
                 MAX(CASE WHEN m.race = 'Black'           THEN 1 ELSE 0 END) AS race_black,
                 MAX(CASE WHEN m.race = 'Hispanic'        THEN 1 ELSE 0 END) AS race_hispanic,
                 MAX(CASE WHEN m.race = 'Asian'           THEN 1
                          WHEN m.race = 'Native American' THEN 1
                          WHEN m.race = 'Other'           THEN 1 ELSE 0 END) AS race_other,
                 MAX(CASE WHEN m.race IS NULL             THEN 1 ELSE 0 END) AS race_missing,
                 MAX(CASE WHEN m.sex = 'M'                THEN 1 ELSE 0 END) AS sex_m,
                 MAX(CASE WHEN m.sex IS NULL              THEN 1 ELSE 0 END) AS sex_missing
            FROM {population} pop
       LEFT JOIN {lookback} lb
              ON pop.riipl_id = lb.riipl_id
       LEFT JOIN {mega} m
              ON pop.riipl_id = m.riipl_id AND
                 lb.yrmo = m.month
        GROUP BY pop.riipl_id
        ORDER BY pop.riipl_id
          """.format(**globals())

    with Connection() as cxn:
        features = pd.read_sql(sql, cxn._connection, index_col="RIIPL_ID")

    labels = {
        "AGE"           : "Age",
        "BMI"           : "Body mass index",
        "MARRIED"       : "Married",
        "RACE_BLACK"    : "Race is African American",
        "RACE_HISPANIC" : "Ethnicity is Hispanic",
        "RACE_OTHER"    : "Race is Asian, Native American, or other",
        "RACE_MISSING"  : "Race is missing",
        "SEX_M"         : "Sex is male",
        "SEX_MISSING"   : "Sex is missing"
    }

    SaveFeatures(features, out, manifest, population, labels)


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
