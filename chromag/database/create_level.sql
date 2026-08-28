-- one per product level, e.g., 0, 1, 2, 3,...

create table chromag_level (
  level_id                              int auto_increment primary key,
  level_name                            char(5) not null,
  description                           varchar(512),

  unique (level_name)
);
