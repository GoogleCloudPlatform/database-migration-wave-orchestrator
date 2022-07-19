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

FROM python:3.9-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

RUN apt-get -y update; apt-get -y install libpq-dev gcc \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get -y remove gcc && apt-get -y autoremove && rm -rf /var/lib/apt/lists/*

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 bms_app:create_app\(\'prod\'\)
