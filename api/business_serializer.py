'''
Created on Jul 19, 2012

@author: zouf
'''
#from photos.models import BusinessPhoto
from api.json_serializer import get_bustypes_data, get_bustopics_data, \
    get_health_info, get_types_data
from api.models import Business, BusinessRating, BusinessTopic, BusinessType, \
    BusinessCache, Type
from api.photos import get_photo_id, get_photo_url_medium, get_photo_url_large
from api.ratings import getBusinessRatings, getBusAverageRating
from decimal import getcontext, Decimal
from recommendation.recengine import get_best_current_recommendation, \
    get_recommendation_by_topic
import json
import logging
import time

logger = logging.getLogger(__name__)
#TODO: matt fix this to handle ratings from 1-4
#is SideBar is true if we're going to use smaller data
def get_bus_data_ios(business_list, user,detail=False):
    data = []
    for b in business_list:
        d = get_single_bus_data_ios(b, user,detail=detail)
        data.append(d)
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
    print('WARNING: could not get post with key ' + str(key))
    return ''

def get_request_postlist_or_warn(key,request):
    if key in request.POST:
        print('in request.postlist')
        print('trying to get list for ' + str(key))
        print(request.POST[key])
        try:
            types = request.POST[key]
            return (json.loads(types))
        except Exception as e:
            print(str(e))
    logger.debug("WARNING: could not get post list with key "+ str(key));
    print('WARNING: could not get post list with key ' + str(key))
    return []


def get_request_get_or_error(key,request):
    if key in request.GET:
        return request.GET[key]
    raise ReadJSONError("GET Key: '" + str(key) + "' not found in request " + str(request.path))

def get_request_postlist_or_error(key,request):
    if key in request.POST:
        print('in request.postlist')
        print('trying to get list for ' + str(key))
        print(request.POST[key])  
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
#    try:
#        d = json.loads(b.businesscache_set.all()[0].cachedata)
#    except Exception as e:
     d = dict()
     bustypes = b.businesstype_set.select_related().all()
     bustopics = b.businesstopic_set.select_related().all()

     
     
     
     d['businessID'] = b.id
     d['businessName'] = b.name
     d['businessID'] = b.id
     d['businessHours'] = b.metadata.hour  #TODO Set hours
     d['averagePrice'] = b.metadata.average_price  #TODO Set hours
     
     d['latitude'] = b.lat
     d['longitude'] = b.lon

     d['types'] = get_bustypes_data(bustypes,user)

     logger.debug('Creating cache for bus ' + str(b))
         
         
     d['businessCity'] = b.city
     d['businessState'] = b.state
     d['streetAddr'] = b.address
     d['zipcode'] = b.zipcode

         
     d['businessPhone'] = b.phone
     d['servesAlcohol'] = b.metadata.serves  #TODO Set hours
     d['hasWiFi'] = b.metadata.wifi  #TODO Set hours
     d['businessURL'] = b.metadata.url #TODO Set URL

     d['photo'] = get_photo_id(b)
     
     d['ratingOverAllUsers']  = getBusAverageRating(b)

     d['categories'] = get_bustopics_data(bustopics,user,detail=True)
     d['health_info'] = get_health_info(b)
     
     d['photoMedURL'] = get_photo_url_medium(b)

     d['photoLargeURL'] = get_photo_url_large(b)
#
#        if BusinessCache.objects.filter(business=b).count() > 0:
#            BusinessCache.objects.filter(business=b).delete()      
#        BusinessCache.objects.create(business=b,cachedata=json.dumps(d))
#        pass



    try:
        if user:
            userRatingSet = BusinessRating.objects.get(user=user, business=b)
            d['ratingForCurrentUser'] = userRatingSet.rating
            d['ratingRecommendation'] = "%.2f" % get_recommendation_by_topic(b, user)    
        else:
            d['ratingForCurrentUser'] = 0
            d['ratingRecommendation'] = "%.2f" % get_recommendation_by_topic(b, user)
    except:
        d['ratingForCurrentUser'] = 0
        d['ratingRecommendation'] = "%.2f" % get_recommendation_by_topic(b, user)




    # if the business has this attribute et (from some other calculation) then use it
    if hasattr(b, 'distance'):
        d['distanceFromCurrentUser'] = "%.2f" % b.distance.mi
    else:
        logger.error('No distance! Should be impossible to get here')
        #calculate it
        dist = b.get_distance(user)
        #dist = None
        if dist is not None:
            d['distanceFromCurrentUser'] =  "%.2f" % dist.miles
        else:
            d['distanceFromCurrentUser'] = str(-1)#b.get_distance(user))




#    if detail:
#        d['businessCity'] = b.city
#        d['businessState'] = b.state
#        d['streetAddr'] = b.address
#        d['zipcode'] = b.zipcode
#   
#            
#        d['businessPhone'] = b.phone
#        d['servesAlcohol'] = b.serves_alcohol()  #TODO Set hours
#        d['hasWiFi'] = b.has_wifi()  #TODO Set hours
#        d['businessURL'] = b.url #TODO Set URL
#
#        d['photo'] = get_photo_id(b)
#        
#        #[hates,neutrals,likes,loves,avg] = getBusinessRatings(b)
#        d['ratingOverAllUsers']  = getBusAverageRating(b)
#
#        d['allTypes'] = get_types_data(Type.objects.all(),user)
#        bustags = BusinessTopic.objects.filter(business=b)   #.exclude(tag=get_master_summary_tag())
#        d['categories'] = get_bustopics_data(bustags,user,detail)
#        d['health_info'] = get_health_info(b)
    return d
