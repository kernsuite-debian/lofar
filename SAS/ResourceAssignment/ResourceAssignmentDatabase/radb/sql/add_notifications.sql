--this file was generated by create_add_notifications.sql.py
--it creates triggers and functions which fire postgres notify events upon the given table actions
--these notify events can be listened to implenting a subclass of the PostgresListener in the lofar.common.postgres python module
--for the radb such a subclass has been made, which listens specifically to the notifications defined below
--RADBPGListener in module lofar.sas.resourceassignment.database.radbpglistener
--this RADBPGListener then broadcasts the event on the lofar bus.


BEGIN;

-- only issue >warnings log messages. (only during this transaction)
SET LOCAL client_min_messages=warning;


CREATE OR REPLACE FUNCTION resource_allocation.NOTIFY_task_INSERT()
RETURNS TRIGGER AS $$
DECLARE payload text;
BEGIN
SELECT CAST(NEW.id AS text) INTO payload;
PERFORM pg_notify(CAST('task_insert' AS text), payload);
RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER T_NOTIFY_task_INSERT
AFTER INSERT ON resource_allocation.task
FOR EACH ROW
EXECUTE PROCEDURE resource_allocation.NOTIFY_task_INSERT();


CREATE OR REPLACE FUNCTION resource_allocation.NOTIFY_task_UPDATE()
RETURNS TRIGGER AS $$
DECLARE payload text;
BEGIN
IF ROW(NEW.*) IS DISTINCT FROM ROW(OLD.*) THEN
SELECT CAST(NEW.id AS text) INTO payload;
PERFORM pg_notify(CAST('task_update' AS text), payload);
END IF;
RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER T_NOTIFY_task_UPDATE
AFTER UPDATE ON resource_allocation.task
FOR EACH ROW
EXECUTE PROCEDURE resource_allocation.NOTIFY_task_UPDATE();


CREATE OR REPLACE FUNCTION resource_allocation.NOTIFY_task_DELETE()
RETURNS TRIGGER AS $$
DECLARE payload text;
BEGIN
SELECT CAST(OLD.id AS text) INTO payload;
PERFORM pg_notify(CAST('task_delete' AS text), payload);
RETURN OLD;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER T_NOTIFY_task_DELETE
AFTER DELETE ON resource_allocation.task
FOR EACH ROW
EXECUTE PROCEDURE resource_allocation.NOTIFY_task_DELETE();


CREATE OR REPLACE FUNCTION resource_allocation.NOTIFY_task_predecessor_INSERT_column_task_id()
RETURNS TRIGGER AS $$
DECLARE payload text;
BEGIN
SELECT CAST(NEW.task_id AS text) INTO payload;
PERFORM pg_notify(CAST('task_predecessor_insert_column_task_id' AS text), payload);
RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER T_NOTIFY_task_predecessor_INSERT_column_task_id
AFTER INSERT ON resource_allocation.task_predecessor
FOR EACH ROW
EXECUTE PROCEDURE resource_allocation.NOTIFY_task_predecessor_INSERT_column_task_id();


CREATE OR REPLACE FUNCTION resource_allocation.NOTIFY_task_predecessor_UPDATE_column_task_id()
RETURNS TRIGGER AS $$
DECLARE payload text;
BEGIN
IF ROW(NEW.*) IS DISTINCT FROM ROW(OLD.*) THEN
SELECT CAST(NEW.task_id AS text) INTO payload;
PERFORM pg_notify(CAST('task_predecessor_update_column_task_id' AS text), payload);
END IF;
RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER T_NOTIFY_task_predecessor_UPDATE_column_task_id
AFTER UPDATE ON resource_allocation.task_predecessor
FOR EACH ROW
EXECUTE PROCEDURE resource_allocation.NOTIFY_task_predecessor_UPDATE_column_task_id();


CREATE OR REPLACE FUNCTION resource_allocation.NOTIFY_task_predecessor_DELETE_column_task_id()
RETURNS TRIGGER AS $$
DECLARE payload text;
BEGIN
SELECT CAST(OLD.task_id AS text) INTO payload;
PERFORM pg_notify(CAST('task_predecessor_delete_column_task_id' AS text), payload);
RETURN OLD;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER T_NOTIFY_task_predecessor_DELETE_column_task_id
AFTER DELETE ON resource_allocation.task_predecessor
FOR EACH ROW
EXECUTE PROCEDURE resource_allocation.NOTIFY_task_predecessor_DELETE_column_task_id();


CREATE OR REPLACE FUNCTION resource_allocation.NOTIFY_task_predecessor_INSERT_column_predecessor_id()
RETURNS TRIGGER AS $$
DECLARE payload text;
BEGIN
SELECT CAST(NEW.predecessor_id AS text) INTO payload;
PERFORM pg_notify(CAST('task_predecessor_insert_column_predecessor_id' AS text), payload);
RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER T_NOTIFY_task_predecessor_INSERT_column_predecessor_id
AFTER INSERT ON resource_allocation.task_predecessor
FOR EACH ROW
EXECUTE PROCEDURE resource_allocation.NOTIFY_task_predecessor_INSERT_column_predecessor_id();


CREATE OR REPLACE FUNCTION resource_allocation.NOTIFY_task_predecessor_UPDATE_column_predecessor_id()
RETURNS TRIGGER AS $$
DECLARE payload text;
BEGIN
IF ROW(NEW.*) IS DISTINCT FROM ROW(OLD.*) THEN
SELECT CAST(NEW.predecessor_id AS text) INTO payload;
PERFORM pg_notify(CAST('task_predecessor_update_column_predecessor_id' AS text), payload);
END IF;
RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER T_NOTIFY_task_predecessor_UPDATE_column_predecessor_id
AFTER UPDATE ON resource_allocation.task_predecessor
FOR EACH ROW
EXECUTE PROCEDURE resource_allocation.NOTIFY_task_predecessor_UPDATE_column_predecessor_id();


CREATE OR REPLACE FUNCTION resource_allocation.NOTIFY_task_predecessor_DELETE_column_predecessor_id()
RETURNS TRIGGER AS $$
DECLARE payload text;
BEGIN
SELECT CAST(OLD.predecessor_id AS text) INTO payload;
PERFORM pg_notify(CAST('task_predecessor_delete_column_predecessor_id' AS text), payload);
RETURN OLD;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER T_NOTIFY_task_predecessor_DELETE_column_predecessor_id
AFTER DELETE ON resource_allocation.task_predecessor
FOR EACH ROW
EXECUTE PROCEDURE resource_allocation.NOTIFY_task_predecessor_DELETE_column_predecessor_id();


CREATE OR REPLACE FUNCTION resource_allocation.NOTIFY_specification_UPDATE()
RETURNS TRIGGER AS $$
DECLARE payload text;
BEGIN
IF ROW(NEW.*) IS DISTINCT FROM ROW(OLD.*) THEN
SELECT CAST(NEW.id AS text) INTO payload;
PERFORM pg_notify(CAST('specification_update' AS text), payload);
END IF;
RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER T_NOTIFY_specification_UPDATE
AFTER UPDATE ON resource_allocation.specification
FOR EACH ROW
EXECUTE PROCEDURE resource_allocation.NOTIFY_specification_UPDATE();


CREATE OR REPLACE FUNCTION resource_allocation.NOTIFY_resource_claim_INSERT()
RETURNS TRIGGER AS $$
DECLARE payload text;
BEGIN
SELECT CAST(NEW.id AS text) INTO payload;
PERFORM pg_notify(CAST('resource_claim_insert' AS text), payload);
RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER T_NOTIFY_resource_claim_INSERT
AFTER INSERT ON resource_allocation.resource_claim
FOR EACH ROW
EXECUTE PROCEDURE resource_allocation.NOTIFY_resource_claim_INSERT();


CREATE OR REPLACE FUNCTION resource_allocation.NOTIFY_resource_claim_UPDATE()
RETURNS TRIGGER AS $$
DECLARE payload text;
BEGIN
IF ROW(NEW.*) IS DISTINCT FROM ROW(OLD.*) THEN
SELECT CAST(NEW.id AS text) INTO payload;
PERFORM pg_notify(CAST('resource_claim_update' AS text), payload);
END IF;
RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER T_NOTIFY_resource_claim_UPDATE
AFTER UPDATE ON resource_allocation.resource_claim
FOR EACH ROW
EXECUTE PROCEDURE resource_allocation.NOTIFY_resource_claim_UPDATE();


CREATE OR REPLACE FUNCTION resource_allocation.NOTIFY_resource_claim_DELETE()
RETURNS TRIGGER AS $$
DECLARE payload text;
BEGIN
SELECT CAST(OLD.id AS text) INTO payload;
PERFORM pg_notify(CAST('resource_claim_delete' AS text), payload);
RETURN OLD;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER T_NOTIFY_resource_claim_DELETE
AFTER DELETE ON resource_allocation.resource_claim
FOR EACH ROW
EXECUTE PROCEDURE resource_allocation.NOTIFY_resource_claim_DELETE();


CREATE OR REPLACE FUNCTION resource_monitoring.NOTIFY_resource_availability_UPDATE_column_resource_id()
RETURNS TRIGGER AS $$
DECLARE payload text;
BEGIN
IF ROW(NEW.*) IS DISTINCT FROM ROW(OLD.*) THEN
SELECT CAST(NEW.resource_id AS text) INTO payload;
PERFORM pg_notify(CAST('resource_availability_update_column_resource_id' AS text), payload);
END IF;
RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER T_NOTIFY_resource_availability_UPDATE_column_resource_id
AFTER UPDATE ON resource_monitoring.resource_availability
FOR EACH ROW
EXECUTE PROCEDURE resource_monitoring.NOTIFY_resource_availability_UPDATE_column_resource_id();


CREATE OR REPLACE FUNCTION resource_monitoring.NOTIFY_resource_capacity_UPDATE_column_resource_id()
RETURNS TRIGGER AS $$
DECLARE payload text;
BEGIN
IF ROW(NEW.*) IS DISTINCT FROM ROW(OLD.*) THEN
SELECT CAST(NEW.resource_id AS text) INTO payload;
PERFORM pg_notify(CAST('resource_capacity_update_column_resource_id' AS text), payload);
END IF;
RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER T_NOTIFY_resource_capacity_UPDATE_column_resource_id
AFTER UPDATE ON resource_monitoring.resource_capacity
FOR EACH ROW
EXECUTE PROCEDURE resource_monitoring.NOTIFY_resource_capacity_UPDATE_column_resource_id();


COMMIT;