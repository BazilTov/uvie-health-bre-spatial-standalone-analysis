# Maintainer/build-runner setup only. End users receive the resulting full bundle.
options(repos=c(CRAN='https://cloud.r-project.org'))
if (!requireNamespace('BiocManager',quietly=TRUE)) install.packages('BiocManager')
packages <- c('GeomxTools','NanoStringNCTools','shiny','zip','outliers','ggrepel',
              'ggforce','cowplot','umap','Rtsne','BiocStyle','networkD3','knitr')
BiocManager::install(packages,version='3.22',ask=FALSE,update=FALSE,Ncpus=2)
workflow <- tempfile(fileext='.tar.gz')
download.file('https://bioconductor.org/packages/3.22/workflows/src/contrib/GeoMxWorkflows_1.16.0.tar.gz',workflow,mode='wb')
install.packages(workflow,repos=NULL,type='source')
if(as.character(packageVersion('GeomxTools'))!='3.14.0' ||
   as.character(packageVersion('NanoStringNCTools'))!='1.18.0' ||
   as.character(packageVersion('GeoMxWorkflows'))!='1.16.0') {
  stop('Reference package versions changed; review required before release.')
}
ip <- installed.packages()
dir.create('runtime',showWarnings=FALSE)
write.csv(ip[,c('Package','Version','License','Built')],'runtime/package-versions.csv',row.names=FALSE)
writeLines(R.home(),'runtime/build-r-home.txt')
writeLines(.libPaths(),'runtime/build-library-paths.txt')
