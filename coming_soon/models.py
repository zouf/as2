from django.db import models
from django.contrib.localflavor.us.us_states import STATE_CHOICES
from django.contrib.localflavor.us.models import USStateField
from django.forms import ModelForm
# Create your models here.


class InterestedUser(models.Model):
    first_name = models.CharField(_('first name'), max_length=30, blank=True, null=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True, null=True)
    email = models.EmailField(_('e-mail address'))
    city = models.CharField(_('city'), max_length=50, blank=True, null=True)
    state = USStateField(choices = STATE_CHOICES, blank=True,null=True)

    def __unicode__(self):
        return self.email


class InterestedUserForm(ModelForm):
    class Meta:
        model = InterestedUser
        exclude = ('first_name','last_name')