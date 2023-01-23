"""Module for Waverunner DMS Integration."""
import ast
import datetime
import logging
import time
import uuid

from bms_app import settings as cs
from bms_app.dmscloudsql import bp
from bms_app.dmscloudsql import dms_sql
import google.auth
import google.auth.transport.requests
from google.cloud import secretmanager
from googleapiclient import discovery
from googleapiclient import errors
from pandarallel import pandarallel
import pandas as pd
import shortuuid
import sqlalchemy

# import dask.dataframe as dd #Remove this later, if not using dask:Sneha

logger = logging.getLogger(__name__)

# Initialization
pandarallel.initialize(use_memory_fs=False)

# Getting the credentials and project details for gcp project
credentials, project_id = google.auth.default(
    scopes=['https://www.googleapis.com/auth/cloud-platform']
)
su = shortuuid.ShortUUID(alphabet='23456789abcdefghijkmnopqrstuvwxyz')

dms_data = pd.DataFrame()


# Remove this test function later:Sneha
@bp.route('/settings')
def test_cloudsql():
  logger.debug('SQL to fetch data: %s', dms_sql.sql_query)
  global dms_data
  if dms_data.empty:
    get_data()
    logger.debug('Reached this assignment section.')
  else:
    logger.debug('DFF already populated: test_cloudsql')
  return dms_data.to_dict()  # {'dms_sql': dms_sql.sql_query}


@bp.route('/profile')
def trigger_profile_creation():
  start_time = datetime.datetime.now()
  logger.debug('Trigger source profile creation')
  global dms_data
  print('is empty: ', dms_data.empty)

  if dms_data.empty:
    logger.debug('Here in this assignment section.')
    get_data()
  else:
    logger.debug('DF already populated: trigger_profile_creation')

  dms_data['sp_output'] = dms_data.parallel_apply(
      step1_create_dms_source_profile, axis=1
  )
  end_time = datetime.datetime.now()
  pp_total_time = end_time - start_time
  logger.debug(
      'Total time taken for source profile creation: %s', pp_total_time
  )
  return dms_data.to_dict()


def get_region(zone_name):
  service = get_service('compute')

  request_region = service.zones().get(
      project=f'{project_id}',
      zone=f'{zone_name}',
  )

  response = request_region.execute()
  response_region = response['region'][response['region'].rfind('/') + 1 :]
  return response_region


def get_service(service_name) -> discovery.Resource:
  """Create discovery resource for database migration service.

  Args:
    service_name:

  Returns:
  """
  dms_service = discovery.build(service_name, 'v1', credentials=credentials)
  return dms_service


def get_secret(secret_name) -> dict:
  """Fetches details of a secret.

  Args:
    secret_name:

  Returns:
  """
  client = secretmanager.SecretManagerServiceClient()
  name = f'projects/{project_id}/secrets/{secret_name}/versions/latest'
  response = client.access_secret_version(request={'name': name})
  data = response.payload.data.decode('UTF-8')
  return data


def get_lro_details(lro_detail: str) -> str:
  """Fetches details of a long running operatation by operationId.

  Args:
    lro_detail:

  Returns:
  """
  name = lro_detail
  service = get_service('datamigration')
  request_get_lro_state = (
      service.projects()
      .locations()
      .operations()
      .get(
          name=f'{name}',
      )
  )
  responseget_lro_state = request_get_lro_state.execute()
  check_wip = responseget_lro_state['done']
  while not check_wip:
    time.sleep(5)
    request_get_lro_state = (
        service.projects()
        .locations()
        .operations()
        .get(
            name=f'{name}',
        )
    )
    responseget_lro_state = request_get_lro_state.execute()
    check_wip = responseget_lro_state['done']
  if responseget_lro_state['done']:
    if 'response' in responseget_lro_state:
      logger.debug('LRO response %s', responseget_lro_state['response'])
      return (
          'SUCCESS-get_lro_details:'
          + '200'
          + ':'
          + responseget_lro_state['response']['name']
      )
    elif 'error' in responseget_lro_state:
      if (
          responseget_lro_state['error']['message']
          == 'Some table(s) have limited support.'
      ):
        logger.warning('LRO warning %s', responseget_lro_state['error'])
        return (
            'WARNING-get_lro_details:'
            + str(responseget_lro_state['error']['code'])
            + ':'
            + responseget_lro_state['error']['message']
        )
      else:
        logger.exception('LRO error %s', responseget_lro_state['error'])
        return (
            'ERROR-get_lro_details:'
            + str(responseget_lro_state['error']['code'])
            + ':'
            + responseget_lro_state['error']['message']
        )


def create_connection_profile(
    gcp_project_id: str, profile_name: str, location: str, config: dict
) -> str:
  """Creates connection profile.

  Args:
    gcp_project_id:
    profile_name:
    location:
    config:

  Returns:
  """
  service = get_service('datamigration')

  request_create_connprofile = (
      service.projects()
      .locations()
      .connectionProfiles()
      .create(
          parent=f'projects/{gcp_project_id}/locations/{location}',
          connectionProfileId=profile_name,
          body=config,
      )
  )

  try:
    response_create_connprofile = request_create_connprofile.execute()
  except errors.HttpError as err:
    logger.exception('ERROR-create_connection_profile: %s', err)
    return (
        'ERROR-create_connection_profile:'
        + str(err.resp.status)
        + ':'
        + err.resp.reason
    )

  logger.debug(
      'API Response for create_connection_profile: %s',
      response_create_connprofile['metadata']['@type'],
  )

  if response_create_connprofile['metadata']['@type'].endswith(
      'OperationMetadata'
  ):
    cp_name = response_create_connprofile['name']
    return get_lro_details(cp_name)
  else:
    logger.exception(
        'ERROR-create_connection_profile: OperationMetadata not found for'
        ' Connection profile creation'
    )
    return (
        'ERROR-create_connection_profile:'
        + '404'
        + ':'
        + 'OperationMetadata not found for Connection profile creation'
    )


def create_migration_job(
    gcp_project_id: str,
    job_name: str,
    job_request_id: str,
    location: str,
    config: dict,
) -> str:
  """Creates migration job.

  Args:
    gcp_project_id:
    job_name:
    job_request_id:
    location:
    config:

  Returns:
  """
  service = get_service('datamigration')
  request_create_migjob = (
      service.projects()
      .locations()
      .migrationJobs()
      .create(
          parent=f'projects/{gcp_project_id}/locations/{location}',
          migrationJobId=job_name,
          requestId=job_request_id,
          body=config,
      )
  )

  try:
    response_create_migjob = request_create_migjob.execute()
  except errors.HttpError as err:
    logger.exception('ERROR-create_migration_job: %s', err)
    return (
        'ERROR-create_migration_job:'
        + str(err.resp.status)
        + ':'
        + err.resp.reason
    )

  logger.debug(
      'API Response for create_migration_job: %s',
      response_create_migjob['metadata']['@type'],
  )

  if response_create_migjob['metadata']['@type'].endswith('OperationMetadata'):
    mj_name = response_create_migjob['name']
    return get_lro_details(mj_name)
  else:
    logger.exception(
        'ERROR-create_migration_job: OperationMetadata not found for'
        ' Migration Job creation'
    )
    return (
        'ERROR-create_migration_job:'
        + '404'
        + ':'
        + 'OperationMetadata not found for Migration Job creation'
    )


def verify_migration_job(job_name: str) -> str:
  """Verifies migration job.

  Ensure the configuration at source is updated to allow incoming connections
  from target CloudSQL instance.

  Args:
    job_name:

  Returns:
  """
  service = get_service('datamigration')
  request_verify_migjob = (
      service.projects()
      .locations()
      .migrationJobs()
      .verify(
          name=f'{job_name}',
      )
  )

  try:
    response_verify_migjob = request_verify_migjob.execute()
  except errors.HttpError as err:
    logger.exception('ERROR-verify_migration_job: %s', err)
    return (
        'ERROR-verify_migration_job:'
        + str(err.resp.status)
        + ':'
        + err.resp.reason
    )

  logger.debug(
      'API Response for verify_migration_job: %s',
      response_verify_migjob['metadata']['@type'],
  )

  if response_verify_migjob['metadata']['@type'].endswith('OperationMetadata'):
    mj_name = response_verify_migjob['name']
    return get_lro_details(mj_name)
  else:
    logger.exception(
        'ERROR-verify_migration_job: OperationMetadata not found for'
        ' Migration Job verification'
    )
    return (
        'ERROR-verify_migration_job:'
        + '404'
        + ':'
        + 'OperationMetadata not found for Migration Job verification'
    )


def start_migration_job(job_name: str) -> str:
  """Starts migration job.

  Args:
    job_name:

  Returns:
  """
  service = get_service('datamigration')
  request_start_migjob = (
      service.projects()
      .locations()
      .migrationJobs()
      .start(
          name=f'{job_name}',
      )
  )

  try:
    response_start_migjob = request_start_migjob.execute()
  except errors.HttpError as err:
    logger.exception('ERROR-start_migration_job: %s', err)
    return (
        'ERROR-start_migration_job:'
        + str(err.resp.status)
        + ':'
        + err.resp.reason
    )

  logger.debug(
      'API Response for start_migration_job: %s',
      response_start_migjob['metadata']['@type'],
  )

  if response_start_migjob['metadata']['@type'].endswith('OperationMetadata'):
    mj_name = response_start_migjob['name']
    return get_lro_details(mj_name)
  else:
    logger.exception(
        'ERROR-start_migration_job: OperationMetadata not found for'
        ' the start of Migration Job'
    )
    return (
        'ERROR-start_migration_job:'
        + '404'
        + ':'
        + 'OperationMetadata not found for the start of Migration Job'
    )


def promote_migration_job(job_name: str) -> str:
  """Promotes migration job.

  Args:
    job_name:

  Returns:
  """
  service = get_service('datamigration')
  request_promote_migjob = (
      service.projects()
      .locations()
      .migrationJobs()
      .promote(
          name=f'{job_name}',
      )
  )

  try:
    response_promote_migjob = request_promote_migjob.execute()
  except errors.HttpError as err:
    logger.exception('ERROR-promote_migration_job: %s', err)
    return (
        'ERROR-promote_migration_job:'
        + str(err.resp.status)
        + ':'
        + err.resp.reason
    )

  logger.debug(
      'API Response for promote_migration_job: %s',
      response_promote_migjob['metadata']['@type'],
  )

  if response_promote_migjob['metadata']['@type'].endswith('OperationMetadata'):
    mj_name = response_promote_migjob['name']
    return get_lro_details(mj_name)
  else:
    logger.exception(
        'ERROR-promote_migration_job: OperationMetadata not found for'
        ' promoting the Migration Job'
    )
    return (
        'ERROR-promote_migration_job:'
        + '404'
        + ':'
        + 'OperationMetadata not found for promoting the Migration Job'
    )


def get_connection_profile(profile_detail: str) -> str:
  """Get details of a specific database migration connection profile.

  Args:
    profile_detail:

  Returns:
  """
  service = get_service('datamigration')
  request_get_connprofile = (
      service.projects()
      .locations()
      .connectionProfiles()
      .get(
          name=f'{profile_detail}',
      )
  )

  try:
    response_get_connprofile = request_get_connprofile.execute()
  except errors.HttpError as err:
    logger.exception('ERROR-get_connection_profile: %s', err)
    return (
        'ERROR-get_connection_profile:'
        + str(err.resp.status)
        + ':'
        + err.resp.reason
    )

  logger.debug(
      'API Response[CloudSQL] for get_connection_profile: %s',
      response_get_connprofile['cloudsql'],
  )
  return (
      'SUCCESS-get_connection_profile:'
      + '200'
      + ':'
      + response_get_connprofile['cloudsql']['publicIp']
  )


def step1_create_dms_source_profile(dms_df) -> str:
  """Create source connection profile using DMS REST API.

  Args:
    dms_df:

  Returns:
  """
  scp_name = dms_df['sp_name']
  sp_host = dms_df['sp_host']
  sp_username = dms_df['sp_username']
  sp_pwd = dms_df['sp_pwd']
  sp_port = dms_df['sp_port']
  sp_location = dms_df['region']
  sp_config = {
      'name': f'{scp_name}',
      'displayName': f'{scp_name}',
      'postgresql': {
          'host': f'{sp_host}',
          'port': sp_port,
          'username': f'{sp_username}',
          'password': f'{sp_pwd}',
      },
  }

  logger.debug('Config for source connection profile: %s', sp_config)

  response = create_connection_profile(
      project_id, scp_name, sp_location, sp_config
  )

  return response


def step2_create_dms_target_profile(dms_df, scp_message) -> str:
  """Create target connection profile using DMS REST API.

  Args:
    dms_df:
    scp_message:

  Returns:
  """
  tcp_name = dms_df['tp_name']
  tp_version = dms_df['tp_version']
  tp_tier = dms_df['tp_tier']
  storageautoresizelimit = dms_df['storageautoresizelimit']
  activationpolicy = dms_df['activationpolicy']
  autostorageincrease = dms_df['autostorageincrease']
  zone = dms_df['zone']
  rootpassword = dms_df['rootpassword']
  ipconfig = dms_df['ipconfig']
  databaseflags = dms_df['databaseflags']
  datadisktype = dms_df['datadisktype']
  datadisksizegb = dms_df['datadisksizegb']
  cmekkeyname = dms_df['cmekkeyname']
  tp_location = dms_df['region']

  tp_config = {
      'name': f'{tcp_name}',
      'displayName': f'{tcp_name}',
      'cloudsql': {
          'settings': {
              'databaseVersion': f'{tp_version}',
              'tier': f'{tp_tier}',
              'storageAutoResizeLimit': storageautoresizelimit,
              'activationPolicy': f'{activationpolicy}',
              'autoStorageIncrease': autostorageincrease,
              'zone': f'{zone}',
              'sourceId': f'{scp_message}',
              'rootPassword': f'{rootpassword}',
              'ipConfig': ipconfig,
              'databaseFlags': databaseflags,
              'dataDiskType': f'{datadisktype}',
              'dataDiskSizeGb': datadisksizegb,
              'cmekKeyName': f'{cmekkeyname}',
          }
      },
  }
  logger.debug('Config for target connection profile: %s', tp_config)

  response = create_connection_profile(
      project_id, tcp_name, tp_location, tp_config
  )

  return response


def step3_create_migration_job(dms_df, scp_message, tcp_message) -> str:
  """Create target connection profile using DMS REST API.

  Args:
    dms_df:
    scp_message:
    tcp_message:

  Returns:
  """
  database_name = dms_df['database']
  mj_name = dms_df['mj_name']
  mj_request_id = uuid.uuid4()
  mj_type = dms_df['type']
  dumpflags = dms_df['dumpflags']
  dumppath = dms_df['dumppath']
  sourcedatabase_provider = dms_df['sourcedatabase_provider']
  sourcedatabase_engine = dms_df['sourcedatabase_engine']
  destinationdatabase_provider = dms_df['destinationdatabase_provider']
  destinationdatabase_engine = dms_df['destinationdatabase_engine']
  connectivity = dms_df['connectivity']  # add logic Sneha
  mj_location = dms_df['region']

  if database_name == 'postgresql':  # Use key: "dumpFlags"
    mj_config = {
        'name': f'{mj_name}',
        'displayName': f'{mj_name}',
        'type': f'{mj_type}',
        'dumpFlags': dumpflags,
        'source': f'{scp_message}',
        'destination': f'{tcp_message}',
        'sourceDatabase': {
            'provider': f'{sourcedatabase_provider}',
            'engine': f'{sourcedatabase_engine}',
        },
        'destinationDatabase': {
            'provider': f'{destinationdatabase_provider}',
            'engine': f'{destinationdatabase_engine}',
        },
    }
  else:  # Use key: "dumppath"
    mj_config = {
        'name': f'{mj_name}',
        'displayName': f'{mj_name}',
        'type': f'{mj_type}',
        'dumppath': f'{dumppath}',
        'source': f'{scp_message}',
        'destination': f'{tcp_message}',
        'sourceDatabase': {
            'provider': f'{sourcedatabase_provider}',
            'engine': f'{sourcedatabase_engine}',
        },
        'destinationDatabase': {
            'provider': f'{destinationdatabase_provider}',
            'engine': f'{destinationdatabase_engine}',
        },
    }

  logger.debug('Config for migration job: %s', mj_config)

  response = create_migration_job(
      project_id, mj_name, mj_request_id, mj_location, mj_config
  )

  return response


def run_dms_test(dms_df) -> str:
  """Innvoke DMS Rest APIs.

  Args:
    dms_df:

  Returns:
  """

  resp_scp = step1_create_dms_source_profile(dms_df)

  logger.debug('Response of source connection profile creation: %s', resp_scp)
  scp_message = resp_scp[resp_scp.rfind(':') + 1 :]
  scp_status_code = resp_scp[resp_scp.find(':') + 1 : resp_scp.rfind(':')]

  resp_tcp = ''
  tcp_status_code = 0
  tcp_message = ''

  if scp_status_code == '200':
    resp_tcp = step2_create_dms_target_profile(dms_df, scp_message)

    logger.debug('Response of target connection profile creation: %s', resp_tcp)
    tcp_message = resp_tcp[resp_tcp.rfind(':') + 1 :]
    tcp_status_code = resp_tcp[resp_tcp.find(':') + 1 : resp_tcp.rfind(':')]

  else:
    logger.exception(
        'Error in source connection profile creation: %s', resp_scp
    )
    return resp_scp

  resp_get_cp_details = ''
  get_cp_status_code = 0
  get_cp_message = ''
  if tcp_status_code == '200':
    resp_get_cp_details = get_connection_profile(tcp_message)
    logger.debug(
        'Response from fetching target connection profile details: %s',
        resp_get_cp_details,
    )
    get_cp_message = resp_get_cp_details[
        resp_get_cp_details.rfind(':') + 1 :
    ]  # stores the public IP of CloudSQL
    get_cp_status_code = resp_get_cp_details[
        resp_get_cp_details.find(':') + 1 : resp_get_cp_details.rfind(':')
    ]

  else:
    logger.exception(
        'Error in target connection profile creation: %s', resp_tcp
    )
    return resp_tcp

  resp_mj = ''
  mj_status_code = 0
  mj_message = ''
  if get_cp_status_code == '200':
    resp_mj = step3_create_migration_job(dms_df, scp_message, tcp_message)

    logger.debug(
        'Response from migration job creation: %s',
        resp_mj,
    )
    mj_message = resp_mj[resp_mj.rfind(':') + 1 :]
    mj_status_code = resp_mj[resp_mj.find(':') + 1 : resp_mj.rfind(':')]

  else:
    logger.exception(
        'Error in fetching target profile details: %s', resp_get_cp_details
    )
    return resp_get_cp_details

  resp_get_mj_details = ''
  get_mj_status_code = 0
  get_mj_message = ''
  if mj_status_code == '200':
    resp_get_mj_details = verify_migration_job(mj_message)
    logger.debug(
        'Response from migration job verification: %s',
        resp_get_mj_details,
    )
    get_mj_message = resp_get_mj_details[resp_get_mj_details.rfind(':') + 1 :]
    get_mj_status_code = resp_get_mj_details[
        resp_get_mj_details.find(':') + 1 : resp_get_mj_details.rfind(':')
    ]

  else:
    logger.exception('Error in migration job creation: %s', resp_mj)
    return resp_mj

  start_mj_status_code = 0
  start_mj_message = ''
  wait_time_before_promote = 60  # Split the code to another file:Sneha
  if mj_status_code == '200' and (
      (get_mj_status_code == '200')
      or (get_mj_message == 'Some table(s) have limited support.')
  ):
    resp_start_mj_details = start_migration_job(mj_message)
    logger.debug(
        'Response from migration job start operation: %s',
        resp_start_mj_details,
    )
    start_mj_message = resp_start_mj_details[
        resp_start_mj_details.rfind(':') + 1 :
    ]
    start_mj_status_code = resp_start_mj_details[
        resp_start_mj_details.find(':') + 1 : resp_start_mj_details.rfind(':')
    ]
  else:
    logger.exception(
        'Error in migration job verification: %s', resp_get_mj_details
    )
    return resp_get_mj_details

  if start_mj_status_code == '200':
    if (
        wait_time_before_promote > 0
    ):  # Remove this section for default timer too:Sneha
      time.sleep(wait_time_before_promote)

    resp_promote_mj_details = promote_migration_job(mj_message)
    logger.debug(
        'Response from migration job promote operation: %s',
        resp_promote_mj_details,
    )
    promote_mj_message = resp_promote_mj_details[
        resp_promote_mj_details.rfind(':') + 1 :
    ]
    promote_mj_status_code = resp_promote_mj_details[
        resp_promote_mj_details.find(':')
        + 1 : resp_promote_mj_details.rfind(':')
    ]
    return resp_promote_mj_details
  else:
    logger.exception(
        'Error in migration job start operation: %s', resp_start_mj_details
    )
    return resp_start_mj_details


def get_db_details(secret_val, attribute1, attribute2, attribute3='') -> str:
  """Fetch details from database.

  Args:
    secret_val:
    attribute1:
    attribute2:
    attribute3: Used only for migration job related attributes

  Returns:
  """
  secret_string = ast.literal_eval(secret_val)
  if attribute1 == 'sp_config':
    if 'postgresql' in secret_string[attribute1]:
      if attribute2 == 'database':
        return 'postgresql'
      return secret_string.get(attribute1).get('postgresql').get(attribute2)
    elif 'mysql' in secret_string[attribute1]:
      if attribute2 == 'database':
        return 'postgresql'
      return secret_string.get(attribute1).get('mysql').get(attribute2)
    else:
      return None
  elif attribute1 == 'tp_config':
    return (
        secret_string.get(attribute1)
        .get('cloudsql')
        .get('settings')
        .get(attribute2)
    )
  elif attribute1 == 'mj_config':
    if attribute3 == '':
      return secret_string.get(attribute1).get(attribute2)
    else:
      return secret_string.get(attribute1).get(attribute2).get(attribute3)


# @bp.route('/dms', methods=['POST'])
def get_data():
  """Update Operation and OperationDetails statuses/steps."""
  start_time = datetime.datetime.now()
  logger.debug('Start of DMS API call: %s', start_time)

  engine = sqlalchemy.create_engine(cs.DATABASE_URL)
  sql = dms_sql.sql_query

  df = pd.read_sql(sql, con=engine)
  engine.dispose()

  if df.empty:
    logger.exception('Database details not found for CloudSQL migration')
    return 'Database details not found for CloudSQL migration', 400

  df['secret_data'] = df.secret_name.apply(get_secret)
  df['database'] = df['secret_data'].apply(
      lambda x: get_db_details(x, 'sp_config', 'database')
  )
  # source connection profile related columns
  df['sp_name'] = (
      'sp-'
      + df['project_name'].astype(str)
      + '-sid-'
      + df['source_db_id'].astype(str)
      + '-'
      + su.uuid()
  )
  df['sp_host'] = (
      df['secret_data']
      .apply(lambda x: get_db_details(x, 'sp_config', 'host'))
      .fillna(df['server'])
  )
  df['sp_port'] = (
      df['secret_data']
      .apply(lambda x: get_db_details(x, 'sp_config', 'port'))
      .fillna(df['source_db_port'])
  )
  df['sp_username'] = df['secret_data'].apply(
      lambda x: get_db_details(x, 'sp_config', 'username')
  )  # must be provided in secret manager, else will lead to issues
  df['sp_pwd'] = df['secret_data'].apply(
      lambda x: get_db_details(x, 'sp_config', 'password')
  )  # must be provided in secret manager, else will lead to issues
  # target connection profile related columns
  df['tp_name'] = (
      'tp-'
      + df['project_name'].astype(str)
      + '-sid-'
      + df['source_db_id'].astype(str)
      + '-tid-'
      + df['target_db_id'].astype(str)
      + '-'
      + su.uuid()
  )
  df['tp_version'] = (
      df['secret_data']
      .apply(lambda x: get_db_details(x, 'tp_config', 'databaseVersion'))
      .fillna('SQL_DATABASE_VERSION_UNSPECIFIED')
  )
  df['tp_tier'] = (
      df['secret_data']
      .apply(lambda x: get_db_details(x, 'tp_config', 'tier'))
      .fillna(df['machine_type'])
  )
  df['storageAutoResizeLimit'] = (
      df['secret_data']
      .apply(lambda x: get_db_details(x, 'tp_config', 'storageAutoResizeLimit'))
      .fillna(0)
  )
  df['activationPolicy'] = (
      df['secret_data']
      .apply(lambda x: get_db_details(x, 'tp_config', 'activationPolicy'))
      .fillna('ALWAYS')
  )
  df['autoStorageIncrease'] = (
      df['secret_data']
      .apply(lambda x: get_db_details(x, 'tp_config', 'autoStorageIncrease'))
      .astype(bool)
      .fillna(False)
  )
  df['zone'] = (
      df['secret_data']
      .apply(lambda x: get_db_details(x, 'tp_config', 'zone'))
      .fillna(df['location'])
  )
  df['region'] = df['location'].apply(lambda x: get_region(x))
  df['rootPassword'] = df['secret_data'].apply(
      lambda x: get_db_details(x, 'tp_config', 'rootPassword')
  )  # must be provided in secret manager, else will lead to issues
  df['ipConfig'] = df['secret_data'].apply(
      lambda x: get_db_details(x, 'tp_config', 'ipConfig')
  )  # test this once: Sneha
  df['databaseFlags'] = df['secret_data'].apply(
      lambda x: get_db_details(x, 'tp_config', 'databaseFlags')
  )
  df['dataDiskType'] = (
      df['secret_data']
      .apply(lambda x: get_db_details(x, 'tp_config', 'dataDiskType'))
      .fillna('PD_SSD')
  )
  df['dataDiskSizeGb'] = (
      df['secret_data']
      .apply(lambda x: get_db_details(x, 'tp_config', 'dataDiskSizeGb'))
      .fillna(10)
  )  # Default is 10 GB
  df['cmekKeyName'] = (
      df['secret_data']
      .apply(lambda x: get_db_details(x, 'tp_config', 'cmekKeyName'))
      .fillna('')
  )
  # migration job related columns
  df['mj_name'] = (
      'mj-'
      + df['project_name'].astype(str)
      + '-sid-'
      + df['source_db_id'].astype(str)
      + '-tid-'
      + df['target_db_id'].astype(str)
      + '-'
      + su.uuid()
  )
  df['type'] = (
      df['secret_data']
      .apply(lambda x: get_db_details(x, 'mj_config', 'type'))
      .fillna('CONTINUOUS')
  )
  df['dumpFlags'] = df['secret_data'].apply(
      lambda x: get_db_details(x, 'mj_config', 'dumpFlags')
  )
  df['dumpPath'] = df['secret_data'].apply(
      lambda x: get_db_details(x, 'mj_config', 'dumpPath')
  )
  df['sourceDatabase_provider'] = (
      df['secret_data']
      .apply(
          lambda x: get_db_details(x, 'mj_config', 'sourceDatabase', 'provider')
      )
      .fillna('DATABASE_PROVIDER_UNSPECIFIED')
  )
  df['sourceDatabase_engine'] = (
      df['secret_data']
      .apply(
          lambda x: get_db_details(x, 'mj_config', 'sourceDatabase', 'engine')
      )
      .fillna('DATABASE_ENGINE_UNSPECIFIED')
  )
  df['destinationDatabase_provider'] = (
      df['secret_data']
      .apply(
          lambda x: get_db_details(
              x, 'mj_config', 'destinationDatabase', 'provider'
          )
      )
      .fillna('CLOUDSQL')
  )
  df['destinationDatabase_engine'] = (
      df['secret_data']
      .apply(
          lambda x: get_db_details(
              x, 'mj_config', 'destinationDatabase', 'engine'
          )
      )
      .fillna('DATABASE_ENGINE_UNSPECIFIED')
  )
  df['connectivity'] = (
      ''  # add logic to get this from cloud_dms_values column:Sneha
  )

  df.columns = map(str.lower, df.columns)

  global dms_data
  dms_data = df


@bp.route('/dms', methods=['POST'])
def start_dms_migration():
  start_time = datetime.datetime.now()
  global dms_data

  if dms_data.empty:
    get_data()

  dms_data['output'] = dms_data.parallel_apply(run_dms_test, axis=1)

  end_time = datetime.datetime.now()
  pp_total_time = end_time - start_time
  logger.debug('End of DMS API call: %s', end_time)
  logger.debug('Total time taken for DMS job: %s', pp_total_time)

  return {'data': 'ok'}, 201
