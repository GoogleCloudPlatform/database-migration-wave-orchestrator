import google.auth
import google.auth.transport.requests

from googleapiclient import discovery

from oauth2client.client import GoogleCredentials
from googleapiclient import errors
from google.cloud import secretmanager
import os
import sqlalchemy

import time
import uuid

import datetime
import re

import pandas as pd
import dask.dataframe as dd
from bms_app import settings as cs #added newly

import swifter #not performing in parallel

from pandarallel import pandarallel

from bms_app.dmscloudsql import bp
from bms_app.dmscloudsql import dms_sql 

# Initialization
pandarallel.initialize(use_memory_fs=False)


# getting the credentials and project details for gcp project
credentials, project_id = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"]) 


#getting request object
auth_req = google.auth.transport.requests.Request()

client = secretmanager.SecretManagerServiceClient()

#secret_detail = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
#response = client.access_secret_version(request={"name": secret_detail})
#data = response.payload.data.decode("UTF-8")
#print("Data: {}".format(data))



#print(credentials.valid) # #prints False
#credentials.refresh(auth_req) #refresh token
#cehck for valid credentials
#print(credentials.valid)  # #prints True
#print(credentials.token) # #prints token
#print(project_id) 
#working block ends

@bp.route('/settings')
def test_cloudsql():

    print("dms_sql",dms_sql.sql_query)
    return {
        'networks': 'kkoo',
        "dms_sql":dms_sql.sql_query
    }



#Function to create a discovery resource for database migration service
def get_service() -> discovery.Resource:
    dms_service = discovery.build('datamigration', 'v1', credentials=credentials)
    return dms_service

#Function to get secret details
@bp.route('/testsm')
def get_secret(secret_name) -> dict:
    service = get_service()
    name=f'projects/{project_id}/secrets/{secret_name}/versions/latest'
    response = client.access_secret_version(request={"name": name})
    data = response.payload.data.decode("UTF-8")
    print("Data: {}".format(data))
    return data
    


#Function to fetch details of a specific long running operation
def get_lro_details(lro_detail: str) -> str:

    name=lro_detail
    service = get_service()
    request_get_lro_state = service.projects().locations().operations().get(
                              name=f'{name}',
                              )
    responseget_lro_state= request_get_lro_state.execute()
    check_wip = responseget_lro_state['done']
    while not check_wip:
        #print('sleeping for 5 sec')
        time.sleep(5)
        request_get_lro_state = service.projects().locations().operations().get(
                          name=f'{name}',
                          )
        responseget_lro_state= request_get_lro_state.execute()
        check_wip = responseget_lro_state['done']
    if responseget_lro_state['done']:
        if 'response' in responseget_lro_state:
            #print('success')
            #print(responseget_lro_state['response'])
            return 'SUCCESS-get_lro_details:' + '200' + ':' + responseget_lro_state['response']['name']
        elif 'error' in responseget_lro_state:
            #print('error')
            #print(responseget_lro_state['error'])
            #print('ERROR:' + str(responseget_lro_state['error']['code']) + ':' + responseget_lro_state['error']['message'])
            return 'ERROR-get_lro_details:' + str(responseget_lro_state['error']['code']) + ':' + responseget_lro_state['error']['message']



#Function to create database migration connection profile
def create_connection_profile(gcp_project_id: str, profile_name: str, config: dict) -> str:
    service = get_service()
    request_create_connprofile = service.projects().locations().connectionProfiles().create(
    parent=f'projects/{gcp_project_id}/locations/us-central1', #get the location programatiically later
    connectionProfileId=profile_name,
    body=config
    )
    
    #print("before calling")
    
    try:
        response_create_connprofile= request_create_connprofile.execute()
    except errors.HttpError as err:
        #print(err.resp.reason)
        #print(err)
        return 'ERROR-create_connection_profile:' + str(err.resp.status) + ':' + err.resp.reason
    
    #print(response_create_connprofile)
    #print(response_create_connprofile['metadata']['@type'])


    if response_create_connprofile['metadata']['@type'].endswith('OperationMetadata'):
        #print("I am here")
        cp_name=response_create_connprofile['name']
        return get_lro_details(cp_name)
    else:
        return 'ERROR-create_connection_profile:' + '404' + ':' + 'OperationMetadata not found for Connection profile creation'
        #print("here")


#Function to create database migration job
def create_migration_job(gcp_project_id: str, job_name: str, job_request_id: str, config: dict) -> str:
    service = get_service()
    request_create_migjob = service.projects().locations().migrationJobs().create(
    parent=f'projects/{gcp_project_id}/locations/us-central1', #get the location programatiically later
    migrationJobId=job_name,
    requestId=job_request_id, 
    body=config
    )
    
    #print("before calling")
    
    try:
        response_create_migjob= request_create_migjob.execute()
    except errors.HttpError as err:
        #print(err.resp.reason)
        #print(err)
        return 'ERROR-create_migration_job:' + str(err.resp.status) + ':' + err.resp.reason
    
    #print(response_create_migjob)
    #print(response_create_migjob['metadata']['@type'])


    if response_create_migjob['metadata']['@type'].endswith('OperationMetadata'):
        #print("I am here")
        mj_name=response_create_migjob['name']
        return get_lro_details(mj_name)
    else:
        return 'ERROR-create_migration_job:' + '404' + ':' + 'OperationMetadata not found for Migration Job creation'
        #print("here")

#Function to verify database migration job
def verify_migration_job(job_name: str) -> str:
    """Login to vm:
       sudo vi /etc/postgresql/12/main/pg_hba.conf
       sudo systemctl restart postgresql@12-main
       sudo -u postgres psql
    """
    service = get_service()
    request_verify_migjob = service.projects().locations().migrationJobs().verify(
     name=f'{job_name}',
    )
    
    #print("before calling migrationJobs.verify")
    
    try:
        response_verify_migjob= request_verify_migjob.execute()
    except errors.HttpError as err:
        #print(err.resp.reason)
        #print(err)
        return 'ERROR-verify_migration_job:' + str(err.resp.status) + ':' + err.resp.reason
    
    #print(response_verify_migjob)
    #print(response_verify_migjob['metadata']['@type'])


    if response_verify_migjob['metadata']['@type'].endswith('OperationMetadata'):
        #print("I am here migrationJobs.verify")
        mj_name=response_verify_migjob['name']
        return get_lro_details(mj_name)
    else:
        return 'ERROR-verify_migration_job:' + '404' + ':' + 'OperationMetadata not found for Migration Job verification'
        #print("here")


#Function to start database migration job
def start_migration_job(job_name: str) -> str:

    service = get_service()
    request_start_migjob = service.projects().locations().migrationJobs().start(
     name=f'{job_name}',
    )
    
    #print("before calling migrationJobs.start")
    
    try:
        response_start_migjob= request_start_migjob.execute()
    except errors.HttpError as err:
        #print(err.resp.reason)
        #print(err)
        return 'ERROR-start_migration_job:' + str(err.resp.status) + ':' + err.resp.reason
    
    #print(response_start_migjob)
    #print(response_start_migjob['metadata']['@type'])


    if response_start_migjob['metadata']['@type'].endswith('OperationMetadata'):
        #print("I am here migrationJobs.start")
        mj_name=response_start_migjob['name']
        return get_lro_details(mj_name)
    else:
        return 'ERROR-start_migration_job:' + '404' + ':' + 'OperationMetadata not found for the start of Migration Job'
        #print("here")


#Function to promote database migration job
def promote_migration_job(job_name: str) -> str:

    service = get_service()
    request_promote_migjob = service.projects().locations().migrationJobs().promote(
     name=f'{job_name}',
    )
    
    #print("before calling migrationJobs.promote")
    
    try:
        response_promote_migjob= request_promote_migjob.execute()
    except errors.HttpError as err:
        #print(err.resp.reason)
        #print(err)
        return 'ERROR-promote_migration_job:' + str(err.resp.status) + ':' + err.resp.reason
    
    #print(response_promote_migjob)
    #print(response_promote_migjob['metadata']['@type'])


    if response_promote_migjob['metadata']['@type'].endswith('OperationMetadata'):
        #print("I am here migrationJobs.promote")
        mj_name=response_promote_migjob['name']
        return get_lro_details(mj_name)
    else:
        return 'ERROR-promote_migration_job:' + '404' + ':' + 'OperationMetadata not found for promoting the Migration Job'
        #print("here")

#Function to fetch details of a specific database migration target connection profile #Change this later to return specfics of source profile as well
def get_connection_profile(profile_detail: str) -> str:
    service = get_service()
    request_get_connprofile = service.projects().locations().connectionProfiles().get(
                                  name=f'{profile_detail}',
                                  )
    
    #print("before calling connectionProfiles.get")
    
    try:
        response_get_connprofile= request_get_connprofile.execute()
    except errors.HttpError as err:
        #print(err.resp.reason)
        #print(err)
        return 'ERROR-get_connection_profile:' + str(err.resp.status) + ':' + err.resp.reason

    return 'SUCCESS-get_connection_profile:' + '200' + ':' + response_get_connprofile['cloudsql']['publicIp']



def run_dms_test(dms_df)-> str:
    #Create the configuration for source connection profile and call the fucnction to create the profile
    #print("------------------------------------------New Starting DMS for job no.:",dms_df["index"],"------------------------------------------")

    engine = sqlalchemy.create_engine(cs.DATABASE_URL)
    sql=dms_sql.sql_query

    df = pd.read_sql(sql,con=engine)
    engine.dispose()
    return df.to_dict('list') #data # working



    cp_name = dms_df["sp_name"]
    sp_host = dms_df["sp_host"]
    sp_username = dms_df["sp_username"]
    sp_pwd = dms_df["sp_pwd"]
    sp_config={"name":f"{cp_name}",
                "displayName":f"{cp_name}",
                "postgresql":{"host":f"{sp_host}",
                "port":5432,
                "username":f"{sp_username}",
                "password":f"{sp_pwd}"}
                }
    #print("for dms_job_no:",dms_df["index"]," ,sp_config:",sp_config)


    resp_scp = create_connection_profile(project_id, cp_name, sp_config)
    scp_message = resp_scp[resp_scp.rfind(':') + 1:]
    scp_status_code = resp_scp[resp_scp.find(':') + 1: resp_scp.rfind(':') ]
    print("for dms_job_no:",dms_df["index"]," ,resp_scp:",resp_scp)
    #print("for dms_job_no:",dms_df["index"]," ,scp_message:",scp_message)
    #print("for dms_job_no:",dms_df["index"]," ,scp_status_code:",scp_status_code)

    tp_config={}
    resp_tcp = ''
    tcp_status_code = 0
    tcp_message = ''

    #Create the configuration for target connection profile and call the fucnction to create the profile
    if scp_status_code == '200':
        #get the location programatiically later
        tcp_name = dms_df["tp_name"]
        tp_version = dms_df["tp_version"]
        tp_tier = dms_df["tp_tier"]


        tp_config={ "name":f"{tcp_name}",
          "displayName": f"{tcp_name}",
          "cloudsql": {
            "settings": {
              "databaseVersion": f"{tp_version}",
              "tier": f"{tp_tier}",
              "storageAutoResizeLimit": 0,
              "activationPolicy": "ALWAYS",
              "autoStorageIncrease": False,
              "zone": "us-central1-b",
              "sourceId": f"{scp_message}",
              "rootPassword":"sourcewaverunner2"    
            }
          }
        }

        #print("for dms_job_no:",dms_df["index"]," ,tp_config:",tp_config)

        resp_tcp = create_connection_profile(project_id, tcp_name, tp_config)
        tcp_message = resp_tcp[resp_tcp.rfind(':') + 1:]
        tcp_status_code = resp_tcp[resp_tcp.find(':') + 1: resp_tcp.rfind(':') ]
        print("for dms_job_no:",dms_df["index"]," ,resp_tcp:",resp_tcp)
        #print("for dms_job_no:",dms_df["index"]," ,tcp_message:",tcp_message)
        #print("for dms_job_no:",dms_df["index"]," ,tcp_status_code:",tcp_status_code)


    else:
        return resp_scp
    

    resp_get_cp_details = ''
    get_cp_status_code = 0
    get_cp_message = ''
    #Fetch details of the given target conection profile by invoking connectionProfiles.get method 
    if tcp_status_code == '200':
        resp_get_cp_details =  get_connection_profile(tcp_message)
        get_cp_message = resp_get_cp_details[resp_get_cp_details.rfind(':') + 1:]
        get_cp_status_code = resp_get_cp_details[resp_get_cp_details.find(':') + 1: resp_get_cp_details.rfind(':') ]
        print("for dms_job_no:",dms_df["index"]," ,resp_get_cp_details:",resp_get_cp_details)
        #print("for dms_job_no:",dms_df["index"]," ,get_cp_message:",get_cp_message)
        #print("for dms_job_no:",dms_df["index"]," ,get_cp_status_code:",get_cp_status_code)

    else:
        return resp_tcp
    #End of connection profile section


    mj_config={}
    resp_mj = ''
    mj_status_code = 0
    mj_message = ''
    #Create the configuration for migration job and call the function to create the job
    if get_cp_status_code == '200':
        #get the location programatiically later
        mj_name = dms_df["mj_name"]
        tp_engine = dms_df["tp_engine"]
        mj_request_id = uuid.uuid4() 
        mj_config={ "name":f"{mj_name}",
          "displayName": f"{mj_name}",
          "type":"CONTINUOUS",
           "source":f"{scp_message}",
           "destination":f"{tcp_message}",
           "sourceDatabase":{
              "provider":"DATABASE_PROVIDER_UNSPECIFIED",
              "engine":f"{tp_engine}"
           },
           "destinationDatabase":{
              "provider":"CLOUDSQL",
              "engine":f"{tp_engine}"
           }
        }

        #print("for dms_job_no:",dms_df["index"]," ,resp_tcp:",mj_config)

        resp_mj = create_migration_job(project_id, mj_name, mj_request_id, mj_config)
        mj_message = resp_mj[resp_mj.rfind(':') + 1:]
        mj_status_code = resp_mj[resp_mj.find(':') + 1: resp_mj.rfind(':') ]
        print("for dms_job_no:",dms_df["index"]," ,resp_mj:",resp_mj)
        #print("for dms_job_no:",dms_df["index"]," ,mj_message:",mj_message)
        #print("for dms_job_no:",dms_df["index"]," ,mj_status_code:",mj_status_code)

    else:
        return resp_get_cp_details



    resp_get_mj_details = ''
    get_mj_status_code = 0
    get_mj_message = ''
    #Fetch details of the migration job verification
    if mj_status_code == '200':
        resp_get_mj_details =  verify_migration_job(mj_message)
        get_mj_message = resp_get_mj_details[resp_get_mj_details.rfind(':') + 1:]
        get_mj_status_code = resp_get_mj_details[resp_get_mj_details.find(':') + 1: resp_get_mj_details.rfind(':') ]
        print("for dms_job_no:",dms_df["index"],",resp_get_mj_details:",resp_get_mj_details)
        #print("for dms_job_no:",dms_df["index"],",get_mj_message:",get_mj_message)
        #print("for dms_job_no:",dms_df["index"],",get_mj_status_code:",get_mj_status_code)

    else:
        return resp_mj    
        


    start_mj_status_code = 0
    start_mj_message = ''
    wait_time_before_promote = 60 # in seconds, to be supplied
    ##print("mj_status_code:",mj_status_code)
    #Start the migration job if the job is created, even if there is a warning for unsupported tables during verification(check Sneha)
    if mj_status_code == '200' and ((get_mj_status_code == '200') or (get_mj_message=='Some table(s) have limited support.')):
        #print("Starting dms_job_no:",dms_df["index"])
        resp_start_mj_details =  start_migration_job(mj_message)
        start_mj_message = resp_start_mj_details[resp_start_mj_details.rfind(':') + 1:]
        start_mj_status_code = resp_start_mj_details[resp_start_mj_details.find(':') + 1: resp_start_mj_details.rfind(':') ]
        print("for dms_job_no:",dms_df["index"],",resp_start_mj_details:",resp_start_mj_details)
        #print("for dms_job_no:",dms_df["index"],",start_mj_message:",start_mj_message)
        #print("for dms_job_no:",dms_df["index"],",start_mj_status_code:",start_mj_status_code)
    else:
        return resp_get_mj_details


    if start_mj_status_code == '200':
        if wait_time_before_promote > 0 : # check if we need a default timer too
            #print('sleeping for secs: ',wait_time_before_promote)
            time.sleep(wait_time_before_promote)

        #print("Promoting dms_job_no:",dms_df["index"])
        resp_promote_mj_details =  promote_migration_job(mj_message)
        promote_mj_message = resp_promote_mj_details[resp_promote_mj_details.rfind(':') + 1:]
        promote_mj_status_code = resp_promote_mj_details[resp_promote_mj_details.find(':') + 1: resp_promote_mj_details.rfind(':') ]
        print("for dms_job_no:",dms_df["index"],",resp_promote_mj_details:",resp_promote_mj_details)
        #print("for dms_job_no:",dms_df["index"],",promote_mj_message:",promote_mj_message)
        #print("for dms_job_no:",dms_df["index"],",promote_mj_status_code:",promote_mj_status_code)
        return resp_promote_mj_details
    else:
        return resp_start_mj_details

    #print("------------------------------------------New Ending DMS for job no.:",dms_df["index"],"------------------------------------------")

#Get data from tables to create a dataframe for all the source instances
source_df = pd.DataFrame({'sp_name': ["wave12-postgres-profile-new-"], 
                            'tp_name': ["wave1t=2-postgres-profile-new-"], 
                            'mj_name': ["wave12dt1-postgres-mj-new-",], 
                            'sp_host': ['34.72.187.12'], 
                            'sp_username': ['dbmig'], 
                            'sp_pwd': ['dbmig'],
                            'tp_version': ['POSTGRES_12'], 
                            'tp_tier': ['db-custom-1-3840'],
                            'tp_version': ['POSTGRES_12'], 
                            'tp_engine': ['POSTGRESQL']
                            })

source_df["index"]= source_df.reset_index().index
source_df["sp_name"]=source_df["sp_name"] + source_df["index"].map(str)
source_df["tp_name"]=source_df["tp_name"] + source_df["index"].map(str)
source_df["mj_name"]=source_df["mj_name"] + source_df["index"].map(str)
source_df=source_df.astype('string')



#@bp.route('', methods=['GET'])


    
    

#@bp.route('/dms', methods=['POST'])
@bp.route('/dms')
def start_dms_migration():
    """Update Operation and OperationDetails statuses/steps."""
    start_time = datetime.datetime.now()
    print("Start pandarallel apply: ")
    source_df = pd.DataFrame({'sp_name': ["waven29s-postgres-profile-new-"], 
                            'tp_name': ["waven29t-postgres-profile-new-"], 
                            'mj_name': ["waven2j-postgres-mj-new-",], 
                            'sp_host': ['34.72.187.12'], 
                            'sp_username': ['dbmig'], 
                            'sp_pwd': ['dbmig'],
                            'tp_version': ['POSTGRES_12'], 
                            'tp_tier': ['db-custom-1-3840'],
                            'tp_version': ['POSTGRES_12'], 
                            'tp_engine': ['POSTGRESQL']
                            })

    source_df["index"]= source_df.reset_index().index
    source_df["sp_name"]=source_df["sp_name"] + source_df["index"].map(str)
    source_df["tp_name"]=source_df["tp_name"] + source_df["index"].map(str)
    source_df["mj_name"]=source_df["mj_name"] + source_df["index"].map(str)
    source_df=source_df.astype('string')
    #source_df['output'] = source_df.parallel_apply(run_dms_test, axis=1) #temp commented out


    #new section
    engine = sqlalchemy.create_engine(cs.DATABASE_URL)
    sql=dms_sql.sql_query

    df = pd.read_sql(sql,con=engine)
    engine.dispose()

    if df.empty:#
        print("df status:",df.empty)
        return "Database details not found for CloudSQL migration", 400


    print("df columns:",df.columns)
    df['sp_name']='sp-' + df['project_name'].astype(str) + '-sourcedbid-' + df['source_db_id'].astype(str)
    df['tp_name']='tp-' + df['project_name'].astype(str) + '-targetdbid-' + df['target_db_id'].astype(str) 
    df['mj_name']='mj-' + df['project_name'].astype(str) + '-sourcedbid-' + df['source_db_id'].astype(str) + '-targetdbid-' + df['target_db_id'].astype(str)
    df['secret_data']= df.secret_name.apply(get_secret)

    return df.to_dict('list') #data # working
    #new section

    end_time = datetime.datetime.now()
    pp_total_time = end_time - start_time
    print("End of pandas and pandarallel apply: ")
    print(source_df)
    print("time taken for pandas and pandarallel apply: ", pp_total_time)


    return source_df.to_dict('list'), 201
    #return {'data':'ok'},201

#commented out temporarily for now:sneha
###start_time = datetime.datetime.now()
####print("Start pandarallel apply: ")
###source_df['output'] = source_df.parallel_apply(run_dms_test, axis=1)
###
###end_time = datetime.datetime.now()
###pp_total_time = end_time - start_time
###print("End of pandas and pandarallel apply: ")
###print(source_df)
###print("time taken for pandas and pandarallel apply: ", pp_total_time)


"""
source_df_pl = dd.from_pandas(source_df, npartitions=32)
start_time = datetime.datetime.now()
dask_series = source_df_pl.apply(run_dms_test, axis=1, meta='string')  
source_df_pl['output'] = dask_series

#### Convert Dask DataFrame back to Pandas DataFrame
df_new = source_df_pl.compute()
end_time = datetime.datetime.now()
print("End of dask apply: ")
print(df_new)
print("time taken for dask apply: ", end_time - start_time)
"""
