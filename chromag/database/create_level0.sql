-- one per level 0 ChroMag file

create table chromag_level0 (
  file_id                               int auto_increment primary key,
  dt_created                            timestamp default current_timestamp,
  filename                              varchar(80) not null,
  filesize                              int,   -- bytes

  date_obs                              datetime not null,
  obsday_id                             mediumint(5) not null,

  datatype                              char(12),
  object                                char(12),
  wave_region                           char(4),
  wavelength                            float,
  exposure                              float,

  scan_i                                int,
  scan_n                                int,

  sgsdimv                               float,
  sgsdims                               float,
  sgssumv                               float,
  sgssums                               float,
  sgsrav                                float,
  sgsras                                float,
  sgsdecv                               float,
  sgsdecs                               float,
  sgsscint                              float,
  sgsloop                               float,
  sgsrazr                               float,
  sgsdeczr                              float,

  -- [TODO]: level 0 specific information
  quality_bitmask                       bigint,

  index (filename),
  index (date_obs),
  index (obsday_id),
  unique (filename),

  foreign key (obsday_id) references mlso_numfiles(day_id)
);
