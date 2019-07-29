import cx_Oracle
import pandas as pd
import os, sys, time
from riipl import SaveFeatures

population, dim_date, mega, outfile, manifest = sys.argv[1:]

def main():
    sql = """
          SELECT pop.riipl_id,
                 age,
                 race,
                 sex,
                 marital_status,
                 bmi
            FROM {population} pop
       LEFT JOIN {dim_date} dd
              ON pop.initial_dt = dd.date_dt
       LEFT JOIN {mega} mega
              ON pop.riipl_id = mega.riipl_id AND
                 dd.yrmo = mega.month
        ORDER BY pop.riipl_id
          """.format(**globals())
 
    with cx_Oracle.connect("/") as cxn:
        features = pd.read_sql(sql, cxn, index_col="RIIPL_ID")
   
    labels = {
        "AGE"            : "Age at first prescription",
        "RACE"           : "Race (Asian, Black, Hispanic, Native American, Other, White)",
        "SEX"            : "Sex at first prescription",
        "MARITAL_STATUS" : "Marital status at first prescription",
        "BMI"            : "Body Mass Index at first prescription"
    }

    SaveFeatures(features, outfile, manifest, population, labels)


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
