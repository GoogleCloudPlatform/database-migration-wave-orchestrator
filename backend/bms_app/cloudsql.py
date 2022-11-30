#Initial draft of end to end DMS invokation with hardcoding and sequential approach
import google.auth
import google.auth.transport.requests

from googleapiclient import discovery

from oauth2client.client import GoogleCredentials
from googleapiclient import errors

import time
import uuid


# getting the credentials and project details for gcp project
credentials, project_id = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"]) 


#getting request object
auth_req = google.auth.transport.requests.Request()

print(credentials.valid) # prints False
credentials.refresh(auth_req) #refresh token
#cehck for valid credentials
print(credentials.valid)  # prints True
print(credentials.token) # prints token
print(project_id) 
#working block ends


#Function to create a discovery resource for database migration service
def get_service() -> discovery.Resource:
    dms_service = discovery.build('datamigration', 'v1', credentials=credentials)
    return dms_service


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
        print('sleeping for 5 sec')
        time.sleep(5)
        request_get_lro_state = service.projects().locations().operations().get(
                          name=f'{name}',
                          )
        responseget_lro_state= request_get_lro_state.execute()
        check_wip = responseget_lro_state['done']
    if responseget_lro_state['done']:
        if 'response' in responseget_lro_state:
            print('success')
            print(responseget_lro_state['response'])
            return 'SUCCESS:' + '200' + ':' + responseget_lro_state['response']['name']
        elif 'error' in responseget_lro_state:
            print('error')
            print(responseget_lro_state['error'])
            print('ERROR:' + str(responseget_lro_state['error']['code']) + ':' + responseget_lro_state['error']['message'])
            return 'ERROR:' + str(responseget_lro_state['error']['code']) + ':' + responseget_lro_state['error']['message']



#Function to create database migration connection profile
def create_connection_profile(gcp_project_id: str, profile_name: str, config: dict) -> str:
    service = get_service()
    request_create_connprofile = service.projects().locations().connectionProfiles().create(
    parent=f'projects/{gcp_project_id}/locations/us-central1', #get the location programatiically later
    connectionProfileId=profile_name,
    body=config
    )
    
    print("before calling")
    
    try:
        response_create_connprofile= request_create_connprofile.execute()
    except errors.HttpError as err:
        print(err.resp.reason)
        print(err)
        return 'ERROR:' + str(err.resp.status) + ':' + err.resp.reason
    
    print(response_create_connprofile)
    print(response_create_connprofile['metadata']['@type'])


    if response_create_connprofile['metadata']['@type'].endswith('OperationMetadata'):
        print("I am here")
        cp_name=response_create_connprofile['name']
        return get_lro_details(cp_name)
    else:
        return 'ERROR:' + '404' + ':' + 'OperationMetadata not found for Connection profile creation'
        print("here")


#Function to create database migration job
def create_migration_job(gcp_project_id: str, job_name: str, job_request_id: str, config: dict) -> str:
    service = get_service()
    request_create_migjob = service.projects().locations().migrationJobs().create(
    parent=f'projects/{gcp_project_id}/locations/us-central1', #get the location programatiically later
    migrationJobId=job_name,
    requestId=job_request_id, 
    body=config
    )
    
    print("before calling")
    
    try:
        response_create_migjob= request_create_migjob.execute()
    except errors.HttpError as err:
        print(err.resp.reason)
        print(err)
        return 'ERROR:' + str(err.resp.status) + ':' + err.resp.reason
    
    print(response_create_migjob)
    print(response_create_migjob['metadata']['@type'])


    if response_create_migjob['metadata']['@type'].endswith('OperationMetadata'):
        print("I am here")
        mj_name=response_create_migjob['name']
        return get_lro_details(mj_name)
    else:
        return 'ERROR:' + '404' + ':' + 'OperationMetadata not found for Migration Job creation'
        print("here")

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
    
    print("before calling migrationJobs.verify")
    
    try:
        response_verify_migjob= request_verify_migjob.execute()
    except errors.HttpError as err:
        print(err.resp.reason)
        print(err)
        return 'ERROR:' + str(err.resp.status) + ':' + err.resp.reason
    
    print(response_verify_migjob)
    print(response_verify_migjob['metadata']['@type'])


    if response_verify_migjob['metadata']['@type'].endswith('OperationMetadata'):
        print("I am here migrationJobs.verify")
        mj_name=response_verify_migjob['name']
        return get_lro_details(mj_name)
    else:
        return 'ERROR:' + '404' + ':' + 'OperationMetadata not found for Migration Job verification'
        print("here")


#Function to start database migration job
def start_migration_job(job_name: str) -> str:

    service = get_service()
    request_start_migjob = service.projects().locations().migrationJobs().start(
     name=f'{job_name}',
    )
    
    print("before calling migrationJobs.start")
    
    try:
        response_start_migjob= request_start_migjob.execute()
    except errors.HttpError as err:
        print(err.resp.reason)
        print(err)
        return 'ERROR:' + str(err.resp.status) + ':' + err.resp.reason
    
    print(response_start_migjob)
    print(response_start_migjob['metadata']['@type'])


    if response_start_migjob['metadata']['@type'].endswith('OperationMetadata'):
        print("I am here migrationJobs.start")
        mj_name=response_start_migjob['name']
        return get_lro_details(mj_name)
    else:
        return 'ERROR:' + '404' + ':' + 'OperationMetadata not found for the start of Migration Job'
        print("here")


#Function to promote database migration job
def promote_migration_job(job_name: str) -> str:

    service = get_service()
    request_promote_migjob = service.projects().locations().migrationJobs().promote(
     name=f'{job_name}',
    )
    
    print("before calling migrationJobs.promote")
    
    try:
        response_promote_migjob= request_promote_migjob.execute()
    except errors.HttpError as err:
        print(err.resp.reason)
        print(err)
        return 'ERROR:' + str(err.resp.status) + ':' + err.resp.reason
    
    print(response_promote_migjob)
    print(response_promote_migjob['metadata']['@type'])


    if response_promote_migjob['metadata']['@type'].endswith('OperationMetadata'):
        print("I am here migrationJobs.promote")
        mj_name=response_promote_migjob['name']
        return get_lro_details(mj_name)
    else:
        return 'ERROR:' + '404' + ':' + 'OperationMetadata not found for promoting the Migration Job'
        print("here")

#Function to fetch details of a specific database migration target connection profile #Change this later to return specfics of source profile as well
def get_connection_profile(profile_detail: str) -> str:
    service = get_service()
    request_get_connprofile = service.projects().locations().connectionProfiles().get(
                                  name=f'{profile_detail}',
                                  )
    
    print("before calling connectionProfiles.get")
    
    try:
        response_get_connprofile= request_get_connprofile.execute()
    except errors.HttpError as err:
        print(err.resp.reason)
        print(err)
        return 'ERROR:' + str(err.resp.status) + ':' + err.resp.reason

    return 'SUCCESS:' + '200' + ':' + response_get_connprofile['cloudsql']['publicIp']


for dms_job_no in range(3):
    #Create the configuration for source connection profile and call the fucnction to create the profile
    print("------------------------------------------Starting DMS for job no.:",dms_job_no,"------------------------------------------")
    cp_name = "postgres-profile-new-" + str(dms_job_no)
    sp_config={"name":f"{cp_name}","displayName":f"{cp_name}","postgresql":{"host":"34.72.187.12","port":5432,"username":"dbmig","password":"dbmig"}}



    resp_scp = create_connection_profile(project_id, cp_name, sp_config)
    scp_message = resp_scp[resp_scp.rfind(':') + 1:]
    scp_status_code = resp_scp[resp_scp.find(':') + 1: resp_scp.rfind(':') ]
    print("for dms_job_no:",dms_job_no," ,scp_message:",scp_message)
    print("for dms_job_no:",dms_job_no," ,scp_status_code:",scp_status_code)

    tp_config={}
    tcp_status_code = 0
    tcp_message = ''
    #Create the configuration for target connection profile and call the fucnction to create the profile
    if scp_status_code == '200':
        #get the location programatiically later
        tcp_name = "postgres-target-profile-new-" + str(dms_job_no)
        tp_config={ "name":f"{tcp_name}",
          "displayName": f"{tcp_name}",
          "cloudsql": {
            "settings": {
              "databaseVersion": "POSTGRES_12",
              "tier": "db-custom-1-3840",
              "storageAutoResizeLimit": 0,
              "activationPolicy": "ALWAYS",
              "autoStorageIncrease": False,
              "zone": "us-central1-b",
              "sourceId": f"{scp_message}",
              "rootPassword":"sourcewaverunner2"    
            }
          }
        }

        print("for dms_job_no:",dms_job_no," ,tp_config:",tp_config)

        resp_tcp = create_connection_profile(project_id, tcp_name, tp_config)
        tcp_message = resp_tcp[resp_tcp.rfind(':') + 1:]
        tcp_status_code = resp_tcp[resp_tcp.find(':') + 1: resp_tcp.rfind(':') ]
        print("for dms_job_no:",dms_job_no," ,resp_tcp:",resp_tcp)
        print("for dms_job_no:",dms_job_no," ,tcp_message:",tcp_message)
        print("for dms_job_no:",dms_job_no," ,tcp_status_code:",tcp_status_code)


    get_cp_status_code = 0
    get_cp_message = ''
    #Fetch details of the given target conection profile by invoking connectionProfiles.get method 
    if tcp_status_code == '200':
        resp_get_cp_details =  get_connection_profile(tcp_message)
        get_cp_message = resp_get_cp_details[resp_get_cp_details.rfind(':') + 1:]
        get_cp_status_code = resp_get_cp_details[resp_get_cp_details.find(':') + 1: resp_get_cp_details.rfind(':') ]
        print("for dms_job_no:",dms_job_no," ,resp_get_cp_details:",resp_get_cp_details)
        print("for dms_job_no:",dms_job_no," ,get_cp_message:",get_cp_message)
        print("for dms_job_no:",dms_job_no," ,get_cp_status_code:",get_cp_status_code)



    mj_config={}
    mj_status_code = 0
    mj_message = ''
    #Create the configuration for migration job and call the function to create the job
    if get_cp_status_code == '200':
        #get the location programatiically later
        mj_name = "postgres-migjob-new-"+ str(dms_job_no)
        mj_request_id = uuid.uuid4() 
        mj_config={ "name":f"{mj_name}",
          "displayName": f"{mj_name}",
          "type":"CONTINUOUS",
           "source":f"{scp_message}",
           "destination":f"{tcp_message}",
           "sourceDatabase":{
              "provider":"DATABASE_PROVIDER_UNSPECIFIED",
              "engine":"POSTGRESQL"
           },
           "destinationDatabase":{
              "provider":"CLOUDSQL",
              "engine":"POSTGRESQL"
           }
        }

        #print("for dms_job_no:",dms_job_no," ,resp_tcp:",mj_config)

        resp_mj = create_migration_job(project_id, mj_name, mj_request_id, mj_config)
        mj_message = resp_mj[resp_mj.rfind(':') + 1:]
        mj_status_code = resp_mj[resp_mj.find(':') + 1: resp_mj.rfind(':') ]
        print("for dms_job_no:",dms_job_no," ,resp_mj:",resp_mj)
        print("for dms_job_no:",dms_job_no," ,mj_message:",mj_message)
        print("for dms_job_no:",dms_job_no," ,mj_status_code:",mj_status_code)



    get_mj_status_code = 0
    get_mj_message = ''
    #Fetch details of the migration job verification
    if mj_status_code == '200':
        resp_get_mj_details =  verify_migration_job(mj_message)
        get_mj_message = resp_get_mj_details[resp_get_mj_details.rfind(':') + 1:]
        get_mj_status_code = resp_get_mj_details[resp_get_mj_details.find(':') + 1: resp_get_mj_details.rfind(':') ]
        print("for dms_job_no:",dms_job_no,",resp_get_mj_details:",resp_get_mj_details)
        print("for dms_job_no:",dms_job_no,",get_mj_message:",get_mj_message)
        print("for dms_job_no:",dms_job_no,",get_mj_status_code:",get_mj_status_code)
        


    start_mj_status_code = 0
    start_mj_message = ''
    wait_time_before_promote = 60 # in seconds, to be supplied
    #print("mj_status_code:",mj_status_code)
    #Start the migration job if the job is created, even if there is a warning for unsupported tables during verification(check Sneha)
    if mj_status_code == '200' and ((get_mj_status_code == '200') or (get_mj_message=='Some table(s) have limited support.')):
        print("Starting dms_job_no:",dms_job_no)
        resp_start_mj_details =  start_migration_job(mj_message)
        start_mj_message = resp_start_mj_details[resp_start_mj_details.rfind(':') + 1:]
        start_mj_status_code = resp_start_mj_details[resp_start_mj_details.find(':') + 1: resp_start_mj_details.rfind(':') ]
        print("for dms_job_no:",dms_job_no,",resp_start_mj_details:",resp_start_mj_details)
        print("for dms_job_no:",dms_job_no,",start_mj_message:",start_mj_message)
        print("for dms_job_no:",dms_job_no,",start_mj_status_code:",start_mj_status_code)


    if start_mj_status_code == '200':
        if wait_time_before_promote > 0 : # check if we need a default timer too
            print('sleeping for secs: ',wait_time_before_promote)
            time.sleep(wait_time_before_promote)

        print("Promoting dms_job_no:",dms_job_no)
        resp_promote_mj_details =  promote_migration_job(mj_message)
        promote_mj_message = resp_promote_mj_details[resp_promote_mj_details.rfind(':') + 1:]
        promote_mj_status_code = resp_promote_mj_details[resp_promote_mj_details.find(':') + 1: resp_promote_mj_details.rfind(':') ]
        print("for dms_job_no:",dms_job_no,",resp_promote_mj_details:",resp_promote_mj_details)
        print("for dms_job_no:",dms_job_no,",promote_mj_message:",promote_mj_message)
        print("for dms_job_no:",dms_job_no,",promote_mj_status_code:",promote_mj_status_code)

    print("------------------------------------------Ending DMS for job no.:",dms_job_no,"------------------------------------------")
