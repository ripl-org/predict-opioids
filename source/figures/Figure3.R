library(dplyr)
library(ggplot2)
library(gridExtra)
library(readr)
library(reshape2)
library(scales)

args <- commandArgs(trailingOnly=TRUE)

csv_path <- args[1]
out_path <- args[2]

csv <- read_csv(csv_file)

pdf(out_path, width=6, height=8)
grid.arrange(csv %>% select(Race="All") %>%
                     ggplot(aes(x=Decile, y=CostRatio)) +
                     ggtitle("a") +
                     geom_ribbon(aes(ymin=CostRatioLower, ymax=CostRatioUpper), alpha=0.25) +
                     geom_point() +
                     labs(x="", y="Cost Ratio") +
                     theme_classic() +
                     scale_x_continuous(limits=c(1, 10), breaks=seq(1, 10)) +
                     scale_y_continuous(limits=c(0, 0.3), breaks=seq(0, 0.3, 0.05), sec.axis=sec_axis(~ . * 450000, name="Diversion Cost"))
	     csv %>% select(Race!="All") %>%
                     ggplot(aes(x=Decile, y=CostRatio, color=Race)) +
                     ggtitle("b") +
                     geom_ribbon(aes(ymin=CostRatioLower, ymax=CostRatioUpper, fill=Race), alpha=0.25, color=NA) +
                     geom_point() +
                     labs(x="Cumulative Deciles by Decreasing Risk", y="Cost Ratio") +
                     theme_classic() +
                     theme(legend.position="right", plot.title=element_text(face="bold")) +
                     scale_x_continuous(limits=c(1, 10), breaks=seq(1, 10)) +
                     scale_y_continuous(limits=c(0, 0.3), breaks=seq(0, 0.3, 0.05), sec.axis=sec_axis(~ . * 450000, name="Diversion Cost"))
                     scale_color_brewer("Race/ethnicity", labels=c("Black"="African-American"), palette="Set2") +
                     scale_fill_brewer("Race/ethnicity", labels=c("Black"="African-American"), palette="Set2"),
             nrow=2)
dev.off()

