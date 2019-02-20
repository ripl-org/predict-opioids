library(dplyr)
library(stringr)
library(readr)
library(reshape2)
library(scales)

args <- commandArgs(trailingOnly=TRUE)

outcomes_path  <- args[1]
demo_path      <- args[2]
census_path    <- args[3]
wages_path     <- args[4]
benefits_path  <- args[5]
family_path    <- args[6]
incarc_path    <- args[7]
ma_enroll_path <- args[8]
diagnoses_path <- args[9]
ma_ids_path    <- args[10]
fpl_path       <- args[11]
out_path       <- args[12]

# Load inputs
outcomes  <- read_csv(outcomes_path)
demo      <- read_csv(demo_path)
census    <- read_csv(census_path)
wages     <- read_csv(wages_path)
benefits  <- read_csv(benefits_path)
family    <- read_csv(family_path)
incarc    <- read_csv(incarc_path)
ma_enroll <- read_csv(ma_enroll_path)
diagnoses <- read_csv(diagnoses_path)
ma_ids    <- read_csv(ma_ids_path)
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
                                     TRUE ~ ">60")),
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
                    variable="Race",
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
             mutate(value=factor(case_when(value >= belowfpl75 ~ paste0("At least ", percent(belowfpl75)),
                                           is.na(value) ~ "NA",
                                           TRUE ~ "Otherwise")),
                    inner_rank=case_when(value == "NA" ~ 3,
                                         value == "Otherwise" ~ 2,
                                         TRUE ~ 1),
                    variable="Blockgroup fraction of residents below FPL",
                    rank=6)) %>%
       rbind(wages %>%
             select(RIIPL_ID, WAGES_SUM) %>%
             melt(id.vars=c("RIIPL_ID")) %>%
             mutate(value=factor(case_when(value > 15000 ~ ">$15000",
                                           value > 7500 ~ "$7500-$15000",
                                           value > 2500 ~ "$2500-$7500",
                                           value > 0 ~ "<$2500",
                                           TRUE ~ "$0 or NA")),
                    inner_rank=case_when(value == "<$2500" ~ 1,
                                         value == "$2500-$7500" ~ 2,
                                         value == "$7500-$15000" ~ 3,
                                         value == ">$15000" ~ 4,
                                         value == "$0 or NA" ~ 5),
                    variable="Wages in previous year",
                    rank=7)) %>%
       rbind(benefits %>%
             select(RIIPL_ID, SNAP_PAYMENTS) %>%
             melt(id.vars=c("RIIPL_ID")) %>%
             mutate(value=factor(ifelse(value > 0, "Yes", "No")),
                    inner_rank=case_when(value == "Yes" ~ 1,
                                         value == "No" ~ 2),
                    variable="Received SNAP in previous year",
                    rank=8)) %>%
       rbind(benefits %>%
             select(RIIPL_ID, SSI_SUPPLEMENT) %>%
             melt(id.vars=c("RIIPL_ID")) %>%
             mutate(value=factor(ifelse(value > 0, "Yes", "No")),
                    inner_rank=case_when(value == "Yes" ~ 1,
                                         value == "No" ~ 2),
                    variable="Received SSI in previous year",
                    rank=9)) %>%
       rbind(benefits %>%
             select(RIIPL_ID, UI_PAYMENTS) %>%
             melt(id.vars=c("RIIPL_ID")) %>%
             mutate(value=factor(ifelse(value > 0, "Yes", "No")),
                    inner_rank=case_when(value == "Yes" ~ 1,
                                         value == "No" ~ 2),
                    variable="Received UI in previous year",
                    rank=10)) %>%
       rbind(benefits %>%
             select(RIIPL_ID, TDI_PAYMENTS) %>%
             melt(id.vars=c("RIIPL_ID")) %>%
             mutate(value=factor(ifelse(value > 0, "Yes", "No")),
                    inner_rank=case_when(value == "Yes" ~ 1,
                                         value == "No" ~ 2),
                    variable="Received TDI in previous year",
                    rank=11)) %>%
       rbind(family %>%
             select(RIIPL_ID, N_CHILD) %>%
             melt(id.vars=c("RIIPL_ID")) %>%
             mutate(value=factor(case_when(value >= 2 ~ "2+",
                                           value == 1 ~ "1",
                                           TRUE ~ "0 or NA")),
                    inner_rank=1,
                    variable="# of children in SNAP household in previous year",
                    rank=12)) %>%
       rbind(incarc %>%
             select(RIIPL_ID, INCARC_EVER) %>%
             melt(id.vars=c("RIIPL_ID")) %>%
             mutate(value=factor(ifelse(value > 0, "Yes", "No")),
                    inner_rank=case_when(value == "Yes" ~ 1,
                                         value == "No" ~ 2),
                    variable="Incarcerated in previous year",
             rank=13)) %>%
       rbind(ma_enroll %>%
             select(RIIPL_ID, DISABLED) %>%
             melt(id.vars=c("RIIPL_ID")) %>%
             mutate(value=factor(ifelse(value > 0, "Disabled", "Not disabled")),
                    inner_rank=1,
                    variable="Medicaid-eligible due to disablement",
                    rank=14)) %>%
       rbind(diagnoses %>%
             select(RIIPL_ID, MENTAL_HEALTH) %>%
             melt(id.vars=c("RIIPL_ID")) %>%
             mutate(value=factor(ifelse(value > 0, "1+", "0")),
                    inner_rank=1,
                    variable="# of mental health diagnoses in previous year",
                    rank=15)) %>%
       rbind(ma_ids %>%
          select(RIIPL_ID, N_ID) %>%
          melt(id.vars=c("RIIPL_ID")) %>%
          mutate(value=factor(ifelse(value > 1, "2+", 1)),
                 inner_rank=1,
                 variable="# of Medicaid IDs",
                 rank=16)) %>%
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
                      variable=ifelse(rnum == 1, variable, "")) %>%
               ungroup() %>%
               select(variable, value, n, pct_positive)

write.table(stats_table, file=out_path,
            sep="\t", row.names=FALSE, col.names=FALSE, na="", quote=FALSE)
