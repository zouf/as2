'''
Created on Apr 2, 2012

@author: Joey
'''
from api.business_operations import add_business_server
from api.models import Topic, Business, BusinessType, BusinessRating, \
    BusinessMeta, Type, BusinessTopicRating, BusinessTopic, UserTopic
from api.photos import add_photo_by_url
from api.topic_operations import add_topic_to_bus, add_topic
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


def prepop_topics(user=get_default_user()):
    Topic.objects.all().delete()
    reader = csv.reader(open(settings.BASE_DIR+'/prepop/topics.csv', 'U'), delimiter=',', quotechar='"')
    i = 0
    for row in reader:
        i+=1
        if i == 1:
            continue
       
        descr = row[0]
        icon = row[1]
        all_parents = row[2].split(', ')
        parents = []
        for p in all_parents:
            parents.append(p.strip(None))
        #print('Adding topic ' + str(descr) + ' parent is ' + str(parents))
        add_topic(descr,parents,icon)
    
        
def prepop_types(user):
    reader = csv.reader(open(settings.BASE_DIR+'/prepop/types.csv', 'U'), delimiter=',', quotechar='"')
    i = 0
    for row in reader:
        i+=1
        if i == 1:
            continue
       
        descr = row[0]
        icon = row[1]

        tset = Type.objects.filter(descr=descr)
        if tset.count() > 0:
            continue
        t = Type(descr=descr,creator=user,icon=icon)
        t.save()
        
        
        

    

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
    

     
        b = add_business_server(name=name,addr=addr,state=state,city=city,phone=phone,
                            types='', hours=hours,wifi=wifi,serves=serves, url=businessURL, 
                            average_price=average_price)
        
        add_photo_by_url(phurl=phurl,business=b,user=user, default=True,caption="Photo of "+str(b.name), title=str(b.name))

        for t in types.split(','):
            t = t.strip(None)
            if Type.objects.filter(descr=t).count() > 0:
                typeofbus = Type.objects.get(descr=t)
            else:
                typeofbus = Type.objects.create(descr=t,creator=get_default_user(),icon="blankicon.png")
            BusinessType.objects.create(business=b,bustype=typeofbus)    
        
          
        for t,rindex in tag_indices.items():    
            print("Adding " + str(t) + " to business" )       
            topic = Topic.objects.get(descr=t)
            bustopic = add_topic_to_bus(b, topic, user)
            if row[rindex] != '':
                print(t)
                pg = Page.objects.get(bustopic=bustopic)
                print('Populating page' + str(bustopic.topic.descr))
                pg.content = row[rindex]
                pg.save()
                print('Page done. ID is '+ str(pg.id))
                print('content should be ' + str(row[rindex]))
        
        

            
        
        
      
def prepop_queries(user):
    user = get_default_user()
    for t in Topic.objects.all():
        q = Query(name=t.descr,proximity=5,value=5,score=5,price=5,visited=False,deal=False,networked=False,text="",creator=user,is_default=True)
        q.save()


def prepop_topic_ratings():
    random.seed(666)
    
    BusinessTopicRating.objects.all().delete()
    BusinessTopic.objects.all().delete()
    UserTopic.objects.all().delete()
    
    NumBusiness = Business.objects.count()
    NumTopics = Topic.objects.count()
      
    user = get_default_user()
    print('User ' + str(user))
    i = 0
    center = random.randint(0, NumTopics-1)
    
    for t in Topic.objects.all():
        for b in Business.objects.all():
            print('Rating ' + str(b) + ' under the topic ' + str(t))
            #norm_given_rat = stats.norm(center,rating_given_sd)  #gaussian distribution for giving a rating
            prob_rat_given =  0.5 # norm_given_rat.pdf(i)  *  1/norm_given_rat.pdf(center)

            rat_given_rv = binomial(1, prob_rat_given, 1) #1 if rated, 0 otherwise
            if rat_given_rv[0] != 0:
                #norm_pos_rat = stats.norm(center,pos_rating_sd) #create a normal distribution
                prob_pos_rat =  0.8 #norm_pos_rat.pdf(i)  *  1/norm_pos_rat.pdf(center) #probability positive
                
                SIZE = 5
                #We'll ge tan array that is of lenght SIZE and the probability of the event being '1' is prob_pos_rat
                pos_rat_rv = binomial(1, prob_pos_rat, SIZE) #1 if positive, 0 negative
                

                #sum up the array and divide to get a rating between 0 and 1
                rating_scaled = 0                    
                SUM = 0.0
                for r in pos_rat_rv:
                    SUM += r
                rating_scaled = float(SUM)/float(SIZE)
                print('giving rating' + str(rating_scaled))
                bt = BusinessTopic.objects.create(business=b,topic=t)
                UserTopic.objects.create(user=user,topic=t,importance=1)
                rat = BusinessTopicRating(businesstopic=bt, user=user, rating=float(rating_scaled))
                rat.save()
            #no rating        
            i=i+1
            


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
