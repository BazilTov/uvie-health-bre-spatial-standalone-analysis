# Read supported, already-processed expression without rerunning a different
# study's QC or normalization. Uploaded method claims remain user supplied.
source('spatial_input.R',local=TRUE)
read_processed_input <- function(directory) {
  required <- c('matrix.csv','metadata.csv','provenance.json')
  if (!all(file.exists(file.path(directory,required)))) stop('Processed ZIP requires matrix.csv, metadata.csv and provenance.json at its root.')
  provenance <- jsonlite::fromJSON(file.path(directory,'provenance.json'),simplifyVector=FALSE)
  scalar_text <- function(x) is.character(x) && length(x)==1L && !is.na(x) && nzchar(trimws(x))
  if (!identical(provenance$schema_version,1L) && !identical(provenance$schema_version,1)) stop('Unsupported provenance schema_version; expected 1.')
  if (!scalar_text(provenance$method) || !scalar_text(provenance$value_type) || !scalar_text(provenance$scale) ||
      !provenance$scale %in% c('linear','log2') || !scalar_text(provenance$qc_status) ||
      !provenance$qc_status %in% c('not_assessed','partial','completed')) stop('Provenance needs method, value_type, scale (linear or log2), and qc_status (not_assessed, partial or completed).')
  table <- read.csv(file.path(directory,'matrix.csv'),check.names=FALSE,stringsAsFactors=FALSE)
  if (ncol(table)<2L || nrow(table)<1L || names(table)[1]!='gene' || anyDuplicated(names(table)) ||
      anyNA(table$gene) || any(!nzchar(trimws(table$gene))) || anyDuplicated(table$gene)) stop('Matrix requires a unique gene column followed by unique sample identifiers.')
  ids <- names(table)[-1]
  if (any(!nzchar(trimws(ids))) || any(!vapply(table[-1],is.numeric,logical(1))) ||
      as.double(nrow(table))*length(ids)>1e7) stop('Expression columns must be numeric, with named samples and no more than ten million values.')
  values <- as.matrix(table[-1]); rownames(values) <- table$gene
  if (any(!is.finite(values)) || (provenance$scale=='linear' && any(values<0))) stop('Expression must be finite; linear expression must be nonnegative.')
  meta <- read.csv(file.path(directory,'metadata.csv'),check.names=FALSE,stringsAsFactors=FALSE,colClasses='character')
  fields <- c('Sample_ID','participant','tissue','compartment','is_control')
  if (anyDuplicated(names(meta)) || !all(fields %in% names(meta))) stop('Metadata requires Sample_ID, participant, tissue, compartment and is_control columns.')
  if (anyNA(meta$Sample_ID) || anyDuplicated(meta$Sample_ID) || !setequal(ids,meta$Sample_ID) || length(ids)!=nrow(meta)) stop('Matrix sample identifiers and metadata must match exactly, without duplicates.')
  meta <- meta[match(ids,meta$Sample_ID),,drop=FALSE]
  for (field in fields) if (anyNA(meta[[field]]) || any(!nzchar(trimws(meta[[field]])))) stop(paste('Metadata field is incomplete:',field))
  if (any(!meta$is_control %in% c('TRUE','FALSE'))) stop('is_control must contain TRUE or FALSE explicitly.')
  keep <- meta$is_control=='FALSE'
  if (!any(keep)) stop('No biological compartments supplied.')
  meta[['slide name']] <- meta$tissue; meta[['class']] <- meta$participant; meta$region <- meta$compartment
  rownames(meta) <- meta$Sample_ID
  spatial <- read_spatial_input(directory,ids[keep],meta[keep,,drop=FALSE])
  list(matrix=values[,keep,drop=FALSE],metadata=meta[keep,,drop=FALSE],provenance=provenance,spatial=spatial,
       controls_excluded=sum(!keep),input_samples=length(ids))
}
