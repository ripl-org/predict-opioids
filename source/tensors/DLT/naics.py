import cx_Oracle
import pandas as pd
import os, sys, time
from riipl import SaveTensor

population, lookback, dlt_wage, out = sys.argv[1:]

def main():
    sql = """
          SELECT DISTINCT SUBSTR(naics4, 1, 2) AS naics2
            FROM {dlt_wage}
        ORDER BY naics2
          """.format(**globals())

    with cx_Oracle.connect("/") as cxn:
        naics = pd.read_sql(sql, cxn)

    pivot = ",".join(["'{0}' AS NAICS_{0}".format(n) for n in naics["NAICS2"]])

    sql = """
          SELECT *
            FROM (
                  SELECT pop.riipl_id,
                         lb.timestep,
                         SUBSTR(dw.naics4, 1, 2) AS naics2,
                         1 AS worked
                    FROM {population} pop
               LEFT JOIN {lookback} lb
                      ON pop.riipl_id = lb.riipl_id
              INNER JOIN {dlt_wage} dw
                      ON lb.riipl_id = dw.riipl_id AND
                         lb.yyq = dw.yyq
                 ) 
                 PIVOT (MAX(worked) FOR naics2 IN ({pivot}))
         """.format(pivot=pivot, **globals())

    with cx_Oracle.connect("/") as cxn:
        values = pd.read_sql(sql, cxn)

    naics2_labels = {
        "00": "Unknown",
        "02": "Unknown",
        "11": "Agriculture, Forestry, Fishing, and Hunting",
        "21": "Mining, Quarrying, and Oil and Gas Extraction",
        "22": "Utilities",
        "23": "Construction",
        "24": "Unknown",
        "31": "Manufacturing",
        "32": "Manufacturing",
        "33": "Manufacturing",
        "42": "Wholesale Trade",
        "44": "Retail Trade",
        "45": "Retail Trade",
        "48": "Transportation and Warehousing",
        "49": "Transportation and Warehousing",
        "50": "Unknown",
        "51": "Information",
        "52": "Finance and Insurance",
        "53": "Real Estate and Rental and Leasing",
        "54": "Professional, Scientific, and Technical Services",
        "55": "Management of Companies and Enterprises",
        "56": "Administrative and Support and Waste Management and Remediation Services",
        "61": "Educational Services",
        "62": "Health Care and Social Assistance",
        "71": "Arts, Entertainment, and Recreation",
        "72": "Accommodation and Food Services",
        "81": "Other Services (except Public Administration)",
        "84": "Unknown",
        "92": "Public Administration",
        "94": "Unknown",
        "99": "Unknown"
    }

    labels = {}
    for naics2, sector in naics2_labels.items():
        label = "worked in {} sector (NAICS {})".format(sector, naics2)
        labels["NAICS_{}".format(naics2)] = label 

    tensor = {}
    for feature in labels:
        tensor[feature] = values[["RIIPL_ID", "TIMESTEP", feature]].fillna(0).rename(columns={feature: "VALUE"})

    fill_values = dict((feature, "mean") for feature in tensor)

    SaveTensor(tensor, labels, fill_values, (population, "RIIPL_ID"), out)


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
