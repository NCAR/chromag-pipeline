-- one per level 1 ChroMag file

create table chromag_level1 (
  file_id                               int auto_increment primary key,
  dt_created                            timestamp default current_timestamp,
  filename                              varchar(80) not null,
  l0_filename                           varchar(80) not null,
  filesize                              int,   -- bytes

  date_obs                              datetime not null,
  obsday_id                             mediumint(5) not null,

  wave_region                           char(4),
  wavelength                            float,
  exposure                              float,

  scan_i                                int,
  scan_n                                int,

  -- [TODO]: level 1 specific information

  chromag_sw_id                         int,

  index (filename),
  index (date_obs),
  index (obsday_id),
  unique (filename),

  foreign key (obsday_id) references mlso_numfiles(day_id),
  foreign key (chromag_sw_id) references chromag_sw(sw_id)
);
