import cx_Oracle
import pandas as pd
import os, sys, time
from riipl import CachePopulation, SaveFeatures

population, lookback, dlt_wage, out, manifest = sys.argv[1:]

def main():
    """
    Industry worked in (NAICS code) from DLT wages
    """

    sql = """
          SELECT DISTINCT SUBSTR(naics4, 0, 2) AS naics2
            FROM {dlt_wage}
           ORDER BY naics2
          """.format(**globals())

    with cx_Oracle.connect("/") as cxn:
        naics = pd.read_sql(sql, cxn)

    pivot = ",".join(["'{0}' AS naics_{0}".format(n) for n in naics["NAICS2"]])

    index = ["RIIPL_ID"]
    features = CachePopulation(population, index).set_index(index)

    sql = """
          SELECT *
            FROM (   
                  SELECT pop.riipl_id,
                         SUBSTR(dw.naics4, 0, 2) AS naics2,
                         1 AS worked
                    FROM {population} pop
               LEFT JOIN (
                          SELECT DISTINCT
                                 riipl_id,
                                 yyq
                            FROM {lookback}
                         ) lb
                      ON pop.riipl_id = lb.riipl_id
              INNER JOIN {dlt_wage} dw
                      ON pop.riipl_id = dw.riipl_id AND
                         lb.yyq = dw.yyq
                GROUP BY pop.riipl_id, SUBSTR(dw.naics4, 0, 2)
                 ) 
           PIVOT (MAX(worked) FOR naics2 IN ({pivot}))
         """.format(pivot=pivot, **globals())

    with cx_Oracle.connect("/") as cxn:
        features = features.join(pd.read_sql(sql, cxn).set_index(index))

    # Drop NAICS categories that are missing for the entire population.
    features = features.dropna(axis=1, how="all").fillna(0).astype(int)

    # Missing indicator not needed - provided by WAGES_MISSING
    
    labels = {}
    naics2_labels = {
        "00" : "Unknown",
        "02" : "Unknown",
        "11" : "Agriculture, Forestry, Fishing, and Hunting",
        "21" : "Mining, Quarrying, and Oil and Gas Extraction",
        "22" : "Utilities",
        "23" : "Construction",
        "24" : "Unknown",
        "31" : "Manufacturing",
        "32" : "Manufacturing",
        "33" : "Manufacturing",
        "42" : "Wholesale Trade",
        "44" : "Retail Trade",
        "45" : "Retail Trade",
        "48" : "Transportation and Warehousing",
        "49" : "Transportation and Warehousing",
        "50" : "Unknown",
        "51" : "Information",
        "52" : "Finance and Insurance",
        "53" : "Real Estate and Rental and Leasing",
        "54" : "Professional, Scientific, and Technical Services",
        "55" : "Management of Companies and Enterprises",
        "56" : "Administrative and Support and Waste Management and Remediation Services",
        "61" : "Educational Services",
        "62" : "Health Care and Social Assistance",
        "71" : "Arts, Entertainment, and Recreation",
        "72" : "Accommodation and Food Services",
        "81" : "Other Services (except Public Administration)",
        "84" : "Unknown",
        "92" : "Public Administration",
        "94" : "Unknown",
        "99" : "Unknown"
    }
    for n, sector in naics2_labels.items():
        label = "worked in {} sector (NAICS {}) during lookback period".format(sector, n)
        labels["NAICS_{}".format(n)] = label 

    SaveFeatures(features, out, manifest, (population, index), labels, bool_features=list(labels))


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
