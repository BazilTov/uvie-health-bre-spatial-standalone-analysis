# Optional geometry for processed expression. Coordinates are measurements supplied
# by the dataset, never inferred from embeddings or metadata row order.
read_spatial_input <- function(directory, ids, metadata) {
  paths <- file.path(directory,c('coordinates.csv','spatial.json'))
  present <- file.exists(paths)
  if (!any(present)) return(NULL)
  if (!all(present)) stop('Spatial input requires both coordinates.csv and spatial.json.')
  config <- jsonlite::fromJSON(paths[2],simplifyVector=FALSE)
  text <- function(x) is.character(x) && length(x)==1 && !is.na(x) && nzchar(trimws(x))
  if (!identical(config$schema_version,1L) || !text(config$units) ||
      !config$units %in% c('um','pixel') || !text(config$resolution) ||
      !config$resolution %in% c('cell','spot','region') || !text(config$source) ||
      !identical(config$y_direction,'down')) stop('Spatial schema needs version 1, units (um or pixel), resolution (cell, spot or region), source and y_direction down.')
  coordinates <- read.csv(paths[1],check.names=FALSE,stringsAsFactors=FALSE,
                          colClasses=c(Sample_ID='character',section_id='character'))
  fields <- c('Sample_ID','section_id','x','y')
  if (anyDuplicated(names(coordinates)) || !all(fields %in% names(coordinates)) ||
      anyNA(coordinates$Sample_ID) || anyDuplicated(coordinates$Sample_ID) ||
      !setequal(ids,coordinates$Sample_ID) || nrow(coordinates)!=length(ids)) stop('Spatial sample identifiers must match the biological expression samples exactly, without duplicates.')
  coordinates <- coordinates[match(ids,coordinates$Sample_ID),fields,drop=FALSE]
  if (anyNA(coordinates$section_id) || any(!nzchar(trimws(coordinates$section_id))) ||
      !is.numeric(coordinates$x) || !is.numeric(coordinates$y) ||
      any(!is.finite(coordinates$x)) || any(!is.finite(coordinates$y))) stop('Spatial sections and finite numeric x/y coordinates are required.')
  for (section in unique(coordinates$section_id)) {
    rows <- coordinates$section_id==section
    if (length(unique(metadata$participant[rows]))!=1) stop('Each section must belong to exactly one participant.')
    if (anyDuplicated(coordinates[rows,c('x','y')])) stop('Duplicate coordinates within a section are ambiguous.')
  }
  images <- list()
  if (!is.null(config$images)) {
    if (!is.list(config$images)) stop('Spatial images must be a list.')
    for (item in config$images) {
      numbers <- c('pixels_per_unit','x_origin','y_origin')
      if (!text(item$section_id) || !item$section_id %in% coordinates$section_id ||
          item$section_id %in% names(images) || !text(item$file) ||
          !grepl('^[A-Za-z0-9_-]+\\.png$',item$file) ||
          !all(vapply(numbers,function(n) is.numeric(item[[n]]) && length(item[[n]])==1 && is.finite(item[[n]]),logical(1))) ||
          item$pixels_per_unit<=0) stop('Image mapping requires a unique known section, safe PNG filename, positive pixels_per_unit and numeric origins.')
      path <- file.path(directory,item$file)
      if (!file.exists(path)) stop('Declared tissue image is missing.')
      # Check PNG dimensions before decoding; enforce a preview-sized memory bound.
      connection <- file(path,'rb'); header <- readBin(connection,'raw',n=24);close(connection)
      if (length(header)!=24 || !identical(header[1:8],as.raw(c(137,80,78,71,13,10,26,10)))) stop('Tissue image must be a PNG.')
      width <- sum(as.integer(header[17:20])*256^(3:0));height <- sum(as.integer(header[21:24])*256^(3:0))
      if (width<1 || height<1 || width*height>16e6) stop('Tissue image exceeds the sixteen-million-pixel preview limit.')
      image <- png::readPNG(path)
      points <- coordinates[coordinates$section_id==item$section_id,,drop=FALSE]
      px <- (points$x-item$x_origin)*item$pixels_per_unit
      py <- (points$y-item$y_origin)*item$pixels_per_unit
      if (any(px<0 | px>=width | py<0 | py>=height)) stop('Coordinates fall outside the declared image mapping.')
      images[[item$section_id]] <- list(mapping=item,raster=as.raster(image),width=width,height=height)
    }
  }
  list(coordinates=coordinates,config=config,images=images)
}

draw_spatial_map <- function(spatial, expression, section, title, value_label, opacity=.8) {
  d <- spatial$coordinates[spatial$coordinates$section_id==section,,drop=FALSE]
  if (!nrow(d)) stop('Select a valid tissue section.')
  values <- unname(expression[d$Sample_ID])
  if (any(!is.finite(values))) stop('Map values must align to spatial sample identifiers.')
  palette <- hcl.colors(100,'Viridis')
  limits <- range(values)
  bins <- if(diff(limits)==0) rep(50L,length(values)) else 1L+floor(99*(values-limits[1])/diff(limits))
  colors <- adjustcolor(palette[bins],alpha.f=opacity)
  image <- spatial$images[[section]]
  unit <- if(spatial$config$units=='um') 'micrometres' else 'source-image pixels'
  par(mar=c(5,5,4,2))
  if (!is.null(image)) {
    mapping <- image$mapping
    xr <- mapping$x_origin+c(0,image$width/mapping$pixels_per_unit)
    yr <- mapping$y_origin+c(0,image$height/mapping$pixels_per_unit)
    plot(NA,xlim=xr,ylim=rev(yr),asp=1,xaxs='i',yaxs='i',xlab=paste('x',unit),ylab=paste('y',unit),main=title)
    rasterImage(image$raster,xr[1],yr[2],xr[2],yr[1],interpolate=FALSE)
  } else {
    plot(NA,xlim=range(d$x)+c(-1,1),ylim=rev(range(d$y)+c(-1,1)),asp=1,
         xlab=paste('x',unit),ylab=paste('y',unit),main=title)
  }
  points(d$x,d$y,pch=16,col=colors,cex=.7)
  if (diff(limits)==0) {
    legend('topright',legend=paste('All positions:',signif(limits[1],4)),pch=16,
           col=palette[50],bg='white',cex=.8,title=value_label)
  } else {
    legend('topright',legend=c(paste('Low:',signif(limits[1],4)),paste('High:',signif(limits[2],4))),
           pch=16,col=palette[c(1,100)],bg='white',cex=.8,title=value_label)
  }
  mtext(paste(section,'|',spatial$config$resolution,'measurements | color range is section-specific'),side=3,cex=.75)
  invisible(data.frame(Sample_ID=d$Sample_ID,x=d$x,y=d$y,expression_value=values))
}
