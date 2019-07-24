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
                 CASE WHEN MAX(m.age) >= 18 AND MAX(m.age) < 24 THEN 1 ELSE 0 END  AS age_1,
                 CASE WHEN MAX(m.age) >= 24 AND MAX(m.age) < 30 THEN 1 ELSE 0 END  AS age_2,
                 CASE WHEN MAX(m.age) >= 30 AND MAX(m.age) < 40 THEN 1 ELSE 0 END  AS age_3,
                 CASE WHEN MAX(m.age) >= 40 AND MAX(m.age) < 55 THEN 1 ELSE 0 END  AS age_4,
                 CASE WHEN MAX(m.age) >= 55 AND MAX(m.age) < 65 THEN 1 ELSE 0 END  AS age_5,
                 CASE WHEN MAX(m.age) >= 65                     THEN 1 ELSE 0 END  AS age_6,
                 CASE WHEN AVG(m.bmi) < 18.5                    THEN 1 ELSE 0 END  AS bmi_under,
                 CASE WHEN AVG(m.bmi) >= 25 AND AVG(m.bmi) < 30 THEN 1 ELSE 0 END  AS bmi_over,
                 CASE WHEN AVG(m.bmi) >= 30                     THEN 1 ELSE 0 END  AS bmi_obese,
                 CASE WHEN COUNT(m.bmi) = 0                     THEN 1 ELSE 0 END  AS bmi_missing,
                 MAX(CASE WHEN(m.marital_status) = 1            THEN 1 ELSE 0 END) AS married,
                 CASE WHEN COUNT(m.marital_status) = 0          THEN 1 ELSE 0 END  AS married_missing,
                 MAX(CASE WHEN m.race = 'Black'                 THEN 1 ELSE 0 END) AS race_black,
                 MAX(CASE WHEN m.race = 'Hispanic'              THEN 1 ELSE 0 END) AS race_hispanic,
                 MAX(CASE WHEN m.race = 'Asian'                 THEN 1
                          WHEN m.race = 'Native American'       THEN 1
                          WHEN m.race = 'Other'                 THEN 1 ELSE 0 END) AS race_other,
                 CASE WHEN COUNT(m.race) = 0                    THEN 1 ELSE 0 END  AS race_missing
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
        "AGE_1"           : "Age is 18-23",
        "AGE_2"           : "Age is 24-29",
        "AGE_3"           : "Age is 30-39",
        "AGE_4"           : "Age is 40-54",
        "AGE_5"           : "Age is 55-64",
        "AGE_6"           : "Age is 65+",
        "BMI_UNDER"       : "Body mass index is underweight",
        "BMI_OVER"        : "Body mass index is overweight",
        "BMI_OBESE"       : "Body mass index is obese",
        "BMI_MISSING"     : "Body mass index is missing",
        "MARRIED"         : "Married",
        "MARRIED_MISSING" : "Marital status is missing",
        "RACE_BLACK"      : "Race is African American",
        "RACE_HISPANIC"   : "Ethnicity is Hispanic",
        "RACE_OTHER"      : "Race is Asian, Native American, or other",
        "RACE_MISSING"    : "Race is missing"
    }

    SaveFeatures(features, out, manifest, population, labels, bool_features=list(labels))


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
