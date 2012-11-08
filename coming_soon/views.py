# Create your views here.
from coming_soon.models import InterestedUserForm, InterestedUser, Visitor
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
import datetime
from django.template.context import RequestContext

import logging

logger = logging.getLogger(__name__)


def coming_soon(request):
  try:
    hit = Visitor() #created a visitor log start
    hit.ip = request.META.get("REMOTE_ADDR", "") #get visitor ip
    hit.date = datetime.datetime.now() # get visitor time
    hit.referer = request.META.get("HTTP_REFERER", "") #get visitor referer
    hit.user_agent = request.META.get("HTTP_USER_AGENT", "") # get visitor user agent
    hit.save() #save in database
  except Exception as e:
    print('ERROR IN VISITOR'  + str(e))
    logger.debug('Error in log' + str(e))
    pass


  interesteduser = InterestedUser()
  if request.method == "POST":
      formset = InterestedUserForm(request.POST)
      if formset.is_valid():
          iu = formset.save()
          iu.visited_from = hit
          iu.save()
          # Do something. Should generally end with a redirect. For example:
          return HttpResponseRedirect('')
  else:
      formset = InterestedUserForm(instance=interesteduser, initial={'email': 'E-mail'})
  return render_to_response('coming_soon.html', {
      "form": formset,
  },
  context_instance=RequestContext(request)
  )    

def index(request):
    return render_to_response('index.html', context_instance=RequestContext(request))    
 
##experimenting with web version of app
#def detail(request,oid):
#    req =  get_business(request,oid);
#    context = json.loads(req.content)
#    return render_to_response('detail.html', context, context_instance=RequestContext(request)) 

def health_survey(request):
    return render_to_response('health.html', context_instance=RequestContext(request))    


