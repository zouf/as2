# Create your views here.
from coming_soon.models import InterestedUserForm, InterestedUser
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext



def coming_soon(request):
    interesteduser = InterestedUser()
    if request.method == "POST":
        formset = InterestedUserForm(request.POST)
        if formset.is_valid():
            formset.save()
            # Do something. Should generally end with a redirect. For example:
            return HttpResponseRedirect('allsortz.com')
    else:
        formset = InterestedUserForm(instance=interesteduser)
    return render_to_response('coming_soon.html', {
        "formset": formset,
    })    

def index(request):
    return render_to_response('index.html', context_instance=RequestContext(request))    
 
##experimenting with web version of app
#def detail(request,oid):
#    req =  get_business(request,oid);
#    context = json.loads(req.content)
#    return render_to_response('detail.html', context, context_instance=RequestContext(request)) 

def health_survey(request):
    return render_to_response('health.html', context_instance=RequestContext(request))    


