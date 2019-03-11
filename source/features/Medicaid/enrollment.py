import cx_Oracle
import pandas as pd
import os, sys, time
from riipl import SaveFeatures, CachePopulation

population, lookback, medicaid_enrollment, dim_aid_ctg_cde, recip_demo, recip_x_ssn, out, manifest = sys.argv[1:]

def main():

    index = ["RIIPL_ID"]
    features = CachePopulation(population, index).set_index(index)

    sql = """
          SELECT pop.riipl_id,
                 COUNT(DISTINCT me.re_unique_id)                                           AS medicaid_n_ids,
                 MAX(CASE WHEN UPPER(dim.description) LIKE '%PREG%'     THEN 1 ELSE 0 END) AS medicaid_pregnant,
                 MAX(CASE WHEN UPPER(dim.description) LIKE '%PARTUM%'   THEN 1 ELSE 0 END) AS medicaid_postpartum,
                 MAX(CASE WHEN UPPER(dim.description) LIKE '%BLIND%'    THEN 1 ELSE 0 END) AS medicaid_blind,
                 MAX(CASE WHEN UPPER(dim.description) LIKE '%DISABLED%' THEN 1 ELSE 0 END) AS medicaid_disabled,
                 MAX(CASE WHEN UPPER(dim.description) LIKE '%ALIEN%'    THEN 1 ELSE 0 END) AS medicaid_alien,
                 MAX(CASE WHEN UPPER(dim.description) LIKE '%CHILD%'    THEN 1 ELSE 0 END) AS medicaid_child,
                 MAX(CASE WHEN dim.needy_ind = 'Categorically'          THEN 1 ELSE 0 END) AS medicaid_ctg_needy,
                 MAX(CASE WHEN dim.needy_ind = 'Medically'              THEN 1 ELSE 0 END) AS medicaid_med_needy,
                 MAX(NVL(me.managed_care, 0))                                              AS medicaid_managed_care,
                 MAX(NVL(me.premium_payment, 0))                                           AS medicaid_prem_payment,
                 MAX(CASE WHEN rd.primary_lang_cd = '01'                THEN 1 ELSE 0 END) AS medicaid_lang_spanish,
                 MAX(CASE WHEN rd.primary_lang_cd = '31'                THEN 1 ELSE 0 END) AS medicaid_lang_portu,
                 MAX(CASE WHEN rd.primary_lang_cd <> '00' AND
                               rd.primary_lang_cd <> '01' AND
                               rd.primary_lang_cd <> '31'               THEN 1 ELSE 0 END) AS medicaid_lang_other,
                 MAX(CASE WHEN rxn.payer_cd = 'B'                       THEN 1 ELSE 0 END) AS medicaid_payer_bhddh,
                 MAX(CASE WHEN rxn.payer_cd = 'C'                       THEN 1 ELSE 0 END) AS medicaid_payer_cmap,
                 MAX(CASE WHEN rxn.payer_cd = 'D'                       THEN 1 ELSE 0 END) AS medicaid_payer_doc,
                 MAX(CASE WHEN rxn.payer_cd = 'H'                       THEN 1 ELSE 0 END) AS medicaid_payer_aids,
                 MAX(CASE WHEN rxn.payer_cd = 'O'                       THEN 1 ELSE 0 END) AS medicaid_payer_ors,
                 MAX(CASE WHEN rxn.payer_cd = 'R'                       THEN 1 ELSE 0 END) AS medicaid_payer_ripae
            FROM {population} pop
       LEFT JOIN {lookback} lb
              ON pop.riipl_id = lb.riipl_id
       LEFT JOIN {medicaid_enrollment} me
              ON pop.riipl_id = me.riipl_id AND
                 lb.yrmo = me.yrmo
       LEFT JOIN {dim_aid_ctg_cde} dim
              ON me.aid_category = dim.aid_ctg_cde
       LEFT JOIN {recip_demo} rd
              ON me.re_unique_id = rd.recipient_id
       LEFT JOIN {recip_x_ssn} rxn
              ON me.re_unique_id = rxn.recipient_id
        GROUP BY pop.riipl_id
          """.format(**globals())

    with cx_Oracle.connect("/") as cxn:
        features = features.join(pd.read_sql(sql, cxn).set_index(index))

    features = features.fillna(0)

    labels = {
        "MEDICAID_N_IDS"        : "Number of unique Medicaid IDs",
        "MEDICAID_PREGNANT"     : "Medicaid eligibility category contains the word 'pregnant'",
        "MEDICAID_POSTPARTUM"   : "Medicaid eligibility category contains the word 'postpartum'",
        "MEDICAID_BLIND"        : "Medicaid eligibility category contains the word 'blind'",
        "MEDICAID_DISABLED"     : "Medicaid eligibility category contains the word 'disabled'",
        "MEDICAID_ALIEN"        : "Medicaid eligibility category contains the word 'alien'",
        "MEDICAID_CHILD"        : "Medicaid eligibility category contains the word 'child'",
        "MEDICAID_CTG_NEEDY"    : "Eligible for Medicaid as categorically needy",
        "MEDICAID_MED_NEEDY"    : "Eligible for Medicaid as medically needy",
        "MEDICAID_MANAGED_CARE" : "Enrolled in Medicaid managed care",
        "MEDICAID_PREM_PAYMENT" : "Enrolled in Medicaid premium payment plan",
        "MEDICAID_LANG_SPANISH" : "Primary language is Spanish",
        "MEDICAID_LANG_PORTU"   : "Primary language is Portuguese",
        "MEDICAID_LANG_OTHER"   : "Primary language is not English, Spanish, or Portuguese",
        "MEDICAID_PAYER_BHDDH"  : "Medicaid payer code is BHDDH",
        "MEDICAID_PAYER_CMAP"   : "Enrolled in RI Community Medication Assistance Program",
        "MEDICAID_PAYER_DOC"    : "Medicaid payer code is Department of Corrections",
        "MEDICAID_PAYER_AIDS"   : "Medicaid payer code is Ryan White AIDS Drug Assistance Program",
        "MEDICAID_PAYER_ORS"    : "Medicaid payer code is ORS",
        "MEDICAID_PAYER_RIPAE"  : "Enrolled in RI Pharmaceutical Assistance to the Elderly"
    }

    SaveFeatures(features, out, manifest, population, labels,
                 bool_features=[f for f in labels if f != "MEDICAID_N_IDS"])


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
