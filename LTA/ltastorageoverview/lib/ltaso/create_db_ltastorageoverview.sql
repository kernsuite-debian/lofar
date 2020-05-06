/*
# Copyright (C) 2012-2015  asTRON (Netherlands Institute for Radio Astronomy)
# P.O. Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This file is part of the LOFAR software suite.
# The LOFAR software suite is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The LOFAR software suite is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with the LOFAR software suite. If not, see <http://www.gnu.org/licenses/>.
*/

-- $Id$

-- postgresql create script for ltastorageoverview database

-- run from command line as:
-- psql ltaso -f create_db_ltastorageoverview.sql -W

-- \set VERBOSITY terse

BEGIN;

DROP SCHEMA IF EXISTS lta CASCADE;
DROP SCHEMA IF EXISTS scraper CASCADE;
DROP SCHEMA IF EXISTS metainfo CASCADE;

CREATE SCHEMA lta;
CREATE SCHEMA scraper;
CREATE SCHEMA metainfo;

-- TABLES

CREATE TABLE lta.site (
    id                  serial,
    name                text UNIQUE NOT NULL,
    url                 text UNIQUE NOT NULL,
    PRIMARY KEY (id)
) WITH (OIDS=FALSE);

CREATE INDEX ss_name_idx on lta.site(name);

CREATE TABLE lta.directory (
    id                  serial,
    name                text NOT NULL,
    parent_dir_id       integer REFERENCES lta.directory ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
    PRIMARY KEY (id),
    UNIQUE (name, parent_dir_id)
) WITH (OIDS=FALSE);

CREATE INDEX d_parent_dir_id_idx on lta.directory(parent_dir_id);
CREATE INDEX d_name_idx on lta.directory(name);

CREATE TABLE lta.directory_closure (
    ancestor_id         integer NOT NULL REFERENCES lta.directory ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
    descendant_id       integer NOT NULL REFERENCES lta.directory ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
    depth               integer NOT NULL,
    primary key (ancestor_id, descendant_id)
) WITH (OIDS=FALSE);

CREATE INDEX dc_ancestor_id_idx on lta.directory_closure(ancestor_id);
CREATE INDEX dc_descendant_id_idx on lta.directory_closure(descendant_id);
CREATE INDEX dc_depth_idx on lta.directory_closure(depth);

CREATE TABLE lta.fileinfo (
    id                  serial,
    name                text NOT NULL,
    size                bigint NOT NULL,
    creation_date       timestamp without time zone NOT NULL,
    dir_id              integer NOT NULL REFERENCES lta.directory ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
    PRIMARY KEY (id),
    UNIQUE (name, dir_id)
) WITH (OIDS=FALSE);

CREATE INDEX fi_dir_id_idx on lta.fileinfo(dir_id);
CREATE INDEX fi_creation_date_idx on lta.fileinfo(creation_date);
CREATE INDEX fi_name_idx on lta.fileinfo(name);

CREATE TABLE lta.site_root_dir (
    site_id       integer NOT NULL REFERENCES lta.site ON DELETE CASCADE DEFERRABLE INITIALLY IMMEDIATE,
    root_dir_id   integer NOT NULL REFERENCES lta.directory ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
    primary key (site_id, root_dir_id)
) WITH (OIDS=FALSE);

CREATE INDEX ssr_site_id_idx on lta.site_root_dir(site_id);
CREATE INDEX ssr_root_dir_id_idx on lta.site_root_dir(root_dir_id);

CREATE TABLE lta.site_quota (
    id                  serial,
    site_id             integer NOT NULL REFERENCES lta.site ON DELETE CASCADE DEFERRABLE INITIALLY IMMEDIATE,
    quota               bigint NOT NULL,
    valid_until_date    timestamp without time zone NOT NULL,
    primary key (id)
) WITH (OIDS=FALSE);

CREATE TABLE lta.quota_root_dirs (
    site_id             integer NOT NULL REFERENCES lta.site ON DELETE CASCADE DEFERRABLE INITIALLY IMMEDIATE,
    root_dir_id         integer NOT NULL REFERENCES lta.directory ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
    primary key (site_id, root_dir_id)
);

CREATE TABLE lta._directory_update_cache (
    dir_id              integer NOT NULL REFERENCES lta.directory ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
    PRIMARY KEY (dir_id)
) WITH (OIDS=FALSE);

CREATE TABLE scraper.last_directory_visit (
    id                  serial,
    dir_id              integer NOT NULL REFERENCES lta.directory ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
    visit_date          timestamp without time zone NOT NULL DEFAULT '1970-01-01',
    PRIMARY KEY (id)
) WITH (OIDS=FALSE);

CREATE INDEX ldv_dir_id_idx on scraper.last_directory_visit(dir_id);
CREATE INDEX ldv_visit_date_idx on scraper.last_directory_visit(visit_date);

CREATE TABLE metainfo.stats (
    id serial,
    dir_id integer NOT NULL REFERENCES lta.directory ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
    dir_num_files integer DEFAULT 0 NOT NULL,
    dir_total_file_size bigint DEFAULT 0 NOT NULL,
    dir_min_file_size bigint DEFAULT 0 NOT NULL,
    dir_max_file_size bigint DEFAULT 0 NOT NULL,
    dir_min_file_creation_date timestamp without time zone DEFAULT NULL,
    dir_max_file_creation_date timestamp without time zone DEFAULT NULL,
    tree_num_files integer DEFAULT 0 NOT NULL,
    tree_total_file_size bigint DEFAULT 0 NOT NULL,
    tree_min_file_size bigint DEFAULT NULL,
    tree_max_file_size bigint DEFAULT NULL,
    tree_min_file_creation_date timestamp without time zone DEFAULT NULL,
    tree_max_file_creation_date timestamp without time zone DEFAULT NULL,
    PRIMARY KEY (id)
);

CREATE INDEX stats_dir_id_idx on metainfo.stats(dir_id);
CREATE INDEX stats_dir_min_file_creation_date_idx on metainfo.stats(dir_min_file_creation_date);
CREATE INDEX stats_dir_max_file_creation_date_idx on metainfo.stats(dir_max_file_creation_date);
CREATE INDEX stats_tree_min_file_creation_date_idx on metainfo.stats(tree_min_file_creation_date);
CREATE INDEX stats_tree_max_file_creation_date_idx on metainfo.stats(tree_max_file_creation_date);

CREATE TABLE metainfo.project (
    id              serial,
    name            text UNIQUE NOT NULL,
    PRIMARY KEY (id)
) WITH (OIDS=FALSE);

CREATE INDEX project_name_idx on metainfo.project(name);

CREATE TABLE metainfo.project_top_level_directory (
    project_id      integer NOT NULL REFERENCES metainfo.project ON DELETE CASCADE DEFERRABLE INITIALLY IMMEDIATE,
    dir_id    integer NOT NULL REFERENCES lta.directory ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
    primary key (project_id, dir_id)
) WITH (OIDS=FALSE);

CREATE INDEX ptld_project_id_idx on metainfo.project_top_level_directory(project_id);
CREATE INDEX ptld_dir_id_idx on metainfo.project_top_level_directory(dir_id);

CREATE TABLE metainfo.observation (
    id              int, -- sas id, like 'L123456', but then as integer, so 123456
    PRIMARY KEY (id)
) WITH (OIDS=FALSE);

CREATE TABLE metainfo.project_observation (
    project_id      integer NOT NULL REFERENCES metainfo.project ON DELETE CASCADE DEFERRABLE INITIALLY IMMEDIATE,
    observation_id  integer NOT NULL REFERENCES metainfo.observation ON DELETE CASCADE DEFERRABLE INITIALLY IMMEDIATE,
    PRIMARY KEY (project_id, observation_id)
) WITH (OIDS=FALSE);

CREATE TABLE metainfo.dataproduct (
    id              serial,
    fileinfo_id     integer NOT NULL REFERENCES lta.fileinfo ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
    observation_id  integer NOT NULL REFERENCES metainfo.observation ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
    name            text NOT NULL,
    PRIMARY KEY (id)
) WITH (OIDS=FALSE);

CREATE INDEX dp_dataproduct_name_idx on metainfo.dataproduct(name);
CREATE INDEX dp_fileinfo_id_idx on metainfo.dataproduct(fileinfo_id);

-- END TABLES


-- TRIGGERS

CREATE OR REPLACE FUNCTION lta.on_site_root_dir_deleted_do_delete_directory()
RETURNS trigger AS
$BODY$
BEGIN
    DELETE FROM lta.directory WHERE id = OLD.root_dir_id;
    RETURN OLD;
END;
$BODY$
LANGUAGE plpgsql VOLATILE
COST 100;

CREATE TRIGGER trigger_on_site_root_dir_deleted_do_delete_directory
AFTER DELETE
ON lta.site_root_dir
FOR EACH ROW
EXECUTE PROCEDURE lta.on_site_root_dir_deleted_do_delete_directory();

--------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION lta.on_directory_inserted_add_directory_closure_entry()
RETURNS trigger AS
$BODY$
BEGIN
 INSERT INTO lta.directory_closure (ancestor_id, descendant_id, depth) values (NEW.id, NEW.id, 0) ;

 INSERT INTO lta.directory_closure (ancestor_id, descendant_id, depth)
     SELECT p.ancestor_id, c.descendant_id, p.depth+c.depth+1
     FROM lta.directory_closure p, lta.directory_closure c
     WHERE p.descendant_id=new.parent_dir_id AND c.ancestor_id=new.id ;

 RETURN NEW;
END;
$BODY$
LANGUAGE plpgsql VOLATILE
COST 100;

CREATE TRIGGER trigger_on_directory_inserted_add_directory_closure_entry
AFTER INSERT
ON lta.directory
FOR EACH ROW
EXECUTE PROCEDURE lta.on_directory_inserted_add_directory_closure_entry();

--------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION scraper.on_directory_inserted_add_last_directory_visit_entry()
RETURNS trigger AS
$BODY$
BEGIN
    --RAISE NOTICE 'on_directory_inserted_add_last_directory_visit_entry, NEW=%', NEW;
    --postgres < 9.5 way of doing INSERT...ON CONFLICT DO NOTHING
    INSERT INTO scraper.last_directory_visit(dir_id)
    (SELECT NEW.id WHERE NOT EXISTS (SELECT dir_id FROM scraper.last_directory_visit WHERE dir_id = NEW.id));

    RETURN NEW;
END;
$BODY$
LANGUAGE plpgsql VOLATILE
COST 100;

CREATE TRIGGER trigger_on_directory_inserted_add_last_directory_visit_entry
AFTER INSERT
ON lta.directory
FOR EACH ROW
EXECUTE PROCEDURE scraper.on_directory_inserted_add_last_directory_visit_entry();

--------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION scraper.on_site_root_dir_inserted_do_add_to_quota_root_dirs()
RETURNS trigger AS
$BODY$
BEGIN
    -- by default, add each root directory as 'directory under quota'
    -- users can remove them by hand
    INSERT INTO lta.quota_root_dirs(site_id, root_dir_id)
    VALUES (NEW.site_id, NEW.root_dir_id);

 RETURN NEW;
END;
$BODY$
LANGUAGE plpgsql VOLATILE
COST 100;

CREATE TRIGGER trigger_on_site_root_dir_inserted_do_add_to_quota_root_dirs
AFTER INSERT
ON lta.site_root_dir
FOR EACH ROW
EXECUTE PROCEDURE scraper.on_site_root_dir_inserted_do_add_to_quota_root_dirs();

--------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION metainfo.on_directory_inserted_add_stats_entry()
RETURNS trigger AS
$BODY$
BEGIN
    --RAISE NOTICE 'on_directory_inserted_add_stats_entry, NEW=%', NEW;
    INSERT INTO metainfo.stats(dir_id) values (NEW.id);

    -- always trim trailing slashes from dirname
    NEW.name := trim(trailing '/' from NEW.name);

    RETURN NEW;
END;
$BODY$
LANGUAGE plpgsql VOLATILE
COST 100;

CREATE TRIGGER trigger_on_directory_inserted_add_stats_entry
BEFORE INSERT
ON lta.directory
FOR EACH ROW
EXECUTE PROCEDURE metainfo.on_directory_inserted_add_stats_entry();

--------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION metainfo.on_fileinfo_insert_update_delete_store_in_cache()
RETURNS trigger AS
$BODY$
BEGIN
    IF TG_OP = 'DELETE' THEN
        INSERT INTO lta._directory_update_cache (dir_id) VALUES (OLD.dir_id);
        RETURN OLD;
    END IF;

    --postgres < 9.5 way of doing INSERT...ON CONFLICT DO NOTHING
    INSERT INTO lta._directory_update_cache (dir_id)
    (SELECT NEW.dir_id WHERE NOT EXISTS (SELECT dir_id FROM lta._directory_update_cache WHERE dir_id = NEW.dir_id));

    RETURN NEW;
END;
$BODY$
LANGUAGE plpgsql VOLATILE
COST 100;

CREATE TRIGGER trigger_on_fileinfo_insert_update_delete_store_in_cache
AFTER INSERT OR UPDATE OR DELETE
ON lta.fileinfo
FOR EACH ROW
EXECUTE PROCEDURE metainfo.on_fileinfo_insert_update_delete_store_in_cache();

--------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION metainfo.on_directory_update_cache_commit_do_update_dir_stats()
RETURNS trigger AS
$BODY$
DECLARE
    fileinfo_row lta.fileinfo%ROWTYPE;
    _dir_id integer;
    _dir_num_files bigint;
    _dir_total_file_size bigint;
    _dir_min_file_size bigint;
    _dir_max_file_size bigint;
    _dir_min_file_creation_date timestamp without time zone;
    _dir_max_file_creation_date timestamp without time zone;
BEGIN
    FOR _dir_id in (SELECT DISTINCT(c.dir_id) FROM lta._directory_update_cache c) LOOP
        _dir_num_files := 0;
        _dir_total_file_size := 0;
        _dir_min_file_size := NULL;
        _dir_max_file_size := NULL;

        -- aggregate results
        FOR fileinfo_row IN (SELECT * FROM lta.fileinfo fi where fi.dir_id = _dir_id) LOOP
            _dir_num_files := _dir_num_files + 1;
            _dir_total_file_size := _dir_total_file_size + fileinfo_row.size;
            _dir_min_file_size := LEAST(_dir_min_file_size, fileinfo_row.size);
            _dir_max_file_size := GREATEST(_dir_max_file_size, fileinfo_row.size);
            _dir_min_file_creation_date := LEAST(_dir_min_file_creation_date, fileinfo_row.creation_date);
            _dir_max_file_creation_date := GREATEST(_dir_max_file_creation_date, fileinfo_row.creation_date);
        END LOOP;

        UPDATE metainfo.stats
        SET (dir_num_files, dir_total_file_size, dir_min_file_size, dir_max_file_size, dir_min_file_creation_date, dir_max_file_creation_date) =
            (_dir_num_files, _dir_total_file_size, _dir_min_file_size, _dir_max_file_size, _dir_min_file_creation_date, _dir_max_file_creation_date)
        WHERE dir_id = _dir_id;

        DELETE FROM lta._directory_update_cache WHERE dir_id = _dir_id;
    END LOOP;

    RETURN NULL;
END;
$BODY$
LANGUAGE plpgsql VOLATILE
COST 100;

-- use DEFERRABLE INITIALLY DEFERRED CONSTRAINT trigger which fires only once upon committing the file inserts
-- then run method on_directory_update_cache_commit_do_update_dir_stats to collect all inserted fileinfo's into dir/tree stats
CREATE CONSTRAINT TRIGGER trigger_on_directory_update_cache_commit_do_update_dir_stats
AFTER INSERT
ON lta._directory_update_cache
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW
EXECUTE PROCEDURE metainfo.on_directory_update_cache_commit_do_update_dir_stats();

--------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION metainfo.on_dir_stats_update_do_update_tree_stats()
RETURNS trigger AS
$BODY$
DECLARE
    stats_row metainfo.stats%ROWTYPE;
BEGIN
    -- initialize the NEW.tree_* variables with this dir's dir_stats...
    NEW.tree_num_files := NEW.dir_num_files;
    NEW.tree_total_file_size := NEW.dir_total_file_size;
    NEW.tree_min_file_size := NEW.dir_min_file_size;
    NEW.tree_max_file_size := NEW.dir_max_file_size;
    NEW.tree_min_file_creation_date := NEW.dir_min_file_creation_date;
    NEW.tree_max_file_creation_date := NEW.dir_max_file_creation_date;

    -- loop over the tree stats from all filled subdirs of this directory
    -- and aggregate them to the new_tree_* variables
    FOR stats_row IN SELECT st.* FROM metainfo.stats st
                     INNER JOIN lta.directory dir ON dir.id = st.dir_id
                     WHERE dir.parent_dir_id = NEW.dir_id
                     AND tree_max_file_creation_date IS NOT NULL    
                     AND dir_max_file_creation_date IS NOT NULL LOOP

        -- aggregate
        NEW.tree_num_files := NEW.tree_num_files + stats_row.tree_num_files;
        NEW.tree_total_file_size := NEW.tree_total_file_size + stats_row.tree_total_file_size;
        NEW.tree_min_file_size := LEAST(NEW.tree_min_file_size, stats_row.tree_min_file_size);
        NEW.tree_max_file_size := GREATEST(NEW.tree_max_file_size, stats_row.tree_max_file_size);
        NEW.tree_min_file_creation_date := LEAST(NEW.tree_min_file_creation_date, stats_row.tree_min_file_creation_date);
        NEW.tree_max_file_creation_date := GREATEST(NEW.tree_max_file_creation_date, stats_row.tree_max_file_creation_date);
    END LOOP;

    -- return the NEW row with the updated tree_* variables
    RETURN NEW;
END;
$BODY$
LANGUAGE plpgsql VOLATILE
COST 100;

CREATE TRIGGER trigger_on_dir_stats_update_do_update_tree_stats
BEFORE UPDATE OF dir_num_files, dir_total_file_size, dir_min_file_size, dir_max_file_size, dir_min_file_creation_date, dir_max_file_creation_date
ON metainfo.stats
FOR EACH ROW
EXECUTE PROCEDURE metainfo.on_dir_stats_update_do_update_tree_stats();

--------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION metainfo.on_stats_update_do_update_parents_tree_stats()
RETURNS trigger AS
$BODY$
DECLARE
    stats_row metainfo.stats%ROWTYPE;
    parent_stats_row metainfo.stats%ROWTYPE;
    new_tree_num_files bigint;
    new_tree_total_file_size bigint;
    new_tree_min_file_size bigint;
    new_tree_max_file_size bigint;
    new_tree_min_file_creation_date timestamp without time zone;
    new_tree_max_file_creation_date timestamp without time zone;
BEGIN
    -- climb up the tree until at root, start with the first direct parent
    SELECT st.* FROM metainfo.stats st
    INNER JOIN lta.directory dir on dir.parent_dir_id = st.dir_id
    WHERE dir.id = NEW.dir_id
    LIMIT 1
    INTO parent_stats_row;

    --loop and climb further up the tree until at root
    WHILE parent_stats_row.id IS NOT NULL LOOP
        -- initialize all new_tree_* vars with the current parent_stats_row's values or 0/null.
        new_tree_num_files := GREATEST(0, parent_stats_row.dir_num_files);
        new_tree_total_file_size := GREATEST(0, parent_stats_row.dir_total_file_size);
        new_tree_min_file_size := parent_stats_row.tree_min_file_size;
        new_tree_max_file_size := parent_stats_row.tree_max_file_size;
        new_tree_min_file_creation_date := parent_stats_row.tree_min_file_creation_date;
        new_tree_max_file_creation_date := parent_stats_row.tree_max_file_creation_date;

        -- loop over the tree stats from all filled subdirs of the parent's directory
        -- and aggregate them to the new_tree_* variables
        FOR stats_row in SELECT st.* FROM metainfo.stats st
                         INNER JOIN lta.directory dir ON dir.id = st.dir_id
                         WHERE dir.parent_dir_id = parent_stats_row.dir_id LOOP

            -- aggregate
            new_tree_num_files := new_tree_num_files + stats_row.tree_num_files;
            new_tree_total_file_size := new_tree_total_file_size + stats_row.tree_total_file_size;
            new_tree_min_file_size := LEAST(new_tree_min_file_size, stats_row.tree_min_file_size);
            new_tree_max_file_size := GREATEST(new_tree_max_file_size, stats_row.tree_max_file_size);
            new_tree_min_file_creation_date := LEAST(new_tree_min_file_creation_date, stats_row.tree_min_file_creation_date);
            new_tree_max_file_creation_date := GREATEST(new_tree_max_file_creation_date, stats_row.tree_max_file_creation_date);
        END LOOP;

        -- and update the parent stats row with the aggregated results
        UPDATE metainfo.stats stats
        SET (tree_num_files, tree_total_file_size, tree_min_file_size, tree_max_file_size, tree_min_file_creation_date, tree_max_file_creation_date) =
            (new_tree_num_files, new_tree_total_file_size, new_tree_min_file_size, new_tree_max_file_size, new_tree_min_file_creation_date, new_tree_max_file_creation_date)
        WHERE stats.dir_id = parent_stats_row.dir_id;

        -- climb the tree by selecting the parent's parent, and loop again.
        SELECT st.* FROM metainfo.stats st
        INNER JOIN lta.directory dir on dir.parent_dir_id = st.dir_id
        WHERE dir.id = parent_stats_row.dir_id
        LIMIT 1
        INTO parent_stats_row;
    END LOOP;

    RETURN NEW;
END;
$BODY$
LANGUAGE plpgsql VOLATILE
COST 100;

CREATE TRIGGER trigger_on_stats_update_do_update_parents_tree_stats
AFTER UPDATE OF dir_num_files, dir_total_file_size, dir_min_file_size, dir_max_file_size, dir_min_file_creation_date, dir_max_file_creation_date
ON metainfo.stats
FOR EACH ROW
EXECUTE PROCEDURE metainfo.on_stats_update_do_update_parents_tree_stats();

--------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION lta.on_directory_inserted_parse_project_info()
RETURNS trigger AS
$BODY$
DECLARE
    project_pos int;
    next_slash_pos int;
    new_dir_name text;
    dir_name_tail text;
    new_project_name text;
    new_project_id int;
    project_dir_name text;
    project_dir_id int;
    obs_id int;
    obs_dir_name text;
BEGIN
    new_dir_name := trim(trailing '/' from NEW.name);
    project_pos := strpos(new_dir_name, '/projects');

    IF project_pos > 0 THEN
     dir_name_tail := substring(new_dir_name from project_pos + 10);
     IF length(dir_name_tail) > 0 THEN
         next_slash_pos := strpos(dir_name_tail, '/');
         IF next_slash_pos > 0 THEN
             new_project_name := substring(dir_name_tail from 0 for next_slash_pos);
         ELSE
             new_project_name := dir_name_tail;
         END IF;

         IF length(new_project_name) > 0 THEN
             --postgres < 9.5 way of doing INSERT...ON CONFLICT DO NOTHING
             INSERT INTO metainfo.project(name)
             (SELECT new_project_name WHERE NOT EXISTS (SELECT name FROM metainfo.project WHERE name = new_project_name));

             SELECT id FROM metainfo.project WHERE name = new_project_name LIMIT 1 INTO new_project_id;

             IF new_project_id IS NOT NULL THEN
                 IF next_slash_pos > 0 THEN
                     project_dir_name := substring(new_dir_name from 0 for project_pos + 10 + next_slash_pos - 1);
                 ELSE
                     project_dir_name := new_dir_name;
                 END IF;

                 IF project_dir_name = new_dir_name THEN
                     --postgres < 9.5 way of doing INSERT...ON CONFLICT DO NOTHING
                     INSERT INTO metainfo.project_top_level_directory(project_id, dir_id)
                     (SELECT new_project_id, NEW.id WHERE NOT EXISTS (SELECT ptld.project_id, ptld.dir_id FROM metainfo.project_top_level_directory ptld WHERE ptld.project_id = new_project_id AND ptld.dir_id = NEW.id));
                 ELSE
                     dir_name_tail := substring(dir_name_tail from length(new_project_name)+2);
                     next_slash_pos := strpos(dir_name_tail, '/');
                     IF next_slash_pos > 0 THEN
                         obs_dir_name := substring(dir_name_tail from 0 for next_slash_pos);
                     ELSE
                         obs_dir_name := dir_name_tail;
                     END IF;
                         BEGIN
                             obs_id := obs_dir_name::integer;

                             --postgres < 9.5 way of doing INSERT...ON CONFLICT DO NOTHING
                             INSERT INTO metainfo.observation(id)
                             (SELECT obs_id WHERE NOT EXISTS (SELECT id FROM metainfo.observation WHERE id = obs_id));

                             --postgres < 9.5 way of doing INSERT...ON CONFLICT DO NOTHING
                             INSERT INTO metainfo.project_observation(project_id, observation_id)
                             (SELECT new_project_id, obs_id WHERE NOT EXISTS (SELECT project_id, observation_id FROM metainfo.project_observation WHERE project_id = new_project_id AND observation_id = obs_id));
                         EXCEPTION WHEN invalid_text_representation THEN
                         END;
                 END IF;
             END IF;
         END IF;
     END IF;
    END IF;

    RETURN NEW;
END;
$BODY$
LANGUAGE plpgsql VOLATILE
COST 100;

CREATE TRIGGER trigger_on_directory_inserted_parse_project_info
AFTER INSERT
ON lta.directory
FOR EACH ROW
EXECUTE PROCEDURE lta.on_directory_inserted_parse_project_info();

--------------------------------------------------------------------------------

 CREATE OR REPLACE FUNCTION lta.on_fileinfo_inserted_parse_observation_info()
   RETURNS trigger AS
 $BODY$
 DECLARE
 new_file_name text;
 L_pos int;
 first_underscore_pos int;
 first_dot_pos int;
 obs_id int;
 dataproduct_name text;
 BEGIN
     new_file_name := trim(leading '/' from NEW.name);
     L_pos := strpos(new_file_name, 'L');
     first_underscore_pos := strpos(new_file_name, '_');
     IF L_pos > 0 AND first_underscore_pos > L_pos THEN
         BEGIN
                 obs_id := substring(new_file_name from L_pos+1 for first_underscore_pos-2)::integer;

                 --postgres < 9.5 way of doing INSERT...ON CONFLICT DO NOTHING
                 INSERT INTO metainfo.observation(id)
                 (SELECT obs_id WHERE NOT EXISTS (SELECT id FROM metainfo.observation WHERE id = obs_id));

                 first_dot_pos := strpos(new_file_name, '.');
                 IF first_dot_pos > L_pos THEN
                         dataproduct_name := substring(new_file_name from L_pos for first_dot_pos-1);

                         --postgres < 9.5 way of doing INSERT...ON CONFLICT DO NOTHING
                         INSERT INTO metainfo.dataproduct(fileinfo_id, observation_id, name)
                         (SELECT NEW.id, obs_id, dataproduct_name WHERE NOT EXISTS (SELECT fileinfo_id, observation_id, name FROM metainfo.dataproduct WHERE fileinfo_id = NEW.id AND observation_id = obs_id AND name = dataproduct_name));
                 END IF;

         EXCEPTION WHEN invalid_text_representation THEN
         END;
     END IF;
     RETURN NEW;
 END;
 $BODY$
   LANGUAGE plpgsql VOLATILE
   COST 100;

CREATE TRIGGER trigger_on_fileinfo_inserted_parse_observation_info
   AFTER INSERT
   ON lta.fileinfo
   FOR EACH ROW
   EXECUTE PROCEDURE lta.on_fileinfo_inserted_parse_observation_info();

-- END TRIGGERS


-- BEGIN NORMAL FUNCTIONS

--TODO: this method get_tree_stats is recursive (it calls itself), which is notoriously slow in sql. rewrite method to use WITH RECURSIVE statements, see https://www.postgresql.org/docs/9.3/static/queries-with.html
CREATE OR REPLACE FUNCTION metainfo.get_tree_stats(tree_root_dir_id integer, lower_ts timestamp without time zone DEFAULT NULL, upper_ts timestamp without time zone DEFAULT NULL,
                                                   OUT dir_id integer, OUT tree_num_files bigint, OUT tree_total_file_size bigint)
RETURNS record AS $$
DECLARE
    stats_row metainfo.stats%ROWTYPE;
    dir_num_files bigint;
    dir_total_file_size bigint;
    subdir_tree_num_files bigint;
    subdir_tree_total_file_size bigint;
    subdirs_tree_num_files bigint;
    subdirs_tree_total_file_size bigint;
    rec record;
BEGIN
    -- we need to provide the requested tree_root_dir_id also as an output, so we can join on it
    dir_id := tree_root_dir_id;

    -- check for valid lower_ts/upper_ts
    IF lower_ts IS NULL THEN
        lower_ts := '-infinity';
    END IF;
    IF upper_ts IS NULL THEN
        upper_ts := 'infinity';
    END IF;

    SELECT st.* FROM metainfo.stats st
    WHERE st.dir_id = tree_root_dir_id
    LIMIT 1
    INTO stats_row;

    -- directory has no tree stats. So return 0,0
    IF stats_row.tree_min_file_creation_date IS NULL OR stats_row.tree_max_file_creation_date IS NULL THEN
        tree_num_files := 0;
        tree_total_file_size := 0;
        RETURN;
    END IF;


    -- the tree stats of this directory have no overlap at all for the requested timerange
    IF (stats_row.tree_min_file_creation_date > upper_ts) OR (stats_row.tree_max_file_creation_date < lower_ts) THEN
        tree_num_files := 0;
        tree_total_file_size := 0;
        RETURN;
    END IF;

    -- the tree stats of this directory have full overlap the requested timerange
    IF stats_row.tree_min_file_creation_date >= lower_ts AND stats_row.tree_max_file_creation_date <= upper_ts THEN
        tree_num_files := stats_row.tree_num_files;
        tree_total_file_size := stats_row.tree_total_file_size;
        RETURN;
    END IF;

    -- the tree stats of this directory have partial overlap the requested timerange
    -- recurse into subdirectories, and accumulate subdir results
    IF stats_row.tree_min_file_creation_date <= upper_ts OR stats_row.tree_max_file_creation_date >= lower_ts THEN
        --sum all results from the subdirs which have at least partial overlap
        subdirs_tree_num_files := 0;
        subdirs_tree_total_file_size := 0;

        -- TODO: replace slow for loop with recursive query
        FOR rec in (SELECT * FROM lta.directory d WHERE d.parent_dir_id = tree_root_dir_id) LOOP
            SELECT gts.tree_num_files, gts.tree_total_file_size
            FROM metainfo.get_tree_stats(rec.id, lower_ts, upper_ts) gts
            INTO subdir_tree_num_files, subdir_tree_total_file_size;

            subdirs_tree_num_files := subdirs_tree_num_files + subdir_tree_num_files;
            subdirs_tree_total_file_size := subdirs_tree_total_file_size + subdir_tree_total_file_size;
        END LOOP;

        -- and add the num_files and total_file_size in this dir...
        IF stats_row.dir_num_files > 0 THEN
            IF stats_row.dir_min_file_creation_date >= lower_ts AND stats_row.dir_max_file_creation_date <= upper_ts THEN
                -- all files in this dir are in the requested time range
                -- when 'all files'=0, that's ok, cause then dir_num_files and dir_total_file_size are 0 which is the answer we need
                dir_num_files := stats_row.dir_num_files;
                dir_total_file_size := stats_row.dir_total_file_size;
            ELSE
                -- some files in this dir are in the requested time range
                -- make selection of files in this dir in the requested time range
                SELECT COUNT(fi.id), SUM(fi.size) FROM lta.fileinfo fi
                WHERE fi.dir_id = tree_root_dir_id
                AND fi.creation_date >= lower_ts AND fi.creation_date <= upper_ts
                INTO dir_num_files, dir_total_file_size;
            END IF;

            IF dir_num_files IS NULL OR dir_num_files = 0 THEN
                dir_total_file_size := 0;
            END IF;
        ELSE
            dir_num_files := 0;
            dir_total_file_size := 0;
        END IF;

        tree_num_files := subdirs_tree_num_files + dir_num_files;
        tree_total_file_size := subdirs_tree_total_file_size + dir_total_file_size;

        RETURN;
    END IF;

    --this should never occur
    RAISE EXCEPTION 'metainfo.get_tree_stats could not find no/partial/full overlap';
END;
$$ LANGUAGE plpgsql;


--TODO: this method get_site_stats calls the recursive get_tree_stats methods, which needs a rewrite. After that, it is quite likely that this method also performs way faster.
CREATE OR REPLACE FUNCTION metainfo.get_site_stats(_site_id integer, lower_ts timestamp without time zone DEFAULT NULL::timestamp without time zone, upper_ts timestamp without time zone DEFAULT NULL::timestamp without time zone,
                                                   OUT tree_num_files bigint, OUT tree_total_file_size bigint)
  RETURNS record AS $$
BEGIN
    SELECT SUM(gts.tree_num_files), SUM(gts.tree_total_file_size)
    FROM lta.site_root_dir srd, metainfo.get_tree_stats(srd.root_dir_id, lower_ts, upper_ts) gts
    WHERE srd.site_id = _site_id
    INTO tree_num_files, tree_total_file_size;

    IF tree_num_files IS NULL THEN
        tree_num_files := 0;
    END IF;

    IF tree_total_file_size IS NULL THEN
        tree_total_file_size := 0;
    END IF;
END;
$$ LANGUAGE plpgsql;



--TODO: see remarks at get_site_stats and get_tree_stats for optimizations.
CREATE OR REPLACE FUNCTION metainfo.get_site_quota_usage(_site_quota_id integer, OUT site_id integer, OUT site_name text, OUT quota bigint, OUT total_file_size bigint, OUT space_left bigint, OUT num_files bigint, OUT valid_until_date timestamp without time zone)
  RETURNS record AS $$
BEGIN
    SELECT s.id, s.name, sq.quota, sq.valid_until_date
    FROM lta.site_quota sq
    JOIN lta.site s on s.id = sq.site_id
    WHERE sq.id = _site_quota_id
    LIMIT 1
    INTO site_id, site_name, quota, valid_until_date;

    SELECT gts.tree_total_file_size, gts.tree_num_files
    FROM metainfo.get_site_stats(site_id, NULL, valid_until_date) gts
    LIMIT 1
    INTO total_file_size, num_files;

    space_left := quota - total_file_size;
END;
$$ LANGUAGE plpgsql;

--TODO: see remarks at get_site_stats and get_tree_stats for optimizations.
-- WARNING: SLOW!! Needs to be replaced by recursive select statements
CREATE OR REPLACE FUNCTION metainfo.get_sites_quota_usage(OUT site_id integer, OUT site_name text, OUT site_quota_id integer, OUT quota bigint, OUT total_file_size bigint, OUT space_left bigint, OUT num_files bigint, OUT valid_until_date timestamp without time zone)
  RETURNS SETOF record AS $$
DECLARE rec record;
BEGIN
    FOR rec in SELECT * FROM lta.site_quota LOOP
        SELECT rec.id INTO site_quota_id;
        SELECT squ.site_id, squ.site_name, squ.quota, squ.total_file_size, squ.space_left, squ.num_files, squ.valid_until_date
        FROM metainfo.get_site_quota_usage(site_quota_id) squ
        INTO site_id, site_name, quota, total_file_size, space_left, num_files, valid_until_date;
        RETURN NEXT;
    END LOOP;
END;
$$ LANGUAGE plpgsql;



-- END NORMAL FUNCTIONS

--
--
-- -- VIEWS

CREATE OR REPLACE VIEW lta.site_root_directory as
 select ss.id as site_id, ss.name as site_name, srd.root_dir_id, dir.name as dir_name
     from lta.site_root_dir srd
     join lta.directory dir on dir.id = srd.root_dir_id
     join lta.site ss on ss.id = srd.site_id ;

CREATE OR REPLACE VIEW lta.site_quota_view as
 select ss.id as site_id, ss.name as site_name, ssq.id as site_quota_id, ssq.quota, ssq.valid_until_date
     from lta.site ss
     join lta.site_quota ssq on ssq.site_id = ss.id;

CREATE OR REPLACE VIEW lta.site_quota_root_directory as
    SELECT s.id AS site_id, s.name AS site_name, d.id AS dir_id, d.name AS dir_name
    FROM lta.quota_root_dirs qrd
    JOIN lta.site s ON s.id = qrd.site_id
    JOIN lta.directory d ON d.id = qrd.root_dir_id;

CREATE OR REPLACE VIEW lta.site_directory_tree as
 select rd.site_id as site_id,
     rd.site_name as site_name,
     rd.root_dir_id as root_dir_id,
     rd.dir_name as root_dir_name,
     dir.id as dir_id,
     dir.name as dir_name,
     dir.parent_dir_id as parent_dir_id,
     dc.depth as depth
     from lta.site_root_directory rd
     inner join lta.directory_closure dc on dc.ancestor_id = rd.root_dir_id
     inner join lta.directory dir on dc.descendant_id = dir.id;

CREATE OR REPLACE VIEW scraper.site_scraper_last_directory_visit as
 select rd.site_id as site_id,
     rd.site_name as site_name,
     dir.id as dir_id,
     dir.name as dir_name,
     sldv.visit_date as last_visit
     from lta.site_root_directory rd
     inner join lta.directory_closure dc on dc.ancestor_id = rd.root_dir_id
     inner join lta.directory dir on dc.descendant_id = dir.id
     inner join scraper.last_directory_visit sldv on sldv.dir_id = dir.id ;

CREATE OR REPLACE VIEW lta.site_directory_file as
 select site.id as site_id,
     site.name as site_name,
     dir.id as dir_id,
     dir.name as dir_name,
     fileinfo.id as file_id,
     fileinfo.name as file_name,
     fileinfo.size as file_size,
     fileinfo.creation_date as file_creation_date
     from lta.site site
     join lta.site_root_dir srd on srd.site_id = site.id
     inner join lta.directory_closure dc on dc.ancestor_id = srd.root_dir_id
     inner join lta.directory dir on dc.descendant_id = dir.id
     inner join lta.fileinfo on fileinfo.dir_id = dir.id ;

CREATE OR REPLACE VIEW metainfo.project_directory as
     select
         project.id as project_id,
         project.name as project_name,
         dir.id as dir_id,
         dir.name as dir_name
         from metainfo.project_top_level_directory ptld
         inner join metainfo.project on project.id = ptld.project_id
         inner join lta.directory_closure dc on dc.ancestor_id = ptld.dir_id
         inner join lta.directory dir on dc.descendant_id = dir.id ;

CREATE OR REPLACE VIEW metainfo.site_directory_stats as
 select sdt.site_id,
     sdt.site_name,
     sdt.dir_id,
     sdt.dir_name,
     st.dir_num_files,
     st.dir_total_file_size,
     st.dir_min_file_size,
     st.dir_max_file_size,
     st.dir_min_file_creation_date,
     st.dir_max_file_creation_date,
     st.tree_num_files,
     st.tree_total_file_size,
     st.tree_min_file_size,
     st.tree_max_file_size,
     st.tree_min_file_creation_date,
     st.tree_max_file_creation_date
     from lta.site_directory_tree sdt
     left join metainfo.stats st on st.dir_id = sdt.dir_id;

CREATE OR REPLACE VIEW metainfo.project_directory_stats AS
    SELECT pd.project_id, pd.project_name, sds.*
    FROM metainfo.project_directory pd
    JOIN metainfo.site_directory_stats sds ON sds.dir_id = pd.dir_id;

CREATE OR REPLACE VIEW metainfo.observation_dataproduct_file as
  SELECT sdf.site_id, sdf.site_name, dp.observation_id, dp.id as dataproduct_id, dp.name as dataproduct_name, sdf.dir_id, sdf.dir_name, sdf.file_id, sdf.file_name, sdf.file_size, sdf.file_creation_date
  FROM metainfo.dataproduct dp
    JOIN lta.site_directory_file sdf ON sdf.file_id = dp.fileinfo_id;

CREATE OR REPLACE VIEW metainfo.project_observation_dataproduct as
  SELECT p.id AS project_id,
     p.name AS project_name,
     dp.observation_id,
     dp.id AS dataproduct_id,
     dp.name AS dataproduct_name,
     dp.fileinfo_id AS fileinfo_id
    FROM metainfo.dataproduct dp
      INNER JOIN metainfo.project_observation po ON po.observation_id = dp.observation_id
      INNER JOIN metainfo.project p ON p.id = po.project_id;

CREATE OR REPLACE VIEW metainfo.dataproduct_all as
  SELECT pod.*, sdf.*
    FROM metainfo.project_observation_dataproduct pod
      INNER JOIN lta.site_directory_file sdf on sdf.file_id = pod.fileinfo_id;

CREATE OR REPLACE VIEW metainfo.site_project_stats as
     select ptld.project_id, p.name as project_name, site_id, site_name, sds.dir_id, sds.dir_name, tree_num_files, tree_total_file_size, tree_min_file_creation_date, tree_max_file_creation_date
     from metainfo.project_top_level_directory ptld
     inner join metainfo.project p on p.id = ptld.project_id
     inner join metainfo.site_directory_stats sds on sds.dir_id = ptld.dir_id
     where tree_num_files IS NOT NULL;

CREATE OR REPLACE VIEW metainfo.project_stats AS
	SELECT project_id, project_name, COUNT(site_id) num_sites, SUM(tree_num_files) total_num_files, SUM(tree_total_file_size) total_file_size, MIN(tree_min_file_creation_date) min_file_creation_date, MAX(tree_max_file_creation_date) max_file_creation_date
	FROM metainfo.site_project_stats
	group by project_id, project_name;

CREATE OR REPLACE VIEW metainfo.site_project_observation_dataproduct_dir_file AS
    SELECT sdf.site_id, sdf.site_name, pod.project_id, pod.project_name, pod.observation_id, pod.dataproduct_id, pod.dataproduct_name, sdf.dir_id, sdf.dir_name, sdf.file_id, sdf.file_name, sdf.file_size, sdf.file_creation_date
    FROM metainfo.project_observation_dataproduct pod
    JOIN lta.site_directory_file sdf ON sdf.file_id = pod.fileinfo_id;

CREATE OR REPLACE VIEW metainfo.site_root_dir_tree_stats AS
    SELECT srd.site_id, srd.site_name, srd.root_dir_id as root_dir_id, srd.dir_name as root_dir_name,
    sds.tree_num_files, sds.tree_total_file_size, sds.tree_min_file_size, sds.tree_max_file_size, sds.tree_min_file_creation_date, sds.tree_max_file_creation_date
    FROM lta.site_root_directory srd
    INNER JOIN metainfo.site_directory_stats sds ON sds.dir_id = srd.root_dir_id;

CREATE OR REPLACE VIEW metainfo.site_stats as
    SELECT site_id, site_name, SUM(tree_num_files) total_num_files, SUM(tree_total_file_size) total_file_size, MIN(tree_min_file_size) min_file_size, MAX(tree_max_file_size) max_file_size, MIN(tree_min_file_creation_date) min_file_creation_date, MAX(tree_max_file_creation_date) max_file_creation_date
    from metainfo.site_root_dir_tree_stats
    group by site_id, site_name;

-- WARNING: SLOW!! Needs to be replaced by recursive select statements
CREATE OR REPLACE VIEW metainfo.site_quota_usage AS
  select * from metainfo.get_sites_quota_usage();

CREATE OR REPLACE VIEW metainfo.site_quota_root_dir_stats AS
    SELECT sds.site_id, sds.site_name, sds.dir_id, sds.dir_name, sds.tree_num_files, sds.tree_total_file_size
    FROM lta.quota_root_dirs qrd
    INNER JOIN metainfo.site_directory_stats sds on sds.dir_id = qrd.root_dir_id;


-- END VIEWS

COMMIT;
