'''
Created on Jul 27, 2012

@author: zouf
'''

from api.models import DiscussionRating, PhotoRating, UserTopic, Topic, Edge, \
    AllsortzUser, BusinessMeta
from queries.models import QueryTopic
from wiki.models import Page
import api.ratings as ratings
import logging


logger = logging.getLogger(__name__)

childMapping = {}
parentMapping = {}
userTopicMapping = {}

def set_edge_mapping():
    global childMapping
    global parentMapping
    if childMapping != {} and parentMapping != {}:
        print('already set edge!')
        return
 

    for e in Edge.objects.select_related('to_node', 'from_node').all():
        childMapping.setdefault(e.to_node.id, []).append(e.from_node)
        parentMapping.setdefault(e.from_node.id, []).append(e.to_node)
    # Use stored lists

def unset_edge_mapping():
    global childMapping
    global parentMapping
    childMapping = {}
    parentMapping = {}
    

def set_usertopic_mapping(u):
    global userTopicMapping
    if userTopicMapping != {}:
        print 'already set usertopic'
        return
    print ' set usertopic mapping'
    btset = UserTopic.objects.filter(user=u).prefetch_related('topic')
    for bt in btset:
        userTopicMapping[bt.topic.id] = bt.importance

def unset_usertopic_mapping():
    global userTopicMapping
    userTopicMapping = {}
    
    

    

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


    global childMapping
    global parentMapping
    
    if childMapping == {} or parentMapping == {}:
        set_edge_mapping()
        
    if topic.id in parentMapping:
        childrenEdges = parentMapping[topic.id]
    else:
        childrenEdges = []   
    for t in childrenEdges:
        c = dict()
        c['topicName'] = t.descr
        c['topicID'] = t.id
        c['topicIcon'] =t.icon
        
        if t.id in parentMapping: 
            c['isLeaf']  = 0
        else:
            c['isLeaf'] = 1

        try:
            c['userWeight'] = user.usertopic.get(topic_id=t.id).importance
        except:
            c['userWeight'] = 0
        data['children'].append(c)
    return data
   

def get_user_details(user):
    data = dict()
    data['userName'] = user.username
    data['userEmail'] = user.email
    
    asuser = AllsortzUser.objects.get(user=user)
    if asuser.registered:
        data['registered'] = "true"
    else:
        data['registered'] = "false"
    
    
    return data
 
def get_bustopic_data(bustopic,user,detail):
    data = dict()
    avg = 0.75  #bustopic.avg_rating
    data['bustopicRating'] = avg
    data['topic'] = get_topic_data(bustopic.topic, user)       
        
    if detail:
        if not bustopic.content:
            data['bustopicContent'] = bustopic.content
        else:
            data['bustopicContent'] = ''
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
    for qt in QueryTopic.objects.select_related('topic').filter(query=query):
        querytopics.append(get_topic_data(qt.topic,user))
    data['querytopics'] = querytopics
    
    return data

def get_queries_data(queries,user):
    data = []
    for q in queries:
        data.append(get_query_data(q,user))
    return data
    
    
def get_health_info(bm):
    data = dict()
    data['health_grade'] = str(bm.health_letter_code)
    data['health_points'] = str(bm.health_points)
    data['health_violation_text'] = str(bm.health_violation_text)
    data['inspdate'] = str(bm.inspdate)
    return data
    