from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render

def index(request):
    return render(request, 'home.html')
    #template = loader.get_template('home.html')
    #return HttpResponse(template.render({}, request))

