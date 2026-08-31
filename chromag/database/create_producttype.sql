-- one per product level, e.g., 0, 1, 2, 3,...

create table chromag_producttype (
  producttype_id                        int auto_increment primary key,
  producttype_name                      char(32) not null,
  description                           varchar(512),

  unique (producttype_name)
);
