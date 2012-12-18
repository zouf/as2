from menu.models import *
from django.forms import *

class InterestedBusinessForm(ModelForm):
    class Meta:
        model = InterestedBusiness
        exclude = ('geom','lat', 'lon', 'owner')



class MenuItemForm(ModelForm):
    class Meta:
        model = MenuItem  
        exclude = ('business')



class AllergyInfoForm(ModelForm):
    class Meta:
      model = AllergyInfo
      exclude = ('menuitem')




class NutritionInfoForm(ModelForm):
    class Meta:
      model = NutritionInfo
      exclude = ('menuitem')

class OtherInfoForm(ModelForm):
    class Meta:
      model = OtherRestrictions
      exclude = ('menuitem')

