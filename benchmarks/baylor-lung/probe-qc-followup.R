suppressPackageStartupMessages(library(GeomxTools))
args <- commandArgs(trailingOnly=TRUE)
if (length(args) != 1) stop('Supply the prepared input directory.')
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
data <- setBioProbeQCFlags(data,
  qcCutoffs=list(minProbeRatio=0.1, percentFailGrubbs=20), removeLocalOutliers=TRUE)
flags <- Biobase::fData(data)[['QCFlags']]
summary <- list(features_before=nrow(data),
                low_probe_ratio=sum(flags$LowProbeRatio),
                global_grubbs=sum(flags$GlobalGrubbsOutlier),
                missing_counts_after_local_handling=sum(is.na(Biobase::exprs(data))))
keep <- !flags$LowProbeRatio & !flags$GlobalGrubbsOutlier
data <- data[keep,]
summary$features_after <- nrow(data)
jsonlite::write_json(summary,file.path(root,'probe-qc-stage-summary.json'),pretty=TRUE,auto_unbox=TRUE)
targets <- aggregateCounts(data)
stopifnot(all(rownames(reference) %in% rownames(targets)))
targets <- targets[rownames(reference),]
targets <- normalize(targets, norm_method='quant', desiredQuantile=.75, toElt='q_norm')
result <- log2(Biobase::assayDataElement(targets, 'q_norm'))
write.csv(result, file.path(root,'probe-qc-followup-log2-q3.csv'))
writeLines(capture.output(sessionInfo()),file.path(root,'probe-qc-followup-session-info.txt'))
cat('Probe-QC follow-up produced',nrow(result),'target rows across',ncol(result),'sample columns.\n')
