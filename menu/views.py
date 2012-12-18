
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

logger = logging.getLogger(__name__)
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
  return render_to_response('menu/merc_signup.html',{'form':form}, context_instance=RequestContext(request))    

@login_required
def fill_menu(request,bid):
   menuitemform = MenuItemForm()
   allergyform =AllergyInfoForm()
   otherinfoform = OtherInfoForm()
   nutritionform = NutritionInfoForm()
   b = get_object_or_404(InterestedBusiness,pk=int(bid))
   if request.method == 'POST':
     mi = MenuItem(business=b)
     form = MenuItemForm(request.POST,instance=mi)
     if form.is_valid():
       menuitem = form.save()

       instanceAllergy = AllergyInfo(menuitem=menuitem)
       instanceNutrition = NutritionInfo(menuitem=menuitem)
       instanceOther = OtherRestrictions(menuitem=menuitem)
       allergyform = AllergyInfoForm(request.POST, instance=instanceAllergy)
       otherinfoform = OtherInfoForm(request.POST, instance=instanceOther)
       nutritionform = OtherInfoForm(request.POST, instance=instanceNutrition)
       allergyform.save()
       nutritionform.save()
       otherinfoform.save()
       print 'saved a form!'
     else:
       print 'invalid form'
   menuitems = MenuItem.objects.filter(business=b)  
   mealName = dict()
   for m in menuitems:
    nm = m.get_meal_display()
    if m.meal in mealName:
      if m.category not in mealName[nm]:
        mealName[nm][m.category] =[]
    else:
      mealName[nm] = dict()
      mealName[nm][m.category] =[]
    mealName[nm][m.category].append(m)

   return render_to_response('menu/menu.html',{'business':b,'menuitems':mealName, 'mform':menuitemform, 'nform':nutritionform, 'aform':allergyform, 'oiform': otherinfoform}, context_instance=RequestContext(request))    

@login_required
def edit_menu(request,bid,mid):
  b = get_object_or_404(InterestedBusiness,pk=int(bid))
  mi = MenuItem.objects.get(id=mid)
  menuitemform = MenuItemForm(instance=mi)
  instanceAllergy = AllergyInfo(menuitem=mi)
  instanceNutrition = NutritionInfo(menuitem=mi)
  instanceOther = OtherRestrictions(menuitem=mi)
  
  allergyform = AllergyInfoForm( instance=instanceAllergy)
  otherinfoform = OtherInfoForm(  instance=instanceOther)
  nutritionform = OtherInfoForm( instance=instanceNutrition)
  if request.method == 'POST':
    form = MenuItemForm(request.POST,instance=mi)
    if form.is_valid():
      instanceAllergy = AllergyInfo(menuitem=mi)
      instanceNutrition = NutritionInfo(menuitem=mi)
      instanceOther = OtherRestrictions(menuitem=mi)
      allergyform = AllergyInfoForm(request.POST, instance=instanceAllergy)
      otherinfoform = OtherInfoForm(request.POST, instance=instanceOther)
      nutritionform = OtherInfoForm(request.POST, instance=instanceNutrition)
      allergyform.save()
      nutritionform.save()
      otherinfoform.save()
      print 'saved a form!'
    else:
      print 'invalid form'
    return HttpResponseRedirect('/menu/'+str(b.id))
  menuitems = MenuItem.objects.filter(business=b) 
  mealName = dict()
  for m in menuitems:
    nm = m.get_meal_display()
    if m.meal in mealName:
      if m.category not in mealName[nm]:
        mealName[nm][m.category] =[]
    else:
      mealName[nm] = dict()
      mealName[nm][m.category] =[]

    if m.id == int(mid):
      print 'EDITING SOMETHING'
      m.editing = True
    mealName[nm][m.category].append(m)
  return render_to_response('menu/menu.html',{'business':b,'menuitems':mealName, 'mform':menuitemform, 'nform':nutritionform, 'aform':allergyform, 'oiform': otherinfoform, 'editing':True}, context_instance=RequestContext(request))    

@login_required
def delete_menu(request,bid,mid):
   menuitemform = MenuItemForm()
   allergyform =AllergyInfoForm()
   otherinfoform = OtherInfoForm()
   nutritionform = NutritionInfoForm()
   MenuItem.objects.filter(id=mid).delete()
   
   b = get_object_or_404(InterestedBusiness,pk=int(bid))
   menuitems = MenuItem.objects.filter(business=b)  
   mealName = dict()
   for m in menuitems:
    nm = m.get_meal_display()
    if m.meal in mealName:
      if m.category not in mealName[nm]:
        mealName[nm][m.category] =[]
    else:
      mealName[nm] = dict()
      mealName[nm][m.category] =[]
    mealName[nm][m.category].append(m)

   return render_to_response('menu/menu.html',{'business':b,'menuitems':mealName, 'mform':menuitemform, 'nform':nutritionform, 'aform':allergyform, 'oiform': otherinfoform}, context_instance=RequestContext(request))    


