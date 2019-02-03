Analysis code to reproduce results from the manuscript:

Hastings JS, Howison M, Inman S. Improving policy with data and machine learning to prevent opioid dependence.

This project utilizes the [predictive modeling
template](https://github.com/ripl-org/predictive-template) from [Research
Improving People's Lives](https://ripl.org).  The **SConstuct** file defines
dependencies between analysis steps and automates the analysis run from start
to finish, using the extensible [SCons](http://scons.org/) software
construction tool.

The code is organized as follows:

| Subdirectory | Description |
| --- | --- |
| **input** | Raw data that are not stored in the repo. Please consult the awknowledgements section of the manuscript for more information on data sources. |
| **schema** | Schema files that describe the columns and data types in the raw data. |
| **output** | The output of the analysis, which is also not stored in the repo. Figures and tables will be located in **output/figures** and **output/tables**. |
| **scratch** | Staging area for large intermediate files. These files will be cached by SCons, so they often do not need to be recomputed again after they have been created the first time. SCons caches the output base on the full checksums of all dependencies. |
| **source/lib** | Library code from the predictive modeling template. |
| **source/inputs** | Source files for staging raw files from **input** in an Oracle database using the schema files. |.
| **source/populations** | Source files for defining the population of Medicaid recipients who received an initial opioid prescription between 2006-2012. |
| **source/outcomes** | Source files for defining adverse opioid outcomes. |
| **source/features** | Source files for calculating baseline characteristics of the population, used in Table S1. |
| **source/tensors** | Source files for building tensors from administrative records. |
| **source/models** | Source files for training and tuning neural networks on the tensors. |
| **source/figures** | Source files for generating Fig. 1-2 and S1-S2. |
| **source/tables** | Source files for generating Table 1-2 and S1. |

## Contributors

Mark Howison  
Sarah Inman  
Miraj Shah
