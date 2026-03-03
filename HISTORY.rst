=======
History
=======

3.0.12 2022-12-21
-----------------
* valid range for Neukum 2001 lunar PF modified and citation added

3.1.0
-----
* sequence plot added

3.2.0
-----
* uncertainty plots added

3.2.1
-----
* uncertainty saturation calculation replaced with user-selected equilibrium function

3.3.0
-----
* upgrade python version to 3.12

3.4.0
-----
* add Windows binary release

3.4.1
-----
* add support for *_CRATER.shp as input format from ArcPro (requires paired *_AREA.shp file and unprojected (geographic)
coordinate system for both layers)

3.5.0
-----
* support for conversion between .scc and .shp formats

3.6.0
-----
- Spatial randomness analysis (see Michael et al., 2012) using spherical geometry for calculations
- Conversion of .scc/.shp data sources to map plots

3.6.3
-----
- Add MacOS binaries as beta
- fix --functions_user config for pyinstaller versions

3.7.0 (pending)
---------------
- Add ``BootstrapSFD`` class: KDE/EDF-based bootstrap confidence intervals for
  crater size-frequency distributions, following Robbins et al. (2018),
  *Meteoritics & Planetary Science* 53, 891–931.  Implements all four bootstrap
  versions (V1.1 direct resample, V1.2 smoothed resample, V2 EDF sampling,
  V3 hybrid — recommended).  CI can be expressed in differential, cumulative,
  R-plot, or Hartmann presentation.
- Add ``PowerLawMLE`` class: maximum likelihood estimation for crater SFD
  power-law fitting (Robbins et al. 2018, §4–5).  Provides analytic MLE for
  the unbounded Pareto distribution (Eqs. 9–11), numeric MLE for the truncated
  Pareto (Eqs. 14–17), production-function regression through the origin
  (Eqs. 18–23), and Pareto CI envelope plotting utilities.
- Integrate bootstrap CI into ``Craterplot`` via new ``bootstrap_ci``,
  ``bootstrap_version``, ``bootstrap_M``, ``bootstrap_psi``,
  ``bootstrap_bw``, and ``bootstrap_show_2sigma`` settings.
- Fix missing ``legend`` default in ``Craterplotset`` settings.