# Local XAR test packages

This folder contains local build helpers for incremental BEBB data package tests during the TEI Publisher 10 migration.

The generated XAR files are written to `build_codex/out/`, which is intentionally ignored by Git. The source TEI data structure is not changed by these test builds.

## Build the Daniel II sample package

```sh
ant -f build_codex/build-test-xars.xml xar-daniel-ii
```

This creates a small package containing the standard package metadata plus the Daniel II letter sample under the original data path.

## Build a letters-only package

```sh
ant -f build_codex/build-test-xars.xml xar-letters
```

This creates a larger package with all letters, excluding image data and duplicate-letter folders. Use it only after the small Daniel II package has deployed successfully.


## Build a register-only package

```sh
ant -f build_codex/build-test-xars.xml xar-register
```

This creates a package with the register data only. Use it to test whether the TP10 app can install and resolve register resources independently from the letters.

## Build a letters plus register package

```sh
ant -f build_codex/build-test-xars.xml xar-letters-register
```

This creates a combined package with letters, ancillary files, and register data.
