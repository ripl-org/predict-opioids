import sys
from riipl import Connection

medicaid_enrollment, table = sys.argv[1:]

sql = """
      CREATE TABLE %table% NOLOGGING PCTFREE 0 PARALLEL AS 
      SELECT riipl_id,
             SUM(n) AS months
        FROM (
              SELECT riipl_id,
                     yr,
                     COUNT(yrmo) AS n
                FROM (
                      SELECT DISTINCT
                             riipl_id,
                             TO_NUMBER(SUBSTR(yrmo, 1, 4)) AS yr,
                             TO_NUMBER(yrmo) AS yrmo
                        FROM %medicaid_enrollment%
                     )
               WHERE yr BETWEEN 2007 AND 2011
            GROUP BY riipl_id, yr
              )
        WHERE n >= 6              
     GROUP BY riipl_id
       HAVING COUNT(*) = 5
     ORDER BY riipl_id
      """

with Connection() as cxn:
    cxn.clear_tables(table)
    cxn.execute(sql)
    cxn.save_table(table, "RIIPL_ID")

# vim: syntax=python expandtab sw=4 ts=4
