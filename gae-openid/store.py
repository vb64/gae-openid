#!/usr/bin/python

import time, md5

from openid.association import Association as xAssociation
from openid.store.interface import OpenIDStore
from openid.store import nonce

from google.appengine.ext import db
from google.appengine.api import memcache

consumer_session_key = "consumer_sess_%s"

class OpenID_Hosts(db.Model):
  """An association with another OpenID server, either a consumer or a provider.
  """
  url = db.LinkProperty()
  handle = db.StringProperty()
  association = db.TextProperty()

def saveConsumerSession(data):
  key = md5.new("%s" % data).hexdigest()
  memcache.set(consumer_session_key % key, data)
  return key

def restoreConsumerSession(key):
  return memcache.get(consumer_session_key % key)

class DatastoreStore(OpenIDStore):
  """An OpenIDStore implementation that uses the datastore. See
  openid/store/interface.py for in-depth descriptions of the methods.

  They follow the OpenID python library's style, not Google's style, since
  they override methods defined in the OpenIDStore class.
  """

  def storeAssociation(self, server_url, assoc):
    """
    This method puts a C{L{Association <openid.association.Association>}}
    object into storage, retrievable by server URL and handle.
    """
    assoc = OpenID_Hosts(url=server_url,
                        handle=assoc.handle,
                        association=assoc.serialize())
    assoc.put()

  def getAssociation(self, server_url, handle=None):
    """
    This method returns an C{L{Association <openid.association.Association>}}
    object from storage that matches the server URL and, if specified, handle.
    It returns C{None} if no such association is found or if the matching
    association is expired.

    If no handle is specified, the store may return any association which
    matches the server URL. If multiple associations are valid, the
    recommended return value for this method is the one that will remain valid
    for the longest duration.
    """
    query = OpenID_Hosts.all().filter('url', server_url)
    if handle:
      query.filter('handle', handle)

    results = query.fetch(1)
    assoc = None
    if len(results) > 0:
      assoc = xAssociation.deserialize(results[0].association)
      if assoc.getExpiresIn() <= 0:
        results[0].delete() #self.removeAssociation(server_url, handle)
        assoc = None
    
    return assoc


  def removeAssociation(self, server_url, handle):
    """
    This method removes the matching association if it's found, and returns
    whether the association was removed or not.
    """
    query = OpenID_Hosts.gql('WHERE url = :1 AND handle = :2', server_url, handle)
    return self._delete_first(query)

  def useNonce(self, server_url, timestamp, salt):
    anonce = "oi_nonce_%s" % str((str(server_url), int(timestamp), str(salt)))
    if (abs(timestamp - time.time()) > nonce.SKEW) or memcache.get(anonce):
      return False
    memcache.set(anonce, True)
    return True

  def cleanunNonces(self):
    return 0


  def _delete_first(self, query):
    """Deletes the first result for the given query.

    Returns True if an entity was deleted, false if no entity could be deleted
    or if the query returned no results.
    """
    results = query.fetch(1)

    if results:
      try:
        results[0].delete()
        return True
      except db.Error:
        return False
    else:
      return False
