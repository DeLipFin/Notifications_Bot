CREATE TABLE public.telegram_users (
	id serial PRIMARY KEY,
	telegram_id int NOT null,
	first_name varchar NOT null,
	last_name varchar null,
	username varchar null,
	phone int null,
	is_active bool NOT NULL DEFAULT true,
	is_active_birthdays bool NOT NULL DEFAULT true,
	is_active_holidays bool NOT NULL DEFAULT true,
	is_active_notifications bool NOT NULL DEFAULT true,
	create_time timestamp NOT NULL DEFAULT now(),
	update_time timestamp NOT NULL DEFAULT now()
);

CREATE FUNCTION update_timestamp() RETURNS trigger AS $update_timestamp$
    BEGIN
        NEW.update_time := current_timestamp;
        RETURN NEW;
    END;
$update_timestamp$ LANGUAGE plpgsql;

CREATE TRIGGER update_timestamp BEFORE INSERT OR UPDATE ON telegram_users
    FOR EACH ROW EXECUTE PROCEDURE update_timestamp();

CREATE TABLE public.users (
	id serial PRIMARY KEY,
	last_name varchar NOT null,
	first_name varchar NOT null,
	middle_name varchar null,
	birthday date NOT null,
	create_time timestamp NOT NULL DEFAULT now()
);

CREATE TABLE public.types_users (
	id serial PRIMARY KEY,
	name varchar NOT null,
	telegram_user_id int NOT null REFERENCES telegram_users (id) ON DELETE CASCADE,
	create_time timestamp NOT NULL DEFAULT now()
);

CREATE TABLE public.members (
	id serial PRIMARY KEY,
	telegram_user_id int NOT null REFERENCES telegram_users (id) ON DELETE CASCADE, 
	user_id int NOT null REFERENCES users (id) ON DELETE CASCADE,
	type int NOT null REFERENCES types_users (id) ON DELETE CASCADE,
	is_active bool NOT NULL DEFAULT true
);

CREATE TABLE public.holidays (
	id serial PRIMARY KEY,
	name varchar NOT null,
	info varchar null,
	date date NOT null
);

CREATE TABLE public.notifications (
	id serial PRIMARY KEY,
	telegram_user_id int NOT null REFERENCES telegram_users (id) ON DELETE CASCADE,
	name varchar NOT null,
	info varchar null,
	date timestamp NOT null,
	is_active bool NOT NULL DEFAULT true,
	create_time timestamp NOT NULL DEFAULT now()
);