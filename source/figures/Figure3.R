library(tidyverse)
library(scales)
library(gridExtra)

args <- commandArgs(trailingOnly=TRUE)

csv_path <- args[1]
out_path <- args[2]

csv <- read_csv(csv_path)
csv$Decile <- csv$Decile * 0.1

plot <- function(df, title, grp_title, grp_labels) {
    return(df %>%
           ggplot(aes(x=Decile, y=FDR, color=Demographic)) +
           ggtitle(title) +
           geom_ribbon(aes(ymin=FDRLower, ymax=FDRUpper, fill=Demographic), alpha=0.25, color=NA) +
           geom_point() +
           labs(x="Cumulative Deciles by Decreasing Risk", y="False Discovery Rate") +
           theme_classic() +
           theme(legend.position=c(0.8, 0.3), plot.title=element_text(face="bold")) +
           scale_x_continuous(limits=c(0.1, 1), breaks=seq(0.1, 1, 0.1), labels=percent_format(accuracy=1)) +
           scale_y_continuous(limits=c(0, 1), breaks=seq(0, 1, 0.2)) +
           scale_color_brewer(grp_title, labels=grp_labels, palette="Set2") +
           scale_fill_brewer(grp_title, labels=grp_labels, palette="Set2"))
}

pdf(out_path, width=13.6, height=3.4)
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

