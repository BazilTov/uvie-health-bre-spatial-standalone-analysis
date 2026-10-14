# Published multi-platform Bioconductor 3.22 / R 4.5.2 image.
FROM bioconductor/bioconductor_docker:RELEASE_3_22@sha256:e34177896c1579f66d48b756e4229b58237499183a089da084af72d7aba1d40a
RUN apt-get update && apt-get install -y --no-install-recommends python3 && rm -rf /var/lib/apt/lists/*
RUN Rscript -e 'BiocManager::install(c("GeomxTools", "NanoStringNCTools", "GeoMxWorkflows"), version="3.22", ask=FALSE, update=FALSE)'
WORKDIR /app
COPY . /app
RUN Rscript -e 'writeLines(capture.output(sessionInfo()), "/app/container-session-info.txt")'
ENTRYPOINT ["python3", "/app/spatial.py"]
