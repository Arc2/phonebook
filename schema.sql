drop table if exists contacts;
create table contacts (
  id integer primary key autoincrement,
  name text not null,
  telephone text not null,
  address text not null,
  comment text,
  owner integer not null
);
