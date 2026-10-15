suppressPackageStartupMessages(library(GeomxTools))
args <- commandArgs(trailingOnly=TRUE)
if (length(args) != 1) stop('Supply the prepared input directory.')
root <- normalizePath(args[1], mustWork=TRUE)
metadata <- read.csv(file.path(root, 'sample-annotation.csv'), check.names=FALSE)
rownames(metadata) <- metadata$Sample_ID
data <- readNanoStringGeoMxSet(
    dccFiles=list.files(file.path(root,'intake'), pattern='\\.dcc$', full.names=TRUE),
    pkcFiles=file.path(root,'intake/panel.pkc'), phenoData=metadata)
# Keep all raw columns, including controls. This is not an NTC-QC calculation.
write.csv(Biobase::exprs(data), file.path(root,'geomxtools-imported-probes.csv'))
