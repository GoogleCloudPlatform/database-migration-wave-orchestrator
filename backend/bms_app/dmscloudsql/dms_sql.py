"""SQL script to load data from waverunner database for Migration to CloudSQL"""
# bms_servers.secret_name must be populated for Cloud SQL Migrations
# bms_servers.location is expected to store the zone name(not region)
sql_query="""select
    distinct
    pj.id as project_id,
    pj.name as project_name,
    wv.id as wave_id,
    wv.name as wave_name,
    sd.db_version as source_db_version,
    cast(sd.db_port as varchar) as source_db_port,
    sd.cores,
    sd.ram,
    sd.server,
    td.db_version as target_db_version,
    cast(td.db_port as varchar) as taget_db_port,
    td.machine_type,
    td.secret_name,
    td.location,
    td.name as target_name,
    td.id as target_db_id,
    --json_each_text(cfg.cloud_dms_values) ,
    mp.id as mappings_id,
    mp.db_id mappings_db_id,
    sd.id as source_db_id
from
    public.projects pj,
    public.waves wv,
    public.source_dbs sd,
    public.bms_servers td,
    public.configs cfg,
    public.mappings mp
where
    pj.id = wv.project_id
    and pj.id = sd.project_id
    and sd.id = cfg.db_id
    and sd.id = mp.db_id
    and mp.bms_id = td.id
    and td.secret_name is not null"""
