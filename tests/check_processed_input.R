source('processed_input.R')
root <- tempfile('processed-input-test-');dir.create(root)
on.exit <- NULL
matrix <- data.frame(gene=c('G1','G2'),AOI_A=c(-1,3),AOI_B=c(2,4),NTC=c(0,1),check.names=FALSE)
metadata <- data.frame(Sample_ID=c('AOI_B','NTC','AOI_A'),participant=c('P2','not_applicable','P1'),
 tissue=c('Tissue_B','control','Tissue_A'),compartment=c('Stroma','control','Epithelium'),is_control=c('FALSE','TRUE','FALSE'))
provenance <- list(schema_version=1,method='Test log-scale input',value_type='log2 RNA',scale='log2',qc_status='partial')
write_inputs <- function(x=matrix,m=metadata,p=provenance) {
 write.csv(x,file.path(root,'matrix.csv'),row.names=FALSE)
 write.csv(m,file.path(root,'metadata.csv'),row.names=FALSE)
 jsonlite::write_json(p,file.path(root,'provenance.json'),auto_unbox=TRUE)
}
fails <- function(x=matrix,m=metadata,p=provenance) {
 write_inputs(x,m,p)
 result <- try(read_processed_input(root),silent=TRUE)
 stopifnot(inherits(result,'try-error'))
}
write_inputs();good <- read_processed_input(root)
stopifnot(identical(colnames(good$matrix),c('AOI_A','AOI_B')),good$matrix['G1','AOI_A']==-1,
 identical(good$metadata$participant,c('P1','P2')),good$controls_excluded==1,good$input_samples==3)
m <- metadata;m$Sample_ID[1] <- 'wrong';fails(m=m)
m <- metadata;m$Sample_ID[1] <- m$Sample_ID[3];fails(m=m)
m <- metadata;m$is_control[1] <- 'maybe';fails(m=m)
m <- metadata;m$participant[1] <- NA;fails(m=m)
x <- matrix;x$gene[2] <- x$gene[1];fails(x=x)
x <- matrix;x$AOI_A[1] <- Inf;fails(x=x)
x <- matrix;x$AOI_A <- c('bad','3');fails(x=x)
p <- provenance;p$scale <- 'linear';fails(p=p)
p <- provenance;p$qc_status <- NULL;fails(p=p)
p <- provenance;p$schema_version <- 2;fails(p=p)
unlink(root,recursive=TRUE)
cat('Processed-input tests passed: identifier alignment, controls, log scale, invalid identifiers, provenance and values.\n')
