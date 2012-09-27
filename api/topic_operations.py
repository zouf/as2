'''
Created on Aug 1, 2012

@author: zouf
'''
from api.json_serializer import get_bustopic_data, get_user_details
from api.models import Topic, BusinessTopic, Edge, Discussion, Review, Comment, \
    BusinessCache, UserCache
from django.contrib.auth.models import User
from wiki.models import Page
import api.json_serializer as jsonserial
import datetime
import recommendation.normalization as ratings
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

def get_review_data(business,user):
    data = dict()
    data['allTopics'] = jsonserial.get_topics_data(Topic.objects.all(),user,detail=False)
    data['businessID'] = business.id

    return data
def get_discussion_data(discussion,user,type=None):
    data = dict()
    
    if type:
        data['commentType'] = type
    else:
        try:
            c = discussion.bustopiccomments
            data['commentType'] = 'comment'
        except:
            data['commentType'] = 'review'
            
    
    data['date'] = str(discussion.date.strftime('%b %d %I:%M %p'))    
      
    data['content'] = discussion.content
    data['commentID'] = discussion.id
    (numPos, numNeg, thisUsers) = ratings.getDiscussionRatings(discussion,user)
    data['posRatings'] = numPos
    data['negRatings'] = numNeg
    if thisUsers:
       data['thisUsers'] = thisUsers
    data['creator'] = get_user_details(user)
    
    data['children'] = []
    for d in Discussion.objects.filter(reply_to=discussion):
        cdata = get_discussion_data(d, user,'comment')
        data['children'].append(cdata)
    logger.debug(data)
    return data;
    
    


def get_discussions_data(discussions,user):
    data = []
    filtered = discussions.filter(reply_to=None)
    for d in filtered:
        data.append(get_discussion_data(d, user))
    return data

def add_review_to_business(b,review,user):
    logger.debug("Adding review " + str(review) + " to business " + str(b))
    btd = Review.objects.create(business=b,content=review,user=user,reply_to=None)
    return btd
    
def add_comment_to_businesstopic(bt,review,user, replyTo):
    logger.debug("Adding comment " + str(review) + " to business topic " + str(bt))
    if replyTo == '':
        btd = Comment.objects.create(businesstopic=bt,content=review,user=user,reply_to=None)
    else:
        reply = Discussion.objects.get(id=int(replyTo))
        btd = Comment.objects.create(businesstopic=bt,content=review,user=user,reply_to=reply)

    return btd
    


def add_topic_to_bus(b,topic,user=get_default_user()):  
    logger.debug("Adding " + str(topic) + " to business " + str(b) )       
  
    try: 
        bustopic = BusinessTopic.objects.get(topic=topic,business=b)
    except:
        bustopic = BusinessTopic.objects.create(topic=topic,business=b)
    
#    try:
#        Page.objects.get(bustopic=bustopic)
#        logger.debug('here')
#    except Page.DoesNotExist:
#        logger.debug('create a page')
#        pg = Page(name=topic.descr,bustopic = bustopic)
#        pg.save()
    #BusinessCache.objects.filter(business=b).delete()
    UserCache.objects.filter(business=b).delete()

    return bustopic


def add_topic(descr,parenttopics,icon,user=get_default_user()):    
    tset = Topic.objects.filter(descr=descr)
    if tset.count() > 0:
        return None
    
    if parenttopics != ['']:   

        
        t = Topic(descr=descr,creator=user,icon=icon)
        t.save()
        for p in parenttopics:
            #logger.debug('Parent topic is '+str(p))
            pset = Topic.objects.filter(descr=p)
            if pset.count() == 0:
                return None
            parent = pset[0]
            Edge.objects.create(from_node=parent,to_node=t)
            #t.parent_topics.add(parent)
            logger.debug("add "+str(parent)+" as a parent of " + str(t))
            #logger.debug('add parent done')
        
    else:
        logger.debug('creating parent topic')
        t = Topic(descr=descr,creator=user,icon=icon)
        t.save()
    return t



