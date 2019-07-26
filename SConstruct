import os
from CONSTANTS import CONSTANTS

try:
    # Removes symlink only, not original directory
    os.remove("input")
except OSError:
    pass

os.symlink("/data/opioid/opioidv11", "input")

exec(compile(open("./source/lib/SCons/setup.py").read(), "./source/lib/SCons/setup.py", 'exec'))

env.CacheDir("/data/opioid/{}-cache".format(env.PROJECT_KEY))
env.Decider("MD5-timestamp")

# Export constant values and a master list of tables.
constants = dict((k, Value(v)) for k, v in CONSTANTS.items())
Export("constants")

# List of all tables loaded in inputs
tables = ["address",
          "arrests",
          "car_crashes",
          "cci",
          "ccs",
          "citations",
          "dhs_per",
          "dhs_relations",
          "diag_corr",
          "dim_aid_ctg_cde",
          "dim_date",
          "dlt_ui_payments",
          "dlt_wage",
          "doc_events",
          "doc_ident",
          "doc_sentences",
          "enrolled",
          "eohhs_recip_demo",
          "eohhs_recip_x_ssn",
          "household",
          "lookback",
          "longterm_panel",
          "medicaid_claims",
          "medicaid_diag_cde",
          "medicaid_enrollment_2",
          "medicaid_pharmacy",
          "medicaid_proc_cde",
          "mega_addr",
          "mega_demo",
          "mega_pay",
          "ndc_opioids",
          "outcomes_all",
          "police_demo",
          "population",
          "proc_corr"]
tables = dict((table, SQLTable("{}_{}".format(env.PROJECT_KEY, table)))
               for table in tables)
Export("tables")

# Inputs
env.SConscript("source/inputs/Make")

# Populations
env.SConscript("source/populations/Make")

# Outcomes
env.SConscript("source/outcomes/Make")

# Features
env.SConscript("source/features/Make")

# Tensors
env.SConscript("source/tensors/Make")

# Models
env.SConscript("source/models/Make")

# Figures
env.SConscript("source/figures/Make")

# Tables
env.SConscript("source/tables/Make")

# Appendix
env.SConscript("source/appendix/Make")

# vim: syntax=python expandtab sw=4 ts=4
