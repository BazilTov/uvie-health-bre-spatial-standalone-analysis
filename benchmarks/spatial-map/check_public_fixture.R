# Independent check of the developer fixture against original vendor archives.
# Uses Matrix's Matrix Market reader, not the Python fixture converter.
directory <- normalizePath(commandArgs(trailingOnly=TRUE)[1],mustWork=TRUE)
tmp <- tempfile('visium-independent-');dir.create(tmp)
untar(file.path(directory,'filtered_feature_bc_matrix.tar.gz'),exdir=tmp)
untar(file.path(directory,'spatial.tar.gz'),exdir=tmp)
source_dir <- file.path(tmp,'filtered_feature_bc_matrix')
features <- read.delim(gzfile(file.path(source_dir,'features.tsv.gz')),header=FALSE,quote='',colClasses='character')
barcodes <- readLines(gzfile(file.path(source_dir,'barcodes.tsv.gz')))
connection <- gzfile(file.path(source_dir,'matrix.mtx.gz'))
counts <- Matrix::readMM(connection)
fixture <- read.csv(file.path(directory,'input','matrix.csv'),row.names=1,check.names=FALSE)
indices <- match(rownames(fixture),features[[2]])
stopifnot(!anyNA(indices),!anyDuplicated(barcodes),identical(colnames(fixture),barcodes))
original <- as.matrix(counts[indices,,drop=FALSE])
stopifnot(identical(unname(original),unname(as.matrix(fixture))*1))
positions <- read.csv(file.path(tmp,'spatial','tissue_positions_list.csv'),header=FALSE,colClasses='character')
coordinates <- read.csv(file.path(directory,'input','coordinates.csv'),colClasses=c(Sample_ID='character'))
joined <- positions[match(coordinates$Sample_ID,positions[[1]]),]
stopifnot(!anyNA(joined),all(joined[[2]]=='1'),
          all(coordinates$x==as.numeric(joined[[6]])),all(coordinates$y==as.numeric(joined[[5]])))
source_scale <- jsonlite::fromJSON(file.path(tmp,'spatial','scalefactors_json.json'))
mapping <- jsonlite::fromJSON(file.path(directory,'input','spatial.json'),simplifyVector=FALSE)
stopifnot(mapping$units=='pixel',mapping$resolution=='spot',
          identical(mapping$images[[1]]$pixels_per_unit,source_scale$tissue_lowres_scalef))
image_source <- file.path(tmp,'spatial','tissue_lowres_image.png')
image_fixture <- file.path(directory,'input','tissue.png')
stopifnot(identical(readBin(image_source,'raw',n=file.info(image_source)$size),
                    readBin(image_fixture,'raw',n=file.info(image_fixture)$size)))
report <- list(status='pass',scope='Independent fixture conversion check; not biological validation',
  count_values=length(original),count_differences=0,positions=nrow(coordinates),coordinate_differences=0,
  image_bytes_identical=TRUE,vendor_preview_scale_identical=TRUE,
  reader=paste('Matrix',packageVersion('Matrix')),
  limitations='Six selected genes and all filtered spots in one section; no micrometre conversion, cell annotation or disease inference.')
jsonlite::write_json(report,file.path(directory,'independent-fixture-check.json'),pretty=TRUE,auto_unbox=TRUE)
unlink(tmp,recursive=TRUE)
cat(jsonlite::toJSON(report,auto_unbox=TRUE),'\n')
