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

import logging
import os
from datetime import datetime

import google.auth
import google.auth.transport.requests as tr_requests
from google.cloud import storage
from google.resumable_media.requests import ResumableUpload

from bms_app import settings


READ_WRITE_SCOPE = 'https://www.googleapis.com/auth/devstorage.read_write'
URL_TEMPLATE = (
    'https://www.googleapis.com/upload/storage/v1/b/{bucket}/o'
    '?&uploadType=resumable'
)
CHUNK_SIZE = 1024 * 1024  # 1MB
CONTENT_TYPE = 'application/octet-stream'


logger = logging.getLogger(__name__)


def parse_gcs_uri(gcs_full_path):
    """Extrtact bucket name and file path form the full url.

    Return: (bucket_name, file_path)

    Examples:
    gs://some-bucket/path/file.py -> ('some-bucket', 'path/file.py')
    some-bucket/path/file.py -> ('some-bucket', 'path/file.py')
    """

    if gcs_full_path.startswith('gs://'):
        gcs_full_path = gcs_full_path[5:]

    splited = [x for x in gcs_full_path.split('/') if x]

    bucket_name = splited[0]
    file_path = os.path.join(*splited[1:])

    return (bucket_name, file_path)


def upload_stream_to_gcs(stream, bucket_name, key):
    """Upload stream object to GCS (bucket)."""
    credentials, _ = google.auth.default(scopes=(READ_WRITE_SCOPE,))
    transport = tr_requests.AuthorizedSession(credentials)

    upload_url = URL_TEMPLATE.format(bucket=bucket_name)

    upload = ResumableUpload(upload_url, CHUNK_SIZE)

    metadata = {'name': key}

    response = upload.initiate(
        transport, stream, metadata,
        CONTENT_TYPE, stream_final=False
    )

    response = upload.transmit_next_chunk(transport)

    while response.status_code != 200:
        response = upload.transmit_next_chunk(transport)

    return response.json()


def upload_blob(bucket_name, key, source_file):
    """Uploads a file to the bucket."""
    logger.debug(
        'upload blob bucket:%s key:%s' % (bucket_name, key)
    )
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(key)
    blob.upload_from_file(source_file)


def upload_blob_from_string(bucket_name, key, content):
    """Uploads a file to the bucket."""
    logger.debug(
        'upload blob from string bucket:%s key:%s' % (bucket_name, key)
    )
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(key)
    blob.upload_from_string(content)


def list_blobs(bucket_name, prefix=None):
    """List of the interest blobs in the bucket.

    Keyword arguments:
    bucket_name -- name of bucket
    prefix -- name of folder/subfolder. For example "ora-binaries/". Default=None
    """
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    list_blobs = bucket.list_blobs(prefix=prefix)
    date_format = "%Y-%m-%d %H:%M:%S"
    blobs = []
    for blob in list_blobs:
        if not blob.name.endswith('/'):  # only files
            blobs.append({
                'name': blob.name,
                'size': blob.size,
                'type': blob.content_type,
                'created_date': datetime.fromtimestamp(blob.generation / 10**6).strftime(date_format),
                'last_modified': blob.updated.strftime(date_format)
            })
    return blobs


def get_file_content(bucket_name, file_path):
    """File content from the bucket.

    Keyword arguments:
    bucket_name -- name of bucket
    prefix -- name of folder/subfolder. For example "ora-binaries/"
    file_name -- name of the file. For example "pfile.ora"
    """
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.get_blob(file_path)
    data_string = blob.download_as_string()

    # convert bytes to unicode
    content = data_string.decode()
    return content


def delete_blob(bucket_name, blob_name):
    """Delete a blob from the bucket"""
    # bucket_name = "your-bucket-name"
    # blob_name = "your-object-name"

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    if blob.exists():
        blob.delete()


def copy_blob(bucket_name,
              blob_name,
              destination_bucket_name,
              destination_blob_name):
    """Copies a blob from one bucket to another with a new name."""

    storage_client = storage.Client()

    source_bucket = storage_client.bucket(bucket_name)
    source_blob = source_bucket.blob(blob_name)
    destination_bucket = storage_client.bucket(destination_bucket_name)

    blob_copy = source_bucket.copy_blob(
        source_blob, destination_bucket, destination_blob_name
    )

    logger.debug(
        'copy blob from %s/%s to %s/%s' % (
            bucket_name, blob_name,
            destination_bucket_name, destination_blob_name
        )
    )
    return blob_copy


def create_file_link(gcs_key):
    """Create link to GCS"""
    file_link = os.path.join(
        'https://console.cloud.google.com/storage/browser/_details',
        settings.GCS_BUCKET,
        gcs_key
    )

    return file_link


def blob_exists(bucket_name, key):
    """Check the existence of a file in the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    exist = storage.Blob(bucket=bucket, name=key).exists(storage_client)
    return exist
