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
# Bash to upload JSON metadata to GCS bucket
#

# Get full path for useradd, mkdir, sed, systemctl, tr and perl commands

DATE_CMD="$(which date)";
GSUTIL_CMD="$(which gsutil)";
SED_CMD="$(which sed)";
CAT_CMD="$(which cat)";
MKDIR_CMD="$(which mkdir)";
CHMOD_CMD="$(which chmod)";

DATE_RUN=`${DATE_CMD} +%F-%T`

${CAT_CMD} $HOME/gce_metadata/gce_metadata-??-????-??-??*.json > $HOME/gce_metadata/cat_unified.json; tail -1 $HOME/gce_metadata/cat_unified.json | ${SED_CMD} '$ s/},/}/' $HOME/gce_metadata/cat_unified.json | ${SED_CMD} '1 i [' | ${SED_CMD} '$ a ]' > $HOME/gce_metadata/cat_unified_to_gcs.json

${GSUTIL_CMD} cp $HOME/gce_metadata/cat_unified_to_gcs.json gs://${BUCKET}/gce_metadata/gce_metadata-unified-${DATE_RUN}.json
rm $HOME/gce_metadata/gce_metadata-??-????-??-??*.json
rm $HOME/gce_metadata/cat_unified*.json
${GSUTIL_CMD} rm gs://${BUCKET}/gce_metadata/gce_metadata-??-????-??-??*.json

# End
