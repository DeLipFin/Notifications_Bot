CREATE TABLE public.telegram_users (
	id serial PRIMARY KEY,
	telegram_id int NOT null,
	first_name varchar NOT null,
	last_name varchar null,
	username varchar null,
	is_active bool NOT NULL DEFAULT true,
	is_holidays bool NOT NULL DEFAULT true,
	is_birthdays bool NOT NULL DEFAULT true,
	is_notifications bool NOT NULL DEFAULT true,
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

-- Представления
CREATE OR REPLACE VIEW public.list_birthdays
AS SELECT tu.id AS tu_id,
    tu.first_name AS tu_first_name,
    tu.last_name AS tu_last_name,
    tu.is_active AS tu_is_active,
    tu.is_birthdays AS tu_is_birthdays,
    m.id AS m_id,
    m.is_active AS m_is_active,
    m.type AS m_type,
    u.last_name AS u_last_name,
    u.first_name AS u_first_name,
    u.middle_name AS u_middle_name,
    u.birthday AS u_birthday
   FROM telegram_users tu
     LEFT JOIN members m ON m.telegram_user_id = tu.id
     LEFT JOIN users u ON u.id = m.user_id
  ORDER BY tu.id, m.is_active, (to_char(u.birthday::timestamp with time zone, 'MM-DD'::text));

CREATE OR REPLACE VIEW public.check_list_birthdays
AS SELECT tu.id AS tu_id,
    tu.is_active AS tu_is_active,
    tu.is_birthdays AS tu_is_birthdays,
    m.id AS m_id,
    m.is_active AS m_is_active
   FROM telegram_users tu
     LEFT JOIN members m ON m.telegram_user_id = tu.id
  WHERE tu.is_active AND tu.is_birthdays AND m.id IS NOT NULL AND m.is_active; 
 
CREATE OR REPLACE VIEW public.list_notifications
AS SELECT tu.id AS tu_id,
    tu.first_name AS tu_first_name,
    tu.last_name AS tu_last_name,
    tu.is_active AS tu_is_active,
    tu.is_notifications AS tu_is_notifications,
    n.id AS n_id,
    n.name AS n_name,
    n.info AS n_info,
    n.date AS n_date,
    n.is_active AS n_is_active
   FROM telegram_users tu
     LEFT JOIN notifications n ON n.telegram_user_id = tu.id
  ORDER BY tu.id, n.is_active, n.date;

CREATE OR REPLACE VIEW public.check_list_notifications
AS SELECT tu.id AS tu_id,
    tu.is_active AS tu_is_active,
    tu.is_notifications AS tu_is_notifications,
    n.id AS n_id,
    n.is_active AS n_is_active
   FROM telegram_users tu
     LEFT JOIN notifications n ON n.telegram_user_id = tu.id
  WHERE tu.is_active AND tu.is_notifications AND n.id IS NOT NULL AND n.is_active;
 
 

select * from telegram_users;
select * from users;
select * from types_users;
select * from members;
select * from holidays;
select * from notifications;
select * from list_birthdays;
select * from check_list_birthdays;
select * from list_notifications;
select * from check_list_notifications;