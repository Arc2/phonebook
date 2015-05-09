drop table if exists contacts;
create table contacts (
  id integer primary key autoincrement,
  name text not null,
  telephone text not null,
  address text not null,
  comment text,
  owner integer not null
);

DROP TABLE IF EXISTS accounts;
CREATE TABLE accounts (
  uid      INTEGER PRIMARY KEY AUTOINCREMENT,
  email    TEXT NOT NULL,
  password TEXT NOT NULL
);
