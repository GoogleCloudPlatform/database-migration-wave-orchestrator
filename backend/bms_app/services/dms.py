import uuid
from google.cloud import clouddms_v1
from google.api_core import operation


class DMS:

    def __init__(
            self,
            project_id: str,
            region: str,
            dms_client: clouddms_v1.DataMigrationServiceClient = clouddms_v1.DataMigrationServiceClient(),
    ):
        self.project_id = project_id
        self.region = region
        self.client = dms_client

    def _get_parent(self) -> str:
        return f'projects/{self.project_id}/locations/{self.region}'

    def _get_migration_job_name(self, name: str) -> str:
        return self.client.migration_job_path(self.project_id, self.region, name)

    def _get_connection_profile_name(self, name: str) -> str:
        return self.client.connection_profile_path(self.project_id, self.region, name)

    def _get_new_request_id(self) -> str:
        return str(uuid.uuid4())

    def get_migration_job(self, name: str) -> clouddms_v1.MigrationJob:
        req = clouddms_v1.GetMigrationJobRequest(name=self._get_migration_job_name(name))
        return self.client.get_migration_job(request=req)

    def create_migration_job(
            self, name: str,
            display_name: str,
            source_conn: str,
            destination_conn: str,
    ) -> operation.Operation:
        req = clouddms_v1.CreateMigrationJobRequest(
            parent=self._get_parent(),
            migration_job_id=name,
            migration_job=clouddms_v1.MigrationJob(
                name=self._get_migration_job_name(name),
                labels={},
                display_name=display_name,
                state=clouddms_v1.MigrationJob.State.DRAFT,
                type_=clouddms_v1.MigrationJob.Type.CONTINUOUS,
                source=self._get_connection_profile_name(source_conn),
                destination=self._get_connection_profile_name(destination_conn),
                static_ip_connectivity={},
                source_database=clouddms_v1.DatabaseType(
                    provider=clouddms_v1.DatabaseProvider.DATABASE_PROVIDER_UNSPECIFIED,
                    engine=clouddms_v1.DatabaseEngine.POSTGRESQL
                ),
                destination_database=clouddms_v1.DatabaseType(
                    provider=clouddms_v1.DatabaseProvider.CLOUDSQL,
                    engine=clouddms_v1.DatabaseEngine.POSTGRESQL
                ),
            ),
            request_id=self._get_new_request_id()
        )
        return self.client.create_migration_job(request=req)

    def verify_migration_job(self, name: str) -> operation.Operation:
        req = clouddms_v1.VerifyMigrationJobRequest(name=self._get_migration_job_name(name))
        return self.client.verify_migration_job(request=req)

    def start_migration_job(self, name: str) -> operation.Operation:
        req = clouddms_v1.StartMigrationJobRequest(name=self._get_migration_job_name(name))
        return self.client.start_migration_job(request=req)

    def get_connection_profile(self, name: str) -> clouddms_v1.ConnectionProfile:
        req = clouddms_v1.GetConnectionProfileRequest(name=self._get_connection_profile_name(name))
        return self.client.get_connection_profile(request=req)

    def create_source_connection_profile(self, name: str, host: str) -> operation.Operation:
        req = clouddms_v1.CreateConnectionProfileRequest(
            parent=self._get_parent(),
            connection_profile_id=name,
            connection_profile=clouddms_v1.ConnectionProfile(
                name=self._get_connection_profile_name(name),
                display_name='Source Connection Profile for Waverunner',
                postgresql=clouddms_v1.PostgreSqlConnectionProfile(
                    host=host,
                    port=5432, # TODO: parametrize this
                    username='postgres', # TODO: parametrize this
                    password='waverunner-test' # TODO: use secret manager
                )
            ),
            request_id=self._get_new_request_id(),
        )
        return self.client.create_connection_profile(request=req)

    def create_destination_connection_profile(
            self,
            name: str,
            source_conn_name: str,
    ) -> operation.Operation:
        req = clouddms_v1.CreateConnectionProfileRequest(
            parent=self._get_parent(),
            connection_profile_id=name,
            connection_profile=clouddms_v1.ConnectionProfile(
                name=self._get_connection_profile_name(name),
                labels={},
                display_name='Destination Connection Profile for Waverunner',
                cloudsql=clouddms_v1.CloudSqlConnectionProfile(
                    settings=clouddms_v1.CloudSqlSettings(
                        database_version=clouddms_v1.CloudSqlSettings.SqlDatabaseVersion.POSTGRES_12,
                        # TODO: parametrize
                        tier='db-custom-1-3840',  # TODO: calculate based on database type
                        ip_config=clouddms_v1.SqlIpConfig(
                            enable_ipv4=True
                        ),
                        data_disk_type=clouddms_v1.CloudSqlSettings.SqlDataDiskType.PD_SSD,  # TODO: parametrize
                        data_disk_size_gb=10,  # TODO: parametrize
                        zone='us-central1-c',  # TODO: parametrize
                        source_id=self._get_connection_profile_name(source_conn_name),
                        root_password='waverunner-test'  # TODO: use secret manager
                    ),
                )
            ),
            request_id=self._get_new_request_id()
        )

        return self.client.create_connection_profile(request=req)
