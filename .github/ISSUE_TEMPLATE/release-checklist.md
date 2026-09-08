---
name: Release checklist
about: Checklist for a pipeline release
title: 'Release v'
labels: release
assignees: mgalloy

---

### Pre-release check

- [ ] check to make sure no changes to the production config files are needed
- [ ] add date/link to version line in `CHANGELOG.md`
- [ ] check that version to release in `CHNAGELOG.md` matches version in `pyproject.toml`

### Release to production

- [ ] merge main to production
- [ ] push production to origin
- [ ] tag production with name: `git tag -a vX.Y.Z`
- [ ] push tags: `git push --tags`

### Install production

TODO: need to decide how this will work

- push to PyPI?

### Post-release check

- [ ] send email with new release notes to ChroMag team
- [ ] in master, increment version in `pyproject.toml` and add new "Unreleased" section to `CHANGELOG.md`

### Install at MLSO

A day after production release, release to MLSO.
