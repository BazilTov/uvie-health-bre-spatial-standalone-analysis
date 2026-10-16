# Selected-gene research analysis. No all-gene screening or cell communication.
# Radius graphs use measured section coordinates; no inferred physical calibration.
build_radius_graph <- function(spatial, radius, ids=spatial$coordinates$Sample_ID) {
  if (!is.numeric(radius) || length(radius)!=1L || !is.finite(radius) || radius<=0) stop('Choose a finite positive radius in the supplied coordinate units.')
  d <- spatial$coordinates
  if (anyDuplicated(ids) || !length(ids) || !all(ids %in% d$Sample_ID)) stop('Graph identifiers must be a nonempty unique coordinate subset.')
  d <- d[match(ids,d$Sample_ID),,drop=FALSE]
  if (nrow(d)>5000L) stop('Neighborhood preview supports at most 5,000 positions per selection; reduce the selection.')
  if (!spatial$config$units %in% c('um','pixel')) stop('Neighborhoods require declared coordinate units.')
  edges <- list(); total <- 0L
  for (section in unique(d$section_id)) {
    indexes <- which(d$section_id==section)
    if (length(indexes)<2L) next
    for (k in seq_len(length(indexes)-1L)) {
      i <- indexes[k]; candidates <- indexes[(k+1L):length(indexes)]
      distance <- sqrt((d$x[candidates]-d$x[i])^2+(d$y[candidates]-d$y[i])^2)
      hit <- which(distance<=radius)
      if (!length(hit)) next
      total <- total+length(hit)
      if (total>250000L) stop('Neighborhood preview exceeds 250,000 edges. Choose a smaller radius or selection; no partial graph is returned.')
      edges[[length(edges)+1L]] <- data.frame(section_id=section,from=d$Sample_ID[i],to=d$Sample_ID[candidates[hit]],distance=distance[hit])
    }
  }
  table <- if(length(edges)) do.call(rbind,edges) else data.frame(section_id=character(),from=character(),to=character(),distance=numeric())
  list(edges=table,coordinates=d,radius=radius,units=spatial$config$units,resolution=spatial$config$resolution,
       method='Undirected Euclidean radius graph, distance <= radius; within section only; no self edges',
       scope='Selected section and compartment only; coordinate proximity is not tissue contact or communication.')
}

summarize_radius_graph <- function(graph, values) {
  ids <- graph$coordinates$Sample_ID
  if (is.null(names(values)) || anyDuplicated(names(values)) || !all(ids %in% names(values)) || any(!is.finite(values[ids]))) stop('Neighborhood expression must align to coordinate identifiers and be finite.')
  e <- graph$edges
  # Expand each undirected edge in both directions, retaining isolated observations.
  from <- c(e$from,e$to); to <- c(e$to,e$from)
  count <- tabulate(match(from,ids),nbins=length(ids))
  sums <- tapply(values[to],factor(from,levels=ids),sum)
  mean <- as.numeric(sums)/count
  mean[count==0] <- NA_real_
  data.frame(Sample_ID=ids,section_id=graph$coordinates$section_id,
             neighbor_count=count,expression_value=unname(values[ids]),neighbor_mean_expression=mean)
}

# Equal-weight section means, then equal-weight participants. Spatial sampling
# density is not a number of biological replicates. Values are averaged on log2 scale.
participant_comparison <- function(values, metadata, scale, condition_a, condition_b,
                                   design='paired', spatial=NULL, compartment=NULL,
                                   inference_confirmed=FALSE) {
  fields <- c('Sample_ID','participant','condition','compartment')
  if (!all(fields %in% names(metadata))) stop('Participant comparisons require metadata with explicit participant and condition columns.')
  if (!scale %in% c('linear','log2') || !design %in% c('paired','unpaired')) stop('Unsupported expression scale or comparison design.')
  if (!is.character(condition_a) || !is.character(condition_b) || length(condition_a)!=1L || length(condition_b)!=1L || is.na(condition_a) || is.na(condition_b) || !nzchar(condition_a) || !nzchar(condition_b) || condition_a==condition_b) stop('Choose two different conditions.')
  if (is.null(names(values)) || anyDuplicated(names(values)) || anyDuplicated(metadata$Sample_ID) ||
      !all(metadata$Sample_ID %in% names(values)) || any(!is.finite(values[metadata$Sample_ID])) ||
      anyNA(metadata[,fields]) || any(!nzchar(trimws(unlist(metadata[,fields]))))) stop('Comparison identifiers, participant labels, conditions and finite values are required.')
  if (scale=='linear' && any(values[metadata$Sample_ID]<0)) stop('Linear expression cannot be negative.')
  if (is.null(compartment) || length(compartment)!=1L || !nzchar(compartment)) stop('Select one compartment explicitly for participant comparisons.')
  m <- metadata[metadata$condition %in% c(condition_a,condition_b) & metadata$compartment==compartment,fields,drop=FALSE]
  if (!nrow(m) || !all(c(condition_a,condition_b) %in% m$condition)) stop('Both conditions must have observations in the selected compartment.')
  m$value <- unname(values[m$Sample_ID])
  if (scale=='linear') m$value <- log2(m$value+1)
  # No section inference from slide names: use supplied geometry when available.
  m$section_id <- m$Sample_ID
  if (!is.null(spatial)) {
    c <- spatial$coordinates
    if (!all(m$Sample_ID %in% c$Sample_ID)) stop('Comparison coordinates are incomplete.')
    m$section_id <- c$section_id[match(m$Sample_ID,c$Sample_ID)]
  }
  section <- aggregate(m$value,m[c('participant','condition','section_id')],mean)
  names(section)[4] <- 'mean_log2_expression'
  participants <- aggregate(section$mean_log2_expression,section[c('participant','condition')],mean)
  names(participants)[3] <- 'mean_log2_expression'
  participants$observations <- vapply(seq_len(nrow(participants)),function(i) sum(m$participant==participants$participant[i] & m$condition==participants$condition[i]),integer(1))
  participants$sections <- if(is.null(spatial)) NA_integer_ else vapply(seq_len(nrow(participants)),function(i) sum(section$participant==participants$participant[i] & section$condition==participants$condition[i]),integer(1))
  a <- participants[participants$condition==condition_a,,drop=FALSE]
  b <- participants[participants$condition==condition_b,,drop=FALSE]
  shared <- intersect(a$participant,b$participant)
  excluded <- character()
  if (design=='paired') {
    excluded <- setdiff(union(a$participant,b$participant),shared)
    a <- a[match(shared,a$participant),,drop=FALSE]; b <- b[match(shared,b$participant),,drop=FALSE]
  } else if(length(shared)) stop('Unpaired comparison cannot include the same participant in both conditions. Use paired design or review metadata.')
  used <- union(a$participant,b$participant)
  participants$included <- participants$participant %in% used
  effect <- if(nrow(a) && nrow(b)) mean(b$mean_log2_expression)-mean(a$mean_log2_expression) else NULL
  test <- NULL
  reason <- 'Descriptive only. Confirm that normalized expression is comparable and that the selected design and t-test assumptions are appropriate before enabling exploratory inference.'
  if (isTRUE(inference_confirmed)) {
    if (nrow(a)<3L || nrow(b)<3L) reason <- 'Descriptive only: at least three independent participants per condition (three complete pairs for paired design) are required by this preview.' else {
      result <- tryCatch(stats::t.test(b$mean_log2_expression,a$mean_log2_expression,paired=design=='paired',var.equal=FALSE,conf.level=.95),error=function(e)e)
      if(inherits(result,'error')) reason <- paste('Descriptive only: t-test unavailable:',conditionMessage(result)) else {
        test <- list(method=unname(result$method),statistic=unname(result$statistic),degrees_freedom=unname(result$parameter),p_value_unadjusted=result$p.value,confidence_interval_95=unname(result$conf.int))
        reason <- 'Exploratory selected-gene t-test; p-value is unadjusted. No covariate adjustment, count model, or multiple-testing correction. Repeated gene selection requires an appropriate multiplicity plan.'
      }
    }
  }
  list(schema_version=1,design=design,condition_a=condition_a,condition_b=condition_b,compartment=compartment,
       analysis_scale=if(scale=='linear') 'log2(input + 1)' else 'supplied log2',
       aggregation=if(is.null(spatial)) 'Mean log2 observation expression per participant and condition; no section IDs supplied' else 'Mean log2 expression within each section and condition, then equally weighted section means per participant and condition',
       effect_definition='Mean of condition B minus mean of condition A on analysis scale; not a count-model log fold change',
       effect_b_minus_a=effect,participants_a=nrow(a),participants_b=nrow(b),excluded_incomplete_participants=excluded,
       participant_values=participants,section_values=if(is.null(spatial)) NULL else section,test=test,status=reason,
       inference_confirmed=isTRUE(inference_confirmed),limits=c('Participant identity, conditions, normalized comparability, and biological independence are user supplied, not independently verified.',
       'No adjustment for batch, age, sex, cell composition or other confounders. This is exploratory selected-gene analysis, not a differential-expression pipeline.',
       'Neighborhood observations are correlated; no per-spot significance test is performed.'))
}
