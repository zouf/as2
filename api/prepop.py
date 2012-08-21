'''
Created on Apr 2, 2012

@author: Joey
'''
from api.categories import get_master_summary_tag, add_tag_to_bus
from api.models import Tag, Business, TypeOfBusiness, BusinessType, \
    BusinessRating, BusinessMeta
from api.photos import add_photo_by_url
from as2 import settings
from django.contrib.auth.models import User
from numpy.oldnumeric.random_array import binomial
from queries.models import Query
from wiki.models import Page
import csv
import logging
import random



logger = logging.getLogger(__name__)

def get_default_user():
    try:
        user = User.objects.get(username='matt')
    except:
        user = User(first_name='Matt', email='matty@allsortz.com', username='zouf')
        user.set_password("testing")
        user.save()
        
    return user

def create_blank_user(n):
    try:
        user = User.objects.get(username='blank'+str(n))
    except:
        user = User(first_name='Blank', email='blank'+str(n)+'@allsortz.com', username='blank'+str(n))
        user.set_password("testing")
        user.save()
        
    return user

def create_user(username, uid):
    u = User(username=("u" + str(uid)), first_name=(username[0:20].encode("utf8")), password="")
    # u.set_password("test")
    return u


def prepop_sorts(user):
    reader = csv.reader(open(settings.BASE_DIR+'/prepop/sorts.csv', 'U'), delimiter=',', quotechar='"')
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
        
def prepop_types(user):
    reader = csv.reader(open(settings.BASE_DIR+'/prepop/types.csv', 'U'), delimiter=',', quotechar='"')
    i = 0
    for row in reader:
        i+=1
        if i == 1:
            continue
       
        descr = row[0]
        icon = row[1]

        tset = TypeOfBusiness.objects.filter(descr=descr)
        if tset.count() > 0:
            continue
        t = TypeOfBusiness(descr=descr,creator=user,icon=icon)
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
    indices = {}
    tag_indices ={}
    for row in reader:
        i+=1
        if i == 1:
            bpoint = 0
            for hindex in xrange(0,len(row)):
                if row[hindex] == 'Main':
                    bpoint = hindex
                    break
                indices[row[hindex]] = hindex
            for tindex in xrange(bpoint,len(row)):
                tag_indices[row[tindex]] = tindex
                
            continue
    
        name = row[indices['Business']]
        addr =  row[indices['Address']]
        city =  row[indices['City']]
        state =  row[indices['State']]
        phurl =  row[indices['phurl']]
        types =  row[indices['Types']]
        serves_alcohol = row[ indices['Alcohol']]
        has_wifi =  row[indices['Wifi']]
        average_score =  row[indices['Score']]
        average_price =  row[indices['Price']]
        hours=  row[indices['Hours']]
        phone =  row[indices['Phone']]
        businessURL =  row[indices['URL']]
        
        if has_wifi == 'Yes':
            wifi = True
        else:
            wifi = False
        
        if serves_alcohol == 'Yes':
            serves = True
        else:
            serves = False
    
     
        if Business.objects.filter(name=name,address=addr,state=state,city=city).count() > 0:
            Business.objects.filter(name=name.encode("utf8"), city=city.encode("utf8"), state=state, address=addr.encode("utf8")).delete()
        b = Business(name=name.encode("utf8"), city=city.encode("utf8"), state=state, 
            address=addr.encode("utf8"), lat=0, lon=0,phone=phone, url=businessURL)
        b.save()

        bmset = BusinessMeta.objects.filter(business=b).filter()
        if bmset.count() > 0:
            bmset.delete()
        bm = BusinessMeta(business=b,hours=hours,average_price=average_price,serves=serves,wifi=wifi)
        bm.save()
        
        add_photo_by_url(phurl=phurl,business=b,user=user, default=True,caption="Caption, defaulted to name: "+str(b.name), title=str(b.name))
        
        for t,rindex in tag_indices.items():           
            tg = Tag.objects.get(descr=t)
            bustag = add_tag_to_bus(b, tg, user)
            if row[rindex] != '':
                print(t)
                print('Tag added to bus!')
                pg = Page.objects.get(category=bustag)
                print('Populating page' + str(bustag.tag.descr))
                pg.content = row[rindex]
                pg.save()
                print('Page done. ID is '+ str(pg.id))
                print('content should be ' + str(row[rindex]))
        
        
        for t in types.split(','):
            t = t.strip(None)
            if TypeOfBusiness.objects.filter(descr=t).count() > 0:
                typeofbus = TypeOfBusiness.objects.get(descr=t)
            else:
                typeofbus = TypeOfBusiness.objects.create(descr=t,creator=get_default_user(),icon="blankicon.png")
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

def prepop_ratings():
    print("prepop")
    BusinessRating.objects.all().delete()
    
    
    random.seed(666)
    
    NumBusiness = Business.objects.count()
    rating_given_sd = NumBusiness / 2
    pos_rating_sd = NumBusiness   / 4
    for user in User.objects.all():
        print('User ' + str(user))
        i = 0
        center = random.randint(0, NumBusiness-1)
        
        for business in Business.objects.all():
            print('Rating ' + str(business))
            #norm_given_rat = stats.norm(center,rating_given_sd)  #gaussian distribution for giving a rating
            prob_rat_given =  0.5 # norm_given_rat.pdf(i)  *  1/norm_given_rat.pdf(center)
            
            # print('\n')
            # print("Mu is " + str(center))
            # print("pos_rating_stdev is " + str(rating_given_sd))
            # print("x is " + str(i))
            # print("Prob LHS " + str(prob_lhs))
            # print("Prob RHS " + str(prob_rhs))
            # print("result is " + str(prob_sel))
            
            rat_given_rv = binomial(1, prob_rat_given, 1) #1 if rated, 0 otherwise
            if rat_given_rv[0] != 0:
                #norm_pos_rat = stats.norm(center,pos_rating_sd) #create a normal distribution
                prob_pos_rat =  0.7 #norm_pos_rat.pdf(i)  *  1/norm_pos_rat.pdf(center) #probability positive
                pos_rat_rv = binomial(1, prob_pos_rat, 1) #1 if positive, 0 negative
                rating_scaled = 0
                
                if pos_rat_rv[0] == 1:
                    rating_scaled = random.randint(3,4)  #3,4 = POSITIVE
                else:
                    rating_scaled = random.randint(1,2)  #1,2, = NEGATIVE
                rat = BusinessRating(business=business, user=user, rating=int(rating_scaled))
                rat.save()
            #no rating        
            i=i+1
        
def prepop_users():
    for i in xrange(1,20,1):
        create_blank_user(i)
