# Create your views here.
from django.shortcuts import render_to_response
from django.template.context import RequestContext

def coming_soon(request):
    return render_to_response('coming_soon.html', context_instance=RequestContext(request))    

def index(request):
    return render_to_response('index.html', context_instance=RequestContext(request))    
       
