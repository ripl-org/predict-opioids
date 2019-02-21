library(dplyr)
library(ggplot2)
library(stringr)

args <- commandArgs(trailingOnly=TRUE)

outcomes_path <- args[1]
out_path      <- args[2]

outcomes <- read.csv(outcomes_path)
cols <- names(outcomes)[!str_detect(names(outcomes), '_DAYS') & !str_detect(names(outcomes), '_DT') & str_detect(names(outcomes), 'OUTCOME')]
print(cols)
df <- data.frame()
years <- 5

for(col in cols) {
  # Sample the proportion of outcomes every 30 days
  fail <- sapply(seq(0, years*365, 30), function(x) {
    y <- outcomes[,col]
    y[outcomes[, paste0(col, "_DAYS")] > x] <- 0
    return(mean(y))
  })
  # Append the sampled proportions for this outcome
  df_iter <- data.frame(x=seq(0, years*365, 30)/365,
                        fail=fail,
                        var=col)
  df <- df %>% rbind(df_iter)
}

# Print % for OUTCOME_ANY
print(subset(df, var == "OUTCOME_ANY"))

pdf(out_path, width=6, height=6)
df %>% ggplot(aes(y=fail, x=x, color=var)) +
       geom_line() +
       scale_x_continuous(breaks=seq(0, years, 1)) +
       scale_y_continuous(breaks=seq(0, max(fail, rm.na=TRUE) + 0.01, 0.01),
                          labels=function(x) paste0(x * 100, "%")) +
       labs(x="Years from initial opioid prescription", 
            y="Poportion of adverse outcomes", 
            color="Outcome type") +
       scale_color_brewer(palette="Set2",
                          labels=c("OUTCOME_PROCEDURE"="Treatment",
                                   "OUTCOME_POISONING_HEROIN"="Heroin poisoning",
                                   "OUTCOME_POISONING_RX"="Prescription-opioid poisoning",
                                   "OUTCOME_ABUSE"="Opioid abuse",
                                   "OUTCOME_DEPENDENCE"="Opioid dependence",
                                   "OUTCOME_ANY"="Any adverse outcome")) +
       theme_classic() +
       theme(legend.position=c(0.27, 0.8))
dev.off()

