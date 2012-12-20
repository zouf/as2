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

    def clean(self):
      cleaned_data = self.cleaned_data
      name = cleaned_data.get('name')
      bus = self.instance.business
#      if MenuItem.objects.filter(business=bus, name=name).count() > 0:
#        raise ValidationError("Dish already entered!")
      return cleaned_data
  




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

