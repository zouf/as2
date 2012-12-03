# Create your views here.
from coming_soon.models import InterestedUserForm, InterestedUser, Visitor
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
import datetime
from django.template.context import RequestContext
from django.template import loader
from survey.models import *
from survey.forms import *
import logging
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.mail import EmailMultiAlternatives
logger = logging.getLogger(__name__)

def send_thankyou(to):
  subject, from_email = 'thanks!', 'matt@allsortz.com'
  text_content = 'thanks for signing up!'
  html_content = '<p>thanks for signing up! we will be in touch </p><br><br><p>-the allsortz team</p>'
  msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
  msg.attach_alternative(html_content, "text/html")
  msg.send()

def send_response_email(to,content,subject):
  subject, from_email = subject, 'matt@allsortz.com'
  text_content = 'thanks for signing up!'
  html_content = content 
  msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
  msg.attach_alternative(html_content, "text/html")
  msg.send()



def coming_soon(request):
  #try:
  #  hit = Visitor() #created a visitor log start
  #  hit.ip = request.META.get("REMOTE_ADDR", "") #get visitor ip
  #  hit.date = datetime.datetime.now() # get visitor time
  #  hit.referer = request.META.get("HTTP_REFERER", "") #get visitor referer
  #  hit.user_agent = request.META.get("HTTP_USER_AGENT", "") # get visitor user agent
  #  hit.save() #save in database
  #except Exception as e:
  #  logger.debug('Error in log' + str(e))
  #  pass


  interesteduser = InterestedUser()
  if request.method == "POST":
      formset = InterestedUserForm(request.POST)
      if formset.is_valid():
          iu = formset.save()
          iu.save()
          t = loader.get_template('signup_thanks.html')
          c = Context({})
          content = t.render(c)
          send_response_email(iu.email, content,'Thanks!')
          return HttpResponseRedirect('/')
  else:
    formset = InterestedUserForm(instance=interesteduser, initial={'email': 'E-mail'})
  return render_to_response('coming_soon.html', {
      "form": formset,
  },
  context_instance=RequestContext(request)
  )    


##experimenting with web version of app
#def detail(request,oid):
#    req =  get_business(request,oid);
#    context = json.loads(req.content)
#    return render_to_response('detail.html', context, context_instance=RequestContext(request)) 

def survey_detail(request, survey_slug='eatinghealthy',
               group_slug=None, group_slug_field=None, group_qs=None,
               template_name = 'health.html',
               extra_context=None,
               allow_edit_existing_answers=False,
               *args, **kw):
    """

    """
    survey = get_object_or_404(Survey.objects.filter(visible=True), slug=survey_slug)
    # if user has a session and have answered some questions
    # and the survey does not accept multiple answers,
    # go ahead and redirect to the answers, or a thank you
#    if (hasattr(request, 'session') and
#        survey.has_answers_from(request.session.session_key) and
#        not survey.allows_multiple_interviews and not allow_edit_existing_answers):
#        return _survey_redirect(request, survey,group_slug=group_slug)
    # if the survey is restricted to authentified user redirect
    # annonymous user to the login page
    if survey.restricted and str(request.user) == "AnonymousUser":
        return HttpResponseRedirect(reverse("auth_login")+"?next=%s" % request.path)
    if request.POST and not hasattr(request, 'session'):
        return HttpResponse(unicode(_('Cookies must be enabled.')), status=403)
    if hasattr(request, 'session'):
        skey = 'survey_%d' % survey.id
        request.session[skey] = (request.session.get(skey, False) or
                                 request.method == 'POST')
        request.session.modified = True ## enforce the cookie save.
    survey.forms = forms_for_survey(survey, request, allow_edit_existing_answers)
    if (request.POST and all(form.is_valid() for form in survey.forms)):
        for form in survey.forms:
            form.save()
        t = loader.get_template('survey_thanks.html')
        c = Context({})
        content = t.render(c)
        return HttpResponseRedirect('http://www.allsortz.com')
    # Redirect either to 'survey.template_name' if this attribute is set or
    # to the default template
    return render_to_response(survey.template_name or template_name,
                              {'survey': survey,
                               'title': survey.title,
                               'group_slug': group_slug},
                              context_instance=RequestContext(request))





def about(request):
    return render_to_response('about.html', context_instance=RequestContext(request))    
def contact(request):
  return render_to_response('contact.html', context_instance=RequestContext(request))    
def merchants(request):
  return render_to_response('merchants.html', context_instance=RequestContext(request))    
def learn(request):
  return render_to_response('details.html', context_instance=RequestContext(request))    

