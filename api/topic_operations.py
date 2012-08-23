'''
Created on Aug 1, 2012

@author: zouf
'''
from api.models import Topic, BusinessTopic
from django.contrib.auth.models import User
from wiki.models import Page

def get_default_user():
    try:
        user = User.objects.get(username='matt')
    except:
        user = User(first_name='Matt', email='matty@allsortz.com', username='zouf')
        user.set_password("testing")
        user.save()
        
    return user

def add_topic_to_bus(b,topic,user=get_default_user()):    
    try: 
        bustopic = BusinessTopic.objects.get(topic=topic,business=b)
    except:
        bustopic = BusinessTopic.objects.create(topic=topic,business=b)
    
    try:
        Page.objects.get(bustopic=bustopic)
    except Page.DoesNotExist:
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
            print('Parent topic is '+str(p))
            pset = Topic.objects.filter(descr=p)
            if pset.count() == 0:
                return None
            parent = pset[0]
            t.parent_topics.add(parent)
            print('add parent done')
        
    else:
        print('creating parent topic')
        t = Topic(descr=descr,creator=user,icon=icon)
        t.save()
    return t


