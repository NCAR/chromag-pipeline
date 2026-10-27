#!/usr/bin/env python

import argparse
import datetime
import glob
import time
import os
import numpy as np
from scipy import ndimage
from astropy.io import fits
from scipy.signal import fftconvolve


def convert_to_raw_adu(
    normalized_obs, peak_adu=30000.0, dark_pedestal=40.0, read_noise_std=3.0
):
    """Scales unitless observation (0 to ~1) into raw 16-bit integer camera ADU."""
    photoelectrons = normalized_obs * peak_adu
    noisy_signal = np.random.poisson(photoelectrons).astype(np.float64)
    read_noise = np.random.normal(
        loc=0.0, scale=read_noise_std, size=normalized_obs.shape
    )
    raw_signal = noisy_signal + dark_pedestal + read_noise
    return np.clip(np.round(raw_signal), 0, 65535).astype(np.uint16)


def generate_quadrant_flats(
    quadrant="all",
    ny=2160,
    nx=2560,
    solar_diameter=1754,
    fwhm=818.0,
    offset_fraction=0.15,
    alpha=1.0,
    variation_level=0.10,
    seed=42,
):
    ny, nx = 2160, 2560
    solar_radius = solar_diameter / 2.0
    sigma = fwhm / (2 * np.sqrt(2 * np.log(2)))

    # Generate True Flat
    np.random.seed(seed)
    fy, fx = np.fft.fftfreq(ny)[:, None], np.fft.fftfreq(nx)[None, :]
    f = np.sqrt(fx**2 + fy**2)
    f[0, 0] = 1.0
    amplitude = 1.0 / (f ** (alpha / 2.0))
    amplitude[0, 0] = 0.0

    random_phase = np.random.uniform(0, 2 * np.pi, size=(ny, nx))
    spectrum = amplitude * np.exp(1j * random_phase)
    noise_spatial = np.real(np.fft.ifft2(spectrum))
    noise_spatial = (noise_spatial - np.mean(noise_spatial)) / np.std(noise_spatial)
    true_flat = 1.0 + variation_level * noise_spatial
    true_flat /= np.mean(true_flat)

    # Diffuser Kernel
    k_size = int(6 * sigma) | 1
    ky, kx = np.ogrid[-k_size // 2 : k_size // 2 + 1, -k_size // 2 : k_size // 2 + 1]
    kernel = np.exp(-(kx**2 + ky**2) / (2 * sigma**2))
    kernel /= kernel.sum()

    # Offsets (dy, dx) in pixels
    shift_y = offset_fraction * ny
    shift_x = offset_fraction * nx

    offsets = np.array(
        [
            (-shift_y, shift_x),  # Top-Right
            (-shift_y, -shift_x),  # Top-Left
            (shift_y, -shift_x),  # Bottom-Left
            (shift_y, shift_x),  # Bottom-Right
            (0, 0),  # centered for non-KLL flat
        ]
    )
    # 1 (Top-Right), 2 (Top-Left), 3 (Bottom-Left), 4 (Bottom-Right), "all" for all 4 quads, or "none" for centered non KLL
    offset_mapping = {
        "Top-Right": [0],
        "Top-Left": [1],
        "Bottom-Left": [2],
        "Bottom-Right": 3,
        "all": [0, 1, 2, 3],
        "none": [4],
    }
    offsets = offsets[offset_mapping[quadrant]]

    Y, X = np.ogrid[:ny, :nx]
    observations = []

    for dy, dx in offsets:

        disk = (
            (Y - (ny / 2 + dy)) ** 2 + (X - (nx / 2 + dx)) ** 2 <= solar_radius**2
        ).astype(np.float64)
        blurred = fftconvolve(disk, kernel, mode="same")
        # Apply floor before multiplying flat to avoid log(0) issues
        obs = np.maximum(blurred, 1e-5) * true_flat
        observations.append(obs)

    return observations, true_flat, offsets


def create_flats(
    start_datetime: datetime.datetime,
    exptime: float,
    numflats: int,
    kll_flag: bool,
    peak_adu: float = 30000.0,
    dark_pedestal: float = 40.0,
):
    """
    saves flats to fits files, mimicking real data
    - datetime will increment by 5 s (?)
    """

    if kll_flag:
        quad = "all"
        print(f"creating {4*numflats} KLL flats")
    else:
        quad = "none"
        print(f"creating {numflats} non-KLL flat(s)")

    # prep a primary header for fits files generated
    path = "/hao/mlso25/Data/ChroMag/raw.synthetic-dfarrell/"
    subdir = start_datetime.strftime("%Y%m%d")
    files = glob.glob(path + subdir + "/" + "*fits")
    with fits.open(files[0]) as f:
        primary_header = f[0].header
    primary_header["DATATYPE"] = "Calibration"
    primary_header["OBJECT"] = "Diffuser"
    primary_header["EXPTIME"] = exptime

    # call function above, looping over number of flats
    idx = 0
    for i in range(numflats):
        observations, true_flat, offsets = generate_quadrant_flats(quad)

        target_indices = range(4) if kll_flag else [0]

        for j in target_indices:

            raw_adu_frame = convert_to_raw_adu(
                observations[j], peak_adu=peak_adu, dark_pedestal=dark_pedestal
            )

            primary_header["OFFSET"] = "False"
            if kll_flag:
                primary_header["OFFSET"] = "True"

            new_dt = (start_datetime + datetime.timedelta(seconds=5 * idx)).strftime(
                "%Y-%m-%dT%H:%M:%S.%f"
            )[:-3]
            new_fn = (start_datetime + datetime.timedelta(seconds=5 * idx)).strftime(
                "%Y%m%dT%H%M%S.%f"
            )[:-3] + "Z"
            primary_header["DATE-OBS"] = new_dt
            primary_hdu = fits.PrimaryHDU(data=raw_adu_frame, header=primary_header)
            hdu1 = fits.ImageHDU(true_flat, name="true flat")
            hdu2 = fits.ImageHDU(offsets[j], name="offset")
            hdul = fits.HDUList([primary_hdu, hdu1, hdu2])

            # filename = datetime in utc including ms
            outdir = path + new_dt[:10].replace("-", "") + "/"
            if not os.path.exists(outdir):
                os.makedirs(outdir)
            filename = new_fn + ".fits"
            hdul.writeto(outdir + filename, overwrite=True)
            print(f"saving {outdir+filename}")
            idx += 1

    return


def main():
    parser = argparse.ArgumentParser(description="Create synthetic ChroMag flats")

    datetime_help = "start datetime for flats in the format 'YYYY-MM-DDTHH:MM:SS'"
    parser.add_argument("datetime", type=str, help=datetime_help)

    exp_help = "exposure time for flats in ms"
    parser.add_argument("exptime", type=float, help=exp_help)

    kll_help = "set to generate KLL (i.e. offset from center) flats, otherwise centered"
    parser.add_argument("--kll", action="store_true", help=kll_help)

    numflats_help = (
        "number of flats (int) to generate, if --kll will generate 4 x numflats"
    )
    parser.add_argument("numflats", type=int, help=numflats_help)

    args = parser.parse_args()

    start_datetime = datetime.datetime.strptime(args.datetime, "%Y-%m-%dT%H:%M:%S")

    create_flats(start_datetime, args.exptime, args.numflats, args.kll)


if __name__ == "__main__":
    main()
