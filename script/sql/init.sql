/*
 * name: DB init script
 * @author: ameau2
 * @date: 2021/2/26
 */
DO
$do$
BEGIN
   IF EXISTS (SELECT FROM pg_database WHERE datname = 'WandrLog') THEN
      RAISE NOTICE 'Database already exists';  -- optional
   ELSE
      PERFORM dblink_exec('dbname=' || current_database()  -- current db
                        , 'CREATE DATABASE WandrLog');
   END IF;
END
$do$;


