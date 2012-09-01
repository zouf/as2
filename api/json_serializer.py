'''
Created on Jul 27, 2012

@author: zouf
'''

from api.models import DiscussionRating, PhotoRating, UserTopic, Topic, Edge,\
    AllsortzUser
from queries.models import QueryTopic
from wiki.models import Page
import api.ratings as ratings
import logging


logger = logging.getLogger(__name__)




def get_topics_data(topics,user):
    data = []
    for t in topics:
        data.append(get_topic_data(t,user))
    return data

def get_topic_data(topic,user):
    data = dict()
    data['parentName'] = topic.descr
    data['parentID'] = topic.id
    data['parentIcon'] = topic.icon
    data['children'] = []   
    #print('children of ' + str(topic) + " are " + str(topic.children.all()))

    for edge in topic.children.all():
        c = dict()
        c['topicName'] = edge.to_node.descr
        c['topicID'] = edge.to_node.id
        c['topicIcon'] =edge.to_node.icon
        if edge.to_node.children.all().count() > 0:
            c['isLeaf']  = 0
        else:
            c['isLeaf'] = 1
        topicfilter = UserTopic.objects.filter(user=user,topic=edge.to_node)
        if topicfilter.count() > 0:
            c['userWeight'] = topicfilter[0].importance
        else:
            c['userWeight'] = -1 
        data['children'].append(c)
        #data['children'].append(get_topic_data(edge.to_node,user))


    return data
   

def get_user_details(user):
    data = dict()
    data['userName'] = user.username
    data['userEmail'] = user.email
    
    asuser = AllsortzUser.objects.get(user=user)
    if asuser.registered:
        data['registered'] = True
    else:
        data['registered'] = False
    
    
    return data
 
def get_bustopic_data(bustopic,user,detail):
    data = dict()
    avg = ratings.getBusTopicRatings(bustopic)
    data['bustopicRating'] = avg
    data['topic'] = get_topic_data(bustopic.topic, user)

    try:
        pg = Page.objects.get(bustopic=bustopic)
    except Page.DoesNotExist:
        pg = Page(name=bustopic.topic.descr,bustopic=bustopic)
        pg.save()
        
        
    if detail:
        data['bustopicContent'] = pg.rendered
        if pg.content == '':
            return None

    return data

def get_types_data(types,user):
    data = []
    for t in types:
        data.append(get_type_data(t,user))
    return data

def get_type_data(typeofbusiness,user):
    data = dict()
    data['typeName'] = typeofbusiness.descr
    data['typeID'] = typeofbusiness.id
    data['typeIcon'] = typeofbusiness.icon

    return data

def get_bustype_data(bustype,user):
    data = dict()
    data['type'] = get_type_data(bustype.bustype, user)
    return data
    
def get_bustypes_data(bustypes,user):
    data = []
    for bt in bustypes:
        data.append(get_bustype_data(bt,user))
    return data

def get_bustopics_data(bustopics,user,detail):
    data = []
    for cat in bustopics:
        res = get_bustopic_data(cat,user,detail)
        #ignore blank ones
        if res:
            data.append(res)
    return data
    


def get_comment_data(comment,user):
    data = dict()
    data['commentCreator'] = comment.user.username
    data['posted'] = comment.date
    data['content'] = comment.content
    [pos,neg] = ratings.getCommentRatings(comment)
    data['positiveVotes'] = pos
    data['negativeVotes'] = neg
    
    try:
        thisUsersRating = DiscussionRating.objects.get(discussion=comment,user=user)
    except:
        thisUsersRating = None
    
    data['thisUsersRating'] = thisUsersRating       
    return data
    
    
def get_comments_data(comments,user):
    data = []
    for c in comments:
        data.append(get_comment_data(c,user))
    return data


def get_photo_data(photo,user):
    data = dict()
    data['photoTitle'] = photo.title
    data['photoCaption'] = photo.caption
    data['photoURL'] = photo.image.url
    data['photoCreator'] = photo.user.username
    [pos,neg] = ratings.getPhotoRatings(photo)
    data['positiveVotes'] = pos
    data['negativeVotes'] = neg
    
    try:
        thisUsersRating = PhotoRating.objects.get(photo=photo,user=user)
    except:
        thisUsersRating = None
    
    data['thisUsersRating'] = thisUsersRating       
    return data

def get_photos_data(photos,user,order_by):
    data = []
    for p in photos:
        data.append(get_photo_data(p,user))
    
    if order_by == 'date':
        print('order by date')
    else:
        print('order by rating')
    return data

def get_query_data(query,user):
    data=dict()
    data['queryID'] = query.id
    data['queryName'] = query.name
    data['queryCreator'] = query.creator.username
    data['proximityWeight'] = query.proximity
    data['priceWeight'] = query.price
    data['valueWeight'] = query.value
    data['scoreWeight'] = query.score
    
    data['userHasVisited'] = query.visited
    
    data['searchText'] = query.text

    data['networked'] = query.networked
    data['deal'] = query.deal
    
    data['isCreatedByUs'] = query.is_default
    
    querytopics = []
    for qt in QueryTopic.objects.filter(query=query):
        querytopics.append(get_topic_data(qt.topic,user))
    data['querytopics'] = querytopics
    
    return data

def get_queries_data(queries,user):
    data = []
    for q in queries:
        data.append(get_query_data(q,user))
    return data
    