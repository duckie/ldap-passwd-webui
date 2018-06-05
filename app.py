#!/usr/bin/env python3

import bottle
from bottle import get, post, static_file, request, route, template
from bottle import SimpleTemplate
from configparser import ConfigParser
from ldap3 import Connection, Server
from ldap3 import SIMPLE, SUBTREE
from ldap3.core.exceptions import LDAPBindError, LDAPConstraintViolationResult, \
    LDAPInvalidCredentialsResult, LDAPUserNameIsMandatoryError, \
    LDAPSocketOpenError, LDAPExceptionError, LDAPPasswordIsMandatoryError
import logging
import os
from os import environ, path
from base64 import b64decode


BASE_DIR = path.dirname(__file__)
LOG = logging.getLogger(__name__)
LOG_FORMAT = '%(asctime)s %(levelname)s: %(message)s'
VERSION = '2.0.0'


@get('/')
def get_index():
    return index_tpl()


@post('/')
def post_index():
    form = request.forms.getunicode

    def error(msg):
        return index_tpl(username=form('username'), alerts=[('alert-danger', msg)])

    if form('new-password') != form('confirm-password'):
        return error("Password doesn't match the confirmation!")

    if len(form('new-password')) < 8:
        return error("Password must be at least 8 characters long!")

    try:
        change_password(form('username'), form('old-password'), form('new-password'))
    except Error as e:
        LOG.warning("Unsuccessful attempt to change password for %s: %s" % (form('username'), e))
        return error(str(e))

    LOG.info("Password successfully changed for: %s" % form('username'))

    return index_tpl(alerts=[('alert-success', "Password has been changed to: " + form('new-password'))])

@route('/token/<key>', name='setup')
def read_token(key):
    try:
        data = b64decode(key).decode('ascii').strip().split(' ')
        user = data[0]
        mail = data[1]
        password = data[2]
        check_password(user, password)
    except Exception as e:
        LOG.error('{}: {!s}'.format(e.__class__.__name__, e))
        return error_tpl(alerts=[('alert-danger', 'wrong token provided')])
    return token_tpl(username=user)

@post('/token/<key>', name='setup')
def setup_index(key):
    form = request.forms.getunicode
    try:
        data = b64decode(key).decode('ascii').strip().split(' ')
        user = data[0]
        mail = data[1]
        password = data[2]
        check_password(user, password)
    except:
        return error_tpl(alerts=[('alert-danger', 'wrong token provided')])

    def error(msg):
        return token_tpl(username=form('username'), alerts=[('alert-danger', msg)])

    if form('new-password') != form('confirm-password'):
        return error("Password doesn't match the confirmation!")

    if len(form('new-password')) < 8:
        return error("Password must be at least 8 characters long!")

    try:
        change_password(form('username'), password, form('new-password'))
    except Error as e:
        LOG.warning("Unsuccessful attempt to change password for %s: %s" % (form('username'), e))
        return error(str(e))

    LOG.info("Password successfully changed for: %s" % form('username'))

    return error_tpl(alerts=[('alert-success', "Password has been changed to: " + form('new-password'))])

@route('/static/<filename>', name='static')
def serve_static(filename):
    return static_file(filename, root=path.join(BASE_DIR, 'static'))

@route('/fonts/<filename>', name='fonts')
def serve_fonts(filename):
    return static_file(filename, root=path.join(BASE_DIR, 'fonts'))

def error_tpl(**kwargs):
    return template('error', **kwargs)

def token_tpl(**kwargs):
    return template('token', **kwargs)

def index_tpl(**kwargs):
    return template('index', **kwargs)

def connect_ldap(**kwargs):
    server = Server(host=CONF['ldap']['host'],
                    port=CONF['ldap'].getint('port', None),
                    use_ssl=CONF['ldap'].getboolean('use_ssl', False),
                    connect_timeout=5)

    return Connection(server, raise_exceptions=True, **kwargs)

def check_password(*args):
    try:
        if CONF['ldap'].get('type') == 'ad':
            check_password_ad(*args)
        else:
            check_password_ldap(*args)

    except (LDAPBindError, LDAPInvalidCredentialsResult, LDAPUserNameIsMandatoryError, LDAPPasswordIsMandatoryError):
        raise Error('Username or password is incorrect!')

    except LDAPSocketOpenError as e:
        LOG.error('{}: {!s}'.format(e.__class__.__name__, e))
        raise Error('Unable to connect to the remote server.')

    except LDAPExceptionError as e:
        LOG.error('{}: {!s}'.format(e.__class__.__name__, e))
        raise Error('Encountered an unexpected error while communicating with the remote server.')

def change_password(*args):
    try:
        if CONF['ldap'].get('type') == 'ad':
            change_password_ad(*args)
        else:
            change_password_ldap(*args)

    except (LDAPBindError, LDAPInvalidCredentialsResult, LDAPUserNameIsMandatoryError, LDAPPasswordIsMandatoryError):
        raise Error('Username or password is incorrect!')

    except LDAPConstraintViolationResult as e:
        # Extract useful part of the error message (for Samba 4 / AD).
        msg = e.message.split('check_password_restrictions: ')[-1].capitalize()
        raise Error(msg)

    except LDAPSocketOpenError as e:
        LOG.error('{}: {!s}'.format(e.__class__.__name__, e))
        raise Error('Unable to connect to the remote server.')

    except LDAPExceptionError as e:
        LOG.error('{}: {!s}'.format(e.__class__.__name__, e))
        raise Error('Encountered an unexpected error while communicating with the remote server.')

def change_password_ldap(username, old_pass, new_pass):
    with connect_ldap(user=CONF['ldap']['user'], password=CONF['ldap']['password']) as c:
        c.bind()
        user_dn = find_user_dn(c, username)

    # Note: raises LDAPUserNameIsMandatoryError when user_dn is None.
    with connect_ldap(authentication=SIMPLE, user=user_dn, password=old_pass) as c:
        c.bind()
        c.extend.standard.modify_password(user_dn, old_pass, new_pass)

def check_password_ldap(username, password):
    with connect_ldap(user=CONF['ldap']['user'], password=CONF['ldap']['password']) as c:
        c.bind()
        user_dn = find_user_dn(c, username)

    # Note: raises LDAPUserNameIsMandatoryError when user_dn is None.
    with connect_ldap(authentication=SIMPLE, user=user_dn, password=password) as c:
        c.bind()

def check_password_ad(username, password):
    user = username + '@' + CONF['ldap']['ad_domain']

    with connect_ldap(authentication=SIMPLE, user=user, password=password) as c:
        c.bind()
        user_dn = find_user_dn(c, username)

def find_user_dn(conn, uid):
    search_filter = CONF['ldap']['search_filter'].replace('{uid}', uid)
    conn.search(CONF['ldap']['base'], "(%s)" % search_filter, SUBTREE)

    return conn.response[0]['dn'] if conn.response else None


def read_config():
    config = ConfigParser()

    # create sections just in case
    config.add_section('html')
    config.add_section('ldap')
    config.add_section('server')

    config.read([path.join(BASE_DIR, 'settings.ini'), os.getenv('CONF_FILE', '')])

    if 'WU_PAGE_TITLE' in environ:
      config.set('html', 'page_title', environ['WU_PAGE_TITLE'])
    if 'WU_LDAP_TYPE' in environ:
      config.set('ldap', 'type', environ['WU_LDAP_TYPE'])
    if 'WU_LDAP_HOST' in environ:
      config.set('ldap', 'host', environ['WU_LDAP_HOST'])
    if 'WU_LDAP_PORT' in environ:
      config.set('ldap', 'port', environ['WU_LDAP_PORT'])
    if 'WU_LDAP_USE_SSL' in environ:
      config.set('ldap', 'use_ssl', environ['WU_LDAP_USE_SSL'])
    if 'WU_LDAP_BASE' in environ:
      config.set('ldap', 'base', environ['WU_LDAP_BASE'])
    if 'WU_LDAP_SEARCH_FILTER' in environ:
      config.set('ldap', 'search_filter', environ['WU_LDAP_SEARCH_FILTER'])
    if 'WU_LDAP_USER' in environ:
      config.set('ldap', 'user', environ['WU_LDAP_USER'])
    if 'WU_LDAP_PASSWORD' in environ:
      config.set('ldap', 'password', environ['WU_LDAP_PASSWORD'])
    if 'WU_SERVER_MODE' in environ:
      config.set('server', 'server', environ['WU_SERVER_MODE'])
    if 'WU_SERVER_HOST' in environ:
      config.set('server', 'host', environ['WU_SERVER_HOST'])
    if 'WU_SERVER_PORT' in environ:
      config.set('server', 'port', environ['WU_SERVER_PORT'])

    return config


class Error(Exception):
    pass


if environ.get('DEBUG'):
    bottle.debug(True)

# Set up logging.
logging.basicConfig(format=LOG_FORMAT)
LOG.setLevel(logging.INFO)
LOG.info("Starting ldap-passwd-webui %s" % VERSION)

CONF = read_config()

bottle.TEMPLATE_PATH = [BASE_DIR]

# Set default attributes to pass into templates.
SimpleTemplate.defaults = dict(CONF['html'])
SimpleTemplate.defaults['url'] = bottle.url


# Run bottle internal server when invoked directly (mainly for development).
if __name__ == '__main__':
    bottle.run(**CONF['server'])
# Run bottle in application mode (in production under uWSGI server).
else:
    application = bottle.default_app()
