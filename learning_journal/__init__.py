from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.session import SignedCookieSessionFactory
from passlib.hash import sha256_crypt
from os import environ

from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    Base,
    RootFactory,
    )


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    settings['auth.username'] = environ['ADMIN_UN']
    settings['auth.password'] = environ['ADMIN_PW']
    authn_policy = AuthTktAuthenticationPolicy(environ['AUTH_TKT_KEY'],
                                               hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()
    cookie_factory = SignedCookieSessionFactory(environ['COOKIE_KEY'])
    config = Configurator(settings=settings,
                          authentication_policy=authn_policy,
                          authorization_policy=authz_policy,
                          root_factory=RootFactory,
                          session_factory=cookie_factory)
    config.include('pyramid_jinja2')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('list', '/')
    config.add_route('detail', '/entry/{id:\d+}')
    config.add_route('add_entry', '/entry/add')
    config.add_route('edit_entry', '/entry/{id}/edit')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.scan()
    return config.make_wsgi_app()
