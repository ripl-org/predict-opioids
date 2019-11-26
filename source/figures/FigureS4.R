library(tidyverse)
library(scales)

args <- commandArgs(trailingOnly=TRUE)

csv_path <- args[1]
out_path <- args[2]

csv <- read_csv(csv_path)
csv$Decile <- csv$Decile * 0.1
csv$DiversionCost <- as.factor(csv$DiversionCost)

pdf(out_path, width=6.8, height=3.4)
csv %>% ggplot(aes(x=Decile, y=Rho, color=DiversionCost)) +
        geom_ribbon(aes(ymin=RhoLower, ymax=RhoUpper, fill=DiversionCost), alpha=0.25, color=NA) +
        geom_point() +
        labs(x="Cumulative Deciles by Decreasing Risk", y="rho") +
        theme_classic() +
        theme(legend.position=c(0.8, 0.8), plot.title=element_text(face="bold")) +
        scale_x_continuous(limits=c(0.1, 1), breaks=seq(0.1, 1, 0.1), labels=percent_format(accuracy=1)) +
        scale_color_brewer(expression(alpha), labels=dollar_format(), palette="Set2") +
        scale_fill_brewer(expression(alpha), labels=dollar_format(), palette="Set2")
dev.off()

