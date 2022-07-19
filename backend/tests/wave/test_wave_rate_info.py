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

from bms_app.wave.services.waves import wave_rate_info

from tests.factories import SourceDBFactory, SourceDBStatus, WaveFactory


def test_wave_db_rate(client):
    wave = WaveFactory()
    SourceDBFactory(wave=wave, status=SourceDBStatus.EMPTY)
    SourceDBFactory(wave=wave, status=SourceDBStatus.EMPTY)
    SourceDBFactory(wave=wave, status=SourceDBStatus.DEPLOYED)
    SourceDBFactory(wave=wave, status=SourceDBStatus.DEPLOYED)
    SourceDBFactory(wave=wave, status=SourceDBStatus.FAILED)
    SourceDBFactory(wave=wave, status=SourceDBStatus.ROLLBACKED)
    SourceDBFactory(wave=wave, status=SourceDBStatus.PRE_RESTORE_COMPLETE)

    db_status_for_wave = wave_rate_info(wave_id=wave.id)

    assert db_status_for_wave
    assert isinstance(db_status_for_wave, dict)

    assert db_status_for_wave['undeployed'] == 3
    assert db_status_for_wave['deployed'] == 3
    assert db_status_for_wave['failed'] == 1
