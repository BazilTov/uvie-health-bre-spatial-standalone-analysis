# Standalone local application. All dependencies are supplied in a full release.
suppressPackageStartupMessages(library(shiny))
options(shiny.maxRequestSize = 100 * 1024^2)
required <- c('GeomxTools', 'NanoStringNCTools', 'GeoMxWorkflows', 'jsonlite', 'zip', 'png')
missing <- required[!vapply(required, requireNamespace, logical(1), quietly = TRUE)]
if (length(missing)) stop(paste('Incomplete runtime package:', paste(missing, collapse = ', ')))
root <- normalizePath(getwd())
source(file.path(root,'processed_input.R'),local=TRUE)
ui <- fluidPage(
  tags$head(tags$style(HTML('body{background:#f4f6f1;color:#183d3b;font:16px/1.5 system-ui}.container-fluid{max-width:1200px;padding:30px}h1{font-weight:650}.well{background:#e6ede5;border:0}pre{white-space:pre-wrap;overflow-wrap:anywhere}#observations{max-width:100%;max-height:480px;overflow:auto}#observations table{white-space:nowrap}#expression{max-width:100%;overflow:hidden}#expression img{max-width:100%;height:auto!important}.btn-primary{background:#286f5d;border-color:#286f5d}.notice{padding:16px;background:#fff4d9;margin:20px 0}.form-control{font-size:16px}'))),
  titlePanel('UVIE Health BRE Spatial - Standalone'),
  p('Run the packaged GeoMx reference workflow or explore processed compartment expression with its own methods and provenance.'),
  div(class='notice', strong('Reference pipeline, not a validated clinical product. '),
      'The first benchmark uses the inputs shipped with the same workflow package. Matching published checkpoints is scoped evidence, not independent validation of every output.'),
  sidebarLayout(
    sidebarPanel(
      selectInput('source', 'Input', c('Packaged kidney reference'='package', 'Your GeoMx ZIP: kidney settings'='upload', 'Processed expression ZIP'='processed')),
      conditionalPanel("input.source !== 'package'", fileInput('datazip', 'Dataset ZIP (up to 100 MB)', accept='.zip')),
      conditionalPanel("input.source === 'upload'", p('Expected: dccs/, pkcs/, annotation/ with a Template-sheet XLSX. This runs the kidney reference QC profile; it is not a universal study protocol.')),
      conditionalPanel("input.source === 'processed'", p('Expected at ZIP root: matrix.csv, metadata.csv and provenance.json. Imports existing expression; does not run or verify upstream QC or normalization. See the processed-input guide in the repository.')),
      actionButton('run', 'Run reference pipeline', class='btn-primary'),
      hr(), selectizeInput('gene', 'Gene', choices=NULL),
      selectInput('region', 'Compartment', choices='All'),
      downloadButton('evidence', 'Download gene evidence'),
      downloadButton('bundle', 'Download run outputs'),
      p('Runs locally. No UVIE account or private engine is required. No runtime or package downloads occur when you press Run.')
    ),
    mainPanel(
      h3('Run status'), verbatimTextOutput('status'),
      tabsetPanel(
        tabPanel('Gene evidence', h4(textOutput('current_gene',inline=TRUE)), plotOutput('expression', height='350px'), tableOutput('observations')),
        tabPanel('Tissue map', verbatimTextOutput('spatial_status'),
                 selectInput('section','Tissue section',choices=character()),
                 sliderInput('map_opacity','Expression marker opacity',min=.1,max=1,value=.8,step=.1),
                 plotOutput('tissue_map',height='650px'), downloadButton('map_png','Download tissue map')),
        tabPanel('Benchmark checkpoints', verbatimTextOutput('benchmark')),
        tabPanel('Methods and logs', p('GeoMxWorkflows supplies the reference code. The packaged runner executes it through Q3 normalization, retains source-stage matrices and session information, and does not perform treatment prediction.'),
                 verbatimTextOutput('log'))
      )
    )
  )
)
server <- function(input, output, session) {
  state <- reactiveValues(status='Ready. No analysis has run.', directory=NULL,
                          matrix=NULL, metadata=NULL, stages=NULL, log='', benchmark=NULL,
                          value_type='Q3-normalized RNA',scale='linear',spatial=NULL)
  observeEvent(input$source, {
    state$spatial <- NULL
    state$matrix <- NULL; state$metadata <- NULL; state$directory <- NULL
    state$benchmark <- NULL; state$stages <- NULL; state$log <- ''
    state$status <- 'Ready. No analysis has run.'
    updateActionButton(session,'run',label=if(input$source=='processed') 'Load processed expression' else 'Run reference pipeline')
  },ignoreInit=TRUE)
  observeEvent(input$run, {
    tryCatch({
    state$spatial <- NULL
    state$matrix <- NULL; state$metadata <- NULL; state$benchmark <- NULL; state$directory <- NULL
    state$log <- ''; state$stages <- NULL
    if (input$source != 'package' && is.null(input$datazip)) {
      state$status <- 'Choose a dataset ZIP before running.'
      return()
    }
    state$status <- 'Running reference workflow...'
    directory <- tempfile('uvie-spatial-run-')
    dir.create(directory)
    data <- 'package'
    if (input$source != 'package') {
      req(input$datazip)
      info <- unzip(input$datazip$datapath, list=TRUE)
      unsafe <- grepl('(^/|^[A-Za-z]:|(^|/)\\.\\.(/|$)|\\\\)', info$Name)
      validate(need(!any(unsafe) && sum(info$Length) <= 1024^3 && nrow(info) <= 5000,
                    'ZIP contains unsafe paths or exceeds extraction limits.'))
      unpacked <- file.path(directory, 'input'); dir.create(unpacked)
      unzip(input$datazip$datapath, exdir=unpacked)
      if (input$source == 'processed') {
        loaded <- read_processed_input(unpacked)
        destination <- file.path(directory,'results'); dir.create(destination)
        supplied <- list.files(unpacked,pattern='\\.(csv|json|png)$',full.names=TRUE)
        file.copy(supplied,destination)
        state$spatial <- loaded$spatial
        updateSelectInput(session,'section',choices=if(is.null(loaded$spatial)) character() else unique(loaded$spatial$coordinates$section_id))
        state$matrix <- loaded$matrix; state$metadata <- loaded$metadata
        state$value_type <- loaded$provenance$value_type; state$scale <- loaded$provenance$scale
        state$stages <- list(input_type='processed',supplied_provenance=loaded$provenance,
          spatial_metadata=if(is.null(loaded$spatial)) NULL else loaded$spatial$config,
          provenance_verification='User supplied; upstream QC and normalization not independently verified',
          controls_excluded=loaded$controls_excluded,input_samples=loaded$input_samples)
        state$benchmark <- list(scope='Processed-input integrity checks only; no reference agreement claim',checks=list())
        state$directory <- destination
        jsonlite::write_json(state$stages,file.path(destination,'import-audit.json'),pretty=TRUE,auto_unbox=TRUE)
        state$log <- paste('Imported processed expression. Method supplied by dataset:',loaded$provenance$method,
          '\nReported upstream QC:',loaded$provenance$qc_status,
          '\nNo upstream QC or normalization was run or verified during this import.')
        measurement_label <- if(is.null(loaded$spatial)) 'biological compartments.' else paste0(loaded$spatial$config$resolution,' measurements.')
        state$status <- paste('Processed expression imported.',nrow(state$matrix),'targets across',ncol(state$matrix),
          measurement_label,loaded$controls_excluded,'declared controls excluded from gene evidence. Upstream processing is user supplied.')
        updateSelectizeInput(session,'gene',choices=rownames(state$matrix),selected=rownames(state$matrix)[1],server=TRUE)
        updateSelectInput(session,'region',choices=c('All',sort(unique(state$metadata$region))))
        return()
      }
      candidates <- c(unpacked, list.dirs(unpacked, recursive=FALSE))
      valid <- vapply(candidates, function(d) all(dir.exists(file.path(d, c('dccs','pkcs','annotation')))), logical(1))
      validate(need(sum(valid)==1, 'ZIP must contain one dataset with dccs, pkcs, and annotation folders.'))
      data <- candidates[valid]
    }
    destination <- file.path(directory,'results'); dir.create(destination)
    log <- file.path(directory, 'run.log')
    runner <- if (.Platform$OS.type == 'windows') file.path(R.home('bin'),'Rscript.exe') else file.path(R.home('bin'),'R')
    args <- if (.Platform$OS.type == 'windows') c('--vanilla', shQuote(file.path(root,'scripts/run_reference.R')), shQuote(data), shQuote(destination)) else
      c('--vanilla','--slave', paste0('--file=', shQuote(file.path(root,'scripts/run_reference.R'))), '--args', shQuote(data), shQuote(destination))
    code <- withProgress(message='Processing the reference pipeline', value=.1,
      system2(runner, args, stdout=log, stderr=log))
    state$log <- paste(readLines(log, warn=FALSE), collapse='\n')
    if (code != 0 || !file.exists(file.path(destination,'q3_normalized.csv'))) {
      state$status <- 'Pipeline failed. See Methods and logs; no normalized findings are shown.'
      return()
    }
    state$directory <- destination
    state$value_type <- 'Q3-normalized RNA'; state$scale <- 'linear'
    state$matrix <- as.matrix(read.csv(file.path(destination,'q3_normalized.csv'), row.names=1, check.names=FALSE))
    state$metadata <- read.csv(file.path(destination,'retained_metadata.csv'), row.names=1, check.names=FALSE)
    state$stages <- jsonlite::fromJSON(file.path(destination,'stages.json'))
    # Published dimensional checkpoints are scoped tests, not full-matrix truth.
    expected <- list(segment_qc_probes=c(18642,229), probe_qc_probes=c(18641,229),
                     aggregated_targets=c(18504,229), normalized=c(10131,221))
    checks <- lapply(names(expected), function(name) {
      actual <- if (name=='normalized') state$stages$normalized else state$stages$stages[[name]]
      dimensions <- unname(c(actual$features,actual$samples))
      list(stage=name, expected=unname(expected[[name]]), actual=unname(c(actual$features,actual$samples)),
           matches=length(dimensions)==2 && isTRUE(all(dimensions==expected[[name]])))
    })
    state$benchmark <- list(scope='Published dimensions only; full matrix agreement not established', checks=checks,
                             custom_input=input$source=='upload')
    state$status <- paste('Reference pipeline executed through Q3 normalization.', nrow(state$matrix), 'targets across', ncol(state$matrix), 'retained compartments. Review benchmark scope and logs.')
    updateSelectizeInput(session,'gene',choices=rownames(state$matrix),selected=if('C3' %in% rownames(state$matrix)) 'C3' else rownames(state$matrix)[1],server=TRUE)
    updateSelectInput(session,'region',choices=c('All',sort(unique(state$metadata$region))))
    }, error=function(error) {
      state$spatial <- NULL
      state$matrix <- NULL; state$metadata <- NULL; state$directory <- NULL
      state$status <- paste('Run could not complete:', conditionMessage(error), 'No gene findings are shown.')
    })
  })
  rows <- reactive({
    req(state$matrix,input$gene)
    ids <- colnames(state$matrix)
    meta <- state$metadata[ids,,drop=FALSE]
    result <- data.frame(sample=ids, tissue=meta[['slide name']], group=meta[['class']],
                         compartment=meta[['region']], expression_value=as.numeric(state$matrix[input$gene,]), check.names=FALSE)
    if(input$region!='All') result <- result[result$compartment==input$region,,drop=FALSE]
    result
  })
  output$status <- renderText(state$status)
  output$current_gene <- renderText({req(state$matrix,input$gene); input$gene})
  output$log <- renderText(state$log)
  output$benchmark <- renderText(if(is.null(state$benchmark)) 'No benchmark run yet.' else jsonlite::toJSON(state$benchmark,pretty=TRUE,auto_unbox=TRUE))
  output$observations <- renderTable(rows(), digits=3)
  output$spatial_status <- renderText({
    if (is.null(state$spatial)) return('No spatial map available. Supply matching coordinates.csv and spatial.json with processed expression.')
    paste('Resolution:',state$spatial$config$resolution,'| Units:',state$spatial$config$units,
          '\nSource:',state$spatial$config$source,
          '\nPositions and image alignment are supplied by the dataset. No cell identity, signaling or significance is inferred.',
          '\nThe map displays the selected section and compartment filter. Colors are scaled within the displayed section.')
  })
  map_data <- reactive({
    req(state$spatial,state$matrix,input$gene,input$section)
    spatial <- state$spatial
    if (input$region!='All') spatial$coordinates <- spatial$coordinates[spatial$coordinates$Sample_ID %in% rows()$sample,,drop=FALSE]
    validate(need(any(spatial$coordinates$section_id==input$section),'No observations in this section match the compartment filter.'))
    list(spatial=spatial,values=setNames(as.numeric(state$matrix[input$gene,]),colnames(state$matrix)))
  })
  make_map <- function() {
    data <- map_data()
    display <- if(state$scale=='linear') log2(data$values+1) else data$values
    draw_spatial_map(data$spatial,display,input$section,input$gene,
      if(state$scale=='linear') paste0('log2(',state$value_type,' + 1)') else state$value_type,input$map_opacity)
  }
  output$tissue_map <- renderPlot({make_map()})
  output$map_png <- downloadHandler(filename=function() paste0('uvie-',input$gene,'-tissue-map.png'),content=function(file) {
    req(state$spatial);png(file,width=1600,height=1400,res=160);on.exit(dev.off());make_map()
  })
  output$expression <- renderPlot({
    d <- rows(); req(nrow(d)>0)
    par(mar=c(8,4,3,1))
    set.seed(1)
    display <- if(state$scale=='linear') log2(d$expression_value+1) else d$expression_value
    label <- if(state$scale=='linear') paste0('log2(',state$value_type,' + 1)') else state$value_type
    stripchart(display ~ interaction(d$group,d$compartment), method='jitter', pch=19,
               vertical=TRUE, col='#286f5d', ylab=label, xlab='', main=input$gene, las=2,cex.axis=.85)
    mtext('Tissue group and compartment',side=1,line=6.5)
  })
  output$evidence <- downloadHandler(filename=function() paste0('uvie-',input$gene,'-evidence.json'), content=function(file) {
    req(state$matrix,input$gene)
    jsonlite::write_json(list(schema_version=2,gene=input$gene,value_type=state$value_type,scale=state$scale,observations=rows(),
      benchmark=state$benchmark,workflow=state$stages,
      spatial=if(is.null(state$spatial)) NULL else list(metadata=state$spatial$config,
        coordinates=state$spatial$coordinates[state$spatial$coordinates$Sample_ID %in% rows()$sample,,drop=FALSE]),
      limits=c(if(is.null(state$spatial)) 'No measured coordinates supplied.' else paste('Supplied measurement resolution:',state$spatial$config$resolution),
      'No differential-expression model has been run; observations are not significance findings.',
      'No protein abundance, causation, drug binding, or efficacy established.')), file, pretty=TRUE, auto_unbox=TRUE,digits=NA)
  })
  output$bundle <- downloadHandler(filename='uvie-spatial-run.zip',content=function(file) {
    req(state$directory)
    old <- setwd(state$directory); on.exit(setwd(old))
    zip::zipr(file, list.files('.',recursive=TRUE))
  })
}
port <- as.integer(Sys.getenv('UVIE_PORT','8765'))
runApp(shinyApp(ui,server),host='127.0.0.1',port=port,
       launch.browser=interactive() || Sys.getenv('UVIE_OPEN_BROWSER','1')=='1')
