# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog] and this project adheres to
[Semantic Versioning].

## [Unreleased]

### Added

- Make an averaged dark to apply to science images.
- Apply dark correction to science images.
- Write level 1 FITS file.
- Write intensity and IQUV quicklooks.
- Lock processing directory when starting eod/reprocess run.
- Add reprocess and clearday CLI subcommands.
- Add ability to save intermediate FITS file after each processing step.
- Add completion notification emails.
- Create database tables (and createdb CLI subcommand).
- Update database tables.
- Publish and retract level 1 data.
- Create archive level 0, 1, and 2 tarballs (and archive CLI subcommand).
- Create timeline histogram of the observations for the day.

## [0.0.1]

### Added

- Basic infrastructure of the pipeline.
- Create inventory files for a date's raw observation files.
- Create `chromag` command line tool.
- Create plots of data in housekeeping CSV files.

[Keep a Changelog]: https://keepachangelog.com/en/1.0.0/
[Semantic Versioning]: https://semver.org/spec/v2.0.0.html
[0.0.1]: https://github.com/olivierlacan/keep-a-changelog/releases/tag/v0.0.1
[Unreleased]: https://github.com/olivierlacan/keep-a-changelog/compare/v0.0.1...HEAD
