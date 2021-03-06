# -*- coding: utf-8 -*-

#       Licensed to the Apache Software Foundation (ASF) under one
#       or more contributor license agreements.  See the NOTICE file
#       distributed with this work for additional information
#       regarding copyright ownership.  The ASF licenses this file
#       to you under the Apache License, Version 2.0 (the
#       "License"); you may not use this file except in compliance
#       with the License.  You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#       Unless required by applicable law or agreed to in writing,
#       software distributed under the License is distributed on an
#       "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#       KIND, either express or implied.  See the License for the
#       specific language governing permissions and limitations
#       under the License.

"""REST Controller"""
import logging

import oauth2 as oauth
from paste.util.converters import asbool
from webob import exc
from tg import expose, flash, redirect, config
from pylons import tmpl_context as c, app_globals as g
from pylons import request, response

from ming.orm import session
from ming.utils import LazyProperty

from allura import model as M
from allura.lib import helpers as h
from allura.lib import security
from allura.lib import plugin
from allura.lib.exceptions import Invalid
from allura.lib.decorators import require_post

log = logging.getLogger(__name__)
action_logger = h.log_action(log, 'API:')


class RestController(object):

    def __init__(self):
        self.oauth = OAuthNegotiator()

    def _authenticate_request(self):
        'Based on request.params or oauth, authenticate the request'
        headers_auth = 'Authorization' in request.headers
        params_auth = 'oauth_token' in request.params
        params_auth = params_auth or 'access_token' in request.params
        if headers_auth or params_auth:
            return self.oauth._authenticate()
        else:
            return None

    @expose('json:')
    def index(self, **kw):
        """Return site summary information as JSON.

        Currently, the only summary information returned are any site_stats
        whose providers are defined as entry points under the
        'allura.site_stats' group in a package or tool's setup.py, e.g.::

            [allura.site_stats]
            new_users_24hr = allura.site_stats:new_users_24hr

        The stat provider will be called with no arguments to generate the
        stat, which will be included under a key equal to the name of the
        entry point.

        Example output::

            {
                'site_stats': {
                    'new_users_24hr': 10
                }
            }
        """
        summary = dict()
        stats = dict()
        for stat, provider in g.entry_points['site_stats'].iteritems():
            stats[stat] = provider()
        if stats:
            summary['site_stats'] = stats
        return summary

    @expose()
    def _lookup(self, name, *remainder):
        c.api_token = self._authenticate_request()
        if c.api_token:
            c.user = c.api_token.user
        neighborhood = M.Neighborhood.query.get(url_prefix='/' + name + '/')
        if not neighborhood:
            raise exc.HTTPNotFound, name
        return NeighborhoodRestController(neighborhood), remainder


class OAuthNegotiator(object):

    @LazyProperty
    def server(self):
        result = oauth.Server()
        result.add_signature_method(oauth.SignatureMethod_PLAINTEXT())
        result.add_signature_method(oauth.SignatureMethod_HMAC_SHA1())
        return result

    def _authenticate(self):
        bearer_token_prefix = 'Bearer '
        auth = request.headers.get('Authorization')
        if auth and auth.startswith(bearer_token_prefix):
            access_token = auth[len(bearer_token_prefix):]
        else:
            access_token = request.params.get('access_token')
        if access_token:
            # handle bearer tokens
            # skip https check if auth invoked from tests
            testing = request.environ.get('paste.testing', False)
            debug = asbool(config.get('debug', False))
            if not testing and request.scheme != 'https' and not debug:
                request.environ['pylons.status_code_redirect'] = True
                raise exc.HTTPForbidden
            access_token = M.OAuthAccessToken.query.get(api_key=access_token)
            if not (access_token and access_token.is_bearer):
                request.environ['pylons.status_code_redirect'] = True
                raise exc.HTTPForbidden
            return access_token
        req = oauth.Request.from_request(
            request.method,
            request.url.split('?')[0],
            headers=request.headers,
            parameters=dict(request.params),
            query_string=request.query_string
        )
        consumer_token = M.OAuthConsumerToken.query.get(
            api_key=req['oauth_consumer_key'])
        access_token = M.OAuthAccessToken.query.get(
            api_key=req['oauth_token'])
        if consumer_token is None:
            log.error('Invalid consumer token')
            return None
            raise exc.HTTPForbidden
        if access_token is None:
            log.error('Invalid access token')
            raise exc.HTTPForbidden
        consumer = consumer_token.consumer
        try:
            self.server.verify_request(req, consumer, access_token.as_token())
        except:
            log.error('Invalid signature')
            raise exc.HTTPForbidden
        return access_token

    @expose()
    def request_token(self, **kw):
        req = oauth.Request.from_request(
            request.method,
            request.url.split('?')[0],
            headers=request.headers,
            parameters=dict(request.params),
            query_string=request.query_string
        )
        consumer_token = M.OAuthConsumerToken.query.get(
            api_key=req['oauth_consumer_key'])
        if consumer_token is None:
            log.error('Invalid consumer token')
            raise exc.HTTPForbidden
        consumer = consumer_token.consumer
        try:
            self.server.verify_request(req, consumer, None)
        except:
            log.error('Invalid signature')
            raise exc.HTTPForbidden
        req_token = M.OAuthRequestToken(
            consumer_token_id=consumer_token._id,
            callback=req.get('oauth_callback', 'oob')
        )
        session(req_token).flush()
        log.info('Saving new request token with key: %s', req_token.api_key)
        return req_token.to_string()

    @expose('jinja:allura:templates/oauth_authorize.html')
    def authorize(self, oauth_token=None):
        security.require_authenticated()
        rtok = M.OAuthRequestToken.query.get(api_key=oauth_token)
        if rtok is None:
            log.error('Invalid token %s', oauth_token)
            raise exc.HTTPForbidden
        rtok.user_id = c.user._id
        return dict(
            oauth_token=oauth_token,
            consumer=rtok.consumer_token)

    @expose('jinja:allura:templates/oauth_authorize_ok.html')
    @require_post()
    def do_authorize(self, yes=None, no=None, oauth_token=None):
        security.require_authenticated()
        rtok = M.OAuthRequestToken.query.get(api_key=oauth_token)
        if no:
            rtok.delete()
            flash('%s NOT AUTHORIZED' % rtok.consumer_token.name, 'error')
            redirect('/auth/oauth/')
        if rtok.callback == 'oob':
            rtok.validation_pin = h.nonce(6)
            return dict(rtok=rtok)
        rtok.validation_pin = h.nonce(20)
        if '?' in rtok.callback:
            url = rtok.callback + '&'
        else:
            url = rtok.callback + '?'
        url += 'oauth_token=%s&oauth_verifier=%s' % (
            rtok.api_key, rtok.validation_pin)
        redirect(url)

    @expose()
    def access_token(self, **kw):
        req = oauth.Request.from_request(
            request.method,
            request.url.split('?')[0],
            headers=request.headers,
            parameters=dict(request.params),
            query_string=request.query_string
        )
        consumer_token = M.OAuthConsumerToken.query.get(
            api_key=req['oauth_consumer_key'])
        request_token = M.OAuthRequestToken.query.get(
            api_key=req['oauth_token'])
        if consumer_token is None:
            log.error('Invalid consumer token')
            raise exc.HTTPForbidden
        if request_token is None:
            log.error('Invalid request token')
            raise exc.HTTPForbidden
        pin = req['oauth_verifier']
        if pin != request_token.validation_pin:
            log.error('Invalid verifier')
            raise exc.HTTPForbidden
        rtok = request_token.as_token()
        rtok.set_verifier(pin)
        consumer = consumer_token.consumer
        try:
            self.server.verify_request(req, consumer, rtok)
        except:
            log.error('Invalid signature')
            raise exc.HTTPForbidden
        acc_token = M.OAuthAccessToken(
            consumer_token_id=consumer_token._id,
            request_token_id=request_token._id,
            user_id=request_token.user_id,
        )
        return acc_token.to_string()


def rest_has_access(obj, user, perm):
    """
    Helper function that encapsulates common functionality for has_access API
    """
    security.require_access(obj, 'admin')
    resp = {'result': False}
    user = M.User.by_username(user)
    if user:
        resp['result'] = security.has_access(obj, perm, user=user)()
    return resp


class AppRestControllerMixin(object):
    @expose('json:')
    def has_access(self, user, perm, **kw):
        return rest_has_access(c.app, user, perm)


class NeighborhoodRestController(object):

    def __init__(self, neighborhood):
        self._neighborhood = neighborhood

    @expose('json:')
    def has_access(self, user, perm, **kw):
        return rest_has_access(self._neighborhood, user, perm)

    @expose()
    def _lookup(self, name, *remainder):
        provider = plugin.ProjectRegistrationProvider.get()
        try:
            provider.shortname_validator.to_python(
                name, check_allowed=False, neighborhood=self._neighborhood)
        except Invalid:
            raise exc.HTTPNotFound, name
        name = self._neighborhood.shortname_prefix + name
        project = M.Project.query.get(
            shortname=name, neighborhood_id=self._neighborhood._id, deleted=False)
        if not project:
            raise exc.HTTPNotFound, name

        if project and name and name.startswith('u/'):
            # make sure user-projects are associated with an enabled user
            user = project.user_project_of
            if not user or user.disabled:
                raise exc.HTTPNotFound

        c.project = project
        return ProjectRestController(), remainder


class ProjectRestController(object):

    @expose()
    def _lookup(self, name, *remainder):
        if not name:
            return self, ()
        subproject = M.Project.query.get(
            shortname=c.project.shortname + '/' + name,
            neighborhood_id=c.project.neighborhood_id,
            deleted=False)
        if subproject:
            c.project = subproject
            c.app = None
            return ProjectRestController(), remainder
        app = c.project.app_instance(name)
        if app is None:
            raise exc.HTTPNotFound, name
        c.app = app
        if app.api_root is None:
            raise exc.HTTPNotFound, name
        action_logger.info('', extra=dict(
            api_key=request.params.get('api_key')))
        return app.api_root, remainder

    @expose('json:')
    def index(self, **kw):
        if 'doap' in kw:
            response.headers['Content-Type'] = ''
            response.content_type = 'application/rdf+xml'
            return '<?xml version="1.0" encoding="UTF-8" ?>' + c.project.doap()
        return c.project.__json__()

    @expose('json:')
    def has_access(self, user, perm, **kw):
        return rest_has_access(c.project, user, perm)
