library(dplyr)
library(ggplot2)
library(gridExtra)
library(readr)
library(reshape2)
library(scales)

args <- commandArgs(trailingOnly=TRUE)

csv_path <- args[1]
out_path <- args[2]

csv <- read_csv(csv_path)

plot <- function(df, title, grp_title) {
    return(df %>%
           ggplot(aes(x=Decile, y=CostRatio, color=Demographic)) +
           ggtitle(title) +
           geom_ribbon(aes(ymin=CostRatioLower, ymax=CostRatioUpper, fill=Race), alpha=0.25, color=NA) +
           geom_point(shape=1) +
           labs(x="Cumulative Deciles by Decreasing Risk", y="Break-even Cost Ratio") +
           theme_classic() +
           theme(legend.position=c(0.8, 0.8), plot.title=element_text(face="bold")) +
           scale_x_continuous(~ . * 0.1, limits=c(1, 10), breaks=seq(1, 10), labels=percent) +
           scale_y_continuous(limits=c(0, 0.3), breaks=seq(0, 0.3, 0.05),
                              sec.axis=sec_axis(~ . * 450000, name="Break-even Diversion Cost", breaks=seq(0, 135000, 22500), labels=dollar_format())) +
           scale_color_brewer(grp_title, labels=grp_labels, palette="Set2") +
           scale_fill_brewer(grp_title, labels=grp_labels, palette="Set2"))
}

pdf(out_path, width=6, height=8)
grid.arrange(plot(filter(csv, Demographic=="RACE_BLACK" | Demographic=="RACE_HISPANIC" | Demographic=="RACE_WHITE"),
		  "a",
		  "Race/ethnicity",
                  c("RACE_BLACK"="African-American", "RACE_HISPANIC"="Hispanic", "RACE_WHITE"="White")),
	     plot(filter(csv, Demographic=="INCARC" | Demographic=="NINCARC"),
		  "b",
                  "Incarcerated during\nprevious year",
		  c("INCARC"="At least once", "NINCARC"="Never")),
	     plot(filter(csv, Demographic=="DISABLED" | Demographic=="NDISABLED"),
		  "c",
                  "Medicaid-eligible\ndue to disablement",
                  c("DISABLED"="Yes", "NDISABLED"="No")),
             nrow=3)
dev.off()

