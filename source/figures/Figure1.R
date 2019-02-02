library(boot)
library(dplyr)
library(devEMF)
library(ggplot2)
library(readr)
library(scales)

min_cell_size <- 11
thresholds <- seq(0, 1, 0.01)

args <- commandArgs(trailingOnly=TRUE)

set.seed(args[1])

n_bootstrap <- strtoi(args[2])
y_pred_path <- args[3]
out_path    <- args[4]

y_pred <- read_csv(y_pred_path)

cost_ratio <- function(original, indices, threshold) {
  data <- original[indices,]
  tp <- sum(data$y_pred > threshold & data$y_test == 1)
  fp <- sum(data$y_pred > threshold & data$y_test == 0)
  return(tp/(fp+tp))
}

counts <- sapply(thresholds, function(t) sum(y_pred$y_pred > t))
thresholds <- thresholds[counts > min_cell_size]

bootstrap <- function(threshold) {
  b <- boot(data=y_pred, statistic=cost_ratio, R=n_bootstrap, threshold=threshold)
  ci <- boot.ci(b, type="perc")
  return(c(b$t0, ci$percent[4], ci$percent[5]))
}

bootstraps <- t(sapply(thresholds, bootstrap))

df <- data.frame(threshold=thresholds,
                 cost_ratio=bootstraps[,1],
                 ci_min=bootstraps[,2],
                 ci_max=bootstraps[,3])
print(df)

emf(out_path, width=6, height=4)
df %>% ggplot() +
       geom_ribbon(aes(x=threshold, ymin=ci_min, ymax=ci_max), fill="gray") +
       geom_line(aes(x=threshold, y=cost_ratio), color="black") +
       labs(x="Risk threshold for classifying an adverse outcome", y="Cost ratio") +
       theme(legend.position=c(0.7, 0.2)) +
       theme_classic() +
       scale_x_continuous(limits=c(0, 0.5), breaks=seq(0, 0.5, 0.1)) +
       scale_y_continuous(limits=c(0, 1), breaks=seq(0, 1, 0.2))
dev.off()

