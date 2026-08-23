-- database table listing software versions

create table chromag_sw (
  sw_id            int auto_increment primary key,

  -- release date of version, i.e., first day new version is used
  release_date     datetime not null,

  -- release version and git hash
  version          char(20),   -- ends with "-dev" if not in production
  revision         char(20),   -- ends with "*" if changes since commit

  index(version),
  index(revision),
  unique (revision)
);
