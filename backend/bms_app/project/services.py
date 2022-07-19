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

from marshmallow import ValidationError

from bms_app.models import (
    Config, Label, Mapping, Operation, OperationDetails, OperationDetailsError,
    Project, RestoreConfig, ScheduledTask, SourceDB, Wave, db
)


def validate_name_is_unique(name, exclude_project_id=None):
    qs = Project.query.filter(Project.name == name)

    if exclude_project_id:
        qs = qs.filter(Project.id != exclude_project_id)

    if qs.count():
        raise ValidationError({'name': ['this name already exists']})


class DeleteProjectService:
    def __init__(self, project_id, force):
        self.project_id = project_id
        self.force = force

    def can_be_deleted(self):
        """Return whether project can be deleted.

        It can be deleted if:
        - force == True
        - it does not contains any data (sourcedbs, waves)
        """

        if not self.force:
            count_db = db.session.query(SourceDB) \
                .filter(SourceDB.project_id == self.project_id) \
                .count()
            count_wave = db.session.query(Wave). \
                filter(Wave.project_id == self.project_id) \
                .count()

            if count_db or count_wave:
                return False

        return True

    def delete(self):
        waves = db.session.query(Wave) \
            .filter(Wave.project_id == self.project_id) \
            .all()

        self._delete_waves_related(waves)
        self._delete_mappings()
        self._delete_source_dbs_related()
        self._delete_objects(waves)
        self._delete_labels()

        self._delete_project()

        db.session.commit()

    def _delete_waves_related(self, waves):
        self._delete_operation_details(waves)
        self._delete_operations(waves)

    def _delete_source_dbs_related(self):
        source_dbs = db.session.query(SourceDB) \
            .filter(SourceDB.project_id == self.project_id) \
            .all()
        self._delete_config(source_dbs)
        self._delete_restore_configs(source_dbs)
        self._delete_scheduled_tasks(source_dbs)
        self._delete_objects(source_dbs)

    def _delete_operation_details(self, waves):
        for wave in waves:
            op_details_items = db.session.query(OperationDetails) \
                .filter(OperationDetails.wave_id == wave.id) \
                .all()
            self._delete_operation_details_error(op_details_items)
            self._delete_objects(op_details_items)

    def _delete_operation_details_error(self, op_details_items):
        for op_details_item in op_details_items:
            op_details_errors = db.session.query(OperationDetailsError) \
                .filter(OperationDetailsError.operation_details_id == op_details_item.id) \
                .all()
            self._delete_objects(op_details_errors)

    def _delete_operations(self, waves):
        for wave in waves:
            operations = db.session.query(Operation) \
                .filter(Operation.wave_id == wave.id) \
                .all()
            self._delete_objects(operations)

    def _delete_config(self, source_dbs):
        for source_db in source_dbs:
            configs = db.session.query(Config) \
                .filter(Config.db_id == source_db.id) \
                .all()
            self._delete_objects(configs)

    def _delete_restore_configs(self, source_dbs):
        for source_db in source_dbs:
            restore_configs = db.session.query(RestoreConfig) \
                .filter(RestoreConfig.db_id == source_db.id) \
                .all()
            self._delete_objects(restore_configs)

    def _delete_scheduled_tasks(self, source_dbs):
        for source_db in source_dbs:
            scheduled_tasks = db.session.query(ScheduledTask) \
                .filter(ScheduledTask.db_id == source_db.id) \
                .all()
            self._delete_objects(scheduled_tasks)

    def _delete_labels(self):
        labels = db.session.query(Label) \
            .filter(Label.project_id == self.project_id) \
            .all()
        self._delete_objects(labels)

    def _delete_mappings(self):
        mappings = db.session.query(Mapping) \
            .join(SourceDB) \
            .filter(SourceDB.project_id == self.project_id) \
            .all()
        self._delete_objects(mappings)

    def _delete_project(self):
        project = db.session.query(Project) \
            .filter(Project.id == self.project_id) \
            .all()
        self._delete_objects(project)

    @staticmethod
    def _delete_objects(items):
        for item in items:
            db.session.delete(item)
