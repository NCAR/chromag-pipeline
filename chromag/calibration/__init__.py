# -*- coding: utf-8 -*-
import numpy as np 
import xarray as xr 
"""Routines for handling photometric/ polarimetric calibration."""


class calibration:
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
        #darks = [f for f in catalog if f.is_dark()]
        #dark_times = [d.date_obs for d in darks]
        self.darks = np.array([f for f in catalog if f.is_dark()])
        self.dark_times = np.array([d.date_obs for d in self.darks])
        self.dark_exps = np.array([d.exposure for d in self.darks])
        self.dark_data = np.array([d.data for d in self.darks])
        # TODO: extract info into NumPy arrays for quick access

    def get_dark(self, time, exposure):
        """Get closest dark to the given time matching the exposure."""
        # first generate list of matching exposures
        matching_exps = np.where(self.dark_exps == exposure)[0]
        matching_exps = np.array([int(i) for i in matching_exps])
        darks_matching_exps = np.array(self.darks)[matching_exps]
        
        # then find closest dark timestamp 
        dark_times_matching_exps = self.dark_times[matching_exps]
        closest_time = np.abs(dark_times_matching_exps - time).argmin()
        closest_dark = darks_matching_exps[closest_time]
        return closest_dark # returns closest file, do we want it to return the closest dataset? can do closest_dark.data
        #pass

    def get_flat(self, time, exposure, wavelength):
        """Get closest flat to the given time matching the exposure and wavelength."""
        pass

    def __str__(self):
        n_darks = 0 if self.dark_times is None else len(self.dark_times)
        n_flats = 0 if self.flat_times is None else len(self.flat_times)
        return f"calibration <{n_darks} darks, {n_flats} flats>"

    def get_master_dark(self, exposure): 
        """Get master dark for the day given an exposure time."""
        # average darks of same exposure across first dimension (4 polarization states)
        matching_exps = np.where(self.dark_exps == exposure)[0]
        matching_exps = np.array([int(i) for i in matching_exps])
        dark_data_matching_exps = np.array(self.dark_data)[matching_exps]
        polavg_darks = []  
        for data in dark_data_matching_exps: 
            polavg_data = np.mean(data, axis=0)
            polavg_darks.append(polavg_data)
    
        # then average all into one master dark 
        master_dark = np.mean(polavg_darks, axis=0)
        return master_dark 
    
    def save_calibration_file(self, exposure): 
        """Save calibration file with master dark, should this be for one exposure time or contain multiple master darks?"""
        # master_dark = self.get_master_dark(exposure)
        # dark_ds = xr.Dataset() 
        # dark_ds['MASTER_DARK'] = xr.DataArray(master_dark, dims=('y','x'), attrs={'units': 'DN'})
        # dark_ds['EXPTIME'] = xr.DataArray(exposure, attrs={'units': 's'})
        # dark_ds['DARK_FILES'] = xr.DataArray(darks_matching_exps)
        # flat_ds = xr.Dataset() 
        # outfile = 'calibration_file.nc' # probably need to have exp in name and the date? cal_file_exp_date.nc
        # dark_ds.to_netcdf(outfile, group='master_dark', mode='w')
        # flat_ds.to_netcdf(outfile, group='flats', mode='a')
        # do we need to include anything else? should be able to pull metadata out of files
        # then to read out specific group: dark_ds = xr.open_dataset(outfile, group='master_dark') 


def make_calibration(catalog):
    return calibration(catalog)
