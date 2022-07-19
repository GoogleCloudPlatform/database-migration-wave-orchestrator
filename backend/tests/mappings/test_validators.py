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

import pytest
from marshmallow import ValidationError

from bms_app.mapping.services import validate_bms, validate_db, validate_wave

from tests.factories import (
    BMSServerFactory, MappingFactory, ProjectFactory, SourceDBFactory,
    WaveFactory
)


def test_db_existence_validation(client):
    """Test db existence validation"""
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr)

    with pytest.raises(ValidationError):
        validate_db(
            db_1.id + 1  # fake id
        )


def test_err_if_db_is_mapped_twice(client):
    """Can not mapp if it is already mapped."""
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr, db_type='SI')
    MappingFactory(source_db=db_1)

    with pytest.raises(ValidationError):
        validate_db(
            db_1.id
        )


def test_bms_existence_validation(client):
    """Test bms existence validation"""
    bms_1 = BMSServerFactory()

    with pytest.raises(ValidationError):
        validate_bms(
            bms_1.id + 1  # fake id
        )


def test_err_if_bms_is_mapped_twice(client):
    """Test mapping existence validation"""
    bms_1 = BMSServerFactory()
    MappingFactory(bms=bms_1)

    with pytest.raises(ValidationError):
        validate_bms(
            bms_1.id
        )


def test_wave_validation(client):
    """Test wave existence validation"""
    pr = ProjectFactory()
    wave = WaveFactory(project=pr)

    with pytest.raises(ValidationError):
        validate_wave(
            wave.id + 1  # fake id
        )
