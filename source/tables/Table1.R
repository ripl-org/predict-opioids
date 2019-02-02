library(readr)

args <- commandArgs(trailingOnly=TRUE)

y_pred_path <- args[1]
out_path    <- args[2]

df <- read_csv(y_pred_path)
thresholds <- c(0.1, 0.2, 0.4)

confusion_matrix <- function(threshold) {
    tp <- sum(df$y_pred >= threshold & df$y_test == 1)
    fp <- sum(df$y_pred >= threshold & df$y_test == 0)
    fn <- sum(df$y_pred <  threshold & df$y_test == 1)
    tn <- sum(df$y_pred <  threshold & df$y_test == 0)
    return(c(threshold, tp, fp, fn, tn, nrow(df)))
}

out <- cbind(c("Risk threshold",
               "True positives",
               "False positives",
               "False negatives",
               "True negatives",
               "Test sample size"),
             sapply(thresholds, confusion_matrix))

write.table(out, file=out_path,
            sep="\t", quote=FALSE, col.names=FALSE, row.names=FALSE)
