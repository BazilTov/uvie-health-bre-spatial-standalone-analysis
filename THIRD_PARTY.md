# Bundled software and attribution

Our application source uses the MIT license in LICENSE. That does not relicense
the bundled runtime or third-party packages.

The complete Mac package contains R 4.5.2, originally obtained from the official
CRAN Apple-silicon installer. Its installer signature and Apple notarization were
verified before use. R is distributed under GPL version 2 or 3; the runtime's
COPYING file and documentation are preserved. Its source release is available at
https://cran.r-project.org/src/base/R-4/R-4.5.2.tar.gz .

The R shell launcher was adapted to locate the bundled runtime and its libraries
relative to itself. R executable binaries have not been modified by this task.

Installed analysis libraries are included with their DESCRIPTION, license files,
documentation, and attribution. runtime/package-versions.csv records their exact
versions and declared licenses. Their own licenses govern them independently.

Core reference packages:

- GeomxTools: https://bioconductor.org/packages/GeomxTools/
- NanoStringNCTools: https://bioconductor.org/packages/NanoStringNCTools/
- GeoMxWorkflows: https://bioconductor.org/packages/GeoMxWorkflows/
- Shiny: https://cran.r-project.org/package=shiny

The kidney example data are bundled by the upstream GeoMxWorkflows package.
They remain attributed to that package and assay vendor. Public endometriosis
downloads are not included in the full runtime release.

Before public redistribution, maintainers must preserve each component's notices
and provide corresponding source access as its license requires. This developer
preview is not a signed/notarized UVIE application release.
