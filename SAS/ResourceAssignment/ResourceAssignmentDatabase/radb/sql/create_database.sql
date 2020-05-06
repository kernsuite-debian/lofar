-- Copied from JR's script, maybe we should do this?
-- DROP DATABASE IF EXISTS resourceassignment;
-- CREATE DATABASE resourceassignment
--   WITH OWNER = resourceassignment
--       ENCODING = 'UTF8'
--       TABLESPACE = pg_default
--       LC_COLLATE = 'en_US.UTF-8'
--       LC_CTYPE = 'en_US.UTF-8'
--       CONNECTION LIMIT = -1;

-- psql resourceassignment -U resourceassignment -f create_database.sql -W

BEGIN;

-- only issue >warnings log messages. (only during this transaction)
SET LOCAL client_min_messages=warning;

DROP SCHEMA IF EXISTS virtual_instrument CASCADE;
DROP SCHEMA IF EXISTS resource_monitoring CASCADE;
DROP SCHEMA IF EXISTS resource_allocation CASCADE;

CREATE SCHEMA virtual_instrument;
CREATE SCHEMA resource_monitoring;
CREATE SCHEMA resource_allocation;

-- This is insanity, but works, order needs to be the reverse of the CREATE TABLE statements
DROP VIEW IF EXISTS virtual_instrument.resource_view CASCADE;
DROP VIEW IF EXISTS resource_allocation.task_view CASCADE;
DROP VIEW IF EXISTS resource_allocation.resource_claim_view CASCADE;
DROP VIEW IF EXISTS resource_monitoring.resource_view CASCADE;
DROP TABLE IF EXISTS resource_allocation.config CASCADE;
DROP TABLE IF EXISTS resource_monitoring.resource_group_availability CASCADE;
DROP TABLE IF EXISTS resource_monitoring.resource_availability CASCADE;
DROP TABLE IF EXISTS resource_monitoring.resource_capacity CASCADE;
DROP TABLE IF EXISTS resource_allocation.resource_usage CASCADE;
DROP TABLE IF EXISTS resource_allocation.resource_usage_delta CASCADE;
DROP TABLE IF EXISTS resource_allocation.resource_claim_property CASCADE;
DROP TABLE IF EXISTS resource_allocation.resource_claim_property_type CASCADE;
DROP TABLE IF EXISTS resource_allocation.resource_claim_property_io_type CASCADE;
DROP TABLE IF EXISTS resource_allocation.sap CASCADE;
DROP TABLE IF EXISTS resource_allocation.conflict_reason CASCADE;
DROP TABLE IF EXISTS resource_allocation.resource_claim_conflict_reason CASCADE;
DROP TABLE IF EXISTS resource_allocation.task_conflict_reason CASCADE;
DROP TABLE IF EXISTS resource_allocation.resource_claim CASCADE;
DROP TABLE IF EXISTS resource_allocation.resource_claim_status CASCADE;
DROP TABLE IF EXISTS resource_allocation.task_predecessor CASCADE;
DROP TABLE IF EXISTS resource_allocation.task CASCADE;
DROP TABLE IF EXISTS resource_allocation.specification CASCADE;
DROP TYPE IF EXISTS resource_allocation.antennaset;
DROP TABLE IF EXISTS resource_allocation.observation_specification CASCADE;
DROP TABLE IF EXISTS resource_allocation.task_type CASCADE;
DROP TABLE IF EXISTS resource_allocation.task_status CASCADE;
DROP TABLE IF EXISTS virtual_instrument.resource_group_to_resource_group CASCADE;
DROP TABLE IF EXISTS virtual_instrument.resource_to_resource_group CASCADE;
DROP TABLE IF EXISTS virtual_instrument.resource_group CASCADE;
DROP TABLE IF EXISTS virtual_instrument.resource_group_type CASCADE;
DROP TABLE IF EXISTS virtual_instrument.resource CASCADE;
DROP TABLE IF EXISTS virtual_instrument.resource_type CASCADE;
DROP TABLE IF EXISTS virtual_instrument.unit CASCADE;
-- Would like to use this instead, but I can not get it to do something useful: SET CONSTRAINTS ALL DEFERRED;

CREATE TABLE virtual_instrument.unit (
  id serial NOT NULL,
  units text NOT NULL,
  PRIMARY KEY (id)
) WITH (OIDS=FALSE);
ALTER TABLE virtual_instrument.unit
  OWNER TO resourceassignment;

CREATE TABLE virtual_instrument.resource_type (
  id serial NOT NULL,
  name text NOT NULL,
  unit_id integer NOT NULL REFERENCES virtual_instrument.unit DEFERRABLE INITIALLY IMMEDIATE,
  PRIMARY KEY (id)
) WITH (OIDS=FALSE);
ALTER TABLE virtual_instrument.resource_type
  OWNER TO resourceassignment;

CREATE TABLE virtual_instrument.resource (
  id serial NOT NULL,
  name text NOT NULL,
  type_id integer NOT NULL REFERENCES virtual_instrument.resource_type ON DELETE CASCADE DEFERRABLE INITIALLY IMMEDIATE,
  PRIMARY KEY (id)
) WITH (OIDS=FALSE);
ALTER TABLE virtual_instrument.resource
  OWNER TO resourceassignment;

CREATE TABLE virtual_instrument.resource_group_type (
  id serial NOT NULL,
  name text NOT NULL,
  PRIMARY KEY (id)
) WITH (OIDS=FALSE);
ALTER TABLE virtual_instrument.resource_group_type
  OWNER TO resourceassignment;

CREATE TABLE virtual_instrument.resource_group (
  id serial NOT NULL,
  name text NOT NULL,
  type_id integer NOT NULL REFERENCES virtual_instrument.resource_group_type ON DELETE CASCADE DEFERRABLE INITIALLY IMMEDIATE,
  PRIMARY KEY (id)
) WITH (OIDS=FALSE);
ALTER TABLE virtual_instrument.resource_group
  OWNER TO resourceassignment;

CREATE TABLE virtual_instrument.resource_to_resource_group (
  id serial NOT NULL,
  child_id integer NOT NULL REFERENCES virtual_instrument.resource ON DELETE CASCADE DEFERRABLE INITIALLY IMMEDIATE,
  parent_id integer NOT NULL REFERENCES virtual_instrument.resource_group ON DELETE CASCADE DEFERRABLE INITIALLY IMMEDIATE,
  PRIMARY KEY (id)
) WITH (OIDS=FALSE);
ALTER TABLE virtual_instrument.resource_to_resource_group
  OWNER TO resourceassignment;

CREATE TABLE virtual_instrument.resource_group_to_resource_group (
  id serial NOT NULL,
  child_id integer NOT NULL REFERENCES virtual_instrument.resource_group ON DELETE CASCADE DEFERRABLE INITIALLY IMMEDIATE,
  parent_id integer REFERENCES virtual_instrument.resource_group ON DELETE CASCADE DEFERRABLE INITIALLY IMMEDIATE,
  PRIMARY KEY (id)
) WITH (OIDS=FALSE);
ALTER TABLE virtual_instrument.resource_group_to_resource_group
  OWNER TO resourceassignment;

CREATE TABLE resource_allocation.task_status (
  id serial NOT NULL,
  name text NOT NULL,
  PRIMARY KEY (id)
) WITH (OIDS=FALSE);
ALTER TABLE resource_allocation.task_status
  OWNER TO resourceassignment;

CREATE TABLE resource_allocation.task_type (
  id serial NOT NULL,
  name text NOT NULL,
  PRIMARY KEY (id)
) WITH (OIDS=FALSE);
ALTER TABLE resource_allocation.task_type
  OWNER TO resourceassignment;

CREATE TYPE resource_allocation.antennaset AS ENUM('HBA Zero', 'HBA One', 'HBA Dual', 'HBA Joined', 'LBA Outer', 'LBA Inner', 'LBA Sparse Even', 'LBA Sparse Odd', 'LBA X', 'LBA Y', 'HBA Zero Inner', 'HBA One Inner', 'HBA Dual Inner', 'HBA Joined Inner');
CREATE TABLE resource_allocation.observation_specification (
  id serial NOT NULL,
  clock integer NOT NULL,
  bitmode integer NOT NULL,
  splitter boolean NOT NULL,
  antenna resource_allocation.antennaset NOT NULL,
  PRIMARY KEY (id)
) WITH (OIDS=FALSE);
ALTER TABLE resource_allocation.observation_specification
  OWNER TO resourceassignment;
-- ALTER TABLE distributors -- Maybe we need a check like this?
-- ADD CONSTRAINT check_values 
-- CHECK (clock = 160 OR clock = 200);

CREATE TABLE resource_allocation.specification (
  id serial NOT NULL,
  starttime timestamp,
  endtime timestamp,
  content text,
  cluster text DEFAULT '',
  observation_id integer REFERENCES resource_allocation.observation_specification  ON DELETE CASCADE DEFERRABLE INITIALLY IMMEDIATE,
  PRIMARY KEY (id)
) WITH (OIDS=FALSE);
ALTER TABLE resource_allocation.specification
  OWNER TO resourceassignment;

CREATE INDEX specification_cluster_idx
  ON resource_allocation.specification (cluster);

CREATE INDEX specification_starttime_endtime_idx
  ON resource_allocation.specification (starttime DESC, endtime);

-- I think we need this one?
CREATE INDEX specification_observation_id_idx
  ON resource_allocation.specification (observation_id);

CREATE TABLE resource_allocation.task (
  id serial NOT NULL,
  mom_id integer UNIQUE,
  otdb_id integer UNIQUE,
  status_id integer NOT NULL REFERENCES resource_allocation.task_status DEFERRABLE INITIALLY IMMEDIATE,
  type_id integer NOT NULL REFERENCES resource_allocation.task_type DEFERRABLE INITIALLY IMMEDIATE,
  specification_id integer NOT NULL REFERENCES resource_allocation.specification  ON DELETE CASCADE DEFERRABLE INITIALLY IMMEDIATE,
  PRIMARY KEY (id)
) WITH (OIDS=FALSE);
ALTER TABLE resource_allocation.task
  OWNER TO resourceassignment;

CREATE INDEX task_mom_id_idx
  ON resource_allocation.task (mom_id);

CREATE INDEX task_otdb_id_idx
  ON resource_allocation.task (otdb_id);

CREATE INDEX task_status_id_idx
  ON resource_allocation.task (status_id);

CREATE INDEX task_type_id_idx
  ON resource_allocation.task (type_id);


CREATE TABLE resource_allocation.task_status_before_conlict (
  task_id integer NOT NULL REFERENCES resource_allocation.task(id) ON DELETE CASCADE DEFERRABLE INITIALLY IMMEDIATE,
  status_id integer NOT NULL REFERENCES resource_allocation.task_status ON DELETE CASCADE DEFERRABLE INITIALLY IMMEDIATE,
  PRIMARY KEY (task_id)
) WITH (OIDS=FALSE);
ALTER TABLE resource_allocation.task_status_before_conlict
  OWNER TO resourceassignment;

CREATE TABLE resource_allocation.task_predecessor (
  id serial NOT NULL,
  task_id integer NOT NULL REFERENCES resource_allocation.task(id) ON DELETE CASCADE DEFERRABLE INITIALLY IMMEDIATE,
  predecessor_id integer NOT NULL REFERENCES resource_allocation.task(id) ON DELETE CASCADE DEFERRABLE INITIALLY IMMEDIATE,
  PRIMARY KEY (id),
  CONSTRAINT task_predecessor_unique UNIQUE (task_id, predecessor_id)
) WITH (OIDS=FALSE);
ALTER TABLE resource_allocation.task_predecessor
  OWNER TO resourceassignment;

CREATE INDEX task_predecessor_predecessor_id_idx
  ON resource_allocation.task_predecessor (predecessor_id);

CREATE INDEX task_predecessor_task_id_idx
  ON resource_allocation.task_predecessor (task_id);

CREATE TABLE resource_allocation.resource_claim_status (
  id serial NOT NULL,
  name text NOT NULL,
  PRIMARY KEY (id)
) WITH (OIDS=FALSE);
ALTER TABLE resource_allocation.resource_claim_status
  OWNER TO resourceassignment;


CREATE TABLE resource_allocation.resource_claim (
  id serial NOT NULL,
  resource_id integer NOT NULL REFERENCES virtual_instrument.resource ON DELETE CASCADE DEFERRABLE INITIALLY IMMEDIATE,
  task_id integer NOT NULL REFERENCES resource_allocation.task ON DELETE CASCADE DEFERRABLE INITIALLY IMMEDIATE,
  starttime timestamp NOT NULL,
  endtime timestamp NOT NULL,
  status_id integer NOT NULL REFERENCES resource_allocation.resource_claim_status DEFERRABLE INITIALLY IMMEDIATE,
  claim_size bigint NOT NULL,
  username text,
  user_id integer,
  used_rcus bit VARYING(192),
  PRIMARY KEY (id)
) WITH (OIDS=FALSE);
ALTER TABLE resource_allocation.resource_claim
  OWNER TO resourceassignment;

CREATE INDEX resource_claim_starttime_endtime_idx
  ON resource_allocation.resource_claim
  USING btree
  (starttime DESC, endtime);

CREATE INDEX resource_claim_task_id_idx
  ON resource_allocation.resource_claim (task_id);

CREATE INDEX resource_claim_resource_id_idx
  ON resource_allocation.resource_claim (resource_id);

CREATE INDEX resource_claim_status_id_idx
  ON resource_allocation.resource_claim (status_id);


CREATE TABLE resource_allocation.conflict_reason (
  id serial NOT NULL,
  reason text NOT NULL,
  PRIMARY KEY (id)
) WITH (OIDS=FALSE);
ALTER TABLE resource_allocation.conflict_reason
  OWNER TO resourceassignment;

CREATE TABLE resource_allocation.resource_claim_conflict_reason (
  id serial NOT NULL,
  resource_claim_id integer NOT NULL REFERENCES resource_allocation.resource_claim ON DELETE CASCADE DEFERRABLE INITIALLY IMMEDIATE,
  conflict_reason_id integer NOT NULL REFERENCES resource_allocation.conflict_reason ON DELETE CASCADE DEFERRABLE INITIALLY IMMEDIATE,
  PRIMARY KEY (id)
) WITH (OIDS=FALSE);
ALTER TABLE resource_allocation.resource_claim_conflict_reason
  OWNER TO resourceassignment;

CREATE TABLE resource_allocation.task_conflict_reason (
  id serial NOT NULL,
  task_id integer NOT NULL REFERENCES resource_allocation.task ON DELETE CASCADE DEFERRABLE INITIALLY IMMEDIATE,
  conflict_reason_id integer NOT NULL REFERENCES resource_allocation.conflict_reason ON DELETE CASCADE DEFERRABLE INITIALLY IMMEDIATE,
  PRIMARY KEY (id)
) WITH (OIDS=FALSE);
ALTER TABLE resource_allocation.task_conflict_reason
  OWNER TO resourceassignment;

CREATE TABLE resource_allocation.sap (
  id serial NOT NULL,
  resource_claim_id integer NOT NULL REFERENCES resource_allocation.resource_claim ON DELETE CASCADE DEFERRABLE INITIALLY IMMEDIATE,
  number int NOT NULL,
  PRIMARY KEY (id)
) WITH (OIDS=FALSE);
ALTER TABLE resource_allocation.sap
  OWNER TO resourceassignment;

CREATE TABLE resource_allocation.resource_claim_property_type (
  id serial NOT NULL,
  name text NOT NULL,
  PRIMARY KEY (id)
) WITH (OIDS=FALSE);
ALTER TABLE resource_allocation.resource_claim_property_type
  OWNER TO resourceassignment;

CREATE TABLE resource_allocation.resource_claim_property_io_type (
  id serial NOT NULL,
  name text NOT NULL,
  PRIMARY KEY (id)
) WITH (OIDS=FALSE);
ALTER TABLE resource_allocation.resource_claim_property_io_type
  OWNER TO resourceassignment;

CREATE TABLE resource_allocation.resource_claim_property (
  id serial NOT NULL,
  resource_claim_id integer NOT NULL REFERENCES resource_allocation.resource_claim ON DELETE CASCADE DEFERRABLE INITIALLY IMMEDIATE,
  sap_id integer REFERENCES resource_allocation.sap ON DELETE CASCADE DEFERRABLE INITIALLY IMMEDIATE,
  type_id integer NOT NULL REFERENCES resource_allocation.resource_claim_property_type DEFERRABLE INITIALLY IMMEDIATE,
  value bigint NOT NULL DEFAULT 1,
  io_type_id integer NOT NULL DEFAULT 0 REFERENCES resource_allocation.resource_claim_property_io_type DEFERRABLE INITIALLY IMMEDIATE,
  PRIMARY KEY (id)
) WITH (OIDS=FALSE);
ALTER TABLE resource_allocation.resource_claim_property
  OWNER TO resourceassignment;

CREATE TABLE resource_monitoring.resource_capacity (
  id serial NOT NULL,
  resource_id integer NOT NULL REFERENCES virtual_instrument.resource ON DELETE CASCADE DEFERRABLE INITIALLY IMMEDIATE,
  available bigint NOT NULL,
  total bigint NOT NULL,
  PRIMARY KEY (id)
) WITH (OIDS=FALSE);
ALTER TABLE resource_monitoring.resource_capacity
  OWNER TO resourceassignment;
COMMENT ON COLUMN resource_monitoring.resource_capacity.available IS 'This is the current (momentaneous) available capacity of this resource (which is total-used) and has to be set from a monitoring system.';
COMMENT ON COLUMN resource_monitoring.resource_capacity.total IS 'This is the total (momentaneous) available capacity of this resource. Usually the total capacity is fixed, but it could change, for example when you add an extra disk.';

CREATE TABLE resource_allocation.resource_usage (
  id serial NOT NULL,
  resource_id integer NOT NULL REFERENCES virtual_instrument.resource ON DELETE CASCADE DEFERRABLE INITIALLY IMMEDIATE,
  status_id integer NOT NULL REFERENCES resource_allocation.resource_claim_status ON DELETE CASCADE DEFERRABLE INITIALLY IMMEDIATE,
  as_of_timestamp timestamp NOT NULL,
  usage bigint NOT NULL,
  PRIMARY KEY (id),
  CONSTRAINT usage_unique UNIQUE (resource_id, status_id, as_of_timestamp)
) WITH (OIDS=FALSE);
ALTER TABLE resource_allocation.resource_usage
  OWNER TO resourceassignment;
COMMENT ON TABLE resource_allocation.resource_usage
  IS 'resource_usage is automatically filled (thanks to triggers) whenever claims are inserted/updated/deleted on the resource. It contains a timeseries per resource per status of the used sizes of that resource.';

CREATE INDEX resource_usage_as_of_timestamp_idx
  ON resource_allocation.resource_usage
  USING btree (as_of_timestamp);

CREATE INDEX resource_usage_resource_id_idx
  ON resource_allocation.resource_usage (resource_id);

CREATE INDEX resource_usage_status_id_idx
  ON resource_allocation.resource_usage (status_id);

CREATE TABLE resource_allocation.resource_usage_delta (
  id serial NOT NULL,
  claim_id integer NOT NULL, -- yes, this is a reference to resource_allocation.resource_claim.id, but it's not defined as a reference because it is already used in the before_insert trigger when the claim id does not exist in the claim table yet. We do the consistent bookkeeping in the trigger functions ourselves.
  resource_id integer NOT NULL REFERENCES virtual_instrument.resource ON DELETE CASCADE DEFERRABLE INITIALLY IMMEDIATE,
  status_id integer NOT NULL REFERENCES resource_allocation.resource_claim_status ON DELETE CASCADE DEFERRABLE INITIALLY IMMEDIATE,
  moment timestamp NOT NULL,
  delta bigint NOT NULL,
  PRIMARY KEY (id)
) WITH (OIDS=FALSE);
ALTER TABLE resource_allocation.resource_usage_delta
  OWNER TO resourceassignment;
COMMENT ON TABLE resource_allocation.resource_usage_delta
  IS 'intermediate helper table to quickly compute resource_usage from resource_claim.';

CREATE INDEX resource_usage_delta_moment_idx
  ON resource_allocation.resource_usage_delta
  USING btree (moment);

CREATE INDEX resource_usage_delta_idx
  ON resource_allocation.resource_usage_delta (claim_id, resource_id, status_id);





CREATE TABLE resource_monitoring.resource_availability (
  id serial NOT NULL,
  resource_id integer NOT NULL REFERENCES virtual_instrument.resource ON DELETE CASCADE DEFERRABLE INITIALLY IMMEDIATE,
  available bool NOT NULL,
  PRIMARY KEY (id)
) WITH (OIDS=FALSE);
ALTER TABLE resource_monitoring.resource_availability
  OWNER TO resourceassignment;

CREATE TABLE resource_monitoring.resource_group_availability (
  id serial NOT NULL,
  resource_group_id integer NOT NULL REFERENCES virtual_instrument.resource_group DEFERRABLE INITIALLY IMMEDIATE,
  available bool NOT NULL,
  PRIMARY KEY (id)
) WITH (OIDS=FALSE);
ALTER TABLE resource_monitoring.resource_group_availability
  OWNER TO resourceassignment;

CREATE TABLE resource_allocation.config (
  id serial NOT NULL,
  name text NOT NULL,
  value text,
  PRIMARY KEY (id)
) WITH (OIDS=FALSE);
ALTER TABLE resource_allocation.config
  OWNER TO resourceassignment;

-- VIEWS ----------------------------------------------

CREATE OR REPLACE VIEW resource_allocation.task_view AS
 SELECT t.id, t.mom_id, t.otdb_id, t.status_id, t.type_id, t.specification_id,
    ts.name AS status, tt.name AS type, s.starttime, s.endtime, extract(epoch from age(s.endtime, s.starttime)) as duration, s.cluster,
    (SELECT array_agg(tp.predecessor_id) FROM resource_allocation.task_predecessor tp where tp.task_id=t.id) as predecessor_ids,
    (SELECT array_agg(tp.task_id) FROM resource_allocation.task_predecessor tp where tp.predecessor_id=t.id) as successor_ids,
    (SELECT DISTINCT ARRAY (
		SELECT _tp.predecessor_id
		FROM resource_allocation.task_predecessor _tp, resource_allocation.task _t
		WHERE t.status_id = 400 AND _tp.task_id = t.id AND _t.id = _tp.predecessor_id AND _t.status_id in (300, 320, 335, 1100, 1150, 1200) ) as array_agg
	) as blocked_by_ids
   FROM resource_allocation.task t
   JOIN resource_allocation.task_status ts ON ts.id = t.status_id
   JOIN resource_allocation.task_type tt ON tt.id = t.type_id
   JOIN resource_allocation.specification s ON s.id = t.specification_id;
ALTER VIEW resource_allocation.task_view
  OWNER TO resourceassignment;
COMMENT ON VIEW resource_allocation.task_view
  IS 'plain view on task table including task_status.name task_type.name specification.starttime and specification.endtime, duration in seconds, and the task predecessor- and successor ids';


CREATE OR REPLACE VIEW resource_allocation.resource_claim_view AS
 SELECT rc.*,
    rcs.name AS status
   FROM resource_allocation.resource_claim rc
   JOIN resource_allocation.resource_claim_status rcs ON rcs.id = rc.status_id;
ALTER VIEW resource_allocation.resource_claim_view
  OWNER TO resourceassignment;
COMMENT ON VIEW resource_allocation.resource_claim_view
  IS 'plain view on resource_claim table, including resource_claim_status.name';


CREATE OR REPLACE VIEW virtual_instrument.resource_view AS
  SELECT r.id,
      r.name,
      r.type_id,
      rt.name AS type_name,
      u.id as unit_id,
      u.units as unit
    FROM virtual_instrument.resource r
    JOIN virtual_instrument.resource_type rt ON rt.id = r.type_id
    JOIN virtual_instrument.unit u ON rt.unit_id = u.id;
ALTER VIEW virtual_instrument.resource_view
  OWNER TO resourceassignment;
COMMENT ON VIEW virtual_instrument.resource_view
  IS 'plain view on resource table including task_type.name and units';


CREATE OR REPLACE VIEW resource_allocation.resource_claim_extended_view AS
 SELECT rcv.*, rv.name as resource_name, rv.type_id as resource_type_id, rv.type_name as resource_type_name
   FROM resource_allocation.resource_claim_view rcv
   JOIN virtual_instrument.resource_view rv ON rcv.resource_id = rv.id;
ALTER VIEW resource_allocation.resource_claim_extended_view
  OWNER TO resourceassignment;
COMMENT ON VIEW resource_allocation.resource_claim_extended_view
  IS 'extended view on resource_claim table, including resource_claim_status.name and the resource itself';

CREATE OR REPLACE VIEW resource_allocation.resource_claim_property_view AS
 SELECT rcp.id, rcp.resource_claim_id, rcp.value, rcp.sap_id,
    rcp.type_id, rcpt.name AS type_name,
    rcp.io_type_id, rcpiot.name AS io_type_name
   FROM resource_allocation.resource_claim_property rcp
   JOIN resource_allocation.resource_claim_property_type rcpt ON rcpt.id = rcp.type_id
   JOIN resource_allocation.resource_claim_property_io_type rcpiot ON rcpiot.id = rcp.io_type_id;
ALTER VIEW resource_allocation.resource_claim_property_view
  OWNER TO resourceassignment;
COMMENT ON VIEW resource_allocation.resource_claim_property_view
  IS 'plain view on resource_claim_property table, including resource_claim_property_type.name and resource_claim_property_io_type.name';

CREATE OR REPLACE VIEW resource_monitoring.resource_view AS
  SELECT rv.*,
    rc.available AS available_capacity,
    rc.total - rc.available AS used_capacity,
    rc.total AS total_capacity,
    ra.available AS active
  FROM virtual_instrument.resource_view rv
  LEFT JOIN resource_monitoring.resource_capacity rc ON rc.resource_id = rv.id
  LEFT JOIN resource_monitoring.resource_availability ra ON ra.resource_id = rv.id;
ALTER VIEW resource_monitoring.resource_view
  OWNER TO resourceassignment;
COMMENT ON VIEW resource_monitoring.resource_view
  IS 'view on virtual_instrument.resource_view including availability and capacity';
COMMENT ON COLUMN resource_monitoring.resource_view.available_capacity IS 'This is the current (momentaneous) available capacity of this resource (which is total-used) and has to be set from a monitoring system.';
COMMENT ON COLUMN resource_monitoring.resource_view.used_capacity IS 'This is the current (momentaneous) used capacity of this resource (which is total-available) and has to be set from a monitoring system.';
COMMENT ON COLUMN resource_monitoring.resource_view.total_capacity IS 'This is the total (momentaneous) available capacity of this resource. Usually the total capacity is fixed, but it could change, for example when you add an extra disk.';

CREATE OR REPLACE VIEW resource_monitoring.resource_usage_view AS
  SELECT ru.as_of_timestamp, ru.usage, ru.status_id, rcs.name as status_name, rv.*
  FROM resource_allocation.resource_usage ru
  LEFT JOIN resource_monitoring.resource_view rv ON rv.id = ru.resource_id
  LEFT JOIN resource_allocation.resource_claim_status rcs ON rcs.id = ru.status_id;
ALTER VIEW resource_monitoring.resource_usage_view
  OWNER TO resourceassignment;
COMMENT ON VIEW resource_monitoring.resource_usage_view
  IS 'combined view on resource_monitoring.resource_view and resource_allocation.resource_usage';

CREATE OR REPLACE VIEW resource_allocation.resource_claim_conflict_reason_view AS
  SELECT rccr.id, rccr.resource_claim_id, rccr.conflict_reason_id, rc.resource_id, rc.task_id, cr.reason
    FROM resource_allocation.resource_claim_conflict_reason rccr
    JOIN resource_allocation.conflict_reason cr on cr.id = rccr.conflict_reason_id
    JOIN resource_allocation.resource_claim rc on rc.id = rccr.resource_claim_id;
ALTER VIEW resource_allocation.resource_claim_conflict_reason_view
  OWNER TO resourceassignment;
COMMENT ON VIEW resource_allocation.resource_claim_conflict_reason_view
  IS 'plain view on resource_claim_conflict_reason table including conflict_reason.reason';

CREATE OR REPLACE VIEW resource_allocation.task_conflict_reason_view AS
  SELECT rccr.id, rccr.task_id, rccr.conflict_reason_id, cr.reason
    FROM resource_allocation.task_conflict_reason rccr
    JOIN resource_allocation.conflict_reason cr on cr.id = rccr.conflict_reason_id;
ALTER VIEW resource_allocation.task_conflict_reason_view
  OWNER TO resourceassignment;
COMMENT ON VIEW resource_allocation.task_conflict_reason_view
  IS 'plain view on task_conflict_reason table including conflict_reason.reason';

COMMIT;
