import os
from CONSTANTS import CONSTANTS

try:
    # Removes symlink only, not original directory
    os.remove("input")
except OSError:
    pass

os.symlink("/data/opioid/opioidv11", "input")

exec(compile(open("./source/lib/SCons/setup.py").read(), "./source/lib/SCons/setup.py", 'exec'))

env.CacheDir("/data/opioid/{}-cache".format(env.RIIPL_PROJECT))
env.Decider("MD5-timestamp")

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

# vim: syntax=python expandtab sw=4 ts=4
