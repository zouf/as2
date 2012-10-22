'''
Created on Jul 19, 2012

@author: zouf
'''
#from photos.models import BusinessPhoto
from api.authenticate import get_default_user
from api.models import Business, BusinessRating, BusinessTopic, BusinessType, \
    BusinessCache, Type, BusinessTopicRating, UserTopic, UserCache, Topic
from api.photos import get_photo_id, get_photo_url_medium, get_photo_url_large
from api.ratings import getBusinessRatings, getBusAverageRating
from decimal import getcontext, Decimal
from django.contrib.auth.models import User
from django.db.models.aggregates import Avg
from recommendation.recengine import get_best_current_recommendation, \
    get_recommendation_by_topic, get_node_average, get_main_node_average
import api.json_serializer as topic_type_serializer
import json
import logging
import operator
import time

#TODO put this in a constants file
NUM_STARRED_RESULTS = 3
logger = logging.getLogger(__name__)

       


def test_serializer():
    b = Business.objects.filter(state='NJ')
    filtered =b.select_related('metadata').prefetch_related('businesstopic', 'businesstype','businesstopic__bustopicrating','businesstopic__topic', 'businesstopic__topic__children')
    newlist = []
    for i in range(0,filtered.count()):
        f = filtered[i]
        newlist.append(f)

    t = Topic.objects.get(descr='Main')
    res = get_main_node_average(newlist[0],t.id,get_default_user())

def get_bus_data_ios(business_list, user,detail=False):
    data = dict()
    data['businesses'] = []
    filtered = business_list.select_related('metadata').prefetch_related('businesstopic', 'businesstype','businesstopic__bustopicrating','businesstopic__topic', 'businesstopic__topic__children')
    newlist = []
    for i in range(0,filtered.count()):
        newlist.append(filtered[i])

    for b in newlist:
        logger.debug('BUSINESS IS ' + str(b) + ' + ID IS ' + str(b.id))
        d = get_single_bus_data_ios(b, user,detail=detail)
        data['businesses'].append(d)
     
    newlist = sorted(data['businesses'],key=lambda bus: bus['ratingRecommendation'],reverse=True)
    
    i = 0
    for e in newlist:
        if i < NUM_STARRED_RESULTS:
            e['starred'] =True
        i += 1
    data['businesses'] = newlist
    data['userPreferences'] = topic_type_serializer.get_usertopic_data((user)
    return data

class ReadJSONError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

 
def get_request_post_or_error(key,request):
    if key in request.POST:
        return request.POST[key]
    raise ReadJSONError("POST Key: " + str(key) + " not found in request " + str(request.path))


def get_request_post_or_warn(key,request):
    if key in request.POST:
        return request.POST[key]
    logger.debug("WARNING: could not get post with key"+ str(key));
    logger.debug('WARNING: could not get post with key ' + str(key))
    return ''

def get_request_postlist_or_warn(key,request):
    if key in request.POST:
        logger.debug('in request.postlist')
        logger.debug('trying to get list for ' + str(key))
        logger.debug(request.POST[key])
        try:
            types = request.POST[key]
            return (json.loads(types))
        except Exception as e:
            logger.debug(str(e))
    logger.debug("WARNING: could not get post list with key "+ str(key));
    logger.debug('WARNING: could not get post list with key ' + str(key))
    return []


def get_request_get_or_error(key,request):
    if key in request.GET:
        return request.GET[key]
    raise ReadJSONError("GET Key: '" + str(key) + "' not found in request " + str(request.path))

def get_request_postlist_or_error(key,request):
    if key in request.POST:
        logger.debug('in request.postlist')
        logger.debug('trying to get list for ' + str(key))
        logger.debug(request.POST[key])  
        types = request.POST[key]
        return (json.loads(types))
    raise ReadJSONError("POST Key for list: " + str(key) + " not found in request " + str(request.path))

def get_all_nearby(mylat,mylng,distance=1):

    current_pg_point = "point '({:.5f}, {:.5f})'".format(mylng, mylat)
    buses_query = " ".join(["SELECT *",
                                    "FROM (SELECT id, (point(lon, lat) <@> {}) AS dist FROM ratings_business) AS dists",
                                    "WHERE dist <= {:4f} ORDER BY dist ASC;"]).format(current_pg_point, distance)
    buses = Business.objects.raw(buses_query)
    return buses


#isSideBar is true if we're using small images
def get_single_bus_data_ios(b, user,detail):
    
    d = dict()
    try:
        cache= b.businesscache.cachedata
        d = json.loads(cache)
        logger.debug('cached ' + str(b.name))

    except Exception as e:
        logger.debug('exception ' + str(e))
        #now we just grab the related data
        bustypes = b.businesstype.all()
        #bustopics = b.businesstopic.all()
        
        d['businessID'] = b.id
        d['businessName'] = b.name
    
        d['latitude'] = b.lat
        d['longitude'] = b.lon
        
        d['businessCity'] = b.city
        d['businessState'] = b.state
        d['streetAddr'] = b.address
        d['zipcode'] = b.zipcode
        d['businessPhone'] = b.phone
        
        if b.metadata:
            d['businessHours'] = b.metadata.hours  #TODO Set hours
            d['averagePrice'] = b.metadata.average_price  #TODO Set hours
            d['servesAlcohol'] = b.metadata.serves  #TODO Set hours
            d['hasWiFi'] = b.metadata.wifi  #TODO Set hours
            d['businessURL'] = b.url #TODO Set URL
    
        d['photo'] = get_photo_id(b)
        
        #d['ratingOverAllUsers']  = getBusAverageRating(b)
        d['types'] = topic_type_serializer.get_bustypes_data(bustypes,user)
        
        d['health_info'] = topic_type_serializer.get_health_info(b.metadata)
        
        d['photoMedURL'] = get_photo_url_medium(b)
    #    
        d['photoLargeURL'] = get_photo_url_large(b)
        
        BusinessCache.objects.create(cachedata=json.dumps(d),business=b)
        

    #does caching internally    
    d['ratingRecommendation'] = "%.2f" % get_recommendation_by_topic(b, user) 
    if detail: 
        try:
            #try to get a cached version!
            cache = UserCache.objects.get(user=user,business=b)
            cachedata = json.loads(cache.cachedata)
            d['categories'] = cachedata['categories'] 
            logger.debug('Used cached user data')
        except:
            u = User.objects.filter(id=user.id).prefetch_related('usertopic_set__topic').select_related()[0]
            cachedata = {} 
            d['categories'] = topic_type_serializer.get_bustopics_data(b.businesstopic.all(),u,detail=True)
            cachedata['categories'] = d['categories']
            UserCache.objects.create(cachedata=json.dumps(cachedata),user=user,business=b)

    # if the business has this attribute et (from some other calculation) then use it
    if hasattr(b, 'distance'):
        d['distanceFromCurrentUser'] = "%.2f" % b.distance.mi
    else:
        #calculate it
        dist = b.get_distance(user)
        if dist is not None:
            d['distanceFromCurrentUser'] =  "%.2f" % dist.miles
        else:
            d['distanceFromCurrentUser'] = str(-1)
    return d
