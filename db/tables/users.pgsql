CREATE TABLE public.users (
	id serial4 NOT NULL,
	created_at int4 NOT NULL,
	updated_at int4 NOT NULL,
	"name" text NOT NULL,
	hashed_password text NOT NULL,
	"admin" bool DEFAULT false NOT NULL,
	username text NOT NULL,
	CONSTRAINT users_pkey PRIMARY KEY (id),
	CONSTRAINT users_username_key UNIQUE (username)
);