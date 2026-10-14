# Execute upstream GeoMxWorkflows code through Q3 normalization.
# Executed against the canonical kidney inputs through Q3 normalization.
# Checkpoint agreement is scoped and is not independent biological validation.
# Upstream code is loaded from the installed package, not copied into this repo.
args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 2) stop('Usage: Rscript scripts/run_reference.R KIDNEY_DIRECTORY OUTPUT_DIRECTORY')
datadir <- if (args[1] == 'package') system.file('extdata', 'WTA_NGS_Example', package = 'GeoMxWorkflows') else normalizePath(args[1], mustWork = TRUE)
outdir <- args[2]
dir.create(outdir, recursive = TRUE, showWarnings = FALSE)
for (pkg in c('GeomxTools', 'NanoStringNCTools', 'GeoMxWorkflows')) {
  if (!requireNamespace(pkg, quietly = TRUE)) stop(paste('Missing package:', pkg))
}
script <- system.file('doc', 'GeomxTools_RNA-NGS_Analysis.R', package = 'GeoMxWorkflows')
if (!nzchar(script)) stop('Installed package has no workflow script. Do not substitute silently.')
lines <- readLines(script, warn = FALSE)
start <- grep('^library\\(NanoStringNCTools\\)', lines)[1]
if (is.na(start)) stop('Upstream workflow structure changed; review required.')
expressions <- parse(text = lines[start:length(lines)])
env <- new.env(parent = globalenv())
set.seed(1)
stages <- list()
snapshot <- function(name, obj) {
  stages[[name]] <<- list(features = nrow(obj), samples = ncol(obj))
  write.csv(Biobase::exprs(obj), file.path(outdir, paste0(name, '.csv')))
}
for (expr in expressions) {
  code <- paste(deparse(expr), collapse = ' ')
  if (grepl('^datadir <-', code)) {
    env$datadir <- datadir
  } else if (grepl('^PKCFiles <-', code)) {
    pkc <- list.files(file.path(datadir, 'pkcs'), pattern = '\\.pkc$', full.names = TRUE, recursive = TRUE)
    if (!length(pkc)) {
      archives <- list.files(file.path(datadir, 'pkcs'), pattern = '\\.zip$', full.names = TRUE, recursive = TRUE)
      extraction <- file.path(outdir, 'pkcs')
      dir.create(extraction, recursive = TRUE, showWarnings = FALSE)
      for (archive in archives) unzip(archive, exdir = extraction)
      pkc <- list.files(extraction, pattern = '\\.pkc$', full.names = TRUE, recursive = TRUE)
    }
    if (!length(pkc)) stop('Expected PKC files in kidney input directory.')
    env$PKCFiles <- pkc
  } else {
    eval(expr, envir = env)
  }
  if (grepl('^demoData <- readNanoStringGeoMxSet', code)) snapshot('imported_probes', env$demoData)
  if (grepl('^demoData <- demoData\\[, QCResults', code)) snapshot('segment_qc_probes', env$demoData)
  if (grepl('^demoData <- ProbeQCPassed', code)) snapshot('probe_qc_probes', env$demoData)
  if (grepl('^target_demoData <- aggregateCounts', code)) snapshot('aggregated_targets', env$target_demoData)
  if (grepl('^target_demoData <- normalize', code) && grepl('q_norm', code)) {
    obj <- env$target_demoData
    write.csv(Biobase::exprs(obj), file.path(outdir, 'retained_raw.csv'))
    write.csv(Biobase::assayDataElement(obj, 'q_norm'), file.path(outdir, 'q3_normalized.csv'))
    metadata <- Biobase::pData(obj)
    flat <- vapply(metadata, function(column) is.atomic(column) && is.null(dim(column)), logical(1))
    write.csv(metadata[, flat, drop = FALSE], file.path(outdir, 'retained_metadata.csv'))
    saveRDS(obj, file.path(outdir, 'reference_object.rds'))
    writeLines(capture.output(sessionInfo()), file.path(outdir, 'session-info.txt'))
    jsonlite::write_json(list(stages = stages, normalized = list(features = nrow(obj), samples = ncol(obj)),
                            workflow_version = as.character(packageVersion('GeoMxWorkflows')),
                            workflow_md5 = unname(tools::md5sum(script)),
                            input = if(args[1] == 'package') 'GeoMxWorkflows::WTA_NGS_Example' else basename(datadir)),
                         file.path(outdir, 'stages.json'), pretty = TRUE, auto_unbox = TRUE)
    writeLines('Reference workflow executed through Q3 normalization. Numerical agreement against independent full reference outputs has not yet been evaluated.', file.path(outdir, 'STATUS.txt'))
    quit(status = 0)
  }
}
stop('Q3 checkpoint not reached; upstream workflow structure needs review.')
