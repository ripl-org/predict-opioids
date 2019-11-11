library(tidyverse)

args <- commandArgs(trailingOnly=TRUE)

csv_path <- args[1]
out_path <- args[2]

csv <- read_csv(csv_path)

csv0 <- csv[!csv$selected]
csv1 <- csv[ csv$selected]

ranges <- c(min(csv1$dw), max(csv1$dw), min(csv1$d), max(csv1$d))
print(ranges)

g <- ggplot(csv, aes(x=d, y=dw)) +
     geom_hline(yintercept=ranges[1], linetype="dotted") +
     geom_hline(yintercept=ranges[2], linetype="dotted") +
     geom_vline(xintercept=ranges[3], linetype="dotted") +
     geom_vline(xintercept=ranges[4], linetype="dotted") +
     geom_abline(slope=1, intercept=0, color="grey") +
     geom_point(data=csv0, color="grey") +
     geom_point(data=csv1, color="red") +
     scale_x_continuous(limits=c(-0.6, 0.6)) +
     scale_y_continuous(limits=c(-0.6, 0.6)) +
     labs(x="Standardized Difference", y="Weighted Standardized Difference")

ggsave(out_path, g)
