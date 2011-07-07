alter table playaevents_playaevent add column search_tsv tsvector;
update playaevents_playaevent set search_tsv = to_tsvector('english', coalesce(print_description,''));
create index playaevents_search_idx on playaevents_playaevent using gin(search_tsv);
CREATE TRIGGER tsvectorupdate BEFORE INSERT OR UPDATE
ON playaevents_playaevent FOR EACH ROW EXECUTE PROCEDURE
tsvector_update_trigger(search_tsv, 'pg_catalog.english', print_description);


alter table swingtime_event add column search_tsv tsvector;
update swingtime_event set search_tsv = to_tsvector('english', coalesce(description,'') || coalesce(title,''));
create index event_search_idx on swingtime_event using gin(search_tsv);
CREATE TRIGGER event_tsvectorupdate BEFORE INSERT OR UPDATE
ON swingtime_event FOR EACH ROW EXECUTE PROCEDURE
tsvector_update_trigger(search_tsv, 'pg_catalog.english', title, description);