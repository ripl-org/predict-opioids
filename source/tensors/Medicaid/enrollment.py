import cx_Oracle
import pandas as pd
import os, sys, time
from riipl import SaveTensor

population, lookback, medicaid_enrollment, dim_aid_ctg_cde, eohhs_recip_x_ssn, out = sys.argv[1:]

def main():
    sql = """
          SELECT pop.riipl_id,
                 lb.timestep,
                 1 AS medicaid_enrolled,
                 MAX(CASE WHEN UPPER(dim.description) LIKE '%PREG%'     THEN 1 ELSE 0 END) AS medicaid_pregnant,
                 MAX(CASE WHEN UPPER(dim.description) LIKE '%PARTUM%'   THEN 1 ELSE 0 END) AS medicaid_postpartum,
                 MAX(CASE WHEN UPPER(dim.description) LIKE '%BLIND%'    THEN 1 ELSE 0 END) AS medicaid_blind,
                 MAX(CASE WHEN UPPER(dim.description) LIKE '%DISABLED%' THEN 1 ELSE 0 END) AS medicaid_disabled,
                 MAX(CASE WHEN UPPER(dim.description) LIKE '%ALIEN%'    THEN 1 ELSE 0 END) AS medicaid_alien,
                 MAX(CASE WHEN UPPER(dim.description) LIKE '%CHILD%'    THEN 1 ELSE 0 END) AS medicaid_child,
                 MAX(CASE WHEN dim.needy_ind = 'Categorically'          THEN 1 ELSE 0 END) AS medicaid_ctg_needy,
                 MAX(CASE WHEN dim.needy_ind = 'Medically'              THEN 1 ELSE 0 END) AS medicaid_med_needy,
                 MAX(NVL(me.managed_care, 0)) AS medicaid_managed_care,
                 MAX(NVL(me.premium_payment, 0)) AS medicaid_prem_payment,
                 MAX(CASE WHEN rxn.payer_cd = 'B' THEN 1 ELSE 0 END) AS medicaid_payer_bhddh,
                 MAX(CASE WHEN rxn.payer_cd = 'C' THEN 1 ELSE 0 END) AS medicaid_payer_cmap,
                 MAX(CASE WHEN rxn.payer_cd = 'D' THEN 1 ELSE 0 END) AS medicaid_payer_doc,
                 MAX(CASE WHEN rxn.payer_cd = 'H' THEN 1 ELSE 0 END) AS medicaid_payer_aids,
                 MAX(CASE WHEN rxn.payer_cd = 'M' THEN 1 ELSE 0 END) AS medicaid_payer_med,
                 MAX(CASE WHEN rxn.payer_cd = 'O' THEN 1 ELSE 0 END) AS medicaid_payer_ors,
                 MAX(CASE WHEN rxn.payer_cd = 'R' THEN 1 ELSE 0 END) AS medicaid_payer_ripae
            FROM {population} pop
       LEFT JOIN {lookback} lb
              ON pop.riipl_id = lb.riipl_id
      INNER JOIN {medicaid_enrollment} me
              ON lb.riipl_id = me.riipl_id AND
                 lb.yrmo = me.yrmo
       LEFT JOIN {dim_aid_ctg_cde} dim
              ON me.aid_category = dim.aid_ctg_cde
       LEFT JOIN {eohhs_recip_x_ssn} rxn
              ON me.re_unique_id = rxn.recipient_id
        GROUP BY pop.riipl_id, lb.timestep
          """.format(**globals())

    with cx_Oracle.connect("/") as cxn:
        features = pd.read_sql(sql, cxn)

    labels = {
        "MEDICAID_ENROLLED"     : "enrolled in Medicaid",
        "MEDICAID_PREGNANT"     : "Medicaid eligibility category contains the word 'pregnant'",
        "MEDICAID_POSTPARTUM"   : "Medicaid eligibility category contains the word 'postpartum'",
        "MEDICAID_BLIND"        : "Medicaid eligibility category contains the word 'blind'",
        "MEDICAID_DISABLED"     : "Medicaid eligibility category contains the word 'disabled'",
        "MEDICAID_ALIEN"        : "Medicaid eligibility category contains the word 'alien'",
        "MEDICAID_CHILD"        : "Medicaid eligibility category contains the word 'child'",
        "MEDICAID_CTG_NEEDY"    : "Medicaid eligibility - categorically needy",
        "MEDICAID_MED_NEEDY"    : "Medicaid eligibility - medically needy",
        "MEDICAID_MANAGED_CARE" : "enrolled in Medicaid managed care",
        "MEDICAID_PREM_PAYMENT" : "enrolled in Medicaid premium payment plan",
        "MEDICAID_PAYER_BHDDH"  : "Medicaid payer code is BHDDH",
        "MEDICAID_PAYER_CMAP"   : "Medicaid payer code is Community Medication Assistance Program",
        "MEDICAID_PAYER_DOC"    : "Medicaid payer code is DOC",
        "MEDICAID_PAYER_AIDS"   : "Medicaid payer code is DOH/AIDS",
        "MEDICAID_PAYER_MED"    : "Medicaid payer code is Medical Assistance",
        "MEDICAID_PAYER_ORS"    : "Medicaid payer code is ORS",
        "MEDICAID_PAYER_RIPAE"  : "Medicaid payer code is RI Pharmaceutical Assistance to the Elderly"
    }

    tensor = {}
    for feature in labels:
        tensor[feature] = features.loc[features[feature] == 1, ["RIIPL_ID", "TIMESTEP"]]

    fill_values = dict((feature, 0) for feature in tensor)

    SaveTensor(tensor, labels, fill_values, (population, "RIIPL_ID"), out)


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
