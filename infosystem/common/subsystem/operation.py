import flask
import uuid

# TODO this import here is so strange
from infosystem import database


class Operation(object):

    def __init__(self, manager):
        self.manager = manager
        self.driver = manager.driver

    def pre(self, data, **kwargs):
        return True

    def do(self, **kwargs):
        return True

    def post(self):
        pass

    def __call__(self, data=None, **kwargs):
        session = database.db.session
        self.pre(data=data, session=session, **kwargs)

        if not getattr(session, 'count', None):
           setattr(session, 'count', 1)
        else:
           session.count += 1

        try:
            result = self.do(session, **kwargs)
            session.count -= 1

            self.post()
            if session.count == 0:
                session.commit()
        except Exception as e:
            session.rollback()
            session.count = 0
            raise e
        return result


class Create(Operation):

    def pre(self, data, **kwargs):
        self.entity = self.driver.instantiate(id=uuid.uuid4().hex, **data)
        return self.entity.is_stable()

    def do(self, session, **kwargs):
        self.driver.create(self.entity, session=session)
        return self.entity


class Get(Operation):

    def pre(self, id, **kwargs):
        self.id = id

    def do(self, session, **kwargs):
        entity = self.driver.get(self.id, session=session)
        return entity


class List(Operation):

    def do(self, session, **kwargs):
        entities = self.driver.list(session=session, **kwargs)
        return entities


class Update(Operation):

    def pre(self, id, data, session, **kwargs):
        self.id = id
        self.data = data
        return bool(self.driver.get(id, session=session))

    def do(self, session, **kwargs):
        entity = self.driver.update(self.id, self.data, session=session)
        return entity


class Delete(Operation):

    def pre(self, id, session, **kwargs):
        self.entity = self.driver.get(id, session=session)

    def do(self, session, **kwargs):
        self.driver.delete(self.entity, session=session)
