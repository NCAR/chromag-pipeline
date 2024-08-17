# -*- coding: utf-8 -*-


class photometric_calibration:
    def __init__(self, catalog):
        self.catalog = catalog

        self.dark_images = None
        self.dark_times = None
        self.dark_exposures = None

        self.flat_images = None
        self.flat_times = None
        self.flat_exposures = None
        self.flat_wavelengths = None

        self.add_catalog(catalog)

    def add_catalog(self, catalog):
        darks = [f for f in catalog if f.is_dark()]
        dark_times = [d.date_obs for d in darks]
        # TODO: extract info into NumPy arrays for quick access

    def get_dark(self, time, exposure):
        """Get closest dark to the given time matching the exposure."""
        pass

    def get_flat(self, time, exposure, wavelength):
        """Get closest flat to the given time matching the exposure and wavelength."""
        pass

    def __str__(self):
        n_darks = 0 if self.dark_times is None else len(self.dark_times)
        n_flats = 0 if self.flat_times is None else len(self.flat_times)
        return f"photometric calibration <{n_darks} darks, {n_flats} flats>"


def make_photometric_calibration(catalog):
    return photometric_calibration(catalog)
