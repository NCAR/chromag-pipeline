-- one per file type, e.g.,

create table chromag_filetype (
  filetype_id                           int auto_increment primary key,
  filetype                              char(10) not null,
  description                           varchar(512),

  unique (filetype)
);
