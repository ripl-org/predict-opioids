library(dplyr)
library(stringr)
library(readr)
library(reshape2)
library(scales)

args <- commandArgs(trailingOnly=TRUE)

outcomes_path  <- args[1]
demo_path      <- args[2]
census_path    <- args[3]
household_path <- args[4]
payments_path  <- args[5]
wages_path     <- args[6]
fpl_path       <- args[7]
out_path       <- args[8]

# Load inputs
outcomes  <- read_csv(outcomes_path)
demo      <- read_csv(demo_path)
census    <- read_csv(census_path)
household <- read_csv(household_path)
payments  <- read_csv(payments_path)
wages     <- read_csv(wages_path)
fpl       <- read_csv(fpl_path)

# Calculate top quantile for FPL
fpl <- fpl[2:nrow(fpl), c(4, 6)]
colnames(fpl) <- c("total", "belowfpl")
fpl <- as.data.frame(apply(fpl, 2, as.numeric)) %>%
       mutate(pct_belowfpl=belowfpl/total)
belowfpl75 <- quantile(fpl$pct_belowfpl, na.rm=TRUE)[4]

# Build population
pop <- demo %>%
       select(RIIPL_ID, AGE) %>%
       melt(id.vars=c("RIIPL_ID")) %>%
       mutate(value=factor(case_when(is.na(value) ~ "NA",
                                     value <  18 ~ "<18",
                                     value <= 45 ~ "18-45",
                                     value <= 60 ~ "45-60",
                                     TRUE ~ "61+")),
              inner_rank=1,
              variable="Age",
              rank=1) %>%
       rbind(demo %>%
             select(RIIPL_ID, RACE) %>%
             melt(id.vars=c("RIIPL_ID")) %>%
             mutate(value=factor(case_when(value %in% c("White", "Black", "Hispanic") ~ value,
                                           is.na(value) ~ "NA",
                                           TRUE ~ "Other")),
                    inner_rank=case_when(value == "White" ~ 1,
                                         value == "Black" ~ 2,
                                         value == "Hispanic" ~ 3,
                                         value == "Other" ~ 4,
                                         value == "NA" ~ 5),
                    variable="Race/Ethnicity",
                    rank=2)) %>%
       rbind(demo %>%
             select(RIIPL_ID, SEX) %>%
             melt(id.vars=c("RIIPL_ID")) %>%
             mutate(value=factor(case_when(value == "F" ~ "Female",
                                           value == "M" ~ "Male",
                                           TRUE ~ "NA")),
                    inner_rank=case_when(value == "Female" ~ 1,
                                         value == "Male" ~ 2,
                                         value == "NA" ~ 3),
                    variable="Sex",
                    rank=3)) %>%
       rbind(demo %>%
             select(RIIPL_ID, MARITAL_STATUS) %>%
             melt(id.vars=c("RIIPL_ID")) %>%
             mutate(value=factor(case_when(value == 1 ~ "Married",
                                           value == 0 ~ "Not married",
                                           TRUE ~ "NA")),
                    inner_rank=case_when(value == "Married" ~ 1,
                                         value == "Not married" ~ 2,
                                         value == "NA" ~ 3),
                    variable="Marital status",
                    rank=4)) %>%
       rbind(demo %>%
             select(RIIPL_ID, BMI) %>%
             melt(id.vars=c("RIIPL_ID")) %>%
             mutate(value=factor(case_when(is.na(value) ~ "NA",
                                           value < 18.5 ~ "Underweight (<18.5)",
                                           value < 25 ~ "Normal (18.5-25)",
                                           value < 30 ~ "Overweight (25-30)",
                                           TRUE ~ "Obese (>30)")),
                    inner_rank=case_when(value == "Underweight (<18.5)" ~ 1,
                                         value == "Normal (18.5-25)" ~ 2,
                                         value == "Overweight (25-30)" ~ 3,
                                         value == "Obese (>30)" ~ 4,
                                         value == "NA" ~ 5),
                    variable="Body mass index",
                    rank=5)) %>%
       rbind(census %>%
             select(RIIPL_ID, BLKGRP_BELOWFPL) %>%
             melt(id.vars=c("RIIPL_ID")) %>%
             mutate(value=factor(case_when(value >= belowfpl75 ~ paste("At least", percent(belowfpl75)),
                                           is.na(value) ~ "NA",
                                           TRUE ~ "Otherwise")),
                    inner_rank=case_when(value == "NA" ~ 3,
                                         value == "Otherwise" ~ 2,
                                         TRUE ~ 1),
                    variable="Blockgroup fraction of residents below FPL",
                    rank=6)) %>%
       rbind(payments %>%
             select(RIIPL_ID, SNAP_PAYMENTS) %>%
             melt(id.vars=c("RIIPL_ID")) %>%
             mutate(value=factor(ifelse(value > 0, "Yes", "No")),
                    inner_rank=case_when(value == "Yes" ~ 1,
                                         value == "No" ~ 2),
                    variable="Received SNAP in previous year",
                    rank=8)) %>%
       rbind(payments %>%
             select(RIIPL_ID, SSI_SUPPLEMENT) %>%
             melt(id.vars=c("RIIPL_ID")) %>%
             mutate(value=factor(ifelse(value > 0, "Yes", "No")),
                    inner_rank=case_when(value == "Yes" ~ 1,
                                         value == "No" ~ 2),
                    variable="Received SSI in previous year",
                    rank=9)) %>%
       rbind(payments %>%
             select(RIIPL_ID, UI_PAYMENTS) %>%
             melt(id.vars=c("RIIPL_ID")) %>%
             mutate(value=factor(ifelse(value > 0, "Yes", "No")),
                    inner_rank=case_when(value == "Yes" ~ 1,
                                         value == "No" ~ 2),
                    variable="Received UI in previous year",
                    rank=10)) %>%
       rbind(payments %>%
             select(RIIPL_ID, TDI_PAYMENTS) %>%
             melt(id.vars=c("RIIPL_ID")) %>%
             mutate(value=factor(ifelse(value > 0, "Yes", "No")),
                    inner_rank=case_when(value == "Yes" ~ 1,
                                         value == "No" ~ 2),
                    variable="Received TDI in previous year",
                    rank=11)) %>%
       rbind(household %>%
             select(RIIPL_ID, DHS_HH_SIZE) %>%
             melt(id.vars=c("RIIPL_ID")) %>%
             mutate(value=factor(case_when(value >= 2 ~ "2+",
                                           value == 1 ~ "1",
                                           TRUE ~ "0 or NA")),
                    inner_rank=1,
                    variable="Children in DHS household in previous year",
                    rank=12)) %>%
       rbind(wages %>%
             select(RIIPL_ID, WAGES_AVG) %>%
             melt(id.vars=c("RIIPL_ID")) %>%
             mutate(value=factor(case_when(value > 15000 ~ ">\\$15000",
                                           value > 7500 ~ "\\$7500-\\$15000",
                                           value > 2500 ~ "\\$2500-\\$7500",
                                           value > 0 ~ "<\\$2500",
                                           TRUE ~ "\\$0 or NA")),
                    inner_rank=case_when(value == "<\\$2500" ~ 1,
                                         value == "\\$2500-\\$7500" ~ 2,
                                         value == "\\$7500-\\$15000" ~ 3,
                                         value == ">\\$15000" ~ 4,
                                         value == "\\$0 or NA" ~ 5),
                    variable="Average quarterly wages in previous year",
                    rank=7)) %>%
       mutate(RIIPL_ID=as.numeric(RIIPL_ID)) %>%
       inner_join(outcomes, by="RIIPL_ID")

stats_table <- dcast(pop, rank + variable + inner_rank + value ~ OUTCOME_ANY, fun.aggregate=length)
names(stats_table) <- c("rank", "variable", "inner_rank", "value", "n_negative", "n_positive")

stats_table <- stats_table %>%
               mutate(n=n_positive + n_negative,
                      p_positive=n_positive / n,
                      pct_positive=percent(p_positive)) %>%
               group_by(rank) %>%
               mutate(rnum=1:n(),
                      variable=ifelse(rnum == 1, paste0("\\textbf{", variable, "}"), "")) %>%
               ungroup() %>%
               select(variable, value, n, pct_positive)

stats_table$value <- str_replace(stats_table$value, "%", " percent")
stats_table$pct_positive <- str_replace(stats_table$pct_positive, "%", "")

write("\\begin{tabular}{llrr}", file=out_path)
write("\\em Variable & \\em Value & \\em N & \\em \\% Outcome \\\\[0.5em]", file=out_path, append=TRUE)
write.table(stats_table, file=out_path, append=TRUE,
            sep=" & ", row.names=FALSE, col.names=FALSE, na="", quote=FALSE, eol="\\% \\\\\n")
write("\\end{tabular}", file=out_path, append=TRUE)
