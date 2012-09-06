'''
Created on Aug 1, 2012

@author: zouf
'''
from api.json_serializer import get_bustopic_data, get_user_details
from api.models import Topic, BusinessTopic, Edge, BusinessTopicDiscussion
from django.contrib.auth.models import User
from recommendation.normalization import getNumRatings, \
    getBusinessTopicDiscussionRatings
from wiki.models import Page

def get_default_user():
    try:
        user = User.objects.get(username='matt')
    except:
        user = User(first_name='Matt', email='matty@allsortz.com', username='zouf')
        user.set_password("testing")
        user.save()
        
    return user

def get_discussion_data(discussion,user):
    data = dict()
    data['content'] = str(discussion.content)
    data['discussionID'] = str(discussion.id)
    (numPos, numNeg) = getBusinessTopicDiscussionRatings(discussion)
    data['posRatings'] = numPos
    data['negRatings'] = numNeg
    data['creator'] = get_user_details(user)
    return data;
    
    


def get_discussions_data(discussions,user):
    data = []
    for d in discussions:
        data.append(get_discussion_data(d, user))
    return data

def add_discussion_to_businesstopic(bt,review,user):
    print("Adding review " + str(review) + " to business topic " + str(bt))
    btd = BusinessTopicDiscussion.objects.create(bsuinesstopic=bt,content=review,user=user,reply_to=None)
    return btd
    

def add_topic_to_bus(b,topic,user=get_default_user()):  
    print("Adding " + str(topic) + " to business " + str(b) )       
  
    try: 
        bustopic = BusinessTopic.objects.get(topic=topic,business=b)
    except:
        bustopic = BusinessTopic.objects.create(topic=topic,business=b)
    
    try:
        Page.objects.get(bustopic=bustopic)
        print('here')
    except Page.DoesNotExist:
        print('create a page')
        pg = Page(name=topic.descr,bustopic = bustopic)
        pg.save()
    return bustopic


def add_topic(descr,parenttopics,icon,user=get_default_user()):    
    tset = Topic.objects.filter(descr=descr)
    if tset.count() > 0:
        return None
    
    if parenttopics != ['']:   

        
        t = Topic(descr=descr,creator=user,icon=icon)
        t.save()
        for p in parenttopics:
            #print('Parent topic is '+str(p))
            pset = Topic.objects.filter(descr=p)
            if pset.count() == 0:
                return None
            parent = pset[0]
            Edge.objects.create(from_node=parent,to_node=t)
            #t.parent_topics.add(parent)
            print("add "+str(parent)+" as a parent of " + str(t))
            #print('add parent done')
        
    else:
        print('creating parent topic')
        t = Topic(descr=descr,creator=user,icon=icon)
        t.save()
    return t



