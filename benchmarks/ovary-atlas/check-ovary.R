suppressPackageStartupMessages(library(GeomxTools))
args <- commandArgs(trailingOnly=TRUE)
stopifnot(length(args)==1)
root <- normalizePath(args[1],mustWork=TRUE)
meta <- read.csv(file.path(root,'sample-annotation.csv'),check.names=FALSE)
rownames(meta) <- meta$Sample_ID
obj <- readNanoStringGeoMxSet(dccFiles=list.files(file.path(root,'intake'),pattern='\\.dcc$',full.names=TRUE),
 pkcFiles=file.path(root,'intake/panel.pkc'),phenoData=meta)
write.csv(Biobase::exprs(obj),file.path(root,'geomxtools-imported-probes.csv'))
writeLines(capture.output(GeomxTools::shiftCountsOne),file.path(root,'shiftCountsOne-implementation.txt'))
obj <- shiftCountsOne(obj,useDALogic=TRUE)
# Exact author default-QC settings were not specified; no full QC replication claimed.
target <- aggregateCounts(obj)
fd <- Biobase::fData(target)
keep <- startsWith(as.character(fd$CodeClass),'Endogenous')
target <- target[keep,]
stopifnot(nrow(target)==18676)
x <- Biobase::exprs(target)
write.csv(x,file.path(root,'shifted-endogenous-counts.csv'))
m <- Biobase::pData(target)
ids <- rownames(m)[as.character(m$donor)=='2']
x <- x[,ids,drop=FALSE]
stopifnot(ncol(x)==165,all(x>0))
logcpm <- log2(sweep(x,2,colSums(x),'/')*1e6)
q <- limma::normalizeBetweenArrays(logcpm,method='quantile')
clusters <- as.character(m[ids,'cluster'])
stopifnot(all(clusters %in% as.character(1:9)))
centroids <- vapply(as.character(1:9),function(k) rowMeans(q[,clusters==k,drop=FALSE]),numeric(nrow(q)))
rownames(centroids) <- rownames(q)
write.csv(centroids,file.path(root,'candidate-donor2-centroids.csv'))
write.csv(q,file.path(root,'donor2-log2-cpm-quantile.csv'))
jsonlite::write_json(list(features=nrow(q),samples=ncol(q),clusters=as.list(table(clusters)),
 scope='Conditional donor 2 normalization using provisional row-to-AOI mapping; not full author QC replication'),file.path(root,'normalization-stage-summary.json'),pretty=TRUE,auto_unbox=TRUE)
session <- capture.output(sessionInfo()); session <- gsub(R.home(),'[BUNDLED_R]',session,fixed=TRUE)
writeLines(session,file.path(root,'session-info.txt'))
cat('Raw import and prospectively specified donor 2 centroid calculation completed.\n')
