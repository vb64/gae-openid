import logging
from django.shortcuts import render_to_response

def mainpage(request):
    return render_to_response('main.html')

def success_handler(request, response, openid_url):
    logging.warning("success_handler openid_url: %s" % openid_url)
