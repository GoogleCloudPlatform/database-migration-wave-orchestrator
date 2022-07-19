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
# GCE metadata for BMS application
# --------------------------------
#
#  1) GCE description
#  2) Create time
#  3) State
#  4) Machine Type
#  5) Luns
#  6) Networks
#  7) CPU, RAM memory
#  8) Finally, consolidate all JSON output in one centralized location

# Target nodes setup to simulate BMS servers (boot script for GCE - Single and RAC)
#
#  1) User "customeradmin" creation. HOME /home/customeradmin
#  2) Change /etc/ssh/sshd_config --> PasswordAuthentication yes
#  3) Make customeradmin sudoer (/etc/sudoers)
#  4) Create new secret (secret name: hostname) to store customeradmin password
#  5) Store password for customeradmin user in Secret Manager
#  6) Logs created in /var/log/startup-script-gce-log (to check these steps)
#
#  Once the GCE is created, the password for the customeradmin user can be obtained from Secret Manager:
#  gcloud beta secrets versions access latest --secret='<REPLACE_THIS_WITH_HOSTNAME>'

gcename=`hostname`; sequence=${gcename: -2};

BUCKET=$(curl http://metadata/computeMetadata/v1/instance/attributes/value_of_bucket -H "Metadata-Flavor: Google")
COUNT_GCE_RANDOM=$(curl http://metadata/computeMetadata/v1/instance/attributes/value_of_count -H "Metadata-Flavor: Google")
LOCATION=$(curl http://metadata/computeMetadata/v1/instance/attributes/value_of_region -H "Metadata-Flavor: Google")

# Vars
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)"

# Get full path for useradd, mkdir, sed, systemctl, tr and perl commands
USERADD_CMD="$(which useradd)";
USERMOD_CMD="$(which usermod)";
ADDUSER_CMD="$(which adduser)";
OPENSSL_CMD="$(which openssl)";
MKDIR_CMD="$(which mkdir)";
SYSTEMCTL_CMD="$(which systemctl)";
SED_CMD="$(which sed)";
CHMOD_CMD="$(which chmod)";
TR_CMD="$(which tr)";
PERL_CMD="$(which perl)";

SALT="C51"
USER_PASS="$(tr -dc A-Za-z < /dev/urandom | head -c 8; echo '')"
HASH=`${PERL_CMD} -e "print crypt(${USER_PASS},${SALT})"`

response_mkdir="$($MKDIR_CMD /var/log/startup-script-gce-log >/dev/null 2>&1)"
$CHMOD_CMD go+rw /var/log/startup-script-gce-log

response_useradd="$($USERADD_CMD --home-dir /home/customeradmin customeradmin || echo useradd_failed)"
user_status=$?
echo "User creation (customeradmin) output: " $user_status > /var/log/startup-script-gce-log/useradd_output.log

response_check_sudoer=`grep "customeradmin ALL=(ALL) NOPASSWD: ALL" /etc/sudoers || echo "not found"`
if [[ $response_check_sudoer == "not found" ]]; then
    echo "customeradmin ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
    echo "Status customeradmin in /etc/sudoers: Added"
else
    echo "Status customeradmin in /etc/sudoers: Already existed"
fi

HOSTNAME=`hostname`
gcloud beta secrets create $HOSTNAME --labels application=migscaler
secret_creation=$?
echo "Secret creation: " $secret_creation > /var/log/startup-script-gce-log/useradd_output.log

echo ${USER_PASS} | gcloud beta secrets versions add $HOSTNAME --data-file=-
secret_store_status=$?
echo "Store password in Secret Manager: " $secret_store_status > /var/log/startup-script-gce-log/useradd_output.log

cd /etc/ssh

response_sed="$($SED_CMD -i s/"PasswordAuthentication no"/"PasswordAuthentication yes"/g /etc/ssh/sshd_config || echo sshd_change_failed)"
sed_status=$?
echo "Change parameter PasswordAuthentication status: " $sed_status > /var/log/startup-script-gce-log/sshd_config_output.log

response_restartsshd="$($SYSTEMCTL_CMD restart sshd)"
restart_sshd=$?
echo "Restart sshd daemon output: " $restart_sshd >> /var/log/startup-script-gce-log/sshd_config_output.log

${USERMOD_CMD} -p ${HASH} customeradmin
echo "User pass: " ${USER_PASS} >> /var/log/startup-script-gce-log/useradd_output.log


#
#
#
# GCE metadata
#
#
#
#

# set -xv

# Vars
GCLOUD_CMD="$(which gcloud)";
GSUTIL_CMD="$(which gsutil)";
GREP_CMD="/bin/grep";
SORT_CMD="$(which sort)";
LSBLK_CMD="$(which lsblk)";
PASTE_CMD="$(which paste)";
AWK_CMD="$(which awk)";
SED_CMD="$(which sed)";
CAT_CMD="$(which cat)";
HEAD_CMD="$(which head)";
DATE_CMD="$(which date)";
MKDIR_CMD="$(which mkdir)";
YUM_CMD="$(which yum)";
JQ_CMD="$(which jq)";
IFCONFIG_CMD="$(which ifconfig)";
LSCPU_CMD="$(which lscpu)";
HOSTNAME=`hostname`

${MKDIR_CMD} /var/log/gce_metadata
${MKDIR_CMD} /var/log/gce_metadata/json

chmod -R ug+wr /var/log/gce_metadata

${YUM_CMD} install jq -y

rm -rf /var/log/gce_metadata/*.json
rm -rf /var/log/gce_metadata/json/*.json

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)"

# echo '[' >> $SCRIPT_DIR/local_gce_bms_temp.txt
echo '{' >> $SCRIPT_DIR/local_gce_bms_temp.txt

# ------------------------------------------------------------------------------------------
# Setup to store the JSON output in the centralized location (GCS) - gs://bucket_name
# ------------------------------------------------------------------------------------------

new_file=false
# ${GSUTIL_CMD} ls gs://oracle-bms-go3-inv/gce_metadata/*.json 2> /var/log/gce_metadata/json/gsutil_ls_output.out
${GSUTIL_CMD} ls gs://${BUCKET}/gce_metadata/*.json 2> /var/log/gce_metadata/json/gsutil_ls_output.out

if [ $? == 1 ]; then
        grep 'One or more URLs matched no objects' /var/log/gce_metadata/json/gsutil_ls_output.out
        new_file=true
        json_file_name=`${DATE_CMD} +%F-%T-%Z-%N -u`".json"
        # echo '[' >> $SCRIPT_DIR/gce_bms_temp.txt
        echo '{' >> $SCRIPT_DIR/gce_bms_temp.txt

    else

        cd /var/log/gce_metadata/json

	current_year=`date +%Y`

        # ${GSUTIL_CMD} cp gs://oracle-bms-go3-inv/gce_metadata/*.json /var/log/gce_metadata/json
        ${GSUTIL_CMD} cp gs://${BUCKET}/gce_metadata/*.json /var/log/gce_metadata/json

        chmod ug+w /var/log/gce_metadata/json/*.json
        date_of_most_recent_json_file=`ls -1 ${current_year}*.json | awk -F '.' '{print $1}' | ${SORT_CMD} | tail -1 | awk -F '-' '{print $1"-"$2"-"$3}'`
        timestamp_today=`${DATE_CMD} +%F-%T-%Z-%N -u | ${AWK_CMD} -F '-' '{print $1"-"$2"-"$3}'`

        if [ "$date_of_most_recent_json_file" == "$timestamp_today" ]; then
            json_file_name=`ls -1 ${current_year}*.json | ${AWK_CMD} -F '.' '{print $1}' | ${SORT_CMD} | tail -1`".json"
            # echo '[' >> $SCRIPT_DIR/gce_bms_temp.txt
            echo '{' >> $SCRIPT_DIR/gce_bms_temp.txt

            json_blocks=`${JQ_CMD} length ${json_file_name}`
            json_total_lines=`${CAT_CMD} ${json_file_name} | wc -l`
            json_total_lines_head=`echo ${json_total_lines} | awk '{print int( ($json_total_lines - 2) )}'`
            ${HEAD_CMD} -${json_total_lines_head} ${json_file_name} > $SCRIPT_DIR/gce_bms_existing.txt
            # echo '},' >> $SCRIPT_DIR/gce_bms_existing.txt
            echo '},' >> $SCRIPT_DIR/gce_bms_existing.txt

        else
            new_file=true
            json_file_name=`${DATE_CMD} +%F-%T-%Z-%N -u`".json"
            # echo '[' >> $SCRIPT_DIR/gce_bms_temp.txt
            echo '{' >> $SCRIPT_DIR/gce_bms_temp.txt
        fi
fi


# ------------------------------------------------------------------------------------------
# JSON output creation
# ------------------------------------------------------------------------------------------

# ORIGINAL VERSION APRIL 07 --> $GCLOUD_CMD compute instances describe $HOSTNAME --format="json" --zone=europe-west1-b | jq '{"name": .name}','{"create_time": .creationTimestamp}','{"state": .status}' | grep '"' | sed -e 's/^[ \t]*//'>> $SCRIPT_DIR/gce_bms_temp.txt

# ORIGINAL VERSION APRIL 07 --> $GCLOUD_CMD compute instances describe $HOSTNAME --format="json" --zone=europe-west1-b | jq '{"name": .name}','{"create_time": .creationTimestamp}','{"state": .status}' | grep '"' | sed -e 's/^[ \t]*//'>> $SCRIPT_DIR/local_gce_bms_temp.txt

$GCLOUD_CMD compute instances describe $HOSTNAME --format="json" --zone=europe-west1-b | jq '{"name": .name}','{"state": .status}' | grep '"' | sed -e 's/^[ \t]*//'>> $SCRIPT_DIR/gce_bms_temp.txt

$GCLOUD_CMD compute instances describe $HOSTNAME --format="json" --zone=europe-west1-b | jq '{"name": .name}','{"state": .status}' | grep '"' | sed -e 's/^[ \t]*//'>> $SCRIPT_DIR/local_gce_bms_temp.txt

while read p; do
    if [[ "$p" != "[" && "$p" != "{" ]]; then
        echo $p"," >> $SCRIPT_DIR/gce_bms_description.txt
    else
        echo $p >> $SCRIPT_DIR/gce_bms_description.txt
    fi
done < $SCRIPT_DIR/gce_bms_temp.txt

while read p; do
    if [[ "$p" != "[" && "$p" != "{" ]]; then
        echo $p"," >> $SCRIPT_DIR/local_gce_bms_description.txt
    else
        echo $p >> $SCRIPT_DIR/local_gce_bms_description.txt
    fi
done < $SCRIPT_DIR/local_gce_bms_temp.txt

# REMOVED APRIL 07 --> var_machine_type=`$GCLOUD_CMD compute instances describe $HOSTNAME --zone=europe-west1-b --format="value(machineType.scope(machineTypes))"`
# REMOVED APRIL 07 --> echo '"machineType":' '"'$var_machine_type'",' >> $SCRIPT_DIR/gce_bms_description.txt
# REMOVED APRIL 07 --> echo '"machineType":' '"'$var_machine_type'",' >> $SCRIPT_DIR/local_gce_bms_description.txt

$GCLOUD_CMD compute instances describe $HOSTNAME --format="json" --zone=europe-west1-b | jq .disks[] | jq '[{"name": .deviceName}','{"size_gb": .diskSizeGb}','{"storage_type": .type}]' | jq -c >> $SCRIPT_DIR/gce_bms_luns.txt

$LSBLK_CMD | grep disk | awk '{print "/dev/"$1"| "$4}' > $SCRIPT_DIR/gce_bms_storage_devices.txt

$PASTE_CMD -d "|" $SCRIPT_DIR/gce_bms_storage_devices.txt $SCRIPT_DIR/gce_bms_luns.txt > $SCRIPT_DIR/luns_large_format.txt

while read p; do
    device=`echo $p | $AWK_CMD -F "|" '{print $1}'`
    slot1=`echo $p | $AWK_CMD -F "|" '{print $3}'`
    slot2=`echo $p | $AWK_CMD -F "|" '{print $4}'`
    slot3=`echo $p | $AWK_CMD -F "|" '{print $5}'`
    echo ${slot1}""${slot2}""${slot3},"\"storage_volume\"":"\"$device\"}," >> $SCRIPT_DIR/luns_large_format1.txt
done < $SCRIPT_DIR/luns_large_format.txt

$SED_CMD -e 's/[{}]//g' $SCRIPT_DIR/luns_large_format1.txt > $SCRIPT_DIR/luns_large_format2.txt
$SED_CMD 's/\[//g' $SCRIPT_DIR/luns_large_format2.txt > $SCRIPT_DIR/luns_large_format3.txt
$SED_CMD 's/\]//g' $SCRIPT_DIR/luns_large_format3.txt > $SCRIPT_DIR/luns_large_format4.txt
$SED_CMD 's/:/,/g' $SCRIPT_DIR/luns_large_format4.txt > $SCRIPT_DIR/luns_large_format5.txt
echo '"luns": [' >> $SCRIPT_DIR/luns_large_format5.txt > $SCRIPT_DIR/luns_large_format6.txt
num_lines=`cat $SCRIPT_DIR/luns_large_format5.txt | wc -l`
num_lines1=`expr $num_lines`
count_lines=0

while read q; do
    count_lines=$((count_lines + 1))
    slot1=`echo $q | awk -F "," '{print $1}'`
    slot2=`echo $q | awk -F "," '{print $2}'`
    slot3=`echo $q | awk -F "," '{print $3}'`
    slot4=`echo $q | awk -F "," '{print $4}'`
    slot5=`echo $q | awk -F "," '{print $5}'`
    slot6=`echo $q | awk -F "," '{print $6}'`
    slot7=`echo $q | awk -F "," '{print $7}'`
    slot8=`echo $q | awk -F "," '{print $8}'`
    if [[ $count_lines -gt 1 && $count_lines -lt $num_lines1 ]]; then
       echo '    {'${slot1}": "${slot2}", "${slot3}": "${slot4}", "${slot5}": "${slot6}", "${slot7}": "${slot8}'},' >> $SCRIPT_DIR/luns_large_format6.txt
    fi
    if [ $count_lines -eq $num_lines1 ]; then
       echo '    {'${slot1}": "${slot2}", "${slot3}": "${slot4}", "${slot5}": "${slot6}", "${slot7}": "${slot8}'}' >> $SCRIPT_DIR/luns_large_format6.txt
    fi
done < $SCRIPT_DIR/luns_large_format5.txt
echo '    ],' >> $SCRIPT_DIR/luns_large_format6.txt

$CAT_CMD $SCRIPT_DIR/luns_large_format6.txt >> $SCRIPT_DIR/gce_bms_description.txt
$CAT_CMD $SCRIPT_DIR/luns_large_format6.txt >> $SCRIPT_DIR/local_gce_bms_description.txt

$IFCONFIG_CMD eth0 | grep 'inet' | grep netmask | awk '{print $2}' > $SCRIPT_DIR/ip_addr.txt
IP_ADDR=`cat $SCRIPT_DIR/ip_addr.txt`

echo '"networks": [{"ipAddress":' '"'$IP_ADDR'"', '"name": "eth0", "type": "CLIENT"}],' >> $SCRIPT_DIR/gce_bms_description.txt
echo '"networks": [{"ipAddress":' '"'$IP_ADDR'"', '"name": "eth0", "type": "CLIENT"}],' >> $SCRIPT_DIR/local_gce_bms_description.txt

export MEM=`$CAT_CMD /proc/meminfo | grep MemTotal | $AWK_CMD '{print $2}'`
MEM1=`echo "$MEM 1024" | $AWK_CMD '{print int( ($1/$2) + 1 )}'`
MEM2=`echo "$MEM1 1024" | $AWK_CMD '{print int( ($1/$2) + 1 )}'`

CPU=`$GREP_CMD physical.id /proc/cpuinfo | wc -l`
SOCKET=`$LSCPU_CMD | grep -i "socket(s)" | awk '{print $2}'`

# REMOVED APRIL 7 --> gce_cpu_mem=`echo '"gce_metadata": {"cpu":' '"'$CPU'"'', "ram":' '"'$MEM2'"'}`

gce_cpu=`echo '"cpu":' '"'$CPU'"',`
gce_socket=`echo '"socket":' '"'$SOCKET'"',`
gce_mem=`echo '"ram":' '"'$MEM2'"',`
gce_location=`echo '"location":' '"'$LOCATION'"'`

echo $gce_cpu >> $SCRIPT_DIR/gce_bms_description.txt
echo $gce_socket >> $SCRIPT_DIR/gce_bms_description.txt
echo $gce_mem >> $SCRIPT_DIR/gce_bms_description.txt
echo $gce_location >> $SCRIPT_DIR/gce_bms_description.txt

echo $gce_cpu >> $SCRIPT_DIR/local_gce_bms_description.txt
echo $gce_socket >> $SCRIPT_DIR/local_gce_bms_description.txt
echo $gce_mem >> $SCRIPT_DIR/local_gce_bms_description.txt
echo $gce_location >> $SCRIPT_DIR/local_gce_bms_description.txt

echo '},' >> $SCRIPT_DIR/local_gce_bms_description.txt

cat $SCRIPT_DIR/local_gce_bms_description.txt > /var/log/gce_metadata/${HOSTNAME}_${json_file_name}


# ------------------------------------------------------------------------------------
# In these lines the JSON file is created, then sent to the centralized location (GCS)
# ------------------------------------------------------------------------------------

if [ "$new_file" == true ]; then
        echo '},' >> $SCRIPT_DIR/gce_bms_description.txt
        # echo ']' >> $SCRIPT_DIR/gce_bms_description.txt
    else
        cd /var/log/gce_metadata/json
        cat $SCRIPT_DIR/gce_bms_description.txt > /var/log/gce_metadata/json/${json_file_name}

        if [ "$date_of_most_recent_json_file" == "$timestamp_today" ]; then
            total_lines_json=`cat $SCRIPT_DIR/gce_bms_description.txt | wc -l`

            cat $SCRIPT_DIR/gce_bms_existing.txt >> $SCRIPT_DIR/gce_bms_total.txt
            ${AWK_CMD} 'FNR>1' $SCRIPT_DIR/gce_bms_description.txt >> $SCRIPT_DIR/gce_bms_total.txt
            echo '},' >> $SCRIPT_DIR/gce_bms_total.txt
            # echo ']' >> $SCRIPT_DIR/gce_bms_total.txt
            rm -rf /var/log/gce_metadata/json/gce_bms_description.txt
            mv $SCRIPT_DIR/gce_bms_total.txt $SCRIPT_DIR/gce_bms_description.txt
            rm -rf /var/log/gce_metadata/json/partial_json_name.json
            
        else
            echo '},' >> $SCRIPT_DIR/gce_bms_description.txt
            # echo ']' >> $SCRIPT_DIR/gce_bms_description.txt
        fi
fi

cat $SCRIPT_DIR/gce_bms_description.txt > /var/log/gce_metadata/json/${json_file_name}

DATE_RUN=`date +%F-%T`
# ${GSUTIL_CMD} cp /var/log/gce_metadata/json/$json_file_name gs://${BUCKET}/gce_metadata
${GSUTIL_CMD} cp /var/log/gce_metadata/json/$json_file_name gs://${BUCKET}/gce_metadata/gce_metadata-${sequence}-${DATE_RUN}.json

chmod ug+rw $HOME/*.txt
rm -rf $SCRIPT_DIR/gce_bms_description.txt
rm -rf $SCRIPT_DIR/gce_bms_luns.txt
rm -rf $SCRIPT_DIR/gce_bms_storage_devices.txt
rm -rf $SCRIPT_DIR/gce_bms_temp.txt
rm -rf $SCRIPT_DIR/luns_large_format1.txt
rm -rf $SCRIPT_DIR/luns_large_format2.txt
rm -rf $SCRIPT_DIR/luns_large_format3.txt
rm -rf $SCRIPT_DIR/luns_large_format4.txt
rm -rf $SCRIPT_DIR/luns_large_format5.txt
rm -rf $SCRIPT_DIR/luns_large_format6.txt
rm -rf $SCRIPT_DIR/luns_large_format.txt
rm -rf $SCRIPT_DIR/local_gce_bms_temp.txt
rm -rf $SCRIPT_DIR/local_gce_bms_description.txt
# rm -rf /var/log/gce_metadata/json/*
rm -rf /var/log/gce_metadata/temp/*

# End
