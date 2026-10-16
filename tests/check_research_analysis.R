source('research_analysis.R')
fails <- function(expr) stopifnot(inherits(try(force(expr),silent=TRUE),'try-error'))
s <- list(config=list(units='um',resolution='spot'),coordinates=data.frame(Sample_ID=c('a','b','c','d','e'),section_id=c('S1','S1','S1','S2','S1'),x=c(0,3,6,0,20),y=c(0,4,8,0,0)))
g <- build_radius_graph(s,5)
stopifnot(nrow(g$edges)==2,identical(g$edges$from,c('a','b')),identical(g$edges$to,c('b','c')),all(g$edges$distance==5))
z <- summarize_radius_graph(g,c(e=99,d=100,c=30,b=20,a=10))
stopifnot(identical(z$neighbor_count,c(1L,2L,1L,0L,0L)),identical(z$neighbor_mean_expression[1:3],c(20,20,20)),all(is.na(z$neighbor_mean_expression[4:5])))
stopifnot(nrow(build_radius_graph(s,.1)$edges)==0)
empty <- summarize_radius_graph(build_radius_graph(s,.1),c(a=1,b=2,c=3,d=4,e=5))
stopifnot(all(empty$neighbor_count==0),all(is.na(empty$neighbor_mean_expression)))
# Identifier reorder cannot change the graph; section isolates must stay isolated.
r <- build_radius_graph(s,5,rev(s$coordinates$Sample_ID)); stopifnot(nrow(r$edges)==2)
fails(build_radius_graph(s,0));fails(build_radius_graph(s,Inf));fails(build_radius_graph(s,1,c('a','a')))
fails(summarize_radius_graph(g,c(a=1,b=2)))
large <- s;large$coordinates <- data.frame(Sample_ID=paste0('s',1:5001),section_id='one',x=1:5001,y=0)
fails(build_radius_graph(large,1))
large$coordinates <- large$coordinates[1:710,];fails(build_radius_graph(large,10000))
# Exact paired example: differences B-A = 1,2,3; t=sqrt(12), df=2.
m <- expand.grid(participant=paste0('P',1:3),condition=c('A','B'),stringsAsFactors=FALSE)
m$Sample_ID <- paste0('s',seq_len(nrow(m)));m$compartment <- 'stroma'
v <- setNames(c(1,2,3,2,4,6),m$Sample_ID)
p <- participant_comparison(v,m,'log2','A','B','paired',compartment='stroma',inference_confirmed=TRUE)
stopifnot(p$effect_b_minus_a==2,p$participants_a==3,abs(p$test$statistic-sqrt(12))<1e-12,p$test$degrees_freedom==2,
          abs(p$test$p_value_unadjusted-0.0741799002274485)<1e-12,
          max(abs(p$test$confidence_interval_95-c(-.484137711719545,4.48413771171955)))<1e-10)
# Reordering metadata and expression order preserves paired alignment.
q <- participant_comparison(rev(v),m[c(6,2,4,1,5,3),],'log2','A','B','paired',compartment='stroma',inference_confirmed=TRUE)
stopifnot(abs(q$test$statistic-p$test$statistic)<1e-12)
# Repeated observations must not become independent participants.
mm <- m[rep(seq_len(nrow(m)),each=4),];mm$Sample_ID <- paste0('r',seq_len(nrow(mm)))
vv <- setNames(rep(unname(v),each=4),mm$Sample_ID)
q <- participant_comparison(vv,mm,'log2','A','B','paired',compartment='stroma',inference_confirmed=TRUE)
stopifnot(q$participants_a==3,abs(q$test$p_value_unadjusted-p$test$p_value_unadjusted)<1e-12)
# Unequal sampling density: mean each section, then weight sections equally.
mm <- data.frame(Sample_ID=c('a','b','c','d'),participant=c('P1','P1','P1','P2'),condition=c('A','A','A','B'),compartment='stroma')
ss <- list(coordinates=data.frame(Sample_ID=c('d','b','a','c'),section_id=c('T','S1','S1','S2')))
q <- participant_comparison(c(a=0,b=0,c=10,d=8),mm,'log2','A','B','unpaired',ss,'stroma',TRUE)
stopifnot(q$effect_b_minus_a==3,is.null(q$test),q$participants_a==1)
fails(participant_comparison(v,m,'log2','A','B','unpaired',compartment='stroma'))
fails(participant_comparison(v,m,'log2','A','A',compartment='stroma'))
fails(participant_comparison(v,m,'log2','A','B',compartment=NULL))
# Incomplete pairs explicitly excluded and cannot inflate counts.
mm <- m[-6,]; q <- participant_comparison(v,mm,'log2','A','B','paired',compartment='stroma',inference_confirmed=TRUE)
stopifnot(q$participants_a==2,is.null(q$test),identical(q$excluded_incomplete_participants,'P3'))
q <- participant_comparison(v,m,'log2','A','B','paired',compartment='stroma')
stopifnot(is.null(q$test),!q$inference_confirmed)
# Independent Welch check: A 1,2,3; B 4,6,8. Effect4, varA1,varB4; SE=sqrt(5/3), df=50/17.
m$participant <- paste0('P',1:6);v <- setNames(c(1,2,3,4,6,8),m$Sample_ID)
q <- participant_comparison(v,m,'log2','A','B','unpaired',compartment='stroma',inference_confirmed=TRUE)
stopifnot(q$effect_b_minus_a==4,abs(q$test$statistic-4/sqrt(5/3))<1e-12,abs(q$test$degrees_freedom-50/17)<1e-12)
# Explicit linear->log2 transformation; one participant per condition stays descriptive.
q <- participant_comparison(setNames(2^v-1,names(v)),m,'linear','A','B','unpaired',compartment='stroma',inference_confirmed=TRUE)
stopifnot(q$effect_b_minus_a==4)
# Constant data do not produce infinite significance.
v[] <- 1;q <- participant_comparison(v,m,'log2','A','B','unpaired',compartment='stroma',inference_confirmed=TRUE)
stopifnot(is.null(q$test))
cat('Research analysis checks passed: section-limited radius graphs, isolated positions, exact boundary distances, participant aggregation, paired alignment, Welch arithmetic, replication invariance, inadequate sample counts and inference gates.\n')
