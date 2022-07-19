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

from bms_app.inventory_manager.schema import (
    APIBMSServerSchema, UploadBMSServerSchema
)
from bms_app.models import BMSServer, Mapping, SourceDB, db
from bms_app.services.source_db import clear_bms_target_params
from bms_app.utils import update_object


CLIENT_NETWORK = 'CLIENT'  # Client network, a network peered to a Google Cloud VPC.


upload_bms_schema = UploadBMSServerSchema()
api_bms_schema = APIBMSServerSchema()


def process_bms_instance_data(instance_data, overwrite):
    """Process input data re one bms server.

    Save bms sever, update it or skip it.
    Clear source db config if needed.
    """
    bms_server = db.session.query(BMSServer) \
        .filter(BMSServer.name == instance_data['name']) \
        .first()

    if bms_server:
        if overwrite:
            # Overwrite bms_target if it has not been deployed yet
            # or mapped source_db is deployable.
            mapped_source_db = db.session.query(SourceDB) \
                .outerjoin(Mapping) \
                .filter(Mapping.bms_id == bms_server.id) \
                .first()

            if mapped_source_db and mapped_source_db.is_deployable:
                update_object(bms_server, instance_data)
                # Reset some parameters in the Config because
                # the bms_target parameters have changed.
                config = mapped_source_db.config
                if config:
                    clear_bms_target_params(config)
            elif not mapped_source_db:
                update_object(bms_server, instance_data)

    else:
        bms_server = BMSServer(**instance_data)

    db.session.add(bms_server)


def insert_uploaded_servers(uploaded_instances, overwrite=False):
    """Process data uploaded via html form."""
    for item in uploaded_instances:
        instance_data = upload_bms_schema.load(item)
        process_bms_instance_data(instance_data, overwrite)

    db.session.commit()


def get_client_ip(bms_server):
    """Get ip address used to reach bms from GCP."""
    return next(
        (x for x in bms_server.networks if x.get('type') == CLIENT_NETWORK), {}
    ).get('ipAddress')


def insert_discovered_servers(discovered_instances, overwrite):
    """Process data from BMS API."""
    for item in discovered_instances:
        instance_data = api_bms_schema.load(item)
        process_bms_instance_data(instance_data, overwrite)

    db.session.commit()
