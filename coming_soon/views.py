# Create your views here.
from django.shortcuts import render_to_response
from django.template.context import RequestContext
try:
    import json
except ImportError:
    import simplejson as json
from api.views import *
def coming_soon(request):
    return render_to_response('coming_soon.html', context_instance=RequestContext(request))    

def index(request):
    return render_to_response('index.html', context_instance=RequestContext(request))    
 

def detail(request,oid):
    req =  get_business(request,oid);
    context = json.loads(req.content)
    return render_to_response('detail.html', context, context_instance=RequestContext(request)) 
             
