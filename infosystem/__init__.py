import flask
import os

from infosystem import database
from infosystem import request
from infosystem import subsystem as subsystem_module
from infosystem import scheduler
from infosystem.common import exception


class System(flask.Flask):

    request_class = request.Request

    def __init__(self, **kwargs):
        super().__init__(__name__, static_folder=None)

        self.configure()
        self.init_database()

        subsystem_list = subsystem_module.all + list(kwargs.values())

        self.subsystems = {s.name: s for s in subsystem_list}
        self.inject_dependencies()

        for subsystem in self.subsystems.values():
            self.register_blueprint(subsystem)

        self.scheduler = scheduler.Scheduler()
        self.schedule_jobs()

        self.bootstrap()

        self.before_request(request.RequestManager(self.subsystems).before_request)

    def configure(self):
        self.config['BASEDIR'] = os.path.abspath(os.path.dirname(__file__))
        self.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

    def init_database(self):
        database.db.init_app(self)
        with self.app_context():
            database.db.create_all()

    def schedule_jobs(self):
        pass

    def inject_dependencies(self):
        api = lambda: None
        for name, subsystem in self.subsystems.items():
            setattr(api, name, subsystem.router.controller.manager)

        # Dependency injection
        for subsystem in self.subsystems.values():
            subsystem.router.controller.manager.api = api

    def bootstrap(self):
        """Bootstrap the system.

        - routes;
        - TODO(samueldmq): sysadmin;
        - default domain with admin and capabilities.

        """

        with self.app_context():
            # Register default domain
            try:
                domain = self.subsystems['domains'].manager.create(name='default')
            # TODO(samueldmq): change these Exception to duplicated entry
            except Exception:
                domain = self.subsystems['domains'].manager.list(name='default')[0]

            try:
                role = self.subsystems['roles'].manager.create(name='admin', domain_id=domain.id)
            except Exception:
                role = self.subsystems['roles'].manager.list(name='admin', domain_id=domain.id)[0]

            # Register all system routes and all non-admin routes as capabilities in the default domain
            for subsystem in self.subsystems.values():
                for route in subsystem.router.routes:
                    try:
                        route_ref = self.subsystems['routes'].manager.create(name=route['action'], url=route['url'], method=route['method'], bypass=route.get('bypass', False))
                        # TODO(samueldmq): duplicate the line above here and see what breaks, it's probably the SQL session management!
                    except Exception:
                        route_ref = self.subsystems['routes'].manager.list(name=route['action'], url=route['url'], method=route['method'], bypass=route.get('bypass', False))[0]

                    if not route_ref.admin:
                        try:
                            capability = self.subsystems['capabilities'].manager.create(domain_id=domain.id, route_id=route_ref.id)
                        except Exception:
                            capability = self.subsystems['capabilities'].manager.list(domain_id=domain.id, route_id=route_ref.id)[0]

                        try:
                            self.subsystems['policies'].manager.create(capability_id=capability.id, role_id=role.id)
                        except Exception as e:
                            pass

            try:
                user = self.subsystems['users'].manager.create(domain_id=domain.id, name='admin', password='123456', email="admin@example.com")
            except Exception:
                user = self.subsystems['users'].manager.list(domain_id=domain.id, name='admin', password='123456', email="admin@example.com")[0]

            try:
                self.subsystems['grants'].manager.create(user_id=user.id, role_id=role.id)
            except Exception:
                pass
