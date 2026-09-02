-- one per observing day that ChroMag observed

create table chromag_process (
  process_id                            int auto_increment primary key,
  obsday_id                             mediumint(5) not null,
  chromag_sw_id                         int not null,
  status                                enum("processed", "processing"),

  index (obsday_id),

  foreign key (obsday_id) references mlso_numfiles(day_id),
  foreign key (chromag_sw_id) references chromag_sw(sw_id)
);
