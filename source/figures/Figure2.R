library(boot)
library(dplyr)
library(devEMF)
library(ggplot2)
library(gridExtra)
library(readr)
library(reshape2)
library(scales)

min_cell_size <- 11
thresholds <- seq(0, 1, 0.01)

args <- commandArgs(trailingOnly=TRUE)

set.seed(args[1])

n_bootstrap    <- strtoi(args[2])
y_pred_path    <- args[3]
pop_path       <- args[4]
demo_path      <- args[5]
incarc_path    <- args[6]
ma_enroll_path <- args[7]
out_path       <- args[8]

y_pred    <- read_csv(y_pred_path)
pop       <- read_csv(pop_path)
demo      <- read_csv(demo_path)
incarc    <- read_csv(incarc_path)
ma_enroll <- read_csv(ma_enroll_path)

print(paste0("testing individuals: ", nrow(y_pred)))

y_pred$RACE <- demo %>% merge(pop, by="RIIPL_ID") %>% filter(SUBSET == "TESTING") %>% select(RACE)
y_pred$INCARC <- incarc %>% merge(pop, by="RIIPL_ID") %>% filter(SUBSET == "TESTING") %>% select("INCARC_EVER")
y_pred$DISABLED <- ma_enroll %>% merge(pop, by="RIIPL_ID") %>% filter(SUBSET == "TESTING") %>% select(DISABLED)

fdr <- function(original, indices, threshold) {
  data <- original[indices,]
  tp <- sum(data$y_pred > threshold & data$y_test == 1)
  fp <- sum(data$y_pred > threshold & data$y_test == 0)
  return(fp/(fp+tp))
}

bootstrap <- function(threshold, data) {
  b <- boot(data=data, statistic=fdr, R=n_bootstrap, threshold=threshold)
  ci <- boot.ci(b, type="perc")
  return(c(b$t0, ci$percent[4], ci$percent[5]))
}

group_bootstraps <- function(grp_var, grps) {
  df <- data.frame()
  for (grp in grps) {
    data <- y_pred[which(y_pred[grp_var] == grp), c("y_pred", "y_test")]
    counts <- sapply(thresholds, function(t) sum(data$y_pred > t))
    bootstraps <- sapply(thresholds[counts > min_cell_size], bootstrap, data=data)
    df <- rbind(df, data.frame(threshold=thresholds[counts > min_cell_size],
                               grp=rep(as.character(grp), sum(counts > min_cell_size)),
                               fdr=bootstraps[1,],
                               ci_min=bootstraps[2,],
                               ci_max=bootstraps[3,]))
  }
  return(df)
}

plot <- function(df, grp_var_label, x_label, y_label, grp_labels, title) {
  return(df %>% ggplot(aes(x=threshold, y=fdr, color=grp)) +
                ggtitle(title) +
                geom_ribbon(aes(ymin=ci_min, ymax=ci_max, fill=grp), alpha=0.25, color=NA) +
                geom_line() +
                labs(x=x_label, y=y_label) +
                theme_classic() +
                theme(legend.position="right", plot.title=element_text(face="bold")) +
                scale_x_continuous(limits=c(0, 0.5), breaks=seq(0, 0.5, 0.1)) +
                scale_y_continuous(limits=c(0, 1), breaks=seq(0, 1, 0.2)) +
                scale_color_brewer(grp_var_label, labels=grp_labels, palette="Set2") +
                scale_fill_brewer(grp_var_label, labels=grp_labels, palette="Set2"))
}

emf(out_path, width=6, height=8)
grid.arrange(plot(group_bootstraps("RACE", c("Black", "Hispanic", "White")),
                  "Race",
                  "",
                  "False discovery rate",
                  c("Black"="African-American"),
                  "a"),
             plot(group_bootstraps("INCARC", c(0, 1)),
                  "Incarcerated during\nprevious year",
                  "",
                  "False discovery rate",
                  c("0"="Never", "1"="At least once"),
                  "b"),
             plot(group_bootstraps("DISABLED", c(0, 1)),
                  "Medicaid-eligible\ndue to disablement",
                  "Risk threshold for classifying an adverse outcome",
                  "False discovery rate",
                  c("0"="No", "1"="Yes"),
                  "c"),
             nrow=3)
dev.off()

