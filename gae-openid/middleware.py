# Google App Engine OpenID Consumer Django App
# http://code.google.com/p/google-app-engine-django-openid/
#
# Copyright (C) 2009 Wesley Tanaka <http://wtanaka.com/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
import django.core.urlresolvers
from google.appengine.api import urlfetch

import sys, os
opeid_lib = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'openid.zip')
if opeid_lib not in sys.path:
  sys.path.insert(0, opeid_lib)

import openid
import views

class UrlfetchFetcher(openid.fetchers.HTTPFetcher):
  """An HTTPFetcher subclass that uses Google App Engine's urlfetch module.
  """
  def fetch(self, url, body=None, headers=None):
    if not openid.fetchers._allowedURL(url):
      raise ValueError('Bad URL scheme: %r' % (url,))
    
    if not headers:
      headers = {}

    if body:
      method = urlfetch.POST
      headers['Content-type'] = 'application/x-www-form-urlencoded' 
    else:
      method = urlfetch.GET

    count = 0
    resp = urlfetch.fetch(url, body, method, headers=headers)

    # follow redirects for a while
    while resp.status_code in [301,302]:
      count += 1
      if count >= 3:
        raise Exception('too many redirects')

      if resp.headers.has_key('location'):
        url = resp.headers['location']
      elif resp.headers.has_key('Location'):
        url = resp.headers['Location']
      else:
        raise Exception('Could not find location in headers: %r' % (resp.headers,))
      
      resp = urlfetch.fetch(url, body, method, headers=headers)

    # normalize headers
    for key, val in resp.headers.items():
      resp.headers[key.lower()] = val

    return openid.fetchers.HTTPResponse(url, resp.status_code, resp.headers, resp.content)

class OpenIDMiddleware(object):
  """This middleware initializes some settings to make the
  python-openid library compatible with Google App Engine
  """
  def process_view(self, request, view_func, view_args, view_kwargs):
    openid.fetchers.setDefaultFetcher(UrlfetchFetcher())

    # Switch logger to use logging package instead of stderr
    def myLoggingFunction(message, level=0):
      logging.info(message)
    openid.oidutil.log = myLoggingFunction

  def process_response(self, request, response):
    # Yahoo wants to be able to verify the location of a Relying
    # Party's OpenID 2.0 endpoints using Yadis
    # http://developer.yahoo.com/openid/faq.html
    # so we need to publish our XRDS file on our realm URL.  The Realm
    # URL is specified in OpenIDStartSubmit as the protocol and domain
    # name of the URL, so we check if this request is for the root
    # document there and add the appropriate header if it is.
    if request.path == '/':
      response['X-XRDS-Location'] = ''.join((
          'http', ('', 's')[request.is_secure()], '://',
          request.META['HTTP_HOST'],
          django.core.urlresolvers.reverse(views.RelyingPartyXRDS)
          ))
    return response
