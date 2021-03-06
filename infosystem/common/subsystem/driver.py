import uuid
from sqlalchemy.orm import exc
from infosystem.common import exception


class Driver(object):

    def __init__(self, resource):
        self.resource = resource

    def instantiate(self, **kwargs):
        try:
            embedded = {}
            for attr in self.resource.embedded():
                if attr not in kwargs:
                    raise Exception()
                embedded.update({attr: kwargs.pop(attr)})

            instance = self.resource(**kwargs)

            for attr in embedded:
                value = embedded[attr]
                var = getattr(self.resource, attr)
                # TODO(samueldmq): is this good enough? should we discover it?
                mapped_attr = {self.resource.individual() + '_id': instance.id}
                if isinstance(value, list):
                    new_id = None
                    if len(value) > 0:
                        if value[0].get('id') is not None:
                            new_id = value[0].pop('id')
                    if new_id is None:
                        setattr(instance, attr, [var.property.mapper.class_(
                            id=uuid.uuid4().hex, **dict(ref, **mapped_attr))
                            for ref in value])
                    else:
                        if new_id is None:
                            new_id = uuid.uuid4().hex
                        setattr(instance, attr, [var.property.mapper.class_(
                            id=new_id, **dict(ref, **mapped_attr))
                            for ref in value])
                else:
                    # TODO(samueldmq): id is inserted here. it is in the
                    # manager for the entities. do it all in the resource
                    # contructor
                    setattr(instance, attr, var.property.mapper.class_(
                        id=uuid.uuid4().hex, **dict(value, **mapped_attr)))
        except Exception:
            # TODO(samueldmq): replace with specific exception
            raise exception.BadRequest()

        return instance

    def create(self, entity, session):
        session.add(entity)
        session.flush()

    def update(self, entity, data, session):
        # try:
        #     entity = self.get(id, session)
        # except exc.NoResultFound:
        #     raise exception.NotFound()

        for attr in self.resource.embedded():
            if attr in data:
                value = data.pop(attr)
                var = getattr(self.resource, attr)
                # TODO(samueldmq): is this good enough? should we discover it?
                mapped_attr = {self.resource.individual() + '_id': id}
                if isinstance(value, list):
                    new_id = None
                    if len(value) > 0:
                        if value[0].get('id') is not None:
                            new_id = value[0].pop('id')
                    if new_id is None:
                        setattr(entity, attr, [var.property.mapper.class_(
                            id=uuid.uuid4().hex, **dict(ref, **mapped_attr))
                            for ref in value])
                    else:
                        if new_id is None:
                            new_id = uuid.uuid4().hex
                        setattr(entity, attr, [var.property.mapper.class_(
                            id=new_id, **dict(ref, **mapped_attr))
                            for ref in value])
                else:
                    # TODO(samueldmq): id is inserted here. it is in the
                    # manager for the entities. do it all in the resource
                    # contructor
                    setattr(entity, attr, var.property.mapper.class_(
                        id=uuid.uuid4().hex, **dict(value, **mapped_attr)))

        for key, value in data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
            else:
                raise exception.BadRequest()

        session.flush()
        return entity

    def delete(self, entity, session):
        session.delete(entity)
        session.flush()

    def get(self, id, session):
        try:
            query = session.query(self.resource).filter_by(id=id)
            result = query.one()
        except exc.NoResultFound:
            raise exception.NotFound()

        return result

    def list(self, session, **kwargs):
        query = session.query(self.resource)
        for k, v in kwargs.items():
            if hasattr(self.resource, k):
                if isinstance(v, str) and '%' in v:
                    query = query.filter(getattr(self.resource, k).like(v))
                else:
                    query = query.filter(getattr(self.resource, k) == v)

        result = query.all()
        return result

    def count(self, session):
        try:
            rows = session.query(self.resource.id).count()
            result = rows
        except exc.NoResultFound:
            raise exception.NotFound()

        return result
