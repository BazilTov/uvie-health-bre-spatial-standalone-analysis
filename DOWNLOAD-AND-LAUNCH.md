# UVIE Health BRE Spatial - Standalone

## Choose a complete package

Download one of the four **UVIE-Health-BRE-Spatial-Standalone-v0.4.0-...zip** assets on this release page. They include R, GeoMx libraries, the application, and the kidney reference inputs. You need an existing web browser; no separate R, Python, Docker, or analysis-library installation is required.

| Computer | ZIP filename ending | Launcher |
|---|---|---|
| Mac with Apple silicon | Mac-AppleSilicon.zip | launch.command |
| Mac with Intel processor | Mac-Intel.zip | launch.command |
| Windows x64 | Windows-x64.zip | launch.bat |
| Linux x64, Ubuntu 22.04 baseline | Linux-Ubuntu22.04-x64.zip | launch.command |

Mac: Apple menu > About This Mac identifies the chip or processor. Native release checks ran on macOS 14 Apple silicon, macOS 15 Intel, Windows Server 2022 x64, and Ubuntu 22.04 x64. Compatibility with every OS version or Linux distribution is not established.

**GitHub's “Source code (zip)” and “Source code (tar.gz)” downloads contain source, not the complete runtime.** Choose a platform ZIP above for a ready-to-run environment.

## Launch

1. Download and fully unzip your selected platform package into a writable local folder. Keep the whole `UVIE-Spatial` folder together; it contains the runtime and libraries.
2. On Mac, open `launch.command`. This is an unsigned developer preview; macOS may require approval through its normal security prompts. On Windows, open `launch.bat` from the extracted folder, rather than from inside the ZIP. On Linux, open a terminal in `UVIE-Spatial` and run `chmod +x launch.command`, then `./launch.command`.
3. Keep the launcher terminal open. Your browser opens the local application at `http://127.0.0.1:8765`. If the browser does not open, enter that address yourself. Closing the launcher stops the application.
4. Select **Packaged kidney reference** and click **Run reference pipeline**. Processing can take several minutes. Wait for the completion message before exploring genes and compartments or downloading evidence and run outputs.
5. Download your results before closing the launcher. Runs are local and do not upload tissue data to UVIE.

If port 8765 is already in use, stop the earlier instance or set `UVIE_PORT` to another unused port before launching. If the page does not load, inspect the launcher terminal for its error message and confirm that you downloaded the package for your processor and extracted the entire ZIP.

## Explore processed expression from another study

Choose **Processed expression ZIP**, select a ZIP containing matrix.csv, metadata.csv and provenance.json at its root, then click **Load processed expression**. The included PROCESSED-INPUT.md explains the format. This route preserves the supplied scale, method and QC limitations, aligns sample identifiers and separates declared controls. It does not rerun or verify upstream QC or normalization. It can explore supported compartment data across diseases and healthy tissues; it does not support every spatial platform or input format automatically.

## Try the tissue map

Download **Visium-mouse-brain-six-gene-example.zip** from the release assets. Leave that dataset ZIP zipped. Launch the full application, choose **Processed expression ZIP**, select the example ZIP, and click **Load processed expression**. Open **Tissue map** and choose **Gfap**, **Mbp**, or another supplied gene. Change marker opacity to inspect the underlying image, then download the map or its evidence.

The example includes all 2,825 filtered spots and six selected genes from one mouse-brain section. Each spot can contain multiple cells; no cell identity is inferred. Coordinates use full-resolution source-image pixels mapped to the preview through the vendor scale factor, not an asserted micrometre calibration. This is a display/input-integrity example, not full-transcriptome normalization or disease validation. Data are from 10x Genomics under CC BY 4.0; EXAMPLE-PROVENANCE.json records the source and archive hashes.

For your own inputs, see SPATIAL-INPUT.md. Pixel or micrometre coordinates, explicit section identity and measurement resolution are supported. Images are optional, but declared image mappings must pass bounds and integrity checks. The map does not compute neighborhoods, physical distances, spatial significance or treatment predictions. Public downloads grant no access to the private BRE.

## Verify a download

Download `SHA256SUMS.txt` into the same folder as your ZIP. Compare its SHA-256 value with the corresponding filename in that file.

- Mac terminal: `shasum -a 256 YOUR-PACKAGE.zip`
- Linux terminal: `sha256sum YOUR-PACKAGE.zip`
- Windows PowerShell: `Get-FileHash .\YOUR-PACKAGE.zip -Algorithm SHA256`

`PACKAGE-VERIFICATION.json` links the native build and unpacked-package checks. The accompanying manifest for each ZIP records its checksum and bundled content inventory digest. Checksum agreement verifies file integrity, not scientific validity.

## Scope of this preview

This release runs the established GeoMx kidney workflow through Q3 normalization and exports compartment-level RNA evidence. It does not infer individual-cell coordinates, drug binding, or treatment efficacy. The custom GeoMx ZIP option uses the kidney QC profile and requires study-specific review. Endometriosis processing and participant-level statistics have not yet been validated. See `VALIDATION.md` for the numerical benchmark evidence and limits.
