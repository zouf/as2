'''
Created on Jul 27, 2012

@author: zouf
'''

import api.ratings as ratings 
from api.models import DiscussionRating, PhotoRating, Tag, UserSubscription
from queries.models import QueryTag
from wiki.models import Page
import logging


logger = logging.getLogger(__name__)




def get_tags_data(tags,user):
    data = []
    for t in tags:
        data.append(get_tag_data(t,user))
    return data

def get_tag_data(tag,user):
    data = dict()
    data['tagName'] = tag.descr
    data['tagID'] = tag.id
    tagfilter = UserSubscription.objects.filter(user=user,tag=tag)
    if tagfilter.count() > 0:
        data['userIsSubscribed'] = True
    else:
        data['userIsSubscribed'] = False 
    return data
    
def get_category_data(category,user):
    data = dict()
    avg = ratings.getCategoryRatings(category)
    data['categoryRating'] = avg
    data['tag'] = get_tag_data(category.tag, user)

    try:
        pg = Page.objects.get(category=category)
    except Page.DoesNotExist:
        pg = Page(name=category.tag.descr,category=category)
        pg.save()
    data['categoryContent'] = pg.rendered

    return data

    

def get_categories_data(categories,user):
    data = []
    for cat in categories:
        data.append(get_category_data(cat,user))
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
    
    queryTags = []
    for qt in QueryTag.objects.filter(query=query):
        queryTags.append(get_tag_data(qt.tag,user))
    data['queryTags'] = queryTags
    
    return data

def get_queries_data(queries,user):
    data = []
    for q in queries:
        data.append(get_query_data(q,user))
    return data
    