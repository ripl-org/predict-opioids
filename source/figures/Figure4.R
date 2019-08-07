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
csv$Decile <- csv$Decile * 0.1

plot <- function(df, title, grp_title, grp_labels) {
    return(df %>%
           ggplot(aes(x=Decile, y=CostRatio, color=Demographic)) +
           ggtitle(title) +
           geom_ribbon(aes(ymin=CostRatioLower, ymax=CostRatioUpper, fill=Demographic), alpha=0.25, color=NA) +
           geom_point() +
           labs(x="Cumulative Deciles by Decreasing Risk", y="Break-even Cost Ratio") +
           theme_classic() +
           theme(legend.position=c(0.8, 0.8), plot.title=element_text(face="bold")) +
           scale_x_continuous(limits=c(0.1, 1), breaks=seq(0.1, 1, 0.1), labels=percent_format(accuracy=1)) +
           scale_y_continuous(limits=c(0, 0.5), breaks=seq(0, 0.5, 0.1),
                              sec.axis=sec_axis(~ . * 450000, name="Break-even Diversion Cost", breaks=seq(0, 225000, 45000), labels=dollar_format())) +
           scale_color_brewer(grp_title, labels=grp_labels, palette="Set2") +
           scale_fill_brewer(grp_title, labels=grp_labels, palette="Set2"))
}

pdf(out_path, width=13.4, height=3.4)
grid.arrange(plot(filter(csv, Demographic=="RACE_WHITE" | Demographic=="RACE_MINORITY"),
		  "a",
		  "Race/ethnicity",
                  c("RACE_WHITE"="White", "RACE_MINORITY"="Minority")),
	     plot(filter(csv, Demographic=="INCARC" | Demographic=="NINCARC"),
		  "b",
                  "Incarcerated during\nprevious year",
		  c("INCARC"="At least once", "NINCARC"="Never")),
	     plot(filter(csv, Demographic=="DISABLED" | Demographic=="NDISABLED"),
		  "c",
                  "Medicaid-eligible\ndue to disablement",
                  c("DISABLED"="Yes", "NDISABLED"="No")),
             ncol=3)
dev.off()

