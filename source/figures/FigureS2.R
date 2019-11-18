library(tidyverse)
library(scales)
library(gridExtra)

args <- commandArgs(trailingOnly=TRUE)

csv_path <- args[1]
out_path <- args[2]

csv <- read_csv(csv_path)
csv$Decile <- csv$decile * 0.1
csv$bolasso <- csv$"BOLASSO Logit" / csv$size
csv$ensemble <- csv$"BOLASSO Ensemble" / csv$size
csv$neural <- csv$"Neural Network" / csv$size
csv <- csv %>%
       select(Decile, bolasso, ensemble, neural) %>%
       gather(key="Model", value="Fraction", bolasso, ensemble, neural)
csv$Model <- factor(csv$Model, c("bolasso", "ensemble", "neural"))
print(min(csv$Fraction))
print(max(csv$Fraction))

grplabels <- c("bolasso"="Post-BOLASSO",
               "ensemble"="LASSO Ensemble",
               "neural"="Neural Network")

pdf(out_path, width=6, height=6)
csv %>% ggplot(aes(x=Decile, y=Fraction, fill=Model)) +
        geom_hline(yintercept=0.057) +
        geom_bar(position="dodge", stat="identity") +
        coord_flip() +
        labs(x="Cumulative Deciles by Decreasing Risk", y="Fraction of True Outcomes") +
        theme_classic() +
        theme(axis.line.x=element_blank(),
              axis.ticks.x=element_blank(),
              legend.justification=c(1, 0),
              legend.position=c(1, 0),
              panel.grid.major.x=element_line("gray", 0.5, "dotted"),
              plot.title=element_text(face="bold")) +
        scale_x_reverse(limits=c(1.05, 0.05), breaks=seq(0.1, 1, 0.1), labels=percent_format(accuracy=0)) +
        scale_y_continuous(limits=c(0, 0.25), breaks=seq(0, 0.25, 0.05), position="bottom") +
        scale_fill_manual("Model",
                          labels=grplabels,
                          values=c("#E34E38", "#DF9826", "#45AFAF"))
dev.off()

