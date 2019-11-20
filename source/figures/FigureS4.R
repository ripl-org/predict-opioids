library(tidyverse)
library(scales)
library(ggrepel)

args <- commandArgs(trailingOnly=TRUE)

set.seed(args[1])

coef_path <- args[2]
desc_path <- args[3]
cats_path <- args[4]
pdf_path  <- args[5]

coef <- read_csv(coef_path) %>%
        filter(var != "intercept") %>%
        left_join(read_tsv(desc_path, col_names=c("var", "desc")), by="var") %>%
        mutate(category=factor(case_when(grepl("_X_", var)            ~ "Interaction term",
                                         startsWith(var, "MEDICAID")  ~ "Medicaid claims/enrollment",
                                         startsWith(var, "ASHP")      ~ "Medicaid claims/enrollment",
                                         startsWith(var, "DOC")       ~ "Criminal justice",
                                         startsWith(var, "ARREST")    ~ "Criminal justice",
                                         startsWith(var, "CAR_CRASH") ~ "Criminal justice",
                                         startsWith(var, "CITATION")  ~ "Criminal justice",
                                         startsWith(var, "DHS")       ~ "Social benefit/insurance programs",
                                         startsWith(var, "SNAP")      ~ "Social benefit/insurance programs",
                                         startsWith(var, "TANF")      ~ "Social benefit/insurance programs",
                                         startsWith(var, "SSI")       ~ "Social benefit/insurance programs",
                                         startsWith(var, "CCAP")      ~ "Social benefit/insurance programs",
                                         startsWith(var, "GPA")       ~ "Social benefit/insurance programs",
                                         startsWith(var, "NAICS")     ~ "Employment",
                                         startsWith(var, "WAGE")      ~ "Employment",
                                         startsWith(var, "UNEMP")     ~ "Employment",
                                         startsWith(var, "TDI")       ~ "Employment",
                                         startsWith(var, "UI")        ~ "Employment",
                                         TRUE                         ~ "Demographics"),
                               levels=c("Medicaid claims/enrollment",
                                        "Demographics",
                                        "Social benefit/insurance programs",
                                        "Employment",
                                        "Criminal justice",
                                        "Interaction term")))

print(table(coef$category))
cats <- select(coef, "var", "category", "desc")
write_csv(cats[order(cats$category, cats$var),], cats_path)

coef$jitter <- runif(nrow(coef), min=-1) * (1 - abs(coef$odds - 1)/4.5)^2
labels <- subset(coef, odds < 0.75 | odds > 1.25)

pdf(pdf_path, width=6.8, height=3.5)
coef %>% ggplot(aes(x=jitter, y=odds, label=desc)) +
         geom_point(shape=1) +
         geom_text_repel(data=labels,
                         nudge_x=1.75-labels$jitter,
                         direction="y",
                         hjust=0,
                         segment.size=0.2,
			 segment.alpha=0.3,
                         show.legend=FALSE,
                         size=2.25) +
         labs(y="Odds Ratio") +
         scale_x_continuous(limits=c(min(coef$jitter), 10), breaks=c()) +
         scale_y_continuous(limits=c(0, 5.5), breaks=seq(0, 5.5, 0.25)) +
         theme_classic() +
         theme(
               axis.text.x=element_blank(),
               axis.ticks.x=element_blank(),
               axis.title.x=element_blank(),
               axis.text.y=element_text(size=5),
               axis.title.y=element_text(size=8))
dev.off()

# vim: syntax=R expandtab sw=4 ts=4
