'''
Created on Aug 1, 2012

@author: zouf
'''
from api.json_serializer import get_bustopic_data, get_user_details
from api.models import Topic, BusinessTopic, Edge, Discussion, Review, Comment, \
    BusinessCache, UserCache
from django.contrib.auth.models import User
from wiki.models.article import Article, ArticleRevision
import api.json_serializer as jsonserial
import datetime
import numpy as np 
import pytz
from django.utils import timezone
import logging
import recommendation.normalization as ratings
logger = logging.getLogger(__name__)

def create_revision(bustopic, title, content, summary,request):
    
    
    
    revision =  ArticleRevision()
    revision.inherit_predecessor(bustopic.article)
    if not title:
        revision.title=bustopic.article.current_revision.title
    else:
        revision.title = title
    revision.content = content 
    revision.user_message =  summary 
    revision.deleted = False
    revision.set_from_request(request)
    revision.save()
    return revision


def edit_article(bustopic, title, content, summary,request):
    revision = create_revision(bustopic, title, content, summary,request)
    bustopic.article.add_revision(revision)


def create_article(bustopic,title="Root", article_kwargs={}, content="",user_message="",request=None):
    """Utility function:
    Create a new urlpath with an article and a new revision for the article"""
    article = Article(**article_kwargs)
    ar = ArticleRevision()

    ar.content = content 
    ar.user_message =  user_message 
    ar.deleted = False
    if request:
        ar.set_from_request(request)
    else:
        ar.ip_address = None
        ar.user = get_default_user()
    article.add_revision(ar, save=True)

    article.save()
    bustopic.article=article
    bustopic.save() 
    return ar

    
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
           
    #TODO GET TIMEZONE DATA FROM SOMEWHERE ELSE
    data['date'] = str(discussion.date.astimezone(user.timezone).strftime('%b %d %I:%M %p'))    
    
    #TODO ADD DIFF
    #if isinstance(discussion,Comment):
    try:  
      data['proposedChange'] = discussion.proposedchange.content
      logger.debug('zouf2 proposed change for ' + str(discussion))
    except Exception as e:
      logger.debug('zouf3 for change to ' + str(discussion) + '  due to error ' + str(e))
      
      data['proposedChange'] = ''

    data['content'] = discussion.content
    data['commentID'] = discussion.id
    (numPos, numNeg, thisUsers) = ratings.getDiscussionRatings(discussion,user)
    data['posRatings'] = numPos
    data['negRatings'] = numNeg
    if thisUsers:
        data['thisUsers'] = thisUsers
    data['creator'] = get_user_details(discussion.user,auth=False)
    
    data['children'] = []
    if(isinstance(discussion,Comment)):
      for d in Comment.objects.filter(reply_to=discussion):
        cdata = get_discussion_data(d, user,'comment')
        data['children'].append(cdata)
    else:
       for d in Discussion.objects.filter(reply_to=discussion):
        cdata = get_discussion_data(d, user,'comment')
        data['children'].append(cdata)

    logger.debug(data)
    return data;
    
    

def sort_discussions(dleft,dright):
    return True
def get_discussions_data(discussions,user):
    data = []
    filtered = discussions.filter(reply_to=None)
    for d in filtered:
        data.append(get_discussion_data(d, user))
    

    newlist = data #sorted(data,key=lambda d: (np.log10(len(d['children'])) + 1)*(d['posRatings'] - d['negRatings']),reverse=True)
    return newlist

def add_review_to_business(b,review,user):
    logger.debug("Adding review " + str(review) + " to business " + str(b))
    btd = Review.objects.create(business=b,content=review,user=user,reply_to=None)
    return btd
    
def add_comment_to_businesstopic(bt,review,proposedChange,user, replyTo,request):
    if replyTo == '' or replyTo == -1:
        btd = Comment.objects.create(businesstopic=bt,content=review,user=user,reply_to=None)        
        logger.debug("Adding comment " + str(review) + " to business topic " + str(bt) + ' as a root ')
    else:
        if replyTo != 0:
          reply = Discussion.objects.get(id=int(replyTo))
          btd = Comment.objects.create(businesstopic=bt,content=review,user=user,reply_to=reply)
          logger.debug("Adding discussion " + str(review) + " to business topic " + str(bt) + ' as a child ')
        else:
          btd = Comment.objects.create(businesstopic=bt,content=review,user=user,reply_to=None)
          logger.debug("Adding discussion " + str(review) + " to business topic " + str(bt) + ' as a root comment ')
  

    # if theres a proposed change
    if proposedChange != '':
      try:
          # the intial data for the business is empty
          if bt.article == None:
            btd.proposedchange = create_article(bt,title=bt, user_message=review, content=proposedChange, request=request, article_kwargs={'owner': user,
                    'group': None,
                    'group_read': True,
                    'group_write': True,
                    'other_read': True,
                    'other_write':True,
                    }
                )
            btd.save()
            #invalidate the caches
                      #otherwise just create a revision
          else:
            btd.proposedchange = create_revision(bt,title=None,content=proposedChange,summary=review, request=request)
            btd.save()
          logger.debug('Invalidate the cache!\n"')
          UserCache.objects.filter(user=user,business=bt.business).delete()
      except Exception as e:
          logger.debug('Error in creating a revision: ' + str(e))
    return btd
    



def add_topic_to_bus(b,topic,user=get_default_user()):  
    logger.debug("Adding " + str(topic) + " to business " + str(b) )       
  
    try: 
        bustopic = BusinessTopic.objects.get(topic=topic,business=b)
    except:
        bustopic = BusinessTopic.objects.create(topic=topic,business=b)
    


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



