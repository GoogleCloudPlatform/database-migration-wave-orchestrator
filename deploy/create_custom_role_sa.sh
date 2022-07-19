#!/bin/bash
# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#
# Bash script to create a custom IAM role and service account for Terraform provisiong
#
# First, an IAM (custom) role and a Service Account are created.
# Then, specific IAM permissions are granted to the IAM role.
# Finally, the following native GCP roles are granted to the SA:
#
# 	- role/Cloud SQL Admin
# 	- role/Secret Manager Secret Accessor
# 	- role/Security Reviewer
#
#
# bash create_custom_role_sa.sh PROJECT_ID IAM_CUSTOM_ROLE_NAME IAM_SA_NAME Y|N BUCKET_NAME_TF
#
# Where:
# -----
# PROJECT_ID		: GCP Project ID where the custom role and SA will be created
# IAM_CUSTOM_ROLE	: Name for the GCP IAM custom role to be created
# IAM_SA_NAME		: Name of the GCP Service Account to create
#
# EXAMPLE: bash create_custom_role_sa.sh my_gcp_project123 custom_role_tf_provision sa_tf_provision
# -------
#---------------------------------------------------------------------------------------

# Get full path for gloud command
GCLOUD_CMD="$(which gcloud)";

$GCLOUD_CMD iam roles create $2 --project $1 --title "$2" --description "Custom Role for TF Provisioning" --permissions=clientauthconfig.brands.create,clientauthconfig.brands.delete,clientauthconfig.brands.get,clientauthconfig.brands.list,clientauthconfig.brands.update,clientauthconfig.clients.create,clientauthconfig.clients.createSecret,clientauthconfig.clients.delete,clientauthconfig.clients.get,clientauthconfig.clients.getWithSecret,clientauthconfig.clients.list,clientauthconfig.clients.listWithSecrets,clientauthconfig.clients.undelete,clientauthconfig.clients.update,cloudsql.databases.create,cloudsql.databases.delete,cloudsql.databases.get,cloudsql.databases.list,cloudsql.databases.update,cloudsql.instances.connect,cloudsql.instances.create,cloudsql.instances.delete,cloudsql.instances.get,cloudsql.instances.list,cloudsql.instances.login,cloudsql.users.delete,cloudsql.users.list,cloudsql.users.update,compute.backendServices.create,compute.backendServices.delete,compute.backendServices.get,compute.backendServices.getIamPolicy,compute.backendServices.list,compute.backendServices.setIamPolicy,compute.backendServices.update,compute.backendServices.use,compute.firewalls.create,compute.firewalls.delete,compute.firewalls.get,compute.firewalls.list,compute.firewalls.update,compute.globalAddresses.create,compute.globalAddresses.delete,compute.globalAddresses.get,compute.globalAddresses.list,compute.globalAddresses.use,compute.globalForwardingRules.create,compute.globalForwardingRules.delete,compute.globalForwardingRules.get,compute.globalForwardingRules.list,compute.globalForwardingRules.setLabels,compute.globalForwardingRules.setTarget,compute.globalForwardingRules.update,compute.networks.create,compute.networks.delete,compute.networks.get,compute.networks.list,compute.networks.update,compute.networks.updatePolicy,compute.regionNetworkEndpointGroups.create,compute.regionNetworkEndpointGroups.delete,compute.regionNetworkEndpointGroups.get,compute.regionNetworkEndpointGroups.list,compute.regionNetworkEndpointGroups.use,compute.regionOperations.delete,compute.regionOperations.get,compute.regionOperations.getIamPolicy,compute.regionOperations.list,compute.regionOperations.setIamPolicy,compute.sslCertificates.create,compute.sslCertificates.delete,compute.sslCertificates.get,compute.sslCertificates.list,compute.subnetworks.create,compute.subnetworks.delete,compute.subnetworks.get,compute.subnetworks.list,compute.subnetworks.update,compute.targetHttpProxies.create,compute.targetHttpProxies.delete,compute.targetHttpProxies.get,compute.targetHttpProxies.list,compute.targetHttpProxies.use,compute.targetHttpsProxies.create,compute.targetHttpsProxies.delete,compute.targetHttpsProxies.get,compute.targetHttpsProxies.list,compute.targetHttpsProxies.setSslCertificates,compute.targetHttpsProxies.setSslPolicy,compute.targetHttpsProxies.use,compute.urlMaps.create,compute.urlMaps.delete,compute.urlMaps.get,compute.urlMaps.list,compute.urlMaps.update,compute.urlMaps.use,dns.managedZoneOperations.get,dns.managedZoneOperations.list,dns.managedZones.create,dns.managedZones.delete,dns.managedZones.get,dns.managedZones.list,dns.managedZones.update,iam.roles.create,iam.roles.delete,iam.roles.get,iam.roles.list,iam.roles.undelete,iam.roles.update,iam.serviceAccountKeys.create,iam.serviceAccountKeys.delete,iam.serviceAccountKeys.get,iam.serviceAccountKeys.list,iam.serviceAccounts.actAs,iam.serviceAccounts.create,iam.serviceAccounts.delete,iam.serviceAccounts.disable,iam.serviceAccounts.enable,iam.serviceAccounts.get,iam.serviceAccounts.getAccessToken,iam.serviceAccounts.getIamPolicy,iam.serviceAccounts.list,iam.serviceAccounts.setIamPolicy,iam.serviceAccounts.undelete,iam.serviceAccounts.update,iap.projects.getSettings,iap.projects.updateSettings,iap.web.getIamPolicy,iap.web.getSettings,iap.web.setIamPolicy,iap.web.updateSettings,iap.webServiceVersions.accessViaIAP,iap.webServiceVersions.getIamPolicy,iap.webServiceVersions.getSettings,iap.webServiceVersions.setIamPolicy,iap.webServiceVersions.updateSettings,iap.webServices.getIamPolicy,iap.webServices.getSettings,iap.webServices.setIamPolicy,iap.webServices.updateSettings,iap.webTypes.getIamPolicy,iap.webTypes.getSettings,iap.webTypes.setIamPolicy,monitoring.timeSeries.list,oauthconfig.clientpolicy.get,oauthconfig.testusers.get,oauthconfig.testusers.update,oauthconfig.verification.get,oauthpolicymetadata.brandpolicy.createOrUpdate,oauthpolicymetadata.brandpolicy.get,oauthpolicymetadata.brandpolicy.submitVerification,oauthpolicymetadata.clientpolicy.get,oauthtestapp.userwhitelist.read,pubsub.schemas.attach,pubsub.schemas.create,pubsub.schemas.delete,pubsub.schemas.get,pubsub.schemas.getIamPolicy,pubsub.schemas.list,pubsub.schemas.setIamPolicy,pubsub.schemas.validate,pubsub.snapshots.create,pubsub.snapshots.delete,pubsub.snapshots.get,pubsub.snapshots.list,pubsub.snapshots.setIamPolicy,pubsub.snapshots.update,pubsub.subscriptions.consume,pubsub.subscriptions.create,pubsub.subscriptions.delete,pubsub.subscriptions.get,pubsub.subscriptions.getIamPolicy,pubsub.subscriptions.list,pubsub.subscriptions.setIamPolicy,pubsub.subscriptions.update,pubsub.topics.attachSubscription,pubsub.topics.create,pubsub.topics.delete,pubsub.topics.detachSubscription,pubsub.topics.get,pubsub.topics.getIamPolicy,pubsub.topics.list,pubsub.topics.publish,pubsub.topics.setIamPolicy,pubsub.topics.update,pubsub.topics.updateTag,resourcemanager.projects.get,resourcemanager.projects.getIamPolicy,resourcemanager.projects.setIamPolicy,run.services.create,run.services.delete,run.services.get,run.services.getIamPolicy,run.services.list,run.services.setIamPolicy,run.services.update,secretmanager.locations.get,secretmanager.locations.list,secretmanager.secrets.create,secretmanager.secrets.delete,secretmanager.secrets.get,secretmanager.secrets.getIamPolicy,secretmanager.secrets.list,secretmanager.secrets.setIamPolicy,secretmanager.secrets.update,secretmanager.versions.access,secretmanager.versions.add,secretmanager.versions.destroy,secretmanager.versions.disable,secretmanager.versions.enable,secretmanager.versions.get,secretmanager.versions.list,serviceconsumermanagement.consumers.get,servicemanagement.services.create,servicemanagement.services.delete,servicemanagement.services.get,servicemanagement.services.list,servicemanagement.services.update,serviceusage.quotas.get,serviceusage.quotas.update,serviceusage.services.disable,serviceusage.services.enable,serviceusage.services.get,serviceusage.services.list,storage.buckets.create,storage.buckets.delete,storage.buckets.get,storage.buckets.getIamPolicy,storage.buckets.list,storage.buckets.update,storage.objects.create,storage.objects.delete,storage.objects.get,storage.objects.getIamPolicy,storage.objects.list,storage.objects.setIamPolicy,storage.objects.update,compute.addresses.create,compute.addresses.delete,compute.addresses.list,compute.addresses.get,compute.addresses.use,compute.images.get,compute.images.list,compute.instanceTemplates.create,compute.instanceTemplates.delete,compute.instanceTemplates.get,compute.instanceTemplates.list,compute.zones.get,compute.zones.list,compute.instances.create,compute.instances.delete,compute.instances.get,compute.instances.list,compute.instances.update,compute.instanceTemplates.useReadOnly,compute.disks.create,compute.disks.delete,compute.disks.get,compute.disks.list,compute.disks.update,compute.disks.use,compute.subnetworks.use,compute.subnetworks.useExternalIp,compute.instances.setMetadata,compute.zoneOperations.get

$GCLOUD_CMD iam service-accounts create $3 --description="SA for Terraform Provisioning" --display-name="$3"

# Assign custom role to the SA
$GCLOUD_CMD projects add-iam-policy-binding $1 --member "serviceAccount:$3@$1.iam.gserviceaccount.com" --role "projects/$1/roles/$2"

# Assign native IAM roles to the SA
$GCLOUD_CMD projects add-iam-policy-binding $1 --member "serviceAccount:$3@$1.iam.gserviceaccount.com" --role "roles/cloudsql.admin"
$GCLOUD_CMD projects add-iam-policy-binding $1 --member "serviceAccount:$3@$1.iam.gserviceaccount.com" --role "roles/secretmanager.secretAccessor"
$GCLOUD_CMD projects add-iam-policy-binding $1 --member "serviceAccount:$3@$1.iam.gserviceaccount.com" --role "roles/iam.securityReviewer"
