
-- Function: z_next_free(text, text, text)
DROP FUNCTION IF EXISTS z_next_free(text, text, text) cascade;
CREATE OR REPLACE FUNCTION z_next_free(
    table_name text,
    uid_col text,
    _seq text)
  RETURNS integer AS
$BODY$
                stop=False
                T = {'tbl':table_name,'uid_col':uid_col,'_seq':_seq}
                p = """

                            select count(column_name) c
                            from INFORMATION_SCHEMA.COLUMNS
                            where table_name = '%(tbl)s'
                            and column_name = '%(uid_col)s';

                    """ % T
                cnt = plpy.execute(p)[0]['c']

                if cnt==0:
                    p = "create sequence %(tbl)s_%(uid_col)s_seq start with 1;"%T
                    t = plpy.execute(p)
                    p = "alter table %(tbl)s alter column %(uid_col)s set DEFAULT z_next_free('%(tbl)s'::text, 'uid'::text, '%(tbl)s_uid_seq'::text);"%T
                    t = plpy.execute(p)
                stop=False
                while stop==False:
                    p = "SELECT nextval('%(tbl)s_%(uid_col)s_seq') next_val"%T
                    try:
                        t = plpy.execute(p)[0]['next_val']
                    except plpy.spiexceptions.UndefinedTable:
                        p = "select max(%(uid_col)s) from %(tbl)s;" % T
                        max_num = plpy.execute(p)[0]['max']
                        if max_num:
                            T.update({'max_num':str(max_num)})
                        else:
                            T.update({'max_num':str(1)})
                        p = "create sequence %(tbl)s_%(uid_col)s_seq start with %(max_num)s;" % T
                        t = plpy.execute(p)
                        p = "SELECT nextval('%(tbl)s_%(uid_col)s_seq') next_val"%T
                        t = plpy.execute(p)[0]['next_val']
                    T.update({'next_val':t})
                    p = "SELECT count(%(uid_col)s) cnt from %(tbl)s where %(uid_col)s=%(next_val)s"%T
                    chk = plpy.execute(p)[0]['cnt']
                    if chk==0:
                        stop=True
                        break
                return T['next_val']

                $BODY$
LANGUAGE plpythonu;

-- Function: z_get_seq_value()
drop function if exists z_get_seq_value(text) cascade;
create or replace function z_get_seq_value(seq_name text) returns integer as $$
declare x int;
begin
x = currval(seq_name::regclass)+1;
return x;
exception
    when sqlstate '42P01' then return 1;
    when sqlstate '55000' then return next_val(seq_name::regclass);
end;
$$ language plpgsql;

-- Trigger Function: z_auto_add_primary_key()

DROP FUNCTION IF EXISTS z_auto_add_primary_key() cascade;
CREATE OR REPLACE FUNCTION z_auto_add_primary_key()
  RETURNS event_trigger AS
$BODY$
DECLARE
	has_index boolean;
	tbl text;
	_seq text;
BEGIN
	has_index = (select relhasindex from pg_class
			where relnamespace=2200
			and relkind='r'
			order by oid desc limit 1);

	IF (
		pg_trigger_depth()=0
		and has_index=False )
	THEN
		tbl = (select relname t from pg_class
			where relnamespace=2200
			and relkind='r'
			order by oid desc limit 1);
		_seq = format('%I_uid_seq',tbl);
		execute format('alter table %I add column uid serial primary key',tbl);
		execute format('alter table %I alter column uid set default z_next_free(
					''%I'',
					''uid'',
					''%I'')',tbl,tbl,_seq);
	end if;
END;
$BODY$
  LANGUAGE plpgsql;

DROP EVENT TRIGGER if exists missing_primary_key_trigger;
CREATE EVENT TRIGGER missing_primary_key_trigger
ON ddl_command_end
WHEN TAG IN ('CREATE TABLE','CREATE TABLE AS')
EXECUTE PROCEDURE z_auto_add_primary_key();

-- Trigger Function: z_auto_add_last_updated_field()
DROP FUNCTION if exists z_auto_add_last_updated_field() cascade;
CREATE OR REPLACE FUNCTION z_auto_add_last_updated_field()
  RETURNS event_trigger AS
$BODY$
DECLARE
    last_table text;
    has_last_updated boolean;
BEGIN
    last_table := ( select relname from pg_class
                    where relnamespace=2200
                    and relkind='r'
                    order by oid desc limit 1);

    SELECT count(*)>0 INTO has_last_updated FROM information_schema.columns
        where table_name='||quote_ident(last_table)||'
        and column_name='last_updated';

    IF (
        pg_trigger_depth()=0
        and has_last_updated=False )
    THEN
        execute format('alter table %I drop column if exists last_updated',last_table);
        execute format('alter table %I add column last_updated timestamp with time zone',last_table);
        execute format('DROP FUNCTION if exists z_auto_update_timestamp_on_%s_in_last_updated() cascade',last_table);
        execute format('DROP TRIGGER if exists update_timestamp_on_%s_in_last_updated ON %s',last_table,last_table);

        execute format('CREATE OR REPLACE FUNCTION z_auto_update_timestamp_on_%s_in_last_updated()'
                        || ' RETURNS TRIGGER AS $$'
                        || ' BEGIN'
                        || '     NEW.last_updated := now();'
                        || '     RETURN NEW;'
                        || ' END;'
                        || ' $$ language ''plpgsql'';'
                        || '',last_table);

        execute format('CREATE TRIGGER update_timestamp_on_%s_in_last_updated'
                        || ' BEFORE UPDATE OR INSERT ON %I'
                        || ' FOR EACH ROW'
                        || ' EXECUTE PROCEDURE z_auto_update_timestamp_on_%s_in_last_updated();'
                        || '',last_table,last_table,last_table);

    END IF;

END;
$BODY$
  LANGUAGE plpgsql;

DROP EVENT TRIGGER if exists missing_last_updated_field;
CREATE EVENT TRIGGER missing_last_updated_field
ON ddl_command_end
WHEN TAG IN ('CREATE TABLE','CREATE TABLE AS')
EXECUTE PROCEDURE z_auto_add_last_updated_field();

DROP FUNCTION IF EXISTS json_object_set_keys(json,text[],anyarray);
CREATE OR REPLACE FUNCTION "json_object_set_keys"(
  "json"          json,
  "keys_to_set"   TEXT[],
  "values_to_set" anyarray
)
  RETURNS json
  LANGUAGE sql
  IMMUTABLE
  STRICT
AS $function$
SELECT concat('{', string_agg(to_json("key") || ':' || "value", ','), '}')::json
FROM (SELECT *
      FROM json_each("json")
     WHERE "key" <> ALL ("keys_to_set")
     UNION ALL
    SELECT DISTINCT ON ("keys_to_set"["index"])
           "keys_to_set"["index"],
           CASE
             WHEN "values_to_set"["index"] IS NULL THEN 'null'::json
             ELSE to_json("values_to_set"["index"])
           END
      FROM generate_subscripts("keys_to_set", 1) AS "keys"("index")
      JOIN generate_subscripts("values_to_set", 1) AS "values"("index")
     USING ("index")) AS "fields"
$function$;