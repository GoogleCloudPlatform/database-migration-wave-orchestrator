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

from google.cloud import run_v2


def get_cloud_run_service_object(name):
    """Return google.cloud.run_v2.types.service.Service object data.

    Params:
    - name: full cloud run service name, e.g. projects/<project>/locations/<region>/services/<name>
    """
    client = run_v2.ServicesClient()
    request = run_v2.GetServiceRequest(name=name)
    return client.get_service(request=request)
