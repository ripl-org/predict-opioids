import cx_Oracle
import pandas as pd
import os, sys, time
from riipl.model import SaveFeatures

population, dim_date, medicaid_enrollment, dim_aid_ctg_cde, eohhs_recip_x_ssn, outfile, manifest = sys.argv[1:]

def main():    
    sql = """
          SELECT                                                                              pop.riipl_id,
                 MAX(CASE WHEN UPPER(dim.description) LIKE '%PREG%'     THEN 1 ELSE 0 END) AS pregnant,
                 MAX(CASE WHEN UPPER(dim.description) LIKE '%PARTUM%'   THEN 1 ELSE 0 END) AS postpartum,
                 MAX(CASE WHEN UPPER(dim.description) LIKE '%BLIND%'    THEN 1 ELSE 0 END) AS blind,
                 MAX(CASE WHEN UPPER(dim.description) LIKE '%DISABLED%' THEN 1 ELSE 0 END) AS disabled,
                 MAX(CASE WHEN UPPER(dim.description) LIKE '%ALIEN%'    THEN 1 ELSE 0 END) AS alien,
                 MAX(CASE WHEN UPPER(dim.description) LIKE '%CHILD%'    THEN 1 ELSE 0 END) AS child,
                 MAX(CASE WHEN dim.needy_ind = 'Categorically'          THEN 1 ELSE 0 END) AS categorically_needy,
                 MAX(CASE WHEN dim.needy_ind = 'Medically'              THEN 1 ELSE 0 END) AS medically_needy,
                 MAX(NVL(me.managed_care, 0))                                              AS managed_care,
                 MAX(NVL(me.premium_payment, 0))                                           AS premium_payment,
                 STATS_MODE(CASE WHEN rxn.payer_cd = 'B' THEN 'BHDDH_DD'
                                 WHEN rxn.payer_cd = 'C' THEN 'CMAP'
                                 WHEN rxn.payer_cd = 'D' THEN 'DOC'
                                 WHEN rxn.payer_cd = 'H' THEN 'DOH_AIDS'
                                 WHEN rxn.payer_cd = 'M' THEN 'MEDICAL'
                                 WHEN rxn.payer_cd = 'O' THEN 'ORS'
                                 WHEN rxn.payer_cd = 'R' THEN 'RIPAE'
                                                         ELSE 'OTHER' 
                 END) AS payer_cd
            FROM {population} pop
       LEFT JOIN {dim_date} dd
              ON pop.initial_rx_dt = dd.date_dt
       LEFT JOIN {medicaid_enrollment} me
              ON pop.riipl_id = me.riipl_id AND
                 me.yrmo = dd.yrmo
       LEFT JOIN {dim_aid_ctg_cde} dim
              ON me.aid_category = dim.aid_ctg_cde
       LEFT JOIN {eohhs_recip_x_ssn} rxn
              ON me.re_unique_id = rxn.recipient_id
        GROUP BY pop.riipl_id
        ORDER BY pop.riipl_id
          """.format(**globals())

    with cx_Oracle.connect("/") as cxn:
        features = pd.read_sql(sql, cxn, index_col="RIIPL_ID")

    labels = {
        "PREGNANT"            : "Medicaid eligibility category contains the word 'pregnant'",
        "POSTPARTUM"          : "Medicaid eligibility category contains the word 'postpartum'",
        "BLIND"               : "Medicaid eligibility category contains the word 'blind'",
        "DISABLED"            : "Medicaid eligibility category contains the word 'disabled'",
        "ALIEN"               : "Medicaid eligibility category contains the word 'alien'",
        "CHILD"               : "Medicaid eligibility category contains the word 'child'",
        "CATEGORICALLY_NEEDY" : "Medicaid eligibility - categorically needy",
        "MEDICALLY_NEEDY"     : "Medicaid eligibility - medically needy",
        "MANAGED_CARE"        : "Enrolled in Medicaid managed care at time of prescription",
        "PREMIUM_PAYMENT"     : "Enrolled in Medicaid premium payment plan at time of prescription",
        "PAYER_CD"            : "Medicaid payer code associated with the Medicaid ID"
    }
    bools = list(labels.keys())
    bools.remove("PAYER_CD")

    SaveFeatures(features, outfile, manifest, population, labels, bool_features=bools)


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
