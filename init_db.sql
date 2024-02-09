CREATE SCHEMA test AUTHORIZATION postgres;


CREATE TABLE test.users (
	id SERIAL PRIMARY KEY,
	username varchar NOT NULL,
	"password" varchar NOT NULL
);

INSERT INTO test.users (username, "password") VALUES ('chris', '$2b$12$h9PX.UbK2xl.rXT6Q17cFO3X.Tt/nQ/FHpqmowLRER2I4X6O3aZBu');
