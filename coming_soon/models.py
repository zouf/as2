from django.db import models
from django.contrib.localflavor.us.us_states import STATE_CHOICES
from django.contrib.localflavor.us.models import USStateField
from django.forms import ModelForm
# Create your models here.

class Visitor(models.Model):
  ip = models.IPAddressField(blank=True)#define field ip
  date = models.DateTimeField(auto_now_add=True, editable=False)
  referer = models.URLField(blank=True, verify_exists=False)# define field referer
  user_agent = models.CharField(blank=True, max_length=100) #define field user_agent

class InterestedUser(models.Model):
    first_name = models.CharField( max_length=30, blank=True, null=True)
    last_name = models.CharField( max_length=30, blank=True, null=True)
    email = models.EmailField()
    city = models.CharField( max_length=50, blank=True, null=True)
    state = USStateField(blank=True,null=True)
    visited_from = models.ForeignKey(Visitor, null=True)
    def __unicode__(self):
        return self.email






class InterestedUserForm(ModelForm):
    class Meta:
        model = InterestedUser
        exclude = ('first_name','last_name', 'city', 'state', 'visited_from')

