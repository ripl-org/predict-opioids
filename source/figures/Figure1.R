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
        left_join(read_tsv(desc_path, col_names=c("var", "desc")), by="var") %>%
        mutate(category=factor(case_when(grepl("_X_", var)            ~ "Interaction term",
                                         startsWith(var, "MEDICAID")  ~ "Medicaid claims and enrollment",
                                         startsWith(var, "ASHP")      ~ "Medicaid claims and enrollment",
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
                                         TRUE                         ~ "Demographics"),
                               levels=c("Medicaid claims and enrollment",
                                        "Demographics",
                                        "Social benefit and insurance programs",
                                        "Employment",
                                        "Incarceration and criminal justice",
                                        "Interaction term")))

print(table(coef$category))
cats <- select(coef, "var", "category", "desc")
write_csv(cats[order(cats$category, cats$var),], cats_path)

# Random jitter for x axis, proportional to distance from odds ratio of 1
coef$jitter <- runif(nrow(coef), min=-1) * (1 - abs(coef$odds - 1)/1.25)^2

pdf(pdf_path, width=3.4, height=5)
coef %>% ggplot(aes(x=jitter, y=odds, color=category)) +
         geom_point() +
         labs(y="Odds Ratio") +
         scale_x_continuous(limits=c(-1, 1), breaks=c()) +
         scale_y_continuous(limits=c(0, 2.25), breaks=seq(0, 2.25, 0.25)) +
         theme_classic() +
         theme(
               axis.text.x=element_blank(),
               axis.ticks.x=element_blank(),
               axis.title.x=element_blank(),
               axis.text.y=element_text(size=5),
               axis.title.y=element_text(size=8),
               legend.box.background=element_rect(colour="black"),
               legend.position="right",
               legend.text=element_text(size=7),
               legend.title=element_blank()) +
         scale_color_manual("Category",
                            values=c("#E34E38", "#DF9826", "#45AFAF", "#7030A0", "#5B9BD5", "gray"))
dev.off()

# vim: syntax=R expandtab sw=4 ts=4
