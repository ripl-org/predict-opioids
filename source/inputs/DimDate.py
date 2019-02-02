import sys
from riipl import Connection

def DimDate(table):

    sql = """
CREATE TABLE %table% PCTFREE 0 NOLOGGING PARALLEL AS (
SELECT THEDATE                                                  AS DATE_DT
      ,CAST(TO_CHAR(THEDATE, 'YYYYMM') AS NUMBER(6))            AS YRMO
      ,TRUNC(THEDATE, 'Q')                                      AS QTR_ST_DT
      ,CASE WHEN TO_NUMBER(TO_CHAR(THEDATE, 'YYYY')) > 1917
            THEN TO_CHAR(THEDATE, 'YY') || 
                 TO_CHAR(THEDATE, 'Q')
            ELSE NULL
       END                                                      AS YYQ
  FROM (SELECT TO_DATE('31-DEC-1799') + LEVEL AS THEDATE
          FROM DUAL
       CONNECT BY LEVEL <= (SELECT TO_DATE('01-JAN-2101') - TO_DATE('01-JAN-1800')
                              FROM DUAL)
       )
)"""

    with Connection() as cxn:
        cxn.clear_tables(table)
        cxn.execute(sql)
        cxn.save_table(table, "DATE_DT")

if __name__ == "__main__": DimDate(*sys.argv[1:])

# vim: expandtab sw=4 ts=4
