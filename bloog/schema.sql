drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  title text not null,
  'text' text not null,
  'link' text
);

drop table if exists users;
create table users (
  id integer primary key autoincrement,
  name text not null,
  'mail' text not null,
  'password' text not null,
  'admin' integer not null
);