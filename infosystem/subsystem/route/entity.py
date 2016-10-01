from sqlalchemy import UniqueConstraint
from infosystem.common.subsystem import entity
from infosystem.database import db


class Route(entity.Entity, db.Model):

    # TODO(samueldmq): recheck string lengths for below attributes
    # TODO(samueldmq): add an 'active' attribute
    attributes = ['id', 'name', 'url', 'method', 'admin', 'bypass']
    name = db.Column(db.String(20), nullable=False, unique=True)
    url = db.Column(db.String(80), nullable=False, unique=True)
    method = db.Column(db.String(10), nullable=False, unique=True)
    admin = db.Column(db.Boolean(), nullable=False)
    bypass = db.Column(db.Boolean(), nullable=False)

    def __init__(self, id, name, url, method, admin=False, bypass=False):
        self.id = id
        self.name = name
        self.url = url
        self.method = method
        self.method = method
        self.bypass = bypass
        self.admin = admin