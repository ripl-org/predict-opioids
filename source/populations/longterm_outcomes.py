import numpy as np
import pandas as pd
import sys
from collections import defaultdict
from riipl import *

OUTCOMES = {
  "DIAG": {
    "OUTCOME_DEPENDENCE":       [b"3040",  # ICD-9  Opioid type dependence
                                 b"3047",  # ICD-9  Combinations of opioid type drug with any other drug dependence
                                 b"F112"], # ICD-10 Opioid dependence
    "OUTCOME_ABUSE":            [b"3055",  # ICD-9  Nondependent opioid abuse
                                 b"F111"], # ICD-10 Opioid abuse
    "OUTCOME_POISONING_RX":     [b"96500", # ICD-9  Poisoning by opium (alkaloids), unspecified
                                 b"96502", # ICD-9  Poisoning by methadone
                                 b"96509", # ICD-9  Poisoning by other opiates and related narcotics
                                 b"9701",  # ICD-9  Poisoning by opiate antagonists
                                 b"E8501", # ICD-9  Accidental poisoning by methadone
                                 b"E8502", # ICD-9  Accidental poisoning by other opiates and related narcotics
                                 b"E9351", # ICD-9  Methadone causing adverse effects in therapeutic use
                                 b"E9352", # ICD-9  Other opiates and related narcotics causing adverse effects in therapeutic use
                                 b"E9401", # ICD-9  Opiate antagonists causing adverse effects in therapeutic use
                                 b"T400",  # ICD-10 Poisoning by, adverse effect of and underdosing of opium
                                 b"T402",  # ICD-10 Poisoning by, adverse effect of and underdosing of other opioids
                                 b"T403"], # ICD-10 Poisoning by, adverse effect of and underdosing of methadone
    "OUTCOME_POISONING_HEROIN": [b"96501", # ICD-9  Poisoning by heroin
                                 b"E8500", # ICD-9  Accidental poisoning by heroin
                                 b"E9350", # ICD-9  Heroin causing adverse effects in therapeutic use
                                 b"T401"]  # ICD-10 Poisoning by and adverse effect of heroin
  },
  "PROC": {
    "OUTCOME_PROCEDURE":        [b"J2310", # Naloxone HCI Injection, per 1 mg
                                 b"J2315", # Naltrexone injection, depot form, 1mg
                                 b"J0592", # Buprenorphine HCL injection, 0.1mg
                                 b"X0305", # Methadone detoxification - outpatient
                                 b"X0321", # Methadone maintenance, assesment and evaluation, counseling, medication, treatment and review, and lab testing
                                 b"H0020", # Alcohol and or drug services; methadone administration and or service
                                 b"J1230", # Injection, methadone, up to 10mg
                                 b"83840"] # methadone
  }
}

MAX_DT = 99999999


def Load(claimfile, t, start, end):
    """
    Load all codes/dates for claims in the time period.
    """

    claims = ReadHDF5(claimfile)

    # Select time period
    n = len(claims)
    claims = claims[(claims.CLAIM_DT >= int(start)) & (claims.CLAIM_DT < int(end))]
    print(len(claims), "of", n, "claims in time period")

    # Zero RIIPL_IDs should be <1%
    TestValue(claims.RIIPL_ID, 0, 0.01)

    # No codes should be missing
    TestMissing(claims[t + "_CDE"], 0)

    # No dates should be missing
    TestMissing(claims.CLAIM_DT, 0)

    return claims[claims.RIIPL_ID > 0]


def Classify(claims, t):
    """
    Coalesce dates for codes that match the predefined list of outcomes.
    """
    claim_dt = claims.CLAIM_DT.values

    for outcome, codes in OUTCOMES[t].items():
        print("classifying", outcome)
        outcome_dt = MAX_DT * np.ones_like(claim_dt)
        # For diagnosis codes: for each length of codes, match on a slice of that length.
        if t == "DIAG":
            # Group codes by length.
            codedict = defaultdict(list)
            for code in codes:
                codedict[len(code)].append(code)
            for n, codes in codedict.items():
                i = claims[t + "_CDE"].str.slice(0, n).isin(codes)
                outcome_dt[i] = claim_dt[i]
        # For procedure codes: match on exact codes
        elif t == "PROC":
            i = claims[t + "_CDE"].isin(codes)
            outcome_dt[i] = claim_dt[i]
        
        claims[outcome] = outcome_dt

    return claims


def Prepare(claimsfile, t, start, end):
    outcomes = Classify(Load(claimsfile, t, start, end), t)
    del outcomes["CLAIM_DT"]
    del outcomes[t + "_CDE"]
    return outcomes.groupby("RIIPL_ID")[list(OUTCOMES[t].keys())].min()


def Initial(outcomes):
    """
    Population of Medicaid recipients who received an outcome diagnosis or procedure.

    riipl_id       a Medicaid recipient
    {outcome}      the date of initial diagnosis or procedure for that outcome
    any            the minimum date of an initial outcome diagnosis or procedure
    """
    outcomes["OUTCOME_ANY"] = outcomes.min(axis=1)
    print((outcomes["OUTCOME_ANY"] < MAX_DT).sum(), "of", len(outcomes), "have an adverse outcome")
    return outcomes


if __name__ == "__main__":

    diagfile, procfile, outfile  = sys.argv[1:]
    start = "20070101"
    end   = "20120101"

    outcomes_diag = Prepare(diagfile, "DIAG", start, end)
    outcomes_proc = Prepare(procfile, "PROC", start, end)
    outcomes_all = outcomes_diag.join(outcomes_proc, how="outer").fillna(MAX_DT)

    Initial(outcomes_all).to_csv(outfile, float_format="%g")

# vim: expandtab sw=4 ts=4
