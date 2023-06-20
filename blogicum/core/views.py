from django.shortcuts import render
from django.template import RequestContext


def e_handler500(request):
    context = RequestContext(request)
    response = render('pages/500.html', context)
    response.status_code = 500
    return response


def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)

def csrf_failure(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)
