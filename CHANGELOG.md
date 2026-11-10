# History

## 3.7

- Diagnostic reporting for faulty shapefiles.
- Allow distinctly named _AREA.shp file with shp_area= plot parameter so one crater file can be used across several areas
- Add buffered={0|1} plot parameter, which applies to both data and fitting/Poisson overplots. 'buffered-Poisson' is thus removed.

## 3.6.11

- Improve error reporting for faulty shapefiles.

## 3.6.4

- Refactor in preparation for GUI version.
- Fix Poisson PDF normalisation (reduces uncertainty mainly of low-count, >3 Ga results). Thanks to Sam Bell for pointing this out.

## 3.6.3

- Add macOS binaries as beta.
- Fix `--functions_user` config for PyInstaller versions.

## 3.6.0

- Spatial randomness analysis (see Michael et al., 2012) using spherical geometry for calculations.
- Conversion of `.scc`/`.shp` data sources to map plots.

## 3.5.0

- Support for conversion between `.scc` and `.shp` formats.

## 3.4.1

- Add support for `*_CRATER.shp` as input format from ArcPro (requires paired `*_AREA.shp` file and unprojected (geographic) coordinate system for both layers).

## 3.4.0

- Add Windows binary release.

## 3.3.0

- Upgrade Python version to 3.12.

## 3.2.1

- Uncertainty saturation calculation replaced with user-selected equilibrium function.

## 3.2.0

- Uncertainty plots added.

## 3.1.0

- Sequence plot added.

## 3.0.12 — 2022-12-21

- Valid range for Neukum 2001 lunar PF modified and citation added.