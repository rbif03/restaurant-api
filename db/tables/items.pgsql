CREATE TABLE items (
	id SERIAL PRIMARY KEY,
	created_at INT NOT NULL,
	updated_at INT NOT NULL,
	category TEXT,
	name TEXT NOT NULL,
	description TEXT,
	price MONEY NOT NULL,
	active BOOLEAN NOT NULL
)