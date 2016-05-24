import logging

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect

COOKIE_NAME = 'openid_wg_auth'


def mainpage(request):
    return render_to_response(
        'main.html',
        {'openid': request.COOKIES.get(COOKIE_NAME, None)}
    )


def logout(request):
    response = HttpResponseRedirect('/')
    response.delete_cookie(COOKIE_NAME)
    return response


def success_handler(request, response, openid_url):
    # do not do it in a real application!!! it's just a simple example
    response.set_cookie(COOKIE_NAME, openid_url)
    logging.warning("success_handler openid_url: %s" % openid_url)
