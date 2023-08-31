from sqlalchemy.orm import relationship
from sqlalchemy_utils import ChoiceType
from enum import Enum

from bms_app import db

class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    description = db.Column(db.String)
    properties = db.Column(db.JSON)

    wave = relationship('Wave', back_populates='project')
    databases = relationship('Database', back_populates='project')

class DatabaseEngine(Enum):
    ORACLE = 'ORACLE'
    POSTGRES = 'POSTGRES'
    MYSQL = 'MYSQL'
    UNKNOWN = 'UNKNOWN'

class Database(db.Model):
    __tablename__ = 'databases'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    name = db.Column(db.Integer, nullable=False)
    host = db.Column(db.String, nullable=False)
    engine = db.Column(ChoiceType(DatabaseEngine, impl=db.String), default=DatabaseEngine.UNKNOWN)
    properties = db.Column(db.JSON)

    project = relationship('Project', back_populates='databases', uselist=False)
    operations = relationship('Operation', back_populates='database')

class OperationStatus(Enum):
    NOT_STARTED = 'NOT_STARTED'
    RUNNING = 'RUNNING'
    FAILED = 'FAILED'
    COMPLETED = 'COMPLETED'

class OperationType(Enum):
    BMS_DEPLOYMENT = 'BMS_DEPLOYMENT'
    DMS_DEPLOYMENT = 'DMS_DEPLOYMENT'

class Operation(db.Model):
    __tablename__ = 'operations'

    id = db.Column(db.Integer, primary_key=True)
    database_id = db.Column(db.Integer, db.ForeignKey('databases.id'), nullable=False)
    wave_id = db.Column(db.Integer, db.ForeignKey('waves.id'), nullable=False)
    status = db.Column(ChoiceType(OperationStatus, impl=db.String), nullable=False)
    type_ = db.Column(ChoiceType(OperationType, impl=db.String), nullable=False)
    config = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)

    database = relationship('Database', back_populates='operations', uselist=False)
    wave = relationship('Wave', back_populates='operations', uselist=False)
    logs = relationship('Log', back_populates='operation')

class Wave(db.Model):
    __tablename__ = 'waves'
    __table_args__ = (
        db.UniqueConstraint('project_id', 'name'),
    )

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    name = db.Column(db.String, unique=True)

    operations = relationship('Operation', back_populates='wave')
    project = relationship('Project', back_populates='waves', uselist=False)

class LogLevel(Enum):
    DEBUG = 'DEBUG'
    INFO = 'INFO'
    WARN = 'WARN'
    ERROR = 'ERROR'

class Log(db.Model):
    __tablename__ = 'logs'

    id = db.Column(db.Integer, primary_key=True)
    operation_id = db.Column(db.Integer, db.ForeignKey('operations.id'), nullable=False)
    level = db.Column(ChoiceType(LogLevel, impl=db.String), default=LogLevel.INFO)
    message = db.Column(db.String, nullable=False)
    tags = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, nullable=False)

    operation = relationship('Operation', back_populates='logs', uselist=False)
