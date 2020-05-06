--add triggers and trigger functions to radb (note, there are also the notification triggers in the add_notifications.sql file)

BEGIN;

-- only issue >warnings log messages. (only during this transaction)
SET LOCAL client_min_messages=warning;

CREATE OR REPLACE FUNCTION resource_allocation.on_task_updated()
  RETURNS trigger AS
$BODY$
DECLARE
    claim_tentative_status_id int := 0; --beware: hard coded instead of lookup for performance
    claim_claimed_status_id int := 1; --beware: hard coded instead of lookup for performance
    claim_conflict_status_id int := 2; --beware: hard coded instead of lookup for performance
    task_approved_status_id int := 300; --beware: hard coded instead of lookup for performance
    task_conflict_status_id int := 335; --beware: hard coded instead of lookup for performance
    task_prescheduled_status_id int := 350; --beware: hard coded instead of lookup for performance
    task_scheduled_status_id int := 400; --beware: hard coded instead of lookup for performance
    task_finished_status_id int := 1000; --beware: hard coded instead of lookup for performance
    task_aborted_status_id int  := 1100; --beware: hard coded instead of lookup for performance
BEGIN
  IF NEW.status_id <> OLD.status_id THEN
    IF OLD.status_id = task_conflict_status_id AND NEW.status_id <> task_conflict_status_id THEN
      -- bookkeeping, cleanup task_status_before_conlict table for this task
      DELETE FROM resource_allocation.task_status_before_conlict WHERE task_id = NEW.id;
    END IF;

    IF NEW.status_id = task_scheduled_status_id AND OLD.status_id <> task_prescheduled_status_id THEN
        -- tasks can only be scheduled from the prescheduled state
        RAISE EXCEPTION 'Cannot update task status from % to %', OLD.status_id, NEW.status_id;
    END IF;

    IF OLD.status_id = task_conflict_status_id AND
       NEW.status_id <> task_approved_status_id AND
       EXISTS (SELECT id FROM resource_allocation.resource_claim rc WHERE rc.task_id = NEW.id AND rc.status_id = claim_conflict_status_id) THEN
        RAISE EXCEPTION 'When a task has the conflict status and if has claims in conflict, it has to be set to approved status first by making sure all its claims have no conflict status anymore.';
    END IF;

    IF NEW.status_id = task_approved_status_id OR NEW.status_id = task_conflict_status_id THEN
        UPDATE resource_allocation.resource_claim
        SET status_id=claim_tentative_status_id
        WHERE (task_id=NEW.id AND status_id = claim_claimed_status_id);
    ELSIF NEW.status_id = task_scheduled_status_id THEN
        --prevent task status to be scheduled when not all its claims are claimed
        IF EXISTS (SELECT id FROM resource_allocation.resource_claim WHERE task_id = NEW.id AND status_id <> claim_claimed_status_id) THEN
            RAISE EXCEPTION 'Cannot update task status from % to % when not all its claims are claimed', OLD.status_id, NEW.status_id;
        END IF;
    END IF;

    IF NEW.status_id = task_finished_status_id OR NEW.status_id = task_aborted_status_id THEN
        -- if task ends, remove obsolete claims (keep long lasting claims)
        DELETE FROM resource_allocation.resource_claim rc
        WHERE rc.task_id=NEW.id
        AND rc.endtime <= (SELECT sp.endtime FROM resource_allocation.specification sp WHERE sp.id=NEW.specification_id LIMIT 1);
    END IF;
  END IF;
RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION resource_allocation.on_task_updated()
  OWNER TO resourceassignment;
COMMENT ON FUNCTION resource_allocation.on_task_updated()
  IS 'function which is called by task table update trigger.';

DROP TRIGGER IF EXISTS T_on_task_updated ON resource_allocation.task CASCADE;
CREATE TRIGGER T_on_task_updated
  AFTER UPDATE
  ON resource_allocation.task
  FOR EACH ROW
  EXECUTE PROCEDURE resource_allocation.on_task_updated();

---------------------------------------------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION resource_allocation.on_before_task_status_updated()
  RETURNS trigger AS
$BODY$
DECLARE
    task_approved_status_id int := 300; --beware: hard coded instead of lookup for performance
    task_conflict_status_id int := 335; --beware: hard coded instead of lookup for performance
    task_prescheduled_status_id int := 350; --beware: hard coded instead of lookup for performance
BEGIN
  IF NEW.status_id = task_conflict_status_id AND
     (OLD.status_id = task_approved_status_id OR OLD.status_id = task_prescheduled_status_id) THEN
      -- bookkeeping, log previous status_ud in task_status_before_conlict table for this task
    INSERT INTO resource_allocation.task_status_before_conlict (task_id, status_id) VALUES (OLD.id, OLD.status_id);
  END IF;
RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION resource_allocation.on_before_task_status_updated()
  OWNER TO resourceassignment;
COMMENT ON FUNCTION resource_allocation.on_before_task_status_updated()
  IS 'function which is called by T_on_before_task_status_updated trigger.';

DROP TRIGGER IF EXISTS T_on_before_task_status_updated ON resource_allocation.task CASCADE;
CREATE TRIGGER T_on_before_task_status_updated
  BEFORE UPDATE OF status_id
  ON resource_allocation.task
  FOR EACH ROW
  EXECUTE PROCEDURE resource_allocation.on_before_task_status_updated();

---------------------------------------------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION resource_allocation.delete_conflict_reasons_after_resource_claim_update()
  RETURNS trigger AS
$BODY$
BEGIN
  IF OLD.status_id = 2 AND NEW.status_id <> 2 THEN   --new status is not conflict
    DELETE FROM resource_allocation.resource_claim_conflict_reason rccr WHERE rccr.resource_claim_id = NEW.id;
  END IF;
RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION resource_allocation.delete_conflict_reasons_after_resource_claim_update()
  OWNER TO resourceassignment;
COMMENT ON FUNCTION resource_allocation.delete_conflict_reasons_after_resource_claim_update()
  IS 'function which is called by resource_claim table update trigger, which deletes resource_claim_conflict_reasons when the claim status is updated to !conflict.';

DROP TRIGGER IF EXISTS T_delete_conflict_reasons_after_resource_claim_update ON resource_allocation.resource_claim CASCADE;
CREATE TRIGGER T_delete_conflict_reasons_after_resource_claim_update
  AFTER UPDATE
  ON resource_allocation.resource_claim
  FOR EACH ROW
  EXECUTE PROCEDURE resource_allocation.delete_conflict_reasons_after_resource_claim_update();

---------------------------------------------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION resource_allocation.before_insert_conflict_reason_do_resource_claim_status_check()
  RETURNS trigger AS
$BODY$
BEGIN
  -- check if referred resource_claim is in conflict status, else raise
  IF (SELECT COUNT(id) FROM resource_allocation.resource_claim rc WHERE rc.id = NEW.resource_claim_id AND rc.status_id = 2) = 0 THEN
    RAISE EXCEPTION 'resource_claim has no conflict status';
  END IF;
RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION resource_allocation.before_insert_conflict_reason_do_resource_claim_status_check()
  OWNER TO resourceassignment;
COMMENT ON FUNCTION resource_allocation.before_insert_conflict_reason_do_resource_claim_status_check()
  IS 'check if referred resource_claim is in conflict status, else raise';

DROP TRIGGER IF EXISTS T_before_insert_conflict_reason_do_resource_claim_status_check ON resource_allocation.resource_claim_conflict_reason CASCADE;
CREATE TRIGGER T_before_insert_conflict_reason_do_resource_claim_status_check
  BEFORE INSERT
  ON resource_allocation.resource_claim_conflict_reason
  FOR EACH ROW
  EXECUTE PROCEDURE resource_allocation.before_insert_conflict_reason_do_resource_claim_status_check();

---------------------------------------------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION resource_allocation.delete_conflict_reasons_after_task_update()
  RETURNS trigger AS
$BODY$
BEGIN
  IF OLD.status_id = 335 AND NEW.status_id <> 335 THEN   --new status is not conflict
    DELETE FROM resource_allocation.task_conflict_reason tcr WHERE tcr.task_id = NEW.id;
  END IF;
RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION resource_allocation.delete_conflict_reasons_after_task_update()
  OWNER TO resourceassignment;
COMMENT ON FUNCTION resource_allocation.delete_conflict_reasons_after_task_update()
  IS 'function which is called by task table update trigger, which deletes task_conflict_reasons when the task status is updated to !conflict.';

DROP TRIGGER IF EXISTS T_delete_conflict_reasons_after_task_update ON resource_allocation.task CASCADE;
CREATE TRIGGER T_delete_conflict_reasons_after_task_update
  AFTER UPDATE
  ON resource_allocation.task
  FOR EACH ROW
  EXECUTE PROCEDURE resource_allocation.delete_conflict_reasons_after_task_update();

---------------------------------------------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION resource_allocation.before_insert_conflict_reason_do_task_status_check()
  RETURNS trigger AS
$BODY$
BEGIN
  -- check if referred task is in conflict status, else raise
  IF (SELECT COUNT(id) FROM resource_allocation.task task WHERE task.id = NEW.task_id AND task.status_id = 335) = 0 THEN
    RAISE EXCEPTION 'task has no conflict status';
  END IF;
RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION resource_allocation.before_insert_conflict_reason_do_task_status_check()
  OWNER TO resourceassignment;
COMMENT ON FUNCTION resource_allocation.before_insert_conflict_reason_do_task_status_check()
  IS 'check if referred task is in conflict status, else raise';

DROP TRIGGER IF EXISTS T_before_insert_conflict_reason_do_task_status_check ON resource_allocation.task_conflict_reason CASCADE;
CREATE TRIGGER T_before_insert_conflict_reason_do_task_status_check
  BEFORE INSERT
  ON resource_allocation.task_conflict_reason
  FOR EACH ROW
  EXECUTE PROCEDURE resource_allocation.before_insert_conflict_reason_do_task_status_check();

---------------------------------------------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION resource_allocation.on_insertupdate_check_specification_startendtimes()
  RETURNS trigger AS
$BODY$
DECLARE
    task RECORD;
    pred_task RECORD;
    suc_task RECORD;
    predecessor_task_id int;
    successor_task_id int;
    moved_seconds double precision;
    duration double precision;
    max_pred_endtime timestamp := '1900-01-01 00:00:00';
    tmp_time timestamp;
    min_starttime timestamp;
    min_inter_task_delay int;
BEGIN
    IF NEW.starttime > NEW.endtime THEN
        RAISE EXCEPTION 'task specification starttime > endtime: %', NEW;
    END IF;

    --store task duration
    SELECT EXTRACT(epoch FROM age(NEW.endtime, NEW.starttime)) INTO duration;

    --deterimine max_pred_endtime
    FOR task IN SELECT * FROM resource_allocation.task_view tv WHERE tv.specification_id = NEW.id LOOP
        IF task.predecessor_ids IS NOT NULL THEN
            FOREACH predecessor_task_id IN ARRAY task.predecessor_ids LOOP
                FOR pred_task IN SELECT * FROM resource_allocation.task_view tv WHERE tv.id = predecessor_task_id LOOP
                    IF pred_task.endtime > max_pred_endtime THEN
                        max_pred_endtime := pred_task.endtime;
                    END IF;
                END LOOP;
            END LOOP;
        END IF;
    END LOOP;

    --check if spec is before max_pred_endtime, correct if needed.
    IF max_pred_endtime > '1900-01-01 00:00:00' THEN
        SELECT c.value::integer INTO min_inter_task_delay FROM resource_allocation.config c WHERE c.name = 'min_inter_task_delay';
        IF min_inter_task_delay IS NULL THEN
            min_inter_task_delay := 0;
        END IF;
        min_starttime := max_pred_endtime + min_inter_task_delay * interval '1 second';
        IF min_starttime > NEW.starttime THEN
            NEW.starttime := min_starttime;
            NEW.endtime := min_starttime + duration * interval '1 second';
        END IF;
    END IF;

    --move successor tasks by same amount if needed
    IF TG_OP = 'UPDATE' THEN
        IF NEW.endtime <> OLD.endtime THEN
            SELECT EXTRACT(epoch FROM age(NEW.endtime, OLD.endtime)) INTO moved_seconds;
            FOR task IN SELECT * FROM resource_allocation.task_view tv WHERE tv.specification_id = NEW.id LOOP
                IF task.successor_ids IS NOT NULL THEN
                    FOREACH successor_task_id IN ARRAY task.successor_ids LOOP
                        FOR suc_task IN SELECT * FROM resource_allocation.task_view tv WHERE tv.id = successor_task_id LOOP
                            UPDATE resource_allocation.specification SET (starttime, endtime) = (starttime + moved_seconds * interval '1 second', endtime + moved_seconds * interval '1 second') WHERE id = suc_task.specification_id;
                        END LOOP;
                    END LOOP;
                END IF;
            END LOOP;
        END IF;
    END IF;

RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION resource_allocation.on_insertupdate_check_specification_startendtimes()
  OWNER TO resourceassignment;

DROP TRIGGER IF EXISTS T_specification_insertupdate_check_startendtimes ON resource_allocation.specification;
CREATE TRIGGER T_specification_insertupdate_check_startendtimes
  BEFORE INSERT OR UPDATE
  ON resource_allocation.specification
  FOR EACH ROW
  EXECUTE PROCEDURE resource_allocation.on_insertupdate_check_specification_startendtimes();

---------------------------------------------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION resource_allocation.process_new_claim_into_resource_usages(new_claim resource_allocation.resource_claim)
  RETURNS void AS
$$
DECLARE
BEGIN
    -- insert the claim's start and end delta
    INSERT INTO resource_allocation.resource_usage_delta (claim_id, resource_id, status_id, moment, delta)
    VALUES (new_claim.id, new_claim.resource_id, new_claim.status_id, new_claim.starttime, new_claim.claim_size),
           (new_claim.id, new_claim.resource_id, new_claim.status_id, new_claim.endtime,  -new_claim.claim_size);

    -- with the two new delta entries, use the deltas table to rebuild the usages table from the claim's starttime onwards
    PERFORM resource_allocation.rebuild_resource_usages_from_deltas_for_resource_of_status(new_claim.resource_id, new_claim.status_id, new_claim.starttime);
END;
$$ LANGUAGE plpgsql;
ALTER FUNCTION resource_allocation.process_new_claim_into_resource_usages(new_claim resource_allocation.resource_claim) OWNER TO resourceassignment;
COMMENT ON FUNCTION resource_allocation.process_new_claim_into_resource_usages(new_claim resource_allocation.resource_claim)
  IS 'helper function which is called by resource_claim table insert and update triggers, which fills/updates the resource_allocation.resource_usage table with timeseries of accumulated resource_claim.sizes';

---------------------------------------------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION resource_allocation.rebuild_resource_usages_from_claims()
  RETURNS void AS
$$
DECLARE
    resource virtual_instrument.resource;
BEGIN
    FOR resource IN (SELECT * FROM virtual_instrument.resource ORDER BY id) LOOP
        PERFORM resource_allocation.rebuild_resource_usages_from_claims_for_resource(resource.id);
    END LOOP;
END;
$$ LANGUAGE plpgsql;
ALTER FUNCTION resource_allocation.rebuild_resource_usages_from_claims() OWNER TO resourceassignment;
COMMENT ON FUNCTION resource_allocation.rebuild_resource_usages_from_claims()
  IS 'function which truncates the resource_usages table, and repopulates it by calling process_new_claim_into_resource_usages for each known claim.';

---------------------------------------------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION resource_allocation.rebuild_resource_usages_from_claims_for_resource(_resource_id int)
  RETURNS void AS
$$
DECLARE
    status resource_allocation.resource_claim_status;
BEGIN
    FOR status IN (SELECT * FROM resource_allocation.resource_claim_status ORDER BY id) LOOP
        PERFORM resource_allocation.rebuild_resource_usages_from_claims_for_resource_of_status(_resource_id, status.id);
    END LOOP;
END;
$$ LANGUAGE plpgsql;
ALTER FUNCTION resource_allocation.rebuild_resource_usages_from_claims_for_resource(_resource_id int) OWNER TO resourceassignment;
COMMENT ON FUNCTION resource_allocation.rebuild_resource_usages_from_claims_for_resource(_resource_id int)
  IS 'function which rebuilds the resource_usages table for a specific resource.';

---------------------------------------------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION resource_allocation.rebuild_resource_usages_from_claims_for_resource_of_status(_resource_id int, _status_id int)
  RETURNS void AS
$$
BEGIN
    -- delete all the relevant deltas (so we can re-enter them in this method)
    DELETE FROM resource_allocation.resource_usage_delta WHERE resource_id = _resource_id AND status_id = _status_id;

    -- build up the delta's table by inserting positive claim_size delta's at all claim starttimes...
    INSERT INTO resource_allocation.resource_usage_delta (claim_id, resource_id, status_id, moment, delta)
    (SELECT rc.id, _resource_id, _status_id, rc.starttime, rc.claim_size
            FROM resource_allocation.resource_claim rc
            WHERE rc.resource_id = _resource_id
            AND rc.status_id = _status_id);

    -- ...and by inserting negative claim_size delta's at all claim endtimes
    INSERT INTO resource_allocation.resource_usage_delta (claim_id, resource_id, status_id, moment, delta)
    (SELECT rc.id, _resource_id, _status_id, rc.endtime, -rc.claim_size
            FROM resource_allocation.resource_claim rc
            WHERE rc.resource_id = _resource_id
            AND rc.status_id = _status_id);

    -- now that the deltas table has been rebuild, use it to rebuild the usages table
    PERFORM resource_allocation.rebuild_resource_usages_from_deltas_for_resource_of_status(_resource_id, _status_id);
END;
$$ LANGUAGE plpgsql;
ALTER FUNCTION resource_allocation.rebuild_resource_usages_from_claims_for_resource_of_status(int, int) OWNER TO resourceassignment;
COMMENT ON FUNCTION resource_allocation.rebuild_resource_usages_from_claims_for_resource_of_status(int, int)
  IS 'function which rebuilds the resource_usages table for the claims with a specific status for a specific resource.';


CREATE OR REPLACE FUNCTION resource_allocation.rebuild_resource_usages_from_deltas_for_resource_of_status(_resource_id int, _status_id int, _since timestamp default NULL)
  RETURNS void AS
$$
DECLARE
    combined_delta_row record;
    running_usage_sum bigint;
    usage_before_since resource_allocation.resource_usage;
BEGIN
    -- here are two versions of the same algorithm
    -- if _since is NULL, then run over the entire timespan
    -- else, do time-bound queries which are slightly slower.
    IF _since IS NULL THEN
        -- delete the relevant usages
        DELETE FROM resource_allocation.resource_usage
        WHERE resource_id = _resource_id
        AND status_id = _status_id;

        running_usage_sum := 0;

        -- perform integration over delta's and insert into resource_usage
        FOR combined_delta_row in (SELECT rud.moment, SUM(rud.delta) as summed_delta
                                   FROM resource_allocation.resource_usage_delta rud
                                   WHERE rud.resource_id = _resource_id
                                   AND rud.status_id = _status_id
                                   GROUP BY rud.moment
                                   ORDER BY rud.moment) LOOP
            --integrate
            running_usage_sum := running_usage_sum + combined_delta_row.summed_delta;

            --and insert into resource_usage
            INSERT INTO resource_allocation.resource_usage (resource_id, status_id, as_of_timestamp, usage)
            VALUES (_resource_id, _status_id, combined_delta_row.moment, running_usage_sum);
        END LOOP;
    ELSE
        -- same alghorithm as above, but now timerange-bound as of _since
        -- delete the relevant usages
        DELETE FROM resource_allocation.resource_usage
        WHERE resource_id = _resource_id
        AND status_id = _status_id
        AND as_of_timestamp >= _since;

        -- get the usage_before_since to initialize running_usage_sum with
        SELECT * FROM resource_allocation.get_resource_usage_at_or_before(_resource_id, _status_id, _since, false, true, false)
        INTO usage_before_since;

        IF usage_before_since is NULL THEN
            running_usage_sum := 0;
        ELSE
            running_usage_sum := usage_before_since.usage;
        END IF;

        -- perform integration over delta's since _since and insert into resource_usage
        FOR combined_delta_row in (SELECT rud.moment, SUM(rud.delta) as summed_delta
                                   FROM resource_allocation.resource_usage_delta rud
                                   WHERE rud.resource_id = _resource_id
                                   AND rud.status_id = _status_id
                                   AND rud.moment >= _since
                                   GROUP BY rud.moment
                                   ORDER BY rud.moment) LOOP
            --integrate
            running_usage_sum := running_usage_sum + combined_delta_row.summed_delta;

            --and insert into resource_usage
            INSERT INTO resource_allocation.resource_usage (resource_id, status_id, as_of_timestamp, usage)
            VALUES (_resource_id, _status_id, combined_delta_row.moment, running_usage_sum);
        END LOOP;
    END IF;
END;
$$ LANGUAGE plpgsql;
ALTER FUNCTION resource_allocation.rebuild_resource_usages_from_deltas_for_resource_of_status(int, int, timestamp) OWNER TO resourceassignment;
COMMENT ON FUNCTION resource_allocation.rebuild_resource_usages_from_deltas_for_resource_of_status(int, int, timestamp)
  IS 'function which rebuilds the resource_usages table from the resource_usage_deltas table with a specific status for a specific resource since a given timestamp.';

---------------------------------------------------------------------------------------------------------------------


---------------------------------------------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION resource_allocation.process_old_claim_outof_resource_usages(old_claim resource_allocation.resource_claim)
  RETURNS void AS
$$
DECLARE
BEGIN
    -- get rid of claim in delta's table (this should delete two entries, one for the starttime, and one for the endtime)
    DELETE FROM resource_allocation.resource_usage_delta WHERE claim_id = old_claim.id;

    -- with the two removed delta entries, use the deltas table to rebuild the usages table from the claim's starttime onwards
    PERFORM resource_allocation.rebuild_resource_usages_from_deltas_for_resource_of_status(old_claim.resource_id, old_claim.status_id, old_claim.starttime);
END;
$$ LANGUAGE plpgsql;
ALTER FUNCTION resource_allocation.process_old_claim_outof_resource_usages(old_claim resource_allocation.resource_claim) OWNER TO resourceassignment;
COMMENT ON FUNCTION resource_allocation.process_old_claim_outof_resource_usages(old_claim resource_allocation.resource_claim)
  IS 'helper function which is called by resource_claim table update and delete triggers, which updates/clears the resource_allocation.resource_usage table with timeseries of accumulated resource_claim.sizes';

---------------------------------------------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION resource_allocation.get_resource_usage_at_or_before(_resource_id int, _claim_status_id int, _timestamp timestamp, exactly_at boolean default false, only_before boolean default false, rebuild_usage_when_not_found boolean default false)
  RETURNS resource_allocation.resource_usage AS
$$
DECLARE
    result resource_allocation.resource_usage;
BEGIN
    SELECT * FROM resource_allocation.resource_usage ru
    WHERE ru.resource_id = _resource_id
    AND ru.status_id = _claim_status_id
    AND ru.as_of_timestamp <= _timestamp
    ORDER BY ru.as_of_timestamp DESC
    LIMIT 1 INTO result;

    -- check if as_of_timestamp is exactly_at _timestamp
    IF exactly_at AND result IS NOT NULL THEN
        IF result.as_of_timestamp <> _timestamp THEN
            result := NULL;
        END IF;
    END IF;

    -- check if as_of_timestamp is before _timestamp
    IF only_before AND result IS NOT NULL THEN
        IF result.as_of_timestamp >= _timestamp THEN
            result := NULL;
        END IF;
    END IF;

    -- rebuild usage when not found
    IF rebuild_usage_when_not_found AND result IS NULL THEN
        RAISE NOTICE 'get_resource_usage_at_or_before(_resource_id=%, status_id=%, timestamp=%, exactly_at=%, only_before=%, rebuild_usage_when_not_found=%): result should not be NULL. Rebuilding usages table for resource %.', _resource_id, _claim_status_id, _timestamp, exactly_at, only_before, rebuild_usage_when_not_found, _resource_id;
        PERFORM resource_allocation.rebuild_resource_usages_from_claims_for_resource_of_status(_resource_id, _claim_status_id);
        RAISE NOTICE 'get_resource_usage_at_or_before(_resource_id=%, status_id=%, timestamp=%, exactly_at=%, only_before=%, rebuild_usage_when_not_found=%): Finished rebuilding usages table for resource %.', _resource_id, _claim_status_id, _timestamp, exactly_at, only_before, rebuild_usage_when_not_found, _resource_id;

        -- try again, but now without the option to rebuild_usage_when_not_found (to prevent endless recursion)
        SELECT * FROM resource_allocation.get_resource_usage_at_or_before(_resource_id, _claim_status_id, _timestamp, exactly_at, only_before, false) INTO result;
        RAISE NOTICE 'get_resource_usage_at_or_before(_resource_id=%, status_id=%, timestamp=%, exactly_at=%, only_before=%, rebuild_usage_when_not_found=%): after rebuild, result=%.', _resource_id, _claim_status_id, _timestamp, exactly_at, only_before, false, result;
    END IF;

    RETURN result;
END;
$$ LANGUAGE plpgsql;
ALTER FUNCTION resource_allocation.get_resource_usage_at_or_before(int, int, timestamp, boolean, boolean, boolean) OWNER TO resourceassignment;
COMMENT ON FUNCTION resource_allocation.get_resource_usage_at_or_before(int, int, timestamp, boolean, boolean, boolean)
  IS 'get the resource usage for the given _resource_id for claims with given _claim_status_id at the given _timestamp';

---------------------------------------------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION utcnow()
  RETURNS timestamp AS
$$
  SELECT NOW() AT TIME ZONE 'UTC';
$$ LANGUAGE SQL;
ALTER FUNCTION utcnow() OWNER TO resourceassignment;
COMMENT ON FUNCTION utcnow()
  IS 'get the current time in utc timezone as timestamp (without timezone)';

---------------------------------------------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION resource_allocation.get_current_resource_usage(_resource_id int, _claim_status_id int)
  RETURNS resource_allocation.resource_usage AS
$$
DECLARE
    result resource_allocation.resource_usage;
    now timestamp;
BEGIN
    SELECT * FROM utcnow() INTO now;
    SELECT * FROM resource_allocation.get_resource_usage_at_or_before(_resource_id, _claim_status_id, now, false, false, false) into result;
    RETURN result;
END;
$$ LANGUAGE plpgsql;
ALTER FUNCTION resource_allocation.get_current_resource_usage(_resource_id int, _claim_status_id int) OWNER TO resourceassignment;
COMMENT ON FUNCTION resource_allocation.get_current_resource_usage(_resource_id int, _claim_status_id int)
  IS 'get the current resource usage for the given _resource_id for claims with given _claim_status_id';

---------------------------------------------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION resource_allocation.get_max_resource_usage_between(_resource_id int, _claim_status_id int, _lower timestamp, _upper timestamp)
  RETURNS resource_allocation.resource_usage AS
$$
DECLARE
    max_resource_usage_in_time_window resource_allocation.resource_usage;
    max_resource_at_or_before_starttime resource_allocation.resource_usage;
BEGIN
    SELECT * FROM resource_allocation.resource_usage ru
    WHERE ru.resource_id = _resource_id
    AND ru.status_id = _claim_status_id
    AND ru.as_of_timestamp >= _lower
    AND ru.as_of_timestamp < _upper
    ORDER BY ru.usage DESC
    LIMIT 1 INTO max_resource_usage_in_time_window;

    IF max_resource_usage_in_time_window IS NULL THEN
        -- no usages withing given window, so return first usage before window (which extends in time into this window)
        SELECT * FROM resource_allocation.get_resource_usage_at_or_before(_resource_id, _claim_status_id, _lower, false, false, false) INTO max_resource_at_or_before_starttime;
        RETURN max_resource_at_or_before_starttime;
    END IF;

    IF max_resource_usage_in_time_window.as_of_timestamp > _lower THEN -- Skips as_of_timestamp = _lower on purpose
        -- check if the usage at_or_before_starttime is higher then in_time_window
        SELECT * FROM resource_allocation.get_resource_usage_at_or_before(_resource_id, _claim_status_id, _lower, false, false, false) INTO max_resource_at_or_before_starttime;
        IF max_resource_at_or_before_starttime IS NOT NULL THEN
            IF max_resource_at_or_before_starttime.usage > max_resource_usage_in_time_window.usage THEN
                RETURN max_resource_at_or_before_starttime;
            END IF;
        END IF;
    END IF;

    RETURN max_resource_usage_in_time_window;
END;
$$ LANGUAGE plpgsql;
ALTER FUNCTION resource_allocation.get_max_resource_usage_between(_resource_id int, _claim_status_id int, _lower timestamp, _upper timestamp) OWNER TO resourceassignment;
COMMENT ON FUNCTION resource_allocation.get_max_resource_usage_between(_resource_id int, _claim_status_id int, _lower timestamp, _upper timestamp)
  IS 'get the maximum resource usage for the given _resource_id for claims with given _claim_status_id in the period between the given _lower and _upper timestamps';

---------------------------------------------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION resource_allocation.get_resource_claimable_capacity_between(_resource_id int, _lower timestamp, _upper timestamp)
  RETURNS bigint AS
$$
DECLARE
    claimed_status_id int := 1; --beware: hard coded instead of lookup for performance
    max_resource_usage resource_allocation.resource_usage;
    max_resource_usage_value bigint;
    available_capacity bigint;
    total_capacity bigint;
    current_claimed_usage bigint;
BEGIN
    SELECT usage FROM resource_allocation.get_max_resource_usage_between(_resource_id, claimed_status_id, _lower, _upper) INTO max_resource_usage_value;

    IF max_resource_usage_value IS NULL THEN
        max_resource_usage_value := 0;
    END IF;

    -- determine the available_capacity for this resource
    -- available_capacity is a truly measured metric (by tools like df (disk-free))
    SELECT available, total FROM resource_monitoring.resource_capacity WHERE resource_id = _resource_id LIMIT 1 INTO available_capacity, total_capacity;

    IF available_capacity = total_capacity THEN
        --this is not a monitored resource, and hence we do not know how much space is actually available.
        --make a best guess by subtracting the current_claimed_usage from the total_capacity
        RETURN total_capacity - max_resource_usage_value;
    ELSE
        --this is a monitored resource, and the claimable_capacity is not just the free space (available_capacity) at this moment!
        -- we have to take into account what we know about already claimed portions,
        -- both at this moment (current_claimed_usage) and for the planned claim (max_resource_usage_value, between _lower and _upper)

        -- determine how much of the used_capacity is 'accounted for' by claims.
        -- this is a best guess of the amount of data which we know that should be on the resource.
        -- we can only 'measure' that at this moment,
        -- so take the current resource usage
        SELECT usage FROM resource_allocation.get_current_resource_usage(_resource_id, claimed_status_id) INTO current_claimed_usage;

        IF current_claimed_usage IS NOT NULL THEN
            RETURN available_capacity + current_claimed_usage - max_resource_usage_value;
        END IF;

        RETURN available_capacity - max_resource_usage_value;
    END IF;
END;
$$ LANGUAGE plpgsql;
ALTER FUNCTION resource_allocation.get_resource_claimable_capacity_between(_resource_id int, _lower timestamp, _upper timestamp)
  OWNER TO resourceassignment;
COMMENT ON FUNCTION resource_allocation.get_resource_claimable_capacity_between(_resource_id int, _lower timestamp, _upper timestamp)
  IS 'get the claimable capacity of the resource for the given _resource_id in the period between the given _lower and _upper timestamps';

---------------------------------------------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION resource_allocation.get_resource_claimable_capacities_between(_resource_ids int[], _lower timestamp, _upper timestamp)
  RETURNS bigint[] AS
$$
DECLARE
    resource_claimable_capacity bigint;
    resource_claimable_capacities bigint[];
BEGIN
    FOR i IN 1 .. array_upper(_resource_ids, 1) LOOP
        SELECT * FROM resource_allocation.get_resource_claimable_capacity_between(_resource_ids[i], _lower, _upper) INTO resource_claimable_capacity;
        resource_claimable_capacities[i] := resource_claimable_capacity;
    END LOOP;

    RETURN resource_claimable_capacities;
END;
$$ LANGUAGE plpgsql;
ALTER FUNCTION resource_allocation.get_resource_claimable_capacities_between(_resource_ids int[], _lower timestamp, _upper timestamp)
  OWNER TO resourceassignment;
COMMENT ON FUNCTION resource_allocation.get_resource_claimable_capacities_between(_resource_ids int[], _lower timestamp, _upper timestamp)
  IS 'get the claimable capacity of all the resources for the given _resource_ids in the period between the given _lower and _upper timestamps';

---------------------------------------------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION resource_allocation.has_conflict_with_overlapping_claims(claim resource_allocation.resource_claim)
  RETURNS boolean AS
$$
DECLARE
    free_claimable_capacity bigint;
BEGIN
    -- get the free free_claimable_capacity for this resource for the claim's time window
    -- this does not include the current claim which is (or at least should be) tentative.
    SELECT * FROM resource_allocation.get_resource_claimable_capacity_between(claim.resource_id, claim.starttime, claim.endtime) INTO free_claimable_capacity;

    return claim.claim_size > free_claimable_capacity;
END;
$$ LANGUAGE plpgsql;
ALTER FUNCTION resource_allocation.has_conflict_with_overlapping_claims(claim resource_allocation.resource_claim) OWNER TO resourceassignment;
COMMENT ON FUNCTION resource_allocation.has_conflict_with_overlapping_claims(claim resource_allocation.resource_claim)
  IS 'checks if the claim fits in the free capacity of its resource.';

---------------------------------------------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION resource_allocation.get_overlapping_claims(claim_id int, status int default 1) --beware: hard coded status=1 for claimed claims
  RETURNS SETOF resource_allocation.resource_claim AS
$$
DECLARE
    claim resource_allocation.resource_claim;
BEGIN
    SELECT * FROM resource_allocation.resource_claim
    WHERE id = claim_id
    LIMIT 1
    INTO claim;

    RETURN QUERY SELECT * FROM resource_allocation.get_overlapping_claims(claim, status);
END;
$$ LANGUAGE plpgsql;
ALTER FUNCTION resource_allocation.get_overlapping_claims(int, int) OWNER TO resourceassignment;
COMMENT ON FUNCTION resource_allocation.get_overlapping_claims(int, int)
  IS 'get set of (claimed) claims which cause the given claim to have conflict status.';

---------------------------------------------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION resource_allocation.get_overlapping_claims(claim resource_allocation.resource_claim, status int default 1) --beware: hard coded status=1 for claimed claims
  RETURNS SETOF resource_allocation.resource_claim AS
$$
BEGIN
    -- this function is quite similar to resource_allocation.has_conflict_with_overlapping_claims
    -- for performance reasons we repeat the common code here instead of wrapping the common code in a function

    --get all overlapping_claims, check whether they cause a conflict or not.
    RETURN QUERY SELECT * FROM resource_allocation.resource_claim rc
    WHERE rc.resource_id = claim.resource_id
    AND rc.status_id = status
    AND rc.id <> claim.id
    AND rc.endtime >= claim.starttime
    AND rc.starttime < claim.endtime;
END;
$$ LANGUAGE plpgsql;
ALTER FUNCTION resource_allocation.get_overlapping_claims(resource_allocation.resource_claim, int) OWNER TO resourceassignment;
COMMENT ON FUNCTION resource_allocation.get_overlapping_claims(resource_allocation.resource_claim, int)
  IS 'get set of claims (with given status) which overlap with the given claim.';

---------------------------------------------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION resource_allocation.before_claim_insertupdatedelete()
  RETURNS trigger AS
$BODY$
DECLARE
    claim_tentative_status_id int := 0; --beware: hard coded instead of lookup for performance
    claim_claimed_status_id int := 1; --beware: hard coded instead of lookup for performance
    claim_conflict_status_id int := 2; --beware: hard coded instead of lookup for performance
    task_approved_status_id int := 300; --beware: hard coded instead of lookup for performance
    task_conflict_status_id int := 335; --beware: hard coded instead of lookup for performance
    task_prescheduled_status_id int := 350; --beware: hard coded instead of lookup for performance
    task_scheduled_status_id int := 400; --beware: hard coded instead of lookup for performance
    task_queued_status_id int := 500; --beware: hard coded instead of lookup for performance
    claim_has_conflicts boolean;
BEGIN
    -- BEWARE: this trigger function causes new updates/inserts/deletes on the resource_claim, resource_usage and task tables
    -- this can lead to concurrency issues in a multiprocess environment. See https://support.astron.nl/jira/browse/SW-786
    -- you should always lock these tables when modifying them in your external code, like so:
    -- LOCK TABLE resource_allocation.resource_claim, resource_allocation.resource_usage, resource_allocation.task  IN EXCLUSIVE MODE;

    --order of following steps is important, do not reorder the steps
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        IF NEW.starttime >= NEW.endtime THEN
            -- Conceptually, you can't claim and release a resource at the same timestamp.
            -- Nor can you claim a resource for a negative timespan.
            RAISE EXCEPTION 'claim starttime >= endtime: %', NEW;
        END IF;
    END IF;

    -- bounce any inserted claim which is not tentative
    IF TG_OP = 'INSERT' THEN
        IF NEW.status_id <> claim_tentative_status_id THEN
            RAISE EXCEPTION 'newly inserted claims should not have status other than tentative (%); new claim: % has status %', claim_tentative_status_id, NEW, NEW.status_id;
        END IF;
    END IF;

    IF TG_OP = 'UPDATE' THEN
        -- bounce any updated claim which has conflict state, but is tried to be updated to claimed
        -- only this function can 'reset' the conflict state back to tentative!
        IF NEW.status_id = claim_claimed_status_id AND OLD.status_id = claim_conflict_status_id THEN
            RAISE EXCEPTION 'cannot update claim-in-conflict to status claimed; old:% new:%', OLD, NEW;
        END IF;

        -- bounce any claim_size updates on claimed claims
        IF NEW.status_id = claim_claimed_status_id AND OLD.claim_size <> NEW.claim_size THEN
            RAISE EXCEPTION 'cannot update claim size on claimed claim; old:% new:%', OLD, NEW;
        END IF;

        -- bounce any task_id updates
        IF OLD.task_id <> NEW.task_id THEN
            RAISE EXCEPTION 'cannot change the task to which a claim belongs; old:% new:%', OLD, NEW;
        END IF;

        -- bounce any resource_id updates
        IF OLD.resource_id <> NEW.resource_id THEN
            RAISE EXCEPTION 'cannot change the resource to which a claim belongs; old:% new:%', OLD, NEW;
        END IF;
    END IF;

    IF TG_OP = 'UPDATE' OR TG_OP = 'DELETE' THEN
        --update the resource usages affected by this claim
        --do this before we check for conflicts, because this claim might be shifted for example
        --which might influence the resource_usages which determine wheter a claim fits.
        PERFORM resource_allocation.process_old_claim_outof_resource_usages(OLD);
    END IF;

    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        --check if claim fits or has conflicts
        SELECT * FROM resource_allocation.has_conflict_with_overlapping_claims(NEW) INTO claim_has_conflicts;

        IF claim_has_conflicts THEN
            IF NEW.status_id <> claim_conflict_status_id THEN
                -- only set claims to conflict if task status <= queued
                -- when a claim goes to conflict, then so does it's task, and we don't want that for running/finished/aborted tasks
                IF EXISTS (SELECT 1 FROM resource_allocation.task
                            WHERE id=NEW.task_id
                            AND status_id = ANY(ARRAY[task_approved_status_id, task_conflict_status_id, task_prescheduled_status_id, task_scheduled_status_id, task_queued_status_id])) THEN -- hardcoded tasks statuses <= queued
                    -- conflict with others, so set claim status to conflict
                    NEW.status_id := claim_conflict_status_id;
                END IF;
            END IF;
        ELSE
            -- no conflict (anymore) with others, so set claim status to tentative if currently in conflict
            IF NEW.status_id = claim_conflict_status_id THEN
                NEW.status_id := claim_tentative_status_id;
            END IF;
        END IF;

        --update the resource usages affected by this claim
        PERFORM resource_allocation.process_new_claim_into_resource_usages(NEW);
    END IF;

    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    END IF;

    RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION resource_allocation.before_claim_insertupdatedelete()
  OWNER TO resourceassignment;
COMMENT ON FUNCTION resource_allocation.before_claim_insertupdatedelete()
  IS 'trigger function which is called by resource_claim table insert/update/delete trigger, which fills/updates/clears the resource_allocation.resource_usage table with timeseries of accumulated resource_claim.sizes, and checks if claims fit in the free capacity of a resource';

DROP TRIGGER IF EXISTS T_before_claim_insertupdatedelete ON resource_allocation.resource_claim CASCADE;
CREATE TRIGGER T_before_claim_insertupdatedelete
  BEFORE INSERT OR UPDATE OR DELETE
  ON resource_allocation.resource_claim
  FOR EACH ROW
  EXECUTE PROCEDURE resource_allocation.before_claim_insertupdatedelete();

---------------------------------------------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION resource_allocation.after_claim_insertupdatedelete()
  RETURNS trigger AS
$BODY$
DECLARE
    claim_tentative_status_id int := 0; --beware: hard coded instead of lookup for performance
    claim_claimed_status_id int := 1; --beware: hard coded instead of lookup for performance
    claim_conflict_status_id int := 2; --beware: hard coded instead of lookup for performance
    task_approved_status_id int := 300; --beware: hard coded instead of lookup for performance
    task_conflict_status_id int := 335; --beware: hard coded instead of lookup for performance
    task_finished_status_id int := 1000; --beware: hard coded instead of lookup for performance
    task_aborted_status_id int  := 1100; --beware: hard coded instead of lookup for performance
    affected_claim resource_allocation.resource_claim;
    claim_has_conflicts boolean;
BEGIN
    -- in the before trigger function, everything on the claim has been checked and adapted.
    -- now (in the after trigger, when all claims were inserted/updated in the database), let's check if the task should also be updated (to conflict status for example)
    -- only if claim status was changed or inserted...
    IF TG_OP = 'INSERT' OR (TG_OP = 'UPDATE' AND (OLD.status_id <> NEW.status_id)) THEN
        IF NEW.status_id = claim_conflict_status_id THEN
            --if claim status went to conflict, then set the task status to conflict as well
            UPDATE resource_allocation.task SET status_id=task_conflict_status_id WHERE id=NEW.task_id AND status_id <> task_conflict_status_id;
        ELSIF NEW.status_id = claim_tentative_status_id THEN
             IF NOT EXISTS (SELECT id FROM resource_allocation.resource_claim
                           WHERE task_id = NEW.task_id
                           AND status_id = claim_conflict_status_id) THEN

                 IF NOT EXISTS (SELECT id FROM resource_allocation.task
                           WHERE id = NEW.task_id
                           AND status_id = task_approved_status_id) THEN
                     -- update tasks which were in conflict, but which are not anymore due this claim-update to the approved status
                     UPDATE resource_allocation.task
                     SET status_id=COALESCE((SELECT status_id from resource_allocation.task_status_before_conlict WHERE task_id=NEW.task_id), task_approved_status_id)
                     WHERE id=NEW.task_id AND status_id = task_conflict_status_id;
                END IF;
            END IF;
        END IF;
    END IF;

    -- if this claim was moved or went from claimed to other status
    -- then check all other claims in conflict which might be affected by this change
    -- maybe they can be updated from conflict status to tentative...
    IF (TG_OP = 'UPDATE' AND (OLD.status_id = claim_claimed_status_id OR OLD.starttime <> NEW.starttime OR OLD.endtime <> NEW.endtime OR OLD.claim_size <> NEW.claim_size)) OR
        TG_OP = 'DELETE' THEN
        FOR affected_claim IN SELECT * FROM resource_allocation.resource_claim rc
                                        WHERE rc.resource_id = OLD.resource_id
                                        AND rc.status_id = claim_conflict_status_id
                                        AND rc.id <> OLD.id
                                        AND rc.endtime >= OLD.starttime
                                        AND rc.starttime < OLD.endtime LOOP

            --check if claim fits or has conflicts
            SELECT * FROM resource_allocation.has_conflict_with_overlapping_claims(affected_claim) INTO claim_has_conflicts;

            IF NOT claim_has_conflicts THEN
                -- no conflict (anymore) with others, so set claim status to tentative
                UPDATE resource_allocation.resource_claim SET status_id=claim_tentative_status_id WHERE id = affected_claim.id;
            END IF;
        END LOOP;
    END IF;

    -- if this claim went from to claimed status
    -- then check all other claims in tentative state which might be affected by this change
    -- maybe they should be updated from tentative status to conflict...
    IF TG_OP = 'UPDATE' AND NEW.status_id = claim_claimed_status_id AND (OLD.status_id <> NEW.status_id OR OLD.claim_size <> NEW.claim_size)THEN
        FOR affected_claim IN SELECT * FROM resource_allocation.resource_claim rc
                                        WHERE rc.resource_id = NEW.resource_id
                                        AND rc.status_id = claim_tentative_status_id
                                        AND rc.id <> NEW.id
                                        AND rc.endtime >= NEW.starttime
                                        AND rc.starttime < NEW.endtime LOOP

            --check if claim fits or has conflicts
            SELECT * FROM resource_allocation.has_conflict_with_overlapping_claims(affected_claim) INTO claim_has_conflicts;

            IF claim_has_conflicts THEN
                -- new conflict for affected_claim because this NEW claim is now claimed
                UPDATE resource_allocation.resource_claim SET status_id=claim_conflict_status_id WHERE id = affected_claim.id;
            END IF;
        END LOOP;
    END IF;

    IF TG_OP = 'UPDATE' THEN
      -- delete obsolete claim when task is finished/aborted
      IF NEW.status_id = claim_claimed_status_id AND
         NEW.endtime <> OLD.endtime AND
         NEW.endtime <= (SELECT * FROM utcnow() LIMIT 1) THEN
         -- this claim is obsolete...
        IF EXISTS (SELECT id FROM resource_allocation.task t WHERE t.id = NEW.task_id AND t.status_id IN (task_finished_status_id, task_aborted_status_id) ) THEN
            -- ...and it's task is finished/aborted
            -- so, delete this claim
            DELETE FROM resource_allocation.resource_claim rc
            WHERE rc.id=NEW.id;
        END IF;
      END IF;
    END IF;

    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    END IF;

    RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION resource_allocation.after_claim_insertupdatedelete()
  OWNER TO resourceassignment;
COMMENT ON FUNCTION resource_allocation.after_claim_insertupdatedelete()
  IS '';

DROP TRIGGER IF EXISTS T_after_claim_insertupdatedelete ON resource_allocation.resource_claim CASCADE;
CREATE TRIGGER T_after_claim_insertupdatedelete
  AFTER INSERT OR UPDATE OR DELETE
  ON resource_allocation.resource_claim
  FOR EACH ROW
  EXECUTE PROCEDURE resource_allocation.after_claim_insertupdatedelete();

---------------------------------------------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION resource_allocation.after_claim_truncate()
  RETURNS trigger AS
$BODY$
DECLARE
BEGIN
    TRUNCATE resource_allocation.resource_usage CASCADE;
    TRUNCATE resource_allocation.resource_usage_delta CASCADE;
    RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION resource_allocation.after_claim_truncate()
  OWNER TO resourceassignment;
COMMENT ON FUNCTION resource_allocation.after_claim_truncate()
  IS 'tables resource_allocation.resource_usage and resource_allocation.resource_usage do not have references to the resource_allocation.resource_claim table. So there is no automatic cascading truncate. This function and the truncate trigger on resource_allocation.resource_claim makes sure these tables are truncated as well.';

DROP TRIGGER IF EXISTS T_after_claim_truncate ON resource_allocation.resource_claim CASCADE;
CREATE TRIGGER T_after_claim_truncate
  AFTER TRUNCATE
  ON resource_allocation.resource_claim
  FOR EACH STATEMENT
  EXECUTE PROCEDURE resource_allocation.after_claim_truncate();

---------------------------------------------------------------------------------------------------------------------


COMMIT;
