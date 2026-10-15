suppressPackageStartupMessages(library(GeomxTools))
args <- commandArgs(trailingOnly=TRUE)
if (length(args) != 1) stop('Supply the prepared input directory as the sole argument.')
root <- normalizePath(args[1], mustWork=TRUE)
input <- file.path(root, 'intake')
metadata <- read.csv(file.path(root, 'sample-annotation.csv'), check.names=FALSE)
metadata[['slide name']] <- metadata$slide
rownames(metadata) <- metadata$Sample_ID
reference <- read.csv(gzfile(file.path(root,'published-normalized.csv.gz')), row.names=1, check.names=FALSE)
data <- readNanoStringGeoMxSet(dccFiles=list.files(input,pattern='\\.dcc$',full.names=TRUE),
                              pkcFiles=file.path(input,'panel.pkc'), phenoData=metadata)
data <- shiftCountsOne(data, useDALogic=TRUE)
stopifnot(all(colnames(reference) %in% colnames(data)))
data <- data[,colnames(reference)]
targets <- aggregateCounts(data)
stopifnot(all(rownames(reference) %in% rownames(targets)))
targets <- targets[rownames(reference),]
targets <- normalize(targets, norm_method='quant', desiredQuantile=.75, toElt='q_norm')
result <- log2(Biobase::assayDataElement(targets, 'q_norm'))
write.csv(result, file.path(root,'conditional-log2-q3.csv'))
writeLines(capture.output(sessionInfo()),file.path(root,'conditional-session-info.txt'))
cat('Conditional normalization produced',nrow(result),'target rows across',ncol(result),'sample columns.\n')
