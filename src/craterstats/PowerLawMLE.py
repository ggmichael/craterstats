#  Copyright (c) 2024, implemented per Robbins et al. (2018)
#  Meteoritics & Planetary Science 53, 891-931. doi:10.1111/maps.12990
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import warnings

import numpy as np
import scipy.optimize as sc
from scipy.special import erfinv
from scipy.stats import t as t_dist


class PowerLawMLE:
    """
    Maximum likelihood estimation (MLE) for crater SFD power-law fitting.
    Implements Robbins et al. (2018), Sections 4–5.

    Reference
    ---------
    Robbins et al. (2018), Meteoritics & Planetary Science 53, 891-931.
    doi:10.1111/maps.12990

    Conventions
    -----------
    α > 0 : Pareto exponent (PDF decreases with increasing D).
    ǎ = -(α+1) : differential SFD slope  [Robbins 2018, Eq. 8]
    So α=3 → ǎ=-4, consistent with the canonical lunar SFD.

    Methods
    -------
    fit_pareto            Analytic MLE for unbounded power-law  (Eqs. 9-11)
    fit_truncated_pareto  Numeric MLE with upper cutoff D_max   (Eqs. 14-17)
    fit_pf                Production-function regression         (Eqs. 18-23)
    power_law_envelope    Compute Pareto shape curves for plotting
    """

    # ------------------------------------------------------------------
    # Pareto (unbounded) MLE — Robbins 2018 Eqs. 9-11
    # ------------------------------------------------------------------

    @staticmethod
    def fit_pareto(diameters, d_min=None, ci_levels=(0.683, 0.954)):
        """
        Fit unbounded Pareto distribution to crater diameters via analytic MLE.

        Estimator (Eq. 9):   α̂ = N / Σ ln(D_i / D_min)
        Uncertainty (Eq. 10): σ_α = α̂ / √N
        CI envelope (Eq. 11): λ ≅ √2 · σ_α · erf⁻¹(ψ)

        Parameters
        ----------
        diameters : array-like
            Crater diameters in km.  All D ≥ d_min are used.
        d_min : float, optional
            Minimum diameter for fit.  Defaults to min(diameters).
        ci_levels : tuple of float
            Confidence levels for the CI envelope (e.g. 0.683 = 1σ, 0.954 = 2σ).

        Returns
        -------
        dict with keys:
            'alpha'       – MLE estimate α̂
            'sigma_alpha' – 1-σ uncertainty  σ_α = α̂/√N          (Eq. 10)
            'lambda'      – list of λ values (one per ci_level)    (Eq. 11)
            'ci_levels'   – list of CI levels matching 'lambda'
            'dsfd_slope'  – differential SFD slope  ǎ = -(α̂+1)    (Eq. 8)
            'N'           – number of craters used
            'd_min'       – d_min used
            'model'       – 'pareto'
        """
        diameters = np.asarray(diameters, dtype=float)
        if d_min is None:
            d_min = float(diameters.min())
        else:
            d_min = float(d_min)

        d_fit = diameters[diameters >= d_min]
        N = len(d_fit)
        if N < 2:
            raise ValueError(
                f"Only {N} craters at D ≥ {d_min:.4f} km; need at least 2.")

        # Eq. 9: analytic MLE estimator
        alpha_hat = N / np.sum(np.log(d_fit / d_min))

        # Eq. 10: σ_α = α̂ / √N
        sigma_alpha = alpha_hat / np.sqrt(N)

        # Eq. 11: λ = √2 · σ_α · erf⁻¹(ψ)
        lambdas = [float(np.sqrt(2.0) * sigma_alpha * erfinv(float(psi)))
                   for psi in ci_levels]

        return {
            'alpha':       float(alpha_hat),
            'sigma_alpha': float(sigma_alpha),
            'lambda':      lambdas,
            'ci_levels':   list(ci_levels),
            'dsfd_slope':  float(-(alpha_hat + 1.0)),   # Eq. 8
            'N':           N,
            'd_min':       d_min,
            'model':       'pareto',
        }

    # ------------------------------------------------------------------
    # Truncated Pareto MLE — Robbins 2018 Eqs. 14-17
    # ------------------------------------------------------------------

    @staticmethod
    def fit_truncated_pareto(diameters, d_min=None, d_max=None,
                             ci_levels=(0.683, 0.954)):
        """
        Fit truncated Pareto distribution (D_min ≤ D ≤ D_max) via numeric MLE.

        Score equation (Eq. 14), solved with Brent's method:
            S(α) = N/α + N·r^α·ln(r)/(1−r^α) − Σ ln(D_i/D_min) = 0
            where r = D_min/D_max < 1

        Asymptotic variance from Fisher information (Eqs. 15-17):
            I(α) = N/α² − N·(ln r)²·r^α/(1−r^α)²
            Avar(α̂) = 1/I(α̂)

        Parameters
        ----------
        diameters : array-like
            Crater diameters in km.
        d_min : float, optional
            Lower truncation point.  Defaults to min(diameters).
        d_max : float, optional
            Upper truncation point.  Defaults to max(diameters).
        ci_levels : tuple of float
            Confidence levels for CI envelope.

        Returns
        -------
        dict — same structure as fit_pareto(), with additional key 'd_max'.
        """
        diameters = np.asarray(diameters, dtype=float)
        if d_min is None:
            d_min = float(diameters.min())
        if d_max is None:
            d_max = float(diameters.max())
        d_min, d_max = float(d_min), float(d_max)

        if d_max <= d_min:
            raise ValueError(
                f"d_max ({d_max:.4f}) must be > d_min ({d_min:.4f})")

        d_fit = diameters[(diameters >= d_min) & (diameters <= d_max)]
        N = len(d_fit)
        if N < 2:
            raise ValueError(
                f"Only {N} craters in [{d_min:.4f}, {d_max:.4f}] km; need ≥ 2.")

        r = d_min / d_max        # < 1
        ln_r = np.log(r)         # < 0
        sum_lnD = np.sum(np.log(d_fit / d_min))    # > 0

        # Score function S(α) — Eq. 14
        # Derivation: ∂ℓ/∂α = N/α + N·r^α·ln(r)/(1−r^α) − Σln(D_i/D_min) = 0
        # S → +∞ as α→0⁺;  S → −Σln(D_i/D_min) < 0 as α→+∞
        def score(alpha):
            r_a = r ** alpha
            denom = 1.0 - r_a
            if denom < 1e-300:
                return -np.inf
            return N / alpha + N * r_a * ln_r / denom - sum_lnD

        # Bracket: lo near 0, hi = 2× unbounded estimate (always negative)
        lo = 1e-8
        hi = 2.0 * N / sum_lnD
        for _ in range(80):
            if score(hi) < 0.0:
                break
            hi *= 2.0
        else:
            raise RuntimeError(
                "Could not bracket root of truncated Pareto score function. "
                "Check d_min / d_max values.")

        alpha_hat = sc.brentq(score, lo, hi, xtol=1e-12, rtol=1e-12)

        # Fisher information I(α) = N/α² − N·(ln r)²·r^α/(1−r^α)²
        # (negative expected second derivative of log-likelihood)
        r_a   = r ** alpha_hat
        denom = 1.0 - r_a
        fisher_info = (N / alpha_hat ** 2
                       - N * ln_r ** 2 * r_a / denom ** 2)

        if fisher_info <= 0.0:
            warnings.warn(
                "Fisher information is non-positive; uncertainty estimate may be "
                "unreliable.  Consider widening the diameter range or using the "
                "unbounded Pareto fit.")
            fisher_info = N / alpha_hat ** 2 * 1e-6   # safe fallback

        sigma_alpha = float(np.sqrt(1.0 / fisher_info))

        # Eq. 11 (same form as unbounded case)
        lambdas = [float(np.sqrt(2.0) * sigma_alpha * erfinv(float(psi)))
                   for psi in ci_levels]

        return {
            'alpha':       float(alpha_hat),
            'sigma_alpha': float(sigma_alpha),
            'lambda':      lambdas,
            'ci_levels':   list(ci_levels),
            'dsfd_slope':  float(-(alpha_hat + 1.0)),
            'N':           N,
            'd_min':       d_min,
            'd_max':       d_max,
            'model':       'truncated_pareto',
        }

    # ------------------------------------------------------------------
    # Production-function regression — Robbins 2018 Eqs. 18-23
    # ------------------------------------------------------------------

    @staticmethod
    def fit_pf(sfd_edf, pf, d_range=None, presentation='cumulative', psi=0.683):
        """
        Fit a production function to the EDF by regression through the origin.
        (Robbins 2018, Eqs. 18–23)

        Model:  SFD_EDF(D_i) = β₁ · PF(D_i, a0=0) + ε_i

        Estimator (Eq. 20):
            β̂₁ = Σ [SFD_EDF(D_i) · PF(D_i)] / Σ [PF(D_i)²]

        The EDF is interpolated onto each measured crater diameter D_i.
        PF is evaluated at a0 = 0 (shape only; amplitude encoded in β̂₁).
        Converting: a0_fit = log₁₀(β̂₁).

        Parameters
        ----------
        sfd_edf : BootstrapSFD
            Instance with attributes .diameters, .d_grid, .csfd_scaled,
            .dsfd_scaled, .area.
        pf : Productionfn
            craterstats production-function instance (.C and .F methods).
        d_range : [float, float], optional
            Diameter range [d_lo, d_hi] to use in fit.
            Defaults to full range of sfd_edf.diameters.
        presentation : str
            'cumulative' (default) or 'differential'.
        psi : float
            Confidence level for the t-interval on β̂₁ (default 0.683 ≈ 1σ).

        Returns
        -------
        dict with keys:
            'beta1'        – best-fit scaling factor β̂₁
            'beta1_lo'     – lower CI on β̂₁            (Eq. 23)
            'beta1_hi'     – upper CI on β̂₁
            'sigma_beta1'  – standard error on β̂₁      (Eq. 22)
            'a0'           – log₁₀(β̂₁), i.e. craterstats-equivalent a0
            'a0_lo'        – lower CI on a0
            'a0_hi'        – upper CI on a0
            'mse'          – mean squared error of the fit
            'N'            – number of data points used
            'presentation' – SFD presentation used
        """
        d_all = sfd_edf.diameters   # ascending km

        if d_range is not None:
            mask = (d_all >= d_range[0]) & (d_all <= d_range[1])
        else:
            mask = np.ones(len(d_all), dtype=bool)

        d_pts = d_all[mask]
        N = int(mask.sum())
        if N < 2:
            raise ValueError(f"Only {N} craters in fit range; need at least 2.")

        # Interpolate EDF at each crater diameter
        if presentation == 'cumulative':
            edf_vals = np.interp(d_pts, sfd_edf.d_grid, sfd_edf.csfd_scaled)
            pf_vals  = pf.C(d_pts, 0.0)
        elif presentation == 'differential':
            edf_vals = np.interp(d_pts, sfd_edf.d_grid, sfd_edf.dsfd_scaled)
            pf_vals  = pf.F(d_pts, 0.0)
        else:
            raise ValueError(
                f"presentation must be 'cumulative' or 'differential', "
                f"got '{presentation}'")

        # Eq. 20: β̂₁ = Σ(y_i · x_i) / Σ(x_i²)
        sum_xy = float(np.dot(edf_vals, pf_vals))
        sum_x2 = float(np.dot(pf_vals, pf_vals))
        if sum_x2 == 0.0:
            raise ValueError(
                "Production function evaluates to zero at all data points.")

        beta1 = sum_xy / sum_x2

        # Eq. 21: MSE = Σ(y_i − β̂₁·x_i)² / (N−1)
        residuals = edf_vals - beta1 * pf_vals
        mse = float(np.dot(residuals, residuals)) / max(N - 1, 1)

        # Eq. 22: Var(β̂₁) = MSE / Σ(x_i²)
        sigma_beta1 = float(np.sqrt(max(mse / sum_x2, 0.0)))

        # Eq. 23: t-statistic CI  — P(|T| ≤ t_crit) = psi
        t_crit = float(t_dist.ppf((1.0 + psi) / 2.0, df=max(N - 1, 1)))
        margin    = t_crit * sigma_beta1
        beta1_lo  = max(float(beta1) - margin, 1e-300)
        beta1_hi  = float(beta1) + margin

        with np.errstate(divide='ignore'):
            a0    = float(np.log10(max(float(beta1), 1e-300)))
            a0_lo = float(np.log10(beta1_lo))
            a0_hi = float(np.log10(beta1_hi))

        return {
            'beta1':        float(beta1),
            'beta1_lo':     float(beta1_lo),
            'beta1_hi':     float(beta1_hi),
            'sigma_beta1':  float(sigma_beta1),
            'a0':           a0,
            'a0_lo':        a0_lo,
            'a0_hi':        a0_hi,
            'mse':          float(mse),
            'N':            N,
            'presentation': presentation,
        }

    # ------------------------------------------------------------------
    # Plotting utility — Pareto shape envelopes
    # ------------------------------------------------------------------

    @staticmethod
    def power_law_envelope(d_grid, alpha_hat, d_min, lambdas, ci_levels,
                           presentation='differential'):
        """
        Compute Pareto power-law SFD shapes for the MLE best fit and CI envelopes.

        All shapes are **normalised to 1.0 at d_min**.  To obtain absolute
        densities, multiply by the EDF value at d_min:
            edf_anchor = np.interp(d_min, sfd.d_grid, sfd.dsfd_scaled)

        The CI envelope reflects the uncertainty in slope α:
            y_hi → shallower slope (α̂ − λ) → higher values at large D
            y_lo → steeper slope  (α̂ + λ) → lower  values at large D

        Parameters
        ----------
        d_grid       : array-like – diameter grid (km); d < d_min are excluded
        alpha_hat    : float      – MLE Pareto exponent α̂
        d_min        : float      – reference / normalisation diameter
        lambdas      : list       – λ values from fit_pareto / fit_truncated_pareto
        ci_levels    : list       – confidence levels matching lambdas
        presentation : str        – 'differential', 'cumulative', or 'R-plot'

        Returns
        -------
        dict with keys:
            'd_grid'    – diameters (km), d ≥ d_min
            'y_fit'     – best-fit shape (= 1.0 at d_min)
            'envelopes' – list of dicts, one per CI level:
                          {'psi', 'lambda', 'y_lo', 'y_hi'}
        """
        d_grid = np.asarray(d_grid, dtype=float)
        mask = d_grid >= d_min
        d    = d_grid[mask]
        x    = d / d_min    # ≥ 1

        if presentation == 'differential':
            # DSFD ∝ D^{-(α+1)}
            def shape(alpha):
                return x ** (-(alpha + 1.0))

        elif presentation == 'cumulative':
            # CSFD ∝ D^{-α}
            def shape(alpha):
                return x ** (-alpha)

        elif presentation == 'R-plot':
            # R = DSFD · D³ ∝ D^{2−α}
            def shape(alpha):
                return x ** (2.0 - alpha)

        else:
            raise ValueError(f"Unknown presentation '{presentation}'.")

        y_fit = shape(alpha_hat)

        envelopes = []
        for lam, psi in zip(lambdas, ci_levels):
            envelopes.append({
                'psi':    float(psi),
                'lambda': float(lam),
                'y_lo':   shape(alpha_hat + lam),   # steeper → lower at large D
                'y_hi':   shape(alpha_hat - lam),   # shallower → higher at large D
            })

        return {
            'd_grid':       d,
            'y_fit':        y_fit,
            'envelopes':    envelopes,
            'alpha':        float(alpha_hat),
            'd_min':        float(d_min),
            'presentation': presentation,
        }
