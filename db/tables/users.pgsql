CREATE TABLE users(
	id SERIAL PRIMARY KEY,
	created_at INT NOT NULL,
	updated_at INT NOT NULL,
    email TEXT NOT NULL,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    hashed_password TEXT NOT NULL
)

ALTER TABLE users ADD admin BOOLEAN DEFAULT false;

-- TODO: make email and phone unique