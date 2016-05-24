import datetime
import urllib
import urlparse

from django.http import (
    HttpResponseNotAllowed, HttpResponseRedirect, HttpResponse,
)
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from openid.consumer.consumer import Consumer, SUCCESS as auth_SUCCESS
from openid.consumer import discover

import store

COOKIE_NAME = 'openidgae_sess'
if hasattr(settings, 'OPENIDGAE_COOKIE_NAME'):
    COOKIE_NAME = settings.OPENIDGAE_COOKIE_NAME


def get_continue_url(request, default_success_url):
    continueUrl = request.GET.get('continue', default_success_url)
    # Sanitize
    if continueUrl.find('//') >= 0 or not continueUrl.startswith('/'):
        continueUrl = default_success_url
    return continueUrl


def get_full_path(request):
    full_path = (
        'http',
        ('', 's')[request.is_secure()],
        '://',
        request.META['HTTP_HOST'],
        request.path
    )
    return ''.join(full_path)


def args_to_dict(querydict):
    return dict([(arg, values[0]) for arg, values in querydict.lists()])


def err_page(err_id, msg=''):
    return HttpResponseRedirect(
        reverse(ErrorPage, kwargs={'err_id': err_id, })
    )


# Handlers #
def ErrorPage(request, err_id, success_handler=None):
    return HttpResponse(err_id)


@csrf_exempt
def OpenIDStartSubmit(request, default_success_url='/', success_handler=None):
    response = HttpResponse()
    openid = request.REQUEST.get('openid_identifier', '').strip()
    if not openid:
        return err_page("no_openid_identifier")

    c = Consumer({}, store.DatastoreStore())
    try:
        auth_request = c.begin(openid)

    except discover.DiscoveryFailure, e:
        return err_page(
            "server_discovery",
            msg='OpenID discovery error with begin on %s: %s' % (
                openid, str(e)
            )
        )

    parts = list(urlparse.urlparse(get_full_path(request)))
    # finish URL with the leading "/" character removed
    parts[2] = reverse(OpenIDFinish)[1:]

    continueUrl = get_continue_url(request, default_success_url)
    parts[4] = 'continue=%s' % urllib.quote_plus(continueUrl)
    parts[5] = ''
    return_to = urlparse.urlunparse(parts)

    realm = urlparse.urlunparse(parts[0:2] + [''] * 4)

    # save the openid session stuff
    expires = datetime.datetime.now() + datetime.timedelta(hours=1)
    expires_rfc822 = expires.strftime('%a, %d %b %Y %H:%M:%S +0000')
    response.set_cookie(
        COOKIE_NAME,
        store.saveConsumerSession(c.session),
        expires=expires_rfc822
    )

    # send the redirect!  we use a meta because appengine bombs out
    # sometimes with long redirect urls
    redirect_url = auth_request.redirectURL(realm, return_to)
    response.write(
        "<html>"
        "<head><meta http-equiv=\"refresh\" content=\"0;url=%s\"></head>"
        "<body></body>"
        "</html>"
        % (redirect_url,))
    return response


@csrf_exempt
def OpenIDFinish(request, default_success_url='/', success_handler=None):
    if request.method not in ('GET', 'POST'):
        return HttpResponseNotAllowed(['GET', 'POST'])
    else:
        args = args_to_dict(request.GET)
        assert type(args) is dict
        if request.method == 'POST':
            args.update(args_to_dict(request.POST))
        url = 'http://'+request.META['HTTP_HOST'] + reverse(OpenIDFinish)

        s = {}
        sess_key = request.COOKIES.get(COOKIE_NAME, None)
        if sess_key:
            s = store.restoreConsumerSession(sess_key)

        c = Consumer(s, store.DatastoreStore())
        auth_response = c.complete(args, url)

        if auth_response.status == auth_SUCCESS:

            openid_url = auth_response.getDisplayIdentifier()
            continueUrl = get_continue_url(request, default_success_url)
            response = HttpResponseRedirect(continueUrl)

            if success_handler:
                success_handler(request, response, openid_url)

            return response

        else:
            return err_page("verification_failed")


def RelyingPartyXRDS(request, success_handler=None):
    response = HttpResponse()
    url_finish = reverse(OpenIDFinish)
    if request.method == 'GET':
        xrds = """
    <?xml version='1.0' encoding='UTF-8'?>
    <xrds:XRDS
      xmlns:xrds='xri://$xrds'
      xmlns:openid='http://openid.net/xmlns/1.0'
      xmlns='xri://$xrd*($v*2.0)'>
      <XRD>
        <Service>
          <Type>http://specs.openid.net/auth/2.0/return_to</Type>
          <URI>http://%s%s</URI>
        </Service>
    </XRD>
    </xrds:XRDS>
    """ % (request.META['HTTP_HOST'], url_finish)

        response['Content-Type'] = 'application/xrds+xml'
        response.write(xrds)
        return response
