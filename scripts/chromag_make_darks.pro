; docformat = 'rst'

pro chromag_make_darks
  compile_opt strictarr

  template_filename = '20250813T200527.633Z.fits'

  data = readfits(template_filename, header)

  date_format = '(C(CYI, "-", CMoI2.2, "-", CDI2.2, "T", CHI2.2, ":", CMI2.2, ":", CSF6.3))'
  obs_time = 15.3D / 60.0D / 60.0D / 24.0D   ; seconds

  ; update DATATYPE, OBJECT, WAVELNTH, DATE-OBS, DATE, DATE-END, SCAN_N
  new_times = ['20250813T200312.539', '20250813T200403.372', $   ; before science data
               '20250813T200546.119', '20250813T200548.877', $  ; in the science data
               '20250813T215543.218', '20250813T215545.133']     ; after science data
  for f = 0L, n_elements(new_times) - 1L do begin
    output_filename = new_times[f] + 'Z.fits'

    year = long(strmid(new_times[f], 0, 4))
    month = long(strmid(new_times[f], 4, 2))
    day = long(strmid(new_times[f], 6, 2))
    hour = long(strmid(new_times[f], 9, 2))
    minute = long(strmid(new_times[f], 11, 2))
    second = float(strmid(new_times[f], 13, 6))

    jd = julday(month, day, year, hour, minute, second)

    date_obs = string(jd, format=date_format)
    date_end = string(jd + obs_time, format=date_format)

    sxaddpar, header, 'DATATYPE', 'Calibration'
    sxaddpar, header, 'OBJECT', 'Dark'
    sxaddpar, header, 'WAVELNTH', 0.0
    sxaddpar, header, 'DATE-OBS', date_obs
    sxaddpar, header, 'DATE', date_end
    sxaddpar, header, 'DATE-END', date_end
    sxaddpar, header, 'SCAN_N', 1

    print, output_filename, format='writing %s...'
    writefits, output_filename, data / 4, header
  endfor
end
