
# Create your views here.
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.template.context import RequestContext
from django.http import HttpResponseRedirect
from menu.forms import InterestedBusinessForm, MenuItemForm, AllergyInfoForm, NutritionInfoForm, OtherInfoForm
from menu.models import *
from django.shortcuts import render_to_response, get_object_or_404
import logging
from django.core import serializers

logger = logging.getLogger(__name__)


def generate_menu_list(b,editingID=None):
  menuitems = MenuItem.objects.filter(business=b).select_related('allergy','nutrition','otherinfo')
  mealName = dict()
  for m in menuitems:
    nm = m.get_meal_display()
    if nm  in mealName:
      if m.category not in mealName[nm]:
        mealName[nm][m.category] =[]
    else:
      mealName[nm] = dict()
      mealName[nm][m.category] =[]
    if editingID and editingID == m.id:
      m.editing = True
    mealName[nm][m.category].append(m)
    print mealName
  return mealName



@csrf_exempt
@login_required
def bus_signup(request):
  if request.user.is_authenticated():
    u = request.user
    if InterestedBusiness.objects.filter(owner=u.pk).count() > 0:
      print u.pk
      b =InterestedBusiness.objects.filter(owner=u.pk)[0]
      return HttpResponseRedirect('/menu/'+str(b.id))
    
  form = InterestedBusinessForm(request.POST)
  if form.is_valid():  
    b = form.save()
    b.owner = u
    b.save()
    return HttpResponseRedirect('/menu/'+str(b.id))
  else:
    form = InterestedBusinessForm()
  return render_to_response('menu/merchant/signup.html',{'form':form}, context_instance=RequestContext(request))    


@login_required
def get_menulist(request):
  businesses = InterestedBusiness.objects.all().select_related('menuitem')
  return render_to_response('menu/menus.html',{'businesses':businesses}, context_instance=RequestContext(request))    
 

@login_required
def get_edit_business(request,bid):
  b = get_object_or_404(InterestedBusiness,pk=int(bid))
  editing = True
  businessform = InterestedBusinessForm(instance=b)
  if request.method == 'POST':
    if request.user != b.owner:
      return HttpResponseRedirect('/invalid')
    bform = InterestedBusinessForm(request.POST, instance=b)
    if bform.is_valid():
      bform.save()
      return HttpResponseRedirect('/menu/'+str(b.id))

  return render_to_response('menu/menuelements/menu.html',{'business':b,'busform': businessform, 'editing':editing}, context_instance=RequestContext(request))    
    
@login_required
def get_edit_menu(request,bid):
   form = MenuItemForm()
   allergyform =AllergyInfoForm()
   otherinfoform = OtherInfoForm()
   nutritionform = NutritionInfoForm()
   b = get_object_or_404(InterestedBusiness,pk=int(bid))
   if request.method == 'POST':
     if request.user != b.owner:
       return HttpResponseRedirect('/invalid')
     mi = MenuItem(business=b)
     form = MenuItemForm(request.POST,instance=mi)
     if form.is_valid():
       menuitem = form.save()
       instanceAllergy = AllergyInfo(menuitem=menuitem)
       instanceNutrition = NutritionInfo(menuitem=menuitem)
       instanceOther = OtherRestrictions(menuitem=menuitem)
       
       allergyform = AllergyInfoForm(request.POST, instance=instanceAllergy)
       otherinfoform = OtherInfoForm(request.POST, instance=instanceOther)
       nutritionform = NutritionInfoForm(request.POST, instance=instanceNutrition)
       allergyform.save()
       nutritionform.save()
       otherinfoform.save()
       print 'saved a form!'
     else:
       print 'invalid form'
     return HttpResponseRedirect('/menu/'+str(b.id))
   mealName = generate_menu_list(b)
   return render_to_response('menu/menuelements/menu.html',{'business':b,'menuitems':mealName, 'mform':form, 'nform':nutritionform, 'aform':allergyform, 'oiform': otherinfoform}, context_instance=RequestContext(request))    

@login_required
def edit_menu(request,bid,mid):
  b = get_object_or_404(InterestedBusiness,pk=int(bid))
  mi = MenuItem.objects.get(id=mid)
  menuitemform = MenuItemForm(instance=mi)
  instanceAllergy = mi.allergy
  instanceNutrition = mi.nutrition
  instanceOther = mi.otherinfo
  
  allergyform = AllergyInfoForm( instance=instanceAllergy)
  otherinfoform = OtherInfoForm(  instance=instanceOther)
  nutritionform = NutritionInfoForm( instance=instanceNutrition)
  print ' before and method is ' + str(request.method)
  if request.method == 'POST':
    if request.user != b.owner:
      return HttpResponseRedirect('/invalid')
    form = MenuItemForm(request.POST,instance=mi)
    print 'here and form is ' + str(form)
    if form.is_valid():
      mi = form.save()
      instanceAllergy = mi.allergy
      instanceNutrition = mi.nutrition
      instanceOther = mi.otherinfo
      allergyform = AllergyInfoForm(request.POST, instance=instanceAllergy)
      otherinfoform = OtherInfoForm(request.POST, instance=instanceOther)
      nutritionform = NutritionInfoForm(request.POST, instance=instanceNutrition)
      print nutritionform
      allergyform.save()
      nutritionform.save()
      otherinfoform.save()
      print 'saved a form!'
    else:
      print 'invalid form'
    return HttpResponseRedirect('/menu/'+str(b.id))
  mealName = generate_menu_list(b,int(mid))
  return render_to_response('menu/menuelements/menu.html',{'business':b,'menuitems':mealName, 'mform':menuitemform, 'nform':nutritionform, 'aform':allergyform, 'oiform': otherinfoform, 'editing':True}, context_instance=RequestContext(request))    

@login_required
def delete_menu(request,bid,mid):
   b = get_object_or_404(InterestedBusiness,pk=int(bid))
   if request.user != b.owner:
     return HttpResponseRedirect('/invalid')
   MenuItem.objects.filter(id=mid).delete()
   return HttpResponseRedirect('/menu/'+str(b.id))


@login_required
def get_edit_details(request,bid,mid):
  b = get_object_or_404(InterestedBusiness,pk=int(bid))
  mi = MenuItem.objects.get(id=mid)
  instanceAllergy = mi.allergy
  instanceNutrition = mi.nutrition
  instanceOther = mi.otherinfo
    

  if 'editing' in request.GET:
    if request.user != b.owner:
     return HttpResponseRedirect('/invalid')
    editing = True
  else:
    editing = False

  form = MenuItemForm(instance=mi)
  allergyform = AllergyInfoForm( instance=instanceAllergy)
  otherinfoform = OtherInfoForm(  instance=instanceOther)
  nutritionform = NutritionInfoForm( instance=instanceNutrition)
  print ' before and method is ' + str(request.method)
  if request.method == 'POST':
    if request.user != b.owner:
     return HttpResponseRedirect('/invalid')
    form = MenuItemForm(request.POST,instance=mi)
    print 'here and form is ' + str(form)
    if form.is_valid():
      mi = form.save()
      instanceAllergy = mi.allergy
      instanceNutrition = mi.nutrition
      instanceOther = mi.otherinfo
      allergyform = AllergyInfoForm(request.POST, instance=instanceAllergy)
      otherinfoform = OtherInfoForm(request.POST, instance=instanceOther)
      nutritionform = NutritionInfoForm(request.POST, instance=instanceNutrition)
      print nutritionform
      allergyform.save()
      nutritionform.save()
      otherinfoform.save()
      print 'saved a form!'
    else:
      print 'invalid form'
    return HttpResponseRedirect('/menu/'+str(b.id)+'/details/'+str(mi.id))
  return render_to_response('menu/dish/dishdetails.html',{'business':b,'m':mi, 'mform':form, 'nform':nutritionform, 'aform':allergyform, 'oiform': otherinfoform, 'editing':editing}, context_instance=RequestContext(request))    

