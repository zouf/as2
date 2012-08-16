'''
Created on Jul 19, 2012

@author: zouf
'''
#from photos.models import BusinessPhoto
from api.json_serializer import get_categories_data, get_bustypes_data
from api.models import Business, BusinessRating, BusinessCategory, BusinessType
from api.photos import get_photo_url, get_photo_id
from api.ratings import getBusinessRatings
from decimal import getcontext, Decimal
from recommendation.recengine import get_best_current_recommendation
import json
import logging

logger = logging.getLogger(__name__)
#TODO: matt fix this to handle ratings from 1-4
#is SideBar is true if we're going to use smaller data
def get_bus_data_ios(business_list, user):
    data = []
    for b in business_list:
        d = get_single_bus_data_ios(b, user)
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
            print(e.value)
    logger.debug("WARNING: could not get post list with key "+ str(key));
    print('WARNING: could not get post list with key ' + str(key))
    return ''


def get_request_get_or_error(key,request):
    if key in request.GET:
        return request.GET[key]
    raise ReadJSONError("GET Key: '" + str(key) + "' not found in request " + str(request.path))



def get_all_nearby(mylat,mylng,distance=1):

    current_pg_point = "point '({:.5f}, {:.5f})'".format(mylng, mylat)
    buses_query = " ".join(["SELECT *",
                                    "FROM (SELECT id, (point(lon, lat) <@> {}) AS dist FROM ratings_business) AS dists",
                                    "WHERE dist <= {:4f} ORDER BY dist ASC;"]).format(current_pg_point, distance)
    buses = Business.objects.raw(buses_query)
    return buses


#isSideBar is true if we're using small images
def get_single_bus_data_ios(b, user):
    d = dict()
    d['businessID'] = b.id
    d['businessName'] = b.name
    d['businessCity'] = b.city
    d['businessState'] = b.state
    d['streetAddr'] = b.address

    d['latitude'] = b.lat
    d['longitude'] = b.lon
    d['businessID'] = b.id
    if b.phone == None or b.phone == '':
        d['businessPhone'] = '555 555-5555'
    else:
        d['businessPhone'] = b.phone
    d['businessHours'] = ['M-F 9am-9pm','S-Sun 9am-9pm'] #TODO Set hours
    d['businessURL'] = 'http://www.allsortz.com' #TODO Set URL


    
    d['zipcode'] = b.zipcode
  
    if b.get_distance(user) is not None:
        dec = Decimal(float(b.get_distance(user)))
        getcontext().prec = 2
        d['distanceFromCurrentUser'] = str(dec/Decimal(1))
    else:
        d['distanceFromCurrentUser'] = str(-1)#b.get_distance(user))
    d['photo'] = get_photo_id(b)
    d['photoURL'] = get_photo_url(b)
    [hates,neutrals,likes,loves,avg] = getBusinessRatings(b)
    d['ratingOverAllUsers']  = avg
    d['numberOfRatings'] = hates+neutrals+likes+loves
    d['numberOfLoves'] = loves
    d['numberOfLikes'] =likes
    d['numberOfNeutrals'] = neutrals
    d['numberOfHates'] = hates

    #the user exists and has rated something
    if user and BusinessRating.objects.filter(user=user, business=b).count() > 0:
        try:
            r = BusinessRating.objects.get(user=user, business=b)
        except BusinessRating.MultipleObjectsReturned:
            r = BusinessRating.objects.filter(user=user,business=b)[0]
        d['ratingForCurrentUser'] = r.rating
    else:
        d['ratingForCurrentUser'] = 0

    bustags = BusinessCategory.objects.filter(business=b)   #.exclude(tag=get_master_summary_tag())
    d['categories'] = get_categories_data(bustags,user)

    bustypes = BusinessType.objects.filter(business=b)  
    d['types'] = get_bustypes_data(bustypes,user)

    if d['ratingForCurrentUser'] == 0:
        #b.recommendation = get_best_current_recommendation(b, user)
        d['ratingRecommendation'] = get_best_current_recommendation(b, user)
    return d
