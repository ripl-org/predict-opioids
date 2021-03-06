library(tidyverse)
library(scales)

args <- commandArgs(trailingOnly=TRUE)

csv_path <- args[1]
out_path <- args[2]

csv <- read_csv(csv_path)
csv$Decile <- csv$Decile * 0.1
csv$Rho <- factor(csv$Rho, c(0, 0.5, 1, 4.02))

pdf(out_path, width=6.8, height=3.4)
csv %>% ggplot(aes(x=Decile, y=CostRatio, color=Rho)) +
        geom_ribbon(aes(ymin=CostRatioLower, ymax=CostRatioUpper, fill=Rho), alpha=0.25, color=NA) +
        geom_point() +
        labs(x="Cumulative Deciles by Decreasing Risk", y="Break-even Cost Ratio") +
        theme_classic() +
        theme(legend.position=c(0.8, 0.8), plot.title=element_text(face="bold")) +
        scale_x_continuous(limits=c(0.1, 1), breaks=seq(0.1, 1, 0.1), labels=percent_format()) +
        scale_y_continuous(limits=c(-0.05, 0.5), breaks=seq(0, 0.5, 0.1),
                           sec.axis=sec_axis(~ . * 450000, name="Break-even Diversion Cost", breaks=seq(0, 225000, 45000), labels=dollar_format())) +
        scale_color_brewer(expression(rho), labels=c("1"="1.00", "0.5"="0.50", "0"="0.00"), palette="Set2") +
        scale_fill_brewer(expression(rho), labels=c("1"="1.00", "0.5"="0.50", "0"="0.00"), palette="Set2")
dev.off()

