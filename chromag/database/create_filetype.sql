-- one per file type, e.g.,

create table chromag_filetype (
  filetype_id                           int auto_increment primary key,
  filetype_name                         char(10) not null,
  description                           varchar(512),

  unique (filetype_name)
);
