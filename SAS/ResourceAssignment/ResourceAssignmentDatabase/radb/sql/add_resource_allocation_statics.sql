-- resourceassignment password for testing on mcu005 is the same as the password on the president's luggage +6
-- psql resourceassignment -U resourceassignment -f add_resource_allocation_statics.sql -W
BEGIN;


-- General Warning: if you change any of these values, make sure you update the hardcoded values in add_functions_and_triggers.sql too.
INSERT INTO resource_allocation.task_status VALUES (200, 'prepared'), (300, 'approved'), (320, 'on_hold'), (335, 'conflict'),
(350, 'prescheduled'), (400, 'scheduled'), (500, 'queued'), (600, 'active'), (900, 'completing'), (1000, 'finished'), (1100, 'aborted'),
(1150, 'error'), (1200, 'obsolete'); -- This is the list from OTDB, we'll need to merge it with the list from MoM in the future, might use different indexes?
INSERT INTO resource_allocation.task_type VALUES (0, 'observation'),(1, 'pipeline'),(2, 'reservation'); -- We'll need more types
INSERT INTO resource_allocation.resource_claim_status VALUES (0, 'tentative'), (1, 'claimed'), (2, 'conflict');
INSERT INTO resource_allocation.resource_claim_property_type VALUES (0, 'nr_of_is_files'),(1, 'nr_of_cs_files'),(2, 'nr_of_uv_files'),(3, 'nr_of_im_files'),(4, 'nr_of_img_files'),/*(5, 'nr_of_pulp_files'),unused duplicate #10869*/(6, 'nr_of_cs_stokes'),(7, 'nr_of_is_stokes'),(8, 'is_file_size'),(9, 'cs_file_size'),(10, 'uv_file_size'),(11, 'im_file_size'),(12, 'img_file_size'),(13, 'nr_of_pulp_files'),(14, 'nr_of_cs_parts'),(15, 'start_sb_nr'),(16,'uv_otdb_id'),(17,'cs_otdb_id'),(18,'is_otdb_id'),(19,'im_otdb_id'),(20,'img_otdb_id'),(21,'pulp_otdb_id'),(22, 'is_tab_nr'),(23, 'start_sbg_nr'),(24, 'pulp_file_size');
INSERT INTO resource_allocation.resource_claim_property_io_type VALUES (0, 'output'),(1, 'input');
INSERT INTO resource_allocation.config VALUES (0, 'max_fill_ratio_CEP4_storage', '0.85'), (1, 'claim_timeout', '172800'), (2, 'min_inter_task_delay', '60'), (3, 'max_fill_ratio_CEP4_bandwidth', '0.75'); -- Just some values 172800 is two days in seconds
INSERT INTO resource_allocation.conflict_reason
VALUES
(1, 'Not enough total free storage space'),
(2, 'Storage node inactive'),
(3, 'Number of storage nodes available less than minimum required'),
(4, 'No suitable storage options found'),
(5, 'No storage nodes available'),
(6, 'Not enough available storage nodes for required bandwidth'),
(7, 'Network bandwidth to storage node too high'),
(8, 'Bandwidth required for single file too high');
COMMIT;
