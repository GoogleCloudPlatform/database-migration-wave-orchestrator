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

import base64
import json
from datetime import datetime

from bms_app.models import BMSServer, Mapping, Operation, OperationDetails, db
from bms_app.services.status_handlers.operation import (
    DeploymentOperationStatusHandler, DMSDeploymentOperationStatusHandler,
    FailOverOperationStatusHandler, PreRestoreOperationStatusHandler,
    RestoreOperationStatusHandler, RollbackOperationStatusHandler,
    RollbackRestoreOperationStatusHandler
)
from bms_app.services.status_handlers.operation_detail import (
    DeploymentOperationDetailStatusHandler,
    DMSDeploymentOperationDetailStatusHandler,
    FailOverOperationDetailStatusHandler,
    PreRestoreOperationDetailStatusHandler,
    RestoreOperationDetailStatusHandler, RollbackOperationDetailStatusHandler,
    RollbackRestoreOperationDetailStatusHandler
)


operation_details_handler_mapper = {
    'DEPLOYMENT': DeploymentOperationDetailStatusHandler,
    'DMS_DEPLOYMENT': DMSDeploymentOperationDetailStatusHandler,
    'ROLLBACK': RollbackOperationDetailStatusHandler,
    'PRE_RESTORE': PreRestoreOperationDetailStatusHandler,
    'BACKUP_RESTORE': RestoreOperationDetailStatusHandler,
    'ROLLBACK_RESTORE': RollbackRestoreOperationDetailStatusHandler,
    'DB_FAILOVER': FailOverOperationDetailStatusHandler,
}


operation_handler_mapper = {
    'DEPLOYMENT': DeploymentOperationStatusHandler,
    'DMS_DEPLOYMENT': DMSDeploymentOperationStatusHandler,
    'ROLLBACK': RollbackOperationStatusHandler,
    'PRE_RESTORE': PreRestoreOperationStatusHandler,
    'BACKUP_RESTORE': RestoreOperationStatusHandler,
    'ROLLBACK_RESTORE': RollbackRestoreOperationStatusHandler,
    'DB_FAILOVER': FailOverOperationStatusHandler,
}


def process_host_related_data(msg, completed_at):
    """Update host related data: source_db, mapping, operation details."""
    for hostname in msg['hostnames']:
        op_detail = (
            db.session.query(OperationDetails)
            .join(Mapping)
            .join(BMSServer, Mapping.bms_id == BMSServer.id)
            .filter(OperationDetails.operation_id == msg['operation_id'],
                    BMSServer.name == hostname)
            .first()
        )

        cls_handler = operation_details_handler_mapper.get(
            op_detail.operation_type.value
        )
        status_handler = cls_handler(op_detail, completed_at)

        if 'step' in msg:
            status_handler.set_step(msg['step'], msg['timestamp'])

        if 'host_status' in msg:
            if msg['host_status'] == 'FAILED':
                status_handler.fail()

            elif msg['host_status'] == 'COMPLETE':
                status_handler.complete()

            else:
                status_handler.set_status(msg['host_status'])

        db.session.flush()

def process_dms_data(msg, completed_at):
    op_detail = (
        db.session.query(OperationDetails)
        .filter(OperationDetails.operation_id == msg['operation_id'])
        .first()
    )

    cls_handler = operation_details_handler_mapper.get(
        op_detail.operation_type.value
    )

    status_handler = cls_handler(op_detail, completed_at)

    if 'step' in msg:
        status_handler.set_step(msg['step'], msg['timestamp'])
    
    if 'dms_status' in msg:
        if msg['dms_status'] == 'FAILED':
            status_handler.fail()
        elif msg['dms_status'] == 'COMPLETE':
            status_handler.complete()
        else:
            status_handler.set_status(msg['dms_status'])
    
    db.session.flush()



def process_operation_data(msg, completed_at):
    """Process operation data."""
    operation = db.session.query(Operation).get(msg['operation_id'])

    cls_handler = operation_handler_mapper.get(operation.operation_type.value)
    status_handler = cls_handler(operation, completed_at)

    if msg['status'] == 'TERMINATED':
        status_handler.terminate()

    elif msg['status'] == 'FINISHED':
        status_handler.finish()

    else:
        status_handler.set_status(msg['status'])


def process_msg(envelope):
    """Process pub/sub msg.

    Msg exmaple:
    {
        "message": {
            "attributes": {
                "key": "value"
            },
            "data": "SGVsbG8gQ2xvdWQgUHViL1N1YiEgSGVyZSBpcyBteSBtZXNzYWdlIQ==",
            "messageId": "2070443601311540",
            "message_id": "2070443601311540",
            "publishTime": "2021-02-26T19:13:55.749Z",
            "publish_time": "2021-02-26T19:13:55.749Z",
        },
       "subscription": "projects/myproject/subscriptions/mysubscription"
    }
    """
    raw_msg = base64.b64decode(envelope['message']['data'])
    msg = json.loads(raw_msg)

    completed_at = datetime.now()

    # lock in order to prevent running this function more than once
    Operation.query.with_for_update().get(msg['operation_id'])

    if 'dms' in msg:
        process_dms_data(msg, completed_at)

    if 'hostnames' in msg:
        process_host_related_data(msg, completed_at)

    if 'status' in msg:
        process_operation_data(msg, completed_at)

    db.session.commit()
