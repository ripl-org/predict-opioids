library(dplyr)
library(ggplot2)
library(readr)
library(scales)

args <- commandArgs(trailingOnly=TRUE)

set.seed(args[1])

coef_path <- args[2]
desc_path <- args[3]
cats_path <- args[4]
pdf_path  <- args[5]

coef <- read_csv(coef_path) %>%
        left_join(read_csv(desc_path, col_names=c("var", "desc")), by="var") %>%
        mutate(category=factor(case_when(grepl("_X_", var)            ~ "Interaction term",
                                         startsWith(var, "MEDICAID")  ~ "Medicaid claims and enrollment",
                                         startsWith(var, "ASHP")      ~ "Medicaid claims and enrollment",
                                         startsWith(var, "LANG")      ~ "Medicaid claims and enrollment",
                                         startsWith(var, "DOC")       ~ "Incarceration and criminal justice",
                                         startsWith(var, "ARREST")    ~ "Incarceration and criminal justice",
                                         startsWith(var, "CAR_CRASH") ~ "Incarceration and criminal justice",
                                         startsWith(var, "CITATION")  ~ "Incarceration and criminal justice",
                                         startsWith(var, "DHS")       ~ "Social benefit and insurance programs",
                                         startsWith(var, "SNAP")      ~ "Social benefit and insurance programs",
                                         startsWith(var, "TANF")      ~ "Social benefit and insurance programs",
                                         startsWith(var, "SSI")       ~ "Social benefit and insurance programs",
                                         startsWith(var, "CCAP")      ~ "Social benefit and insurance programs",
                                         startsWith(var, "GPA")       ~ "Social benefit and insurance programs",
                                         startsWith(var, "NAICS")     ~ "Employment",
                                         startsWith(var, "WAGE")      ~ "Employment",
                                         startsWith(var, "UNEMP")     ~ "Employment",
                                         startsWith(var, "TDI")       ~ "Employment",
                                         startsWith(var, "UI")        ~ "Employment",
                                         TRUE                         ~ "Demographics")))

cats <- select(coef, "var", "category", "desc")
write_csv(cats[order(cats$category, cats$var), :], cats_path)

# Random jitter for x axis, proportional to distance from odds ratio of 1
coef$jitter <- runif(rows(coef), min=-0.9, max=0.9) * (1 - abs(coef$odds - 1))^2

pdf(pdf_path, width=6, height=10)
coef %>% ggplot(aes(x=jitter, y=odds, color=category)) +
         geom_point(shape=1) +
         labs(y="Odds Ratio") +
         scale_y_continuous(limits=c(0, 2), breaks=seq(0, 2, 0.2)) +
         theme_classic() +
         theme(legend.position=c(0.5, 0.5)) +
         scale_color_brewer("Category", palette="Set2")
dev.off()

# vim: syntax=R expandtab sw=4 ts=4
