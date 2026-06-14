-- TABLE CREATION
CREATE TABLE USERS(
ID BIGSERIAL PRIMARY KEY,
NAME TEXT NOT NULL,
EMAIL TEXT UNIQUE NOT NULL,
AGE INT,
ACTIVE BOOLEAN DEFAULT TRUE,
CREATED_AT TIMESTAMPTZ DEFAULT NOW()
);

create table posts(
id bigserial primary key,
user_id bigint references users(id) on delete cascade,
title text not null,
body text, 
created_at timestamptz default now()
);

create table comments(
id bigserial primary key,
post_id bigint references posts(id) on delete cascade,
user_id bigint references users(id) on delete cascade,
body text not null,
created_at timestamptz default now()
);

create table tags(
id bigserial primary key,
name text unique not null
);

create table post_tags(
post_id bigint references posts(id) on delete cascade,
tag_id bigint references tags(id) on delete cascade,
primary key(post_id,tag_id)
);

-- TABLE INSERTION

INSERT INTO users (name, email, age) VALUES ('Alice','alice@example.com',30), 
('Bob','bob@example.com', 25), 
('Carol', 'carol@example.com',35), 
('Dave','dave@example.com', 28)
;

INSERT INTO posts (user_id, title,body) VALUES 
(1, 'Hello World','My first post'), 
(1, 'SQL is fun','Learning SQL today'), 
(2, 'Bobs post', 'Written by Bob'),
(3,'Advanced SQL', 'Window functions are great');

INSERT INTO comments(post_id, user_id, body) VALUES 
(1, 2, 'Great post!'), 
(1, 3, 'Thanks for sharing'), 
(2, 4,'Very helpful'), 
(3, 1,'Nice one Bob');

INSERT into tags (name) VALUES ('python'),('sql'),('fastapi'),('beginner');

INSERT into post_tags VALUES (1,2),(1,4),(2,2),(3,1),(4,2),(4,3);

-- SELECT STATEMENTS

select * from users where age>27 order by age desc;

select * from users order by id limit 2 offset 2;

select count(*) from posts;

select avg(age) as avg_age from users;

select user_id, count(id) from posts group by user_id having count(id)>1;

select * from users where users.id not in (select  user_id from posts );

select users.name as name, posts.body as post, posts.title as title from users join posts on users.id=posts.user_id;

select users.name, count(posts.id) from posts join users on posts.user_id=users.id group by users.name;

select posts.title, tags.name from posts join post_tags on posts.id=post_tags.post_id join tags on post_tags.tag_id=tags.id;

select comments.body,users.name from comments join users on comments.user_id=users.id where users.name='Alice';

select * from users where id in (select user_id from comments);

with comment as 
( select distinct user_id from comments) 
select * from users where id in (select user_id from comment);

select id from posts where id = (select post_id from comments group by post_id order by count(*) desc limit 1);

with total_comments as 
(select count(id) as total , post_id from comments group by post_id
)
select post_id, total from total_comments where total>=2;

select user_id,title ,row_number() over (partition by user_id order by created_at) as post_rank from posts;

select  id, age, rank() over (order by age desc) as rank, dense_rank() over (order by age desc) as dense_rank from users;

select title, lag(title) over (order by created_at) as previous_post from posts; 

Insert 50,000 rows into the users table using generate_series. Confirm with SELECT
COUNT(*).

insert into users(name,email,age) 
select 'User_' || gs,
'user' || gs || '@example.com',
18 + (random() * 42) :: int
from generate_series(1,50000) as gs;

select count(*) from users;

Run EXPLAIN ANALYZE on SELECT * FROM users WHERE email = &#39;user999@test.com&#39;.
Note the plan type.

explain analyze select * from users where email = 'user999@test.com' 

create index idx_users_email on users(email);

Write a transaction that inserts a new user and a new post for that user atomically. Roll it back
and confirm neither row was saved.

begin;
insert into users(name,email,age) values ('Rollback User', 'rollback@test.com', 23);
insert into posts(user_id,title) values (currval('user_id_seq'),'Rollback post');
rollback;

SELECT *
FROM users
WHERE email = 'rollback@test.com';


create table events(
id bigserial primary key,
type text,
payload jsonb,
created_at timestamptz default now()
);

insert into events(type,payload) values
('user_signup','{"user_id":1,"plan":"free"}'),
('post_created', '{"post_id": 5, "user_id": 2,"tags":["sql","python"]}'), ('payment', '{"amount": 99.99, "currency": "USD",
"user_id": 1}');

select payload -> 'user_id' as user_id_json from events;

select * from events where payload ->> 'plan' = 'free';