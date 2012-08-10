'''
Created on Apr 2, 2012

@author: Joey
'''
from api.categories import get_master_summary_tag, add_tag_to_bus
from api.models import Tag, Business, TypeOfBusiness, BusinessType
from api.photos import add_photo_by_url
from as2 import settings
from django.contrib.auth.models import User
from queries.models import Query

import csv
import logging

logger = logging.getLogger(__name__)

def get_default_user():
    try:
        user = User.objects.get(username='matt')
    except:
        user = User(first_name='Matt', email='matty@allsortz.com', username='zouf')
        user.set_password("testing")
        user.save()
        
    return user

def create_user(username, uid):
    u = User(username=("u" + str(uid)), first_name=(username[0:20].encode("utf8")), password="")
    # u.set_password("test")
    return u


def prepop_sorts(user):
    reader = csv.reader(open(settings.BASE_DIR+'/prepop/sorts2.csv', 'U'), delimiter=',', quotechar='"')
    i = 0
    for row in reader:
        i+=1
        if i == 1:
            continue
       
        descr = row[0]
        icon = row[1]

        tset = Tag.objects.filter(descr=descr)
        if tset.count() > 0:
            continue
             
        t = Tag(descr=descr,creator=user,icon=icon)
        t.save()
        
        
#def prepop_traits(user):
#    reader = csv.reader(open(settings.BASE_DIR+'/prepop/traits.csv', 'U'), delimiter=',', quotechar='"')
#    i = 0
#    for row in reader:
#        i+=1
#        if i == 1:
#            continue
#       
#        name = row[0]
#        descr = row[1]
#
#        print('Trait name: '+str(name))
#        print('trait descr: '+str(descr))
#        
#        tset = Trait.objects.filter(name=name)
#        if tset.count() > 0:
#            continue
#        
#        t = Trait(name=name,descr=descr,creator=user)
#        t.save()
#
#
#            
        
        

#def prepop_questions(user):
#    reader = csv.reader(open(settings.BASE_DIR+'/prepop/questions.csv', 'U'), delimiter=',', quotechar='"')
#    i = 0
#    for row in reader:
#        i+=1
#        if i == 1:
#            continue
#       
#        question = row[0]
#        descr = row[1]
#        tagtype = row[2]
#        print('tag question: '+str(question))
#        print('tag descr: '+str(descr))
#        
#        
#        if tagtype == 'boolean':
#            
#            tset = HardTag.objects.filter(question=question)
#            if tset.count() > 0:
#                continue
#            
#            t = HardTag(descr=descr,question=question,creator=user)
#            t.save()
#        elif tagtype=='integer':
#            tset = ValueTag.objects.filter(question=question)
#            if tset.count() > 0:
#                continue
#            
#            t = ValueTag(descr=descr,question=question,creator=user)
#            t.save()
#        
#        
        

def prepop_businesses(user):
    if user == None:
        user = get_default_user()
    reader = csv.reader(open(settings.BASE_DIR+'/prepop/businesses.csv', 'U'), delimiter=',', quotechar='"')
    i = 0
    for row in reader:
        i+=1
        if i == 1:
            continue
    
        name = row[0]
        addr = row[1]
        city = row[2]
        state = row[3]
        phurl = row[4]
        types = row[5]
        hours = row[6]
        phone = row[7]
        businessURL = row[8]
        print('name: '+str(name))
        print('addr: '+str(addr))
        print('city: '+str(city))
        print('state: '+str(state))
        
        

            
        if Business.objects.filter(name=name,address=addr,state=state,city=city).count() >= 1:
            Business.objects.filter(name=name.encode("utf8"), city=city.encode("utf8"), state=state, address=addr.encode("utf8")).delete()
        
        #bset = Business.objects.filter(name=name,address=addr,state=state,city=city)
  
        b = Business(name=name.encode("utf8"), city=city.encode("utf8"), state=state, 
            address=addr.encode("utf8"), lat=0, lon=0,phone=phone,
            url=businessURL,hours=hours)
        b.save()
    

        add_photo_by_url(phurl=phurl,business=b,user=user, default=True,caption="Caption, defaulted to name: "+str(b.name), title=str(b.name))
        #setBusLatLng(b)        
        add_tag_to_bus(b, get_master_summary_tag(), get_default_user())
        for t in Tag.objects.all():
            add_tag_to_bus(b, t, get_default_user())
        for t in types.split(','):
            if TypeOfBusiness.objects.filter(descr=t).count() > 0:
                typeofbus = TypeOfBusiness.objects.get(descr=t)
            else:
                typeofbus = TypeOfBusiness.objects.create(descr=t,creator=get_default_user(),icon="default.png")
            BusinessType.objects.create(business=b,bustype=typeofbus)    
            
        
        
      
def prepop_queries(user):
    user = get_default_user()
    for t in Tag.objects.all():
        q = Query(name=t.descr,proximity=5,value=5,score=5,price=5,visited=False,deal=False,networked=False,text="",creator=user,is_default=True)
        q.save()


def create_business(name, address, state, city, lat, lon):
    bset = Business.objects.filter(name=name,address=address,state=state,city=city)
    if bset.count() > 0:
        return
    
    b = Business(name=name.encode("utf8"), city=city.encode("utf8"), state=state, address=address.encode("utf8"), lat=lat, lon=lon)
    b.save()
    
    #setBusLatLng(b)
    
    add_tag_to_bus(b,get_master_summary_tag())
    return b
        


