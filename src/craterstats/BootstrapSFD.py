#  Copyright (c) 2024, implemented per Robbins et al. (2018)
#  Meteoritics & Planetary Science 53, 891-931. doi:10.1111/maps.12990
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import numpy as np
from scipy.stats import norm


class BootstrapSFD:
    """
    Kernel Density Estimate (KDE) based Empirical Distribution Function (EDF)
    with bootstrap confidence intervals, following Robbins et al. (2018).

    The EDF represents a Differential SFD where each crater is a Gaussian
    with mean = measured diameter and sigma = bandwidth (default 0.1 * D_i).

    Bootstrap versions:
      '1.1' : Direct resampling with replacement (simple)
      '1.2' : Direct resampling with smoothing (add Gaussian noise)
      '2'   : Sampling the EDF (inverse CDF method)
      '3'   : Hybrid — version 1.1 where data dense, version 2 where sparse
               (Recommended by Robbins 2018)
    """

    def __init__(self, diameters, area=1.0, bandwidth_fraction=0.1, n_sigma=4, epsilon=1e-3):
        """
        :param diameters:          Array-like of crater diameters in km
        :param area:               Survey area in km^2 (used to normalise to km^-2)
        :param bandwidth_fraction: σ_i = bandwidth_fraction * D_i  (default 0.1)
        :param n_sigma:            Truncation: evaluate kernel out to n_sigma * σ_i
                                   beyond D_min / D_max  (default 4)
        :param epsilon:            Diameter grid spacing in log10 space (default 1e-3)
        """
        diameters = np.asarray(diameters, dtype=float)
        if diameters.ndim != 1 or len(diameters) == 0:
            raise ValueError("diameters must be a non-empty 1-D array")

        self.diameters = np.sort(diameters)          # ascending
        self.N = len(self.diameters)
        self.area = float(area)
        self.bw_frac = float(bandwidth_fraction)
        self.n_sigma = int(n_sigma)
        self.epsilon = float(epsilon)

        # per-crater bandwidths
        self.sigma = self.bw_frac * self.diameters

        # build the EDF on a dense diameter grid
        self._build_edf()

    # ------------------------------------------------------------------
    # EDF construction
    # ------------------------------------------------------------------

    def _build_edf(self):
        """Build the Differential EDF (DSFD_EDF) on a log-spaced diameter grid."""

        D_min = self.diameters[0]
        D_max = self.diameters[-1]
        sigma_min = self.sigma[0]
        sigma_max = self.sigma[-1]

        # Grid extends n_sigma beyond observed range (Robbins 2018, p. 901)
        d_lo = D_min - self.n_sigma * sigma_min
        d_hi = D_max + self.n_sigma * sigma_max
        d_lo = max(d_lo, 1e-6)   # prevent non-positive diameters

        # Equation (5): log-spaced grid
        v = int(np.floor(np.log(d_hi / d_lo) / self.epsilon)) + 1
        i_vals = np.arange(v)
        self.d_grid = d_lo * (d_hi / d_lo) ** (i_vals / max(v - 1, 1))

        # DSFD_EDF = sum of normalised Gaussians (one per crater)
        # Shape: (len(d_grid), N) → sum over craters
        d2d = self.d_grid[:, np.newaxis]           # (v, 1)
        mu = self.diameters[np.newaxis, :]          # (1, N)
        sig = self.sigma[np.newaxis, :]             # (1, N)

        # Gaussian PDF values (not truncated — we just evaluate broadly)
        kernels = norm.pdf(d2d, loc=mu, scale=sig)  # (v, N)
        self.dsfd_edf = kernels.sum(axis=1)         # (v,) raw sum

        # Build CSFD_EDF by trapezoidal integration (Equation 2)
        self.csfd_edf = self._dsfd_to_csfd(self.dsfd_edf, self.d_grid)

        # Scaling factor ζ = N / CSFD_EDF(d_min)  (Equation 3)
        # d_min for scaling is the grid point nearest to D_min - n_sigma*sigma_min
        self.zeta = self.N / self.csfd_edf[0]

        # Normalised (physically scaled) versions
        self.dsfd_scaled = self.dsfd_edf * self.zeta / self.area
        self.csfd_scaled = self.csfd_edf * self.zeta / self.area

    @staticmethod
    def _dsfd_to_csfd(dsfd, d_grid):
        """
        Integrate DSFD → CSFD using the trapezoidal rule, working right to left
        (cumulative counts at diameter d = integral from d to d_max).
        """
        # ISFD_EDF(d_i) = (DSFD(d_i) + DSFD(d_{i+1})) / 2 * (d_{i+1} - d_i)
        dd = np.diff(d_grid)                        # (v-1,)
        isfd = 0.5 * (dsfd[:-1] + dsfd[1:]) * dd   # (v-1,)

        # CSFD(d_i) = sum_{j=i}^{N-2} ISFD(j)  (cumulative from right)
        csfd = np.zeros(len(d_grid))
        csfd[:-1] = np.flip(np.cumsum(np.flip(isfd)))
        return csfd

    # ------------------------------------------------------------------
    # Bootstrap CI computation
    # ------------------------------------------------------------------

    def bootstrap_ci(self, version='3', M=1000, psi=0.683, n_hybrid=0.75,
                     rng=None):
        """
        Compute bootstrap confidence intervals per Robbins et al. (2018).

        :param version:   Bootstrap version: '1.1', '1.2', '2', or '3' (default)
        :param M:         Number of Monte Carlo iterations (default 1000)
        :param psi:       Confidence level fraction (default 0.683 = 1σ)
        :param n_hybrid:  Threshold factor n for hybrid version 3 (default 0.75)
        :param rng:       numpy random Generator or seed for reproducibility
        :return:          dict with keys:
                            'd_grid'    : diameter grid (km)
                            'dsfd_edf'  : original DSFD_EDF (normalised, per km^-2)
                            'ci_lo'     : lower CI bound on DSFD_EDF (per km^-2)
                            'ci_hi'     : upper CI bound on DSFD_EDF (per km^-2)
                            'psi'       : confidence level used
                            'version'   : bootstrap version used
        """
        if rng is None:
            rng = np.random.default_rng()
        elif isinstance(rng, (int, np.integer)):
            rng = np.random.default_rng(int(rng))

        M = int(M)
        v = len(self.d_grid)

        # Collect DSFD values from each bootstrap run: shape (M, v)
        edf_runs = np.zeros((M, v))

        if version == '1.1':
            for i in range(M):
                d_boot = self._resample_direct(rng)
                edf_runs[i] = self._build_edf_from_diameters(d_boot)

        elif version == '1.2':
            for i in range(M):
                d_boot = self._resample_smoothed(rng)
                edf_runs[i] = self._build_edf_from_diameters(d_boot)

        elif version == '2':
            for i in range(M):
                d_boot = self._resample_edf(rng)
                edf_runs[i] = self._build_edf_from_diameters(d_boot)

        elif version == '3':
            for i in range(M):
                d_boot = self._resample_hybrid(rng, n=n_hybrid)
                edf_runs[i] = self._build_edf_from_diameters(d_boot)

        else:
            raise ValueError(f"Unknown bootstrap version '{version}'. "
                             "Choose from '1.1', '1.2', '2', '3'.")

        # Scale each run's EDF by the ORIGINAL ζ (step e in Robbins 2018)
        # edf_runs are raw unscaled sums; multiply by zeta / area
        edf_runs *= (self.zeta / self.area)

        # --- CI construction (steps g–j in Robbins 2018) ---
        # For each diameter, sort the M bootstrap values
        edf_runs_sorted = np.sort(edf_runs, axis=0)     # (M, v)

        # Original EDF (scaled)
        dsfd_orig = self.dsfd_scaled                     # (v,)

        # θ_i = position where bootstrap EDF matches the original (step g)
        # Use searchsorted for efficiency
        theta = np.array([
            np.searchsorted(edf_runs_sorted[:, j], dsfd_orig[j])
            for j in range(v)
        ], dtype=float)

        # Clip to valid range
        theta = np.clip(theta, 0, M)

        # Lower bound position: θ_i · (1−ψ)  (step h)
        lo_pos = theta * (1.0 - psi)
        # Upper bound position: (M − θ_i)·ψ + θ_i  (step i)
        hi_pos = (M - theta) * psi + theta

        # Clip index to [0, M-1] and extract values
        lo_idx = np.clip(lo_pos.astype(int), 0, M - 1)
        hi_idx = np.clip(hi_pos.astype(int), 0, M - 1)

        ci_lo = edf_runs_sorted[lo_idx, np.arange(v)]
        ci_hi = edf_runs_sorted[hi_idx, np.arange(v)]

        return {
            'd_grid': self.d_grid,
            'dsfd_edf': dsfd_orig,
            'csfd_edf': self.csfd_scaled,
            'ci_lo': ci_lo,
            'ci_hi': ci_hi,
            'psi': psi,
            'version': version,
        }

    # ------------------------------------------------------------------
    # Bootstrap resampling strategies
    # ------------------------------------------------------------------

    def _resample_direct(self, rng):
        """Version 1.1: sample N diameters with replacement."""
        idx = rng.integers(0, self.N, size=self.N)
        return np.sort(self.diameters[idx])

    def _resample_smoothed(self, rng):
        """Version 1.2: sample with replacement, then add Gaussian noise."""
        idx = rng.integers(0, self.N, size=self.N)
        d_sampled = self.diameters[idx]
        sigma_sampled = self.bw_frac * d_sampled
        noise = rng.normal(0, sigma_sampled)
        d_new = np.abs(d_sampled + noise)   # keep positive
        d_new = np.maximum(d_new, 1e-6)
        return np.sort(d_new)

    def _resample_edf(self, rng):
        """Version 2: sample N diameters from the EDF via inverse CDF."""
        # Normalise CSFD_EDF to [0, 1]
        csfd_norm = self.csfd_edf / self.csfd_edf[0]   # max at d_lo = 1
        # Draw N uniform samples
        u = rng.uniform(0, 1, size=self.N)
        # Inverse lookup: for each u, find diameter where csfd_norm == u
        # csfd_norm is DECREASING (large at small d), so flip for searchsorted
        csfd_flip = csfd_norm[::-1]
        d_grid_flip = self.d_grid[::-1]
        idx = np.searchsorted(csfd_flip, u)
        idx = np.clip(idx, 0, len(self.d_grid) - 1)
        return np.sort(d_grid_flip[idx])

    def _resample_hybrid(self, rng, n=0.75):
        """
        Version 3: direct resampling where data are dense, EDF sampling where sparse.
        Follows steps b.4-b.5 in Robbins 2018.
        """
        # First, get N diameters from the EDF (version 2 starting point)
        d_edf = self._resample_edf(rng)
        d_boot = np.empty(self.N)

        d_sorted = self.diameters       # ascending
        sigma_sorted = self.sigma       # ascending

        D_min = d_sorted[0]
        D_max = d_sorted[-1]

        for k, d_i in enumerate(d_edf):
            # Find closest original crater
            j = np.argmin(np.abs(d_sorted - d_i))
            D_closest = d_sorted[j]

            if D_closest <= D_min:
                # b.5.i: use D_min
                d_boot[k] = D_min
            elif D_closest >= D_max:
                # b.5.ii: sparse at top — use EDF sample
                d_boot[k] = d_i
            else:
                # b.5.iii: check density condition
                j_prev = max(j - 1, 0)
                j_next = min(j + 1, self.N - 1)
                gap_lo = D_closest - d_sorted[j_prev]
                gap_hi = d_sorted[j_next] - D_closest
                thresh_lo = n * (sigma_sorted[j] + sigma_sorted[j_prev])
                thresh_hi = n * (sigma_sorted[j_next] + sigma_sorted[j])
                if gap_lo < thresh_lo and gap_hi < thresh_hi:
                    # Dense region: use direct resampling (V1.1)
                    d_boot[k] = D_closest
                else:
                    # Sparse region: use EDF sample (V2)
                    d_boot[k] = d_i

        return np.sort(d_boot)

    # ------------------------------------------------------------------
    # Helper: build raw DSFD from a set of diameters (same grid as self)
    # ------------------------------------------------------------------

    def _build_edf_from_diameters(self, diameters):
        """
        Build a raw (unscaled) DSFD on self.d_grid for a bootstrapped diameter set.

        Returns DSFD values (sum of Gaussian kernels) on self.d_grid.
        Uses the ORIGINAL ζ for scaling (applied externally).
        """
        sigma = self.bw_frac * diameters
        d2d = self.d_grid[:, np.newaxis]        # (v, 1)
        mu = diameters[np.newaxis, :]            # (1, N)
        sig = sigma[np.newaxis, :]               # (1, N)
        kernels = norm.pdf(d2d, loc=mu, scale=sig)  # (v, N)
        return kernels.sum(axis=1)               # (v,) raw unscaled

    # ------------------------------------------------------------------
    # Conversion utilities: DSFD_EDF → other SFD formats
    # ------------------------------------------------------------------

    def ci_to_presentation(self, ci_result, presentation):
        """
        Convert bootstrap CI (computed on DSFD_EDF) to another SFD presentation.

        The CI is RELATIVE to the DSFD_EDF, so the same relative fractional
        uncertainty applies to all presentations.  Following Robbins 2018 §6:
        if CI on DSFD_EDF at d_s is (+20%, -30%), then the CI on CSFD_EDF,
        RSFD_EDF, ISFD_EDF at d_s is also (+20%, -30%).

        :param ci_result:    dict returned by bootstrap_ci()
        :param presentation: 'differential' | 'cumulative' | 'R-plot' | 'Hartmann'
        :return: dict with keys 'd_grid', 'y', 'ci_lo', 'ci_hi'
        """
        dsfd = ci_result['dsfd_edf']
        ci_lo = ci_result['ci_lo']
        ci_hi = ci_result['ci_hi']
        d = ci_result['d_grid']

        # Relative CI factors
        with np.errstate(divide='ignore', invalid='ignore'):
            f_lo = np.where(dsfd > 0, ci_lo / dsfd, 0.0)
            f_hi = np.where(dsfd > 0, ci_hi / dsfd, 0.0)

        if presentation == 'differential':
            y = dsfd
            y_lo = ci_lo
            y_hi = ci_hi

        elif presentation == 'cumulative':
            y = ci_result['csfd_edf']
            y_lo = y * f_lo
            y_hi = y * f_hi

        elif presentation == 'R-plot':
            y = dsfd * d ** 3
            y_lo = y * f_lo
            y_hi = y * f_hi

        elif presentation == 'Hartmann':
            # Hartmann: N_inc / bin_width * D * (√2 - 1)
            # For continuous EDF: approximate as DSFD * D * (√2 - 1)
            y = dsfd * d * (np.sqrt(2) - 1)
            y_lo = y * f_lo
            y_hi = y * f_hi

        else:
            raise ValueError(f"Unknown presentation '{presentation}'")

        return {'d_grid': d, 'y': y, 'ci_lo': y_lo, 'ci_hi': y_hi}
