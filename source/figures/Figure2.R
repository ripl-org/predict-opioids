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
csv$Alpha <- factor(csv$Alpha)

pdf(out_path, width=6.8, height=6)
csv %>% ggplot(aes(x=Decile, y=CostRatio, color=Alpha)) +
        geom_ribbon(aes(ymin=CostRatioLower, ymax=CostRatioUpper, fill=Alpha), alpha=0.25, color=NA) +
        geom_point(shape=1) +
        labs(x="Cumulative Deciles by Decreasing Risk", y="Break-even Cost Ratio") +
        theme_classic() +
        theme(legend.position=c(0.8, 0.8), plot.title=element_text(face="bold")) +
        scale_x_continuous(limits=c(0.1, 1), breaks=seq(0.1, 1, 0.1), labels=percent) +
        scale_y_continuous(limits=c(0, 0.5), breaks=seq(0, 0.5, 0.1),
                           sec.axis=sec_axis(~ . * 450000, name="Break-even Diversion Cost", breaks=seq(0, 225000, 45000), labels=dollar_format())) +
        scale_color_brewer("alpha", labels=c("1"="1.000"), palette="Set2") +
        scale_fill_brewer("alpha", labels=c("1"="1.000"), palette="Set2")
dev.off()

