import time
import numpy as np
from scipy import ndimage
from astropy.io import fits


def shift_sub(image, dx, dy):
    """Guaranteed fast order=1 subpixel shift on float32 array."""
    shifted = ndimage.shift(image, shift=[dx, dy], order=1, mode="nearest")
    return np.ascontiguousarray(shifted, dtype=np.float32)


def alignoffset_placeholder(tmp, reference):
    """
    Placeholder for the external IDL 'alignoffset' routine.
    In Python, this is typically done using cross-correlation
    (e.g., skimage.registration.phase_cross_correlation).
    """
    return np.array([0.0, 0.0], dtype=np.float32)


def gaincalib(
    logimages,
    x=None,
    y=None,
    object_param=None,
    maxiter=10,
    silent=False,
    c=None,
    shift_flag=0,
    mask=None,
):
    """
    Python implementation of ALfred's GAINCALIB algorithm.
    """
    nx, ny, nf = logimages.shape

    if mask is None:
        mask = np.ones((nx, ny, nf), dtype=np.uint8)

    i = np.arange(nx, dtype=np.float32).reshape(nx, 1)
    j = np.arange(ny, dtype=np.float32).reshape(1, ny)

    # 1. Initial Estimate of x and y shifts
    if shift_flag == 0 or x is None or y is None:
        x = np.zeros(nf, dtype=np.float32)
        y = np.zeros(nf, dtype=np.float32)
        flat = np.zeros((nx, ny), dtype=np.float32)
        c = np.zeros(nf, dtype=np.float32)

        for k in range(nf):
            masked_pixels = logimages[:, :, k][mask[:, :, k] > 0]
            c[k] = np.median(masked_pixels) if masked_pixels.size > 0 else 0.0

        for ix in range(nx):
            for jy in range(ny):
                mask_sum = np.sum(mask[ix, jy, :])
                if mask_sum > 1.0:
                    flat[ix, jy] = (
                        np.sum((logimages[ix, jy, :] - c) * mask[ix, jy, :]) / mask_sum
                    )
                else:
                    flat[ix, jy] = 0.0

        # Apply running median filter
        flat = ndimage.median_filter(flat, size=5)

        ss = (nf // 2) - 1
        ref_masked = (
            logimages[:, :, ss] - np.median(logimages[:, :, ss]) - flat
        ) * mask[:, :, ss]

        for k in range(nf):
            tmp = (logimages[:, :, k] - np.median(logimages[:, :, k]) - flat) * mask[
                :, :, k
            ]
            sh = alignoffset_placeholder(tmp, ref_masked)
            x[k] = sh[0]
            y[k] = sh[1]

    # Normalize shifts to zero-mean
    x = x - np.sum(x) / nf
    y = y - np.sum(y) / nf

    # 2. Initial Estimates of Flat, Object, and C
    flat = np.zeros((nx, ny), dtype=np.float32)
    object_param = np.sum(logimages, axis=2) / nf

    c = np.zeros(nf, dtype=np.float32)
    total_pixels = nx * ny
    sum_obj = np.sum(object_param)
    for k in range(nf):
        c[k] = (np.sum(logimages[:, :, k]) / total_pixels) - (sum_obj / total_pixels)

    c = c - np.sum(c) / nf

    # Finite difference kernel for tracking derivatives [-1, 8, 0, -8, 1]/12
    deriv_kernel_x = np.array([-1, 8, 0, -8, 1], dtype=np.float32).reshape(5, 1) / 12.0
    deriv_kernel_y = np.array([-1, 8, 0, -8, 1], dtype=np.float32).reshape(1, 5) / 12.0

    t1 = time.time()
    converged = False

    # 3. Optimization Iterations
    for iter_idx in range(1, maxiter + 1):
        aa = np.zeros((nx, ny), dtype=np.float32)
        bb = np.zeros((nx, ny), dtype=np.float32)

        # --- Update Object Space ---
        for k in range(nf):
            cond_i = (i + x[k] >= 0) & (i + x[k] <= nx - 1)
            cond_j = (j + y[k] >= 0) & (j + y[k] <= ny - 1)
            weight = cond_i & cond_j

            shifted_mask = shift_sub(mask[:, :, k].astype(np.float32), -x[k], -y[k])
            weight = weight * (shifted_mask >= 0.9)

            shifted_val = shift_sub(logimages[:, :, k] - flat, -x[k], -y[k])
            aa += (c[k] + object_param - shifted_val) * weight
            bb += weight

        bb_clipped = np.maximum(bb, 1.0)
        del_object = -aa / bb_clipped
        object_param += del_object

        # --- Update Variables C, Shifts, and Flat ---
        aa = np.zeros((nx, ny), dtype=np.float32)
        bb = np.zeros((nx, ny), dtype=np.float32)

        for k in range(nf):
            cond_i = (i - x[k] >= 0) & (i - x[k] <= nx - 1)
            cond_j = (j - y[k] >= 0) & (j - y[k] <= ny - 1)
            weight = cond_i & cond_j
            weight = weight * mask[:, :, k]

            object1 = shift_sub(object_param, x[k], y[k])
            ob = (c[k] + object1 + flat - logimages[:, :, k]) * weight

            weight_sum = np.sum(weight)
            if weight_sum > 0:
                c[k] -= np.sum(ob) / weight_sum

            if shift_flag <= 1:
                oi = ndimage.convolve(object1, deriv_kernel_x, mode="nearest")
                oj = ndimage.convolve(object1, deriv_kernel_y, mode="nearest")

                denom_x = np.sum(weight * (oi**2))
                denom_y = np.sum(weight * (oj**2))

                if denom_x > 0:
                    dx = np.sum(ob * oi) / denom_x
                    x[k] -= np.clip(dx, -1.0, 1.0)
                if denom_y > 0:
                    dy = np.sum(ob * oj) / denom_y
                    y[k] -= np.clip(dy, -1.0, 1.0)

            aa += ob
            bb += weight

        del_flat = -aa / np.maximum(bb, 1.0)
        flat += del_flat

        error = np.max(np.abs(del_flat))

        # check for nan or inf (non-convergence)
        if not np.isfinite(error):
            if not silent:
                print(
                    f"Iteration #{iter_idx}: Divergence detected (NaN/Inf). Aborting and returning best estimate."
                )
            break

        if not silent:
            print(f"Iteration #{iter_idx} = max(abs(dellogflat)) = {error:.6e}")

        if error <= 1.0e-8:
            converged = True
            break

    if not converged and not silent and np.isfinite(error):
        print(
            f"Warning: Reached maxiter ({maxiter}) without full convergence. Returning current flat state."
        )

    # 4. Final Balance Tuning
    mean_flat = np.sum(flat) / total_pixels
    mean_c = np.sum(c) / nf

    object_param = object_param + mean_flat + mean_c
    flat = flat - mean_flat
    c = c - mean_c

    if not silent:
        print(f"{time.time() - t1:.4f} seconds elapsed in GAINCALIB iteration")

    return flat, object_param, c, x, y


def get_flat(
    files,
    dark,
    l=None,
    m=None,
    ndata_integ=1.0,
    object_param=None,
    c=None,
    maxiter=10,
    xr=None,
    yr=None,
    shift_flag=0,
    minfrac=0.01,
    mask=None,
    silent=False,
):
    """
    Produces flat patterns from displaced observations
    **NOTE**: this is currently without dark frames!

    Parameters:
    -----------
    files : list of str, or list/3D array of np.ndarray
        FITS file paths or pre-loaded image arrays of shape (NX, NY).
    dark: "master" dark matching exposure time of the flats
    l, m : np.ndarray, optional
        Initial x and y shifts.
    """
    nf = len(files)
    logimages = None
    s = None

    # 1. Read Data (FITS paths or directly passed arrays)
    for k in range(nf):
        if isinstance(files[k], str):
            # Transpose to convert FITS (NY, NX) to IDL-style (NX, NY)
            raw_tmp = fits.getdata(files[k]).astype(np.float32).T
        else:
            raw_tmp = np.array(files[k], dtype=np.float32)

        tmp = raw_tmp / ndata_integ - dark

        if k == 0:
            s = tmp.shape  # (nx, ny)
            if xr is None:
                xr = [0, s[0] - 1]
            if yr is None:
                yr = [0, s[1] - 1]

            nx = xr[1] - xr[0] + 1
            ny = yr[1] - yr[0] + 1
            logimages = np.zeros((nx, ny, nf), dtype=np.float32)

        # Slice sub-image bounding box
        sub_image = tmp[xr[0] : xr[1] + 1, yr[0] : yr[1] + 1]

        # Enforce minimum intensity floor
        m1 = np.median(sub_image) * minfrac
        clipped_image = np.maximum(sub_image, m1)

        # Take natural log
        logimages[:, :, k] = np.log(clipped_image)

    # 2. Execute Gain Calibration
    flat, object_param, c, solved_x, solved_y = gaincalib(
        logimages=logimages,
        x=l,
        y=m,
        object_param=object_param,
        maxiter=maxiter,
        silent=silent,
        c=c,
        shift_flag=shift_flag,
        mask=mask,
    )

    # 3. Post-Processing & Exponential Restoration
    flat1 = np.ones(s, dtype=np.float32)
    flat1[xr[0] : xr[1] + 1, yr[0] : yr[1] + 1] = np.exp(flat)

    object1 = np.full(s, np.exp(np.median(object_param)), dtype=np.float32)
    object1[xr[0] : xr[1] + 1, yr[0] : yr[1] + 1] = np.exp(object_param)
    object_param = object1

    c = np.exp(c)

    return flat1, object_param, c, solved_x, solved_y


# function for estimating offsets if we dont have them - really speeds up the kll algo
from scipy.ndimage import center_of_mass, gaussian_filter


def estimate_offsets(observations, reference_idx=0):
    """
    Estimates large dither offsets (dy, dx) for solar/coronagraph beam flats.

    Parameters
    ----------
    observations : list of np.ndarray
        The generated observation frames.
    reference_idx : int
        The index of the frame to serve as (0, 0) baseline.

    Returns
    -------
    relative_offsets : np.ndarray
        Array of shape (N, 2) with estimated (dy, dx) offsets relative to reference_idx.
    """
    centroids = []

    for obs in observations:
        # 1. Heavily smooth to remove true_flat spatial noise structure
        smoothed = gaussian_filter(obs, sigma=20)

        # 2. Threshold top brightness (e.g., top 30% intensity range)
        # This isolates the beam center and prevents edge-truncation bias at image borders
        v_min, v_max = smoothed.min(), smoothed.max()
        threshold = v_min + 0.70 * (v_max - v_min)

        masked_beam = np.where(smoothed >= threshold, smoothed, 0.0)

        # 3. Compute center of mass (returns [y, x])
        cy, cx = center_of_mass(masked_beam)
        centroids.append([cy, cx])

    centroids = np.array(centroids)

    # Calculate offset relative to reference frame
    # Note: If frame_i center is further down/right than ref, frame_i position shift is +
    relative_offsets = centroids - centroids[reference_idx]

    return relative_offsets


# then need a function to get offsets and return the flat field (i.e. call both pieces)
def kll_routine(observations, dark):
    """
    Function to:
    (1) estimate the offset from center of the frame for KLL flats
    (2) run the KLL algorithm to deduce the flat

    input: observations (list of the KLL flats) and dark (master dark matching)
    """
    estimated_offsets = estimate_offsets(observations)
    known_y = np.array([dy for dy, dx in estimated_offsets], dtype=np.float32)
    known_x = np.array([dx for dy, dx in estimated_offsets], dtype=np.float32)

    derived_flat, derived_sun, c, solved_x, solved_y = get_flat(
        files=observations,
        dark=dark,
        l=known_y,  # derived Y shifts
        m=known_x,  # derived X shifts
        shift_flag=2,
        maxiter=20,
        silent=True,
    )

    return derived_flat, derived_sun
