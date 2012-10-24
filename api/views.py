#from allsortz.search import get_all_nearbyfrom api.business_operations import add_business_server, edit_business_server
from api.business_operations import add_business_server, edit_business_server
import api.business_serializer as  business_serializer 
from api.json_serializer import get_bustopic_history
from api.models import Photo, PhotoRating, PhotoDiscussion, Discussion, Business, \
    Topic, DiscussionRating, BusinessRating, Type, BusinessType, Rating, \
    BusinessMeta, BusinessTopic, BusinessTopicRating, UserTopic, AllsortzUser, Edge, \
    Comment, BusinessCache, UserCache, Review
from api.photos import add_photo_by_url, add_photo_by_upload
from api.ratings import rate_businesstopic_internal, rate_comment_internal
from api.topic_operations import add_topic_to_bus, get_discussions_data, \
    get_discussion_data, add_review_to_business, add_comment_to_businesstopic, \
    get_review_data, create_article, edit_article
from django.contrib.auth.models import User
from django.contrib.gis.db.models.fields import PolygonField
from django.contrib.gis.geos.factory import fromstr
from django.contrib.gis.geos.point import Point
from django.contrib.gis.geos.polygon import Polygon
from django.contrib.gis.measure import D
from django.db.models.aggregates import Avg
from django.http import HttpResponse
from geopy import geocoders, distance
from geopy.units import radians
from queries.models import Query, QueryTopic
from queries.views import perform_query_from_param, perform_query_from_obj
from recommendation.models import Recommendation
import api.authenticate as auth
import api.business_serializer as busserial
import api.json_serializer as serial
import api.photos as photos
import api.prepop as prepop
import cProfile
import logging
try:
    import json
except ImportError:
    import simplejson as json
#from wiki.models import Page



logger = logging.getLogger(__name__)

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
            
            
MAX_MAP_RESULTS = 40
MAX_SEARCH_LIMIT = 1000

def get_default_user():
    try:
        user = User.objects.get(username='matt')
    except:
        user = User(first_name='Matt', email='matty@allsortz.com', username='zouf')
        user.set_password("testing")
        user.save()
        
    return user



def server_error(msg):
    response_data = dict()
    response_data['success'] = False
    response_data['result'] = msg
    return HttpResponse(json.dumps(response_data), mimetype="application/json")    

def server_data(data,requesttype="unspecified"):
    response_data = dict()
    response_data['success'] = True
    response_data['requestType'] = requesttype
    response_data['result'] = data
    return HttpResponse(json.dumps(response_data), mimetype="application/json")    

'''
PRAGMA Code to handle businesses
'''

def get_business(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "get")
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    except: 
        return server_error('Business with id '+str(oid)+'not found')
    
    
    
    bus = Business.objects.get(id=oid)
    bus_data = business_serializer.get_single_bus_data_ios(bus,user,detail=True)
    return server_data(bus_data,"business")

def rate_business(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "rate")
        rating = int(get_request_get_or_error('rating', request))
        bus = Business.objects.get(id=oid)
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    except: 
        return server_error('Business with id '+str(oid)+'not found')    
    if rating < 0.0:
        rating = 0.0
    elif rating > 1.0:
        rating = 1.0
        
    #XXX TODO allow rating as float
    #remove existing ratings
    if BusinessRating.objects.filter(business=bus,user=user).count() > 0:
        BusinessRating.objects.filter(business=bus,user=user).delete()
    BusinessRating.objects.create(business=bus, rating=rating,user=user) 
    #bus.dist = distance.distance(user.current_location,(bus.lat,bus.lon)).miles
    bus_data = business_serializer.get_single_bus_data_ios(bus,user)
    return server_data(bus_data)
    
def add_business(request):
    try:
        logger.debug('add business')
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "add")
        bus = Business()
        name=get_request_post_or_warn('businessName', request)
        addr=get_request_post_or_warn('businessAddress', request)
        city = get_request_post_or_warn('businessCity', request)
        state = get_request_post_or_warn('businessState', request)
        phone =  get_request_post_or_warn('businessPhone', request)
        url =  get_request_post_or_warn('businessURL', request)
        types = get_request_postlist_or_warn('selectedTypes',request)
        photoURL = get_request_post_or_warn('photoURL',request)
        bus = add_business_server(name=name,addr=addr,city=city,state=state,phone=phone,url=url,types=types)
    
        if photoURL != '':
            add_photo_by_url(phurl=photoURL,business=bus,user=user, default=True,caption="Picture of "+str(bus.name), title=str(bus.name))
        logger.debug(request.POST)
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value) 

    
    bus_data = business_serializer.get_single_bus_data_ios(bus,user,detail=True)
    return server_data(bus_data,"business")

def edit_business(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "edit")
        bus = Business.objects.get(id = oid)
        
        name=get_request_post_or_warn('businessName', request)
        addr=get_request_post_or_warn('businessStreet', request)
        city = get_request_post_or_warn('businessCity', request)
        state = get_request_post_or_warn('businessState', request)
        phone =  get_request_post_or_warn('businessPhone', request)
        url =  get_request_post_or_warn('businessURL', request)
        hours =  get_request_post_or_warn('businessHours', request)

        types = get_request_postlist_or_warn('selectedTypes',request)
        bus = edit_business_server(bus=bus,name=name,addr=addr,city=city,state=state,phone=phone,url=url,types=types,hours=hours)
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)   
    except:
        return server_error("Getting business with id "+str(oid)+" failed")
    
    #bus.dist = distance.distance(user.current_location,(bus.lat,bus.lon)).miles
    bus_data = business_serializer.get_single_bus_data_ios(bus,user,detail=True)
    return server_data(bus_data,"business")

def remove_business(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "remove")
        bus = Business.objects.get(id=oid)
        name = bus.name
        Business.objects.filter(id = oid).delete()
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    except:
        return server_error("Deleting business with id "+str(oid)+" failed")
    return server_data("Deletion of business "+str(name)+ " was a success","message")

def query_businesses(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "query")
        q = Query.objects.get(id=oid)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    except ReadJSONError as e:
        return server_error(e.value)
    except:
        return server_error("Couldn't get query with ID " + str(oid))

    data = perform_query_from_obj(user,user.current_location,q)
    return server_data(data,"business") #server_data(top_businesses)
   
   
def is_searchtext_location(searchText, currentlocation):
    if searchText == '':
        return None
    try:
        g = geocoders.Google()
        searchLocation, (lat,lng) = g.geocode(str(searchText),exactly_one=False)[0] 
    except Exception as e:
        logger.debug('Error in geocoding, so probably not a location!' + str(e))
        logger.debug('Probably not a location!')
        return None
    logger.debug('location is ' + str(searchLocation))
    
    (cLat, cLon) = currentlocation
    dist = distance.distance((lat,lng),currentlocation)
    
    
    #basically dont return its absurdly far away
    if dist.mi > 80:
        return None

    
    return searchLocation, (lat,lng)
        
def get_search_string(searchText,searchLocation, searchTypes,num,isLocationSearch):
    typeString = ""
    for t in searchTypes:
        tp = Type.objects.get(id=t)
        typeString += str(tp.descr) + " "
    

    searchString = ""
    if searchText != "":
        searchString += str(searchText) + " "
    
    if searchLocation != "":
        searchString += " near " + str(searchLocation) + " "
 
    if typeString != "":
        searchString += "(" + typeString+ ") "
    
    if searchString != "":
        old = searchString
        searchString = "Found " + str(num) + "businesses for " + str(old) + "."
    elif isLocationSearch:
        searchString = "Displaying " + str(num) + " businesses near " + searchLocation + "."
    else:
        searchString = "Displaying " + str(num) + " businesses."
        
    return searchString 
  


def search_businesses_server(user,searchText,searchLocation,distanceWeight,searchTypes,low=0,high=0,polygon_search_bound=None):
    if searchLocation != '':
        logger.debug('Search location not nil ')
        g = geocoders.Google()
        try:
            _, (lat,lng) = g.geocode(str(searchLocation),exactly_one=False)[0] 
        except Exception as e:
            logger.error('Error in geocoding' + str(e))
         
    else:
        logger.debug(' location was nil')
        (lat,lng) = user.current_location
        
        
    searchQuery = "Search Term: "+str(searchText)+"\nLocation: "+str(searchLocation)+" \nWeight: "+str(distanceWeight)+"\nSearch Types: "+str(searchTypes)+"\nLat Lng = ("+str(lat)+","+str(lng)+")" 
    logger.debug(searchQuery)
    logger.debug(searchQuery)
    
    if distanceWeight != '':
        if float(distanceWeight) > 0.67:
            dist_limit = D(mi=20)
        elif float(distanceWeight) > 0.33:
            dist_limit = D(mi=60)
        else:
            dist_limit = D(mi=60)
    else:
        dist_limit = D(mi=2)
        
        
    
    businesses_filtered = []
    
    if searchTypes != []:
        for tid in searchTypes:
            t = Type.objects.get(id=tid)
            searchText += t.descr
 
    if searchText == '':
        logger.debug('no search text')
        pnt = fromstr('POINT( '+str(lng)+' '+str(lat)+')')
        logger.debug(str(pnt))
        businesses_filtered = Business.objects.filter(geom__distance_lte=(pnt,dist_limit)).distance(pnt).order_by('distance')
        logger.debug(str(businesses_filtered.count()) + " results")
    else:
        logger.debug('searching with text: ' + str(searchText))
        qset = []
        logger.debug(polygon_search_bound)
        results = Business.search.query(searchText)
        results = Business.search.geoanchor('latit','lonit', radians(lat),radians(lng))\
            .filter(**{'@geodist__lt':dist_limit.m*1.0})\
            .query(searchText).order_by('-@geodist')
        geom_within = []
        logger.debug(results.count())
        if results.count() < MAX_SEARCH_LIMIT:
            limit = results.count()
        else:
            limit = MAX_SEARCH_LIMIT
            

        logger.debug("Limit for search " + str(searchText) + " is " + str(limit))
        for r in results[0:limit]:
            logger.debug('Result: ' + str(r))
            #are we searching with a map bound?
            if polygon_search_bound:
                if r.geom.within(polygon_search_bound):
                    logger.debug('Business ' + str(r) + ' is in the polygon')
                    geom_within.append(r)
            else:
                geom_within.append(r)
                
        qset = geom_within 
        
        businesses_filtered = []
        for b in qset:
            searchWeight = b._sphinx['weight']
            logger.debug('businesss ' + str(b) + ' has weight ' + str(searchWeight))
            businesses_filtered.append(Business.objects.get(id=b.id))
        #for some reason, the sphinx query set is reversed when it's returned. The largest distances are in the front
        # Reverse here
        businesses_filtered.reverse()
        businesses_filtered = businesses_filtered[low:high]
 
   
    
    idlist = []
    logger.debug('done and have ' + str(businesses_filtered) + ' resul;ts')
    for b in businesses_filtered:
        idlist.append(b.id)
    
    if lat and lng:
        pnt = fromstr('POINT( '+str(lng)+' '+str(lat)+')')
        businesses = Business.objects.filter(id__in=idlist).distance(pnt).order_by('distance')    
    else:
        businesses = Business.objects.filter(id__in=idlist)
    
     

    return businesses


 
def get_businesses_map(request):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "get")
    except Exception as e:
        return server_error(str(e))
    
    minx = float(get_request_get_or_error('min_y', request))
    miny = float(get_request_get_or_error('min_x', request))
    maxx =float( get_request_get_or_error('max_y', request))
    maxy = float(get_request_get_or_error('max_x', request))
    
    poly = Polygon( ((minx, miny), (minx, maxy), (maxx, maxy), (maxx, miny), (minx, miny)) )    


    searchText = get_request_post_or_warn('searchText', request)  
    searchLocation = get_request_post_or_warn('searchLocation', request)
    distanceWeight = get_request_post_or_warn('dw', request)
    searchTypes = get_request_postlist_or_warn('selectedTypes', request)
    businesses = []
    
    res = is_searchtext_location(searchText, user.current_location)
    #user puts in an address in the search bar!
    return_type = "business"
    if res:
        searchLocation = res[0]
        logger.debug('using location ' + str(searchLocation))
        (lat,lng) = res[1]
        
        
        logger.debug(res[1])
        pnt = fromstr('POINT( '+str(lng)+' '+str(lat)+')')
        businesses = Business.objects.distance(pnt).select_related().order_by('distance')[0:MAX_MAP_RESULTS]
        return_type = "new_address"
        logger.debug(str(businesses.count()) + " returned")
        
    elif searchText != '' or searchTypes != []:  
        businesses = search_businesses_server(user,searchText,searchLocation,distanceWeight,searchTypes,low=0,high=MAX_MAP_RESULTS,polygon_search_bound=poly)
    else:
        businesses = Business.objects.filter(geom__within=poly)[0:MAX_MAP_RESULTS]
        

    logger.debug('Performing serialization...')
    logger.debug(businesses)
    serialized = busserial.get_bus_data_ios(businesses ,user,detail=False)
    serialized['searchString'] = get_search_string(searchText,searchLocation, searchTypes, businesses.count(),isLocationSearch=res)
    logger.debug('Serialization complete...')
    return server_data(serialized,return_type) 


def get_businesses(request):    
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "get")
    except Exception as e:
        return server_error(str(e))  
    low = int(get_request_get_or_error('bus_low', request))
    high = int(get_request_get_or_error('bus_high', request))
   
    searchText = get_request_post_or_warn('searchText', request)  
    searchLocation = get_request_post_or_warn('searchLocation', request)
    distanceWeight = get_request_post_or_warn('dw', request)
    searchTypes = get_request_postlist_or_warn('selectedTypes', request)
    businesses = []
    
    res = is_searchtext_location(searchText, user.current_location)
    #perform search
    if searchText != '' or searchTypes != []:     
        businesses = search_businesses_server(user,searchText,searchLocation,distanceWeight,searchTypes,low,high)
        
    else:  # DEFAULT FRONT PAGE (i.e. no search params)
        (lat, lng) = user.current_location
        pnt = fromstr('POINT( '+str(lng)+' '+str(lat)+')')
        businesses = Business.objects.distance(pnt).select_related().order_by('distance')[low:high]
        logger.debug(str(businesses.count()) + " returned")
        
    #annotate(avg_rating=Avg('businesstopic__businesstopicrating__rating'))
    logger.debug('Performing serialization...')
    logger.debug(businesses) 
    serialized = busserial.get_bus_data_ios(businesses ,user,detail=False)
    serialized['searchString'] = get_search_string(searchText,searchLocation, searchTypes, businesses.count(),isLocationSearch=res)
    logger.debug('Serialization complete...')
    return server_data(serialized,"business")

'''
PRAGMA Code to handle business bustopics
'''


def get_business_topics(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "get")
        bus = Business.objects.get(id=oid)
    except ReadJSONError as e:
        return server_error(str(e))
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    except: 
        return server_error('Business with id '+str(oid)+'not found')
        
    bustopics = BusinessTopic.objects.filter(business=bus)
    
    data = serial.get_bustopics_data(bustopics,user)
    return server_data(data)

'''Associates a topic with a business '''
def get_business_topic(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "get")
        bustopic = BusinessTopic.objects.get(id=oid)
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    except: 
        return server_error('bustopic with id '+str(oid)+'not found')
    
    data = serial.get_bustopic_data(bustopic,user)
    return server_data(data)

'''Rates a business' topic-business relationship '''
def rate_business_topic(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "rate")
        rating = float(get_request_get_or_error('rating', request))
        bustopic = BusinessTopic.objects.get(id=oid)
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(str(e))
    except Exception as e: 
        return server_error('bustopic with id '+str(oid)+'not found' + str(e))
    
    
    logger.debug('here')
    rate_businesstopic_internal(bustopic=bustopic,user=user,rating=rating)
    return server_data("success","bustopic")


'''Associates a topic with a business '''
def add_business_topic(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "add")
        topicid = get_request_get_or_error('topicID', request)
        bus = Business.objects.get(id=oid)
        topic = Topic.objects.get(id=topicid)
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    except: 
        return server_error('Retrieving business and bustopic failed (IDs: '+str(oid)+ ' and ' + str(topicid))
    
    if BusinessTopic.objects.filter(business=bus,topic=topic).count() > 0:
        bustopic = BusinessTopic.objects.get(business=bus, topic=topic)
    else:
        bustopic = BusinessTopic.objects.create(business=bus,topic=topic,creator=user)
    data = serial.get_bustopic_data(bustopic,user)
    return server_data(data,"BusinessTopic")

'''Disassociates a topic with a business '''
def remove_business_topic(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "remove")
        bustopic = BusinessTopic.objects.get(id=oid)
        #pg = Page.objects.get(bustopic=bustopic)
        #pg.delete()
        bustopic.delete()
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    except:
        return server_error('bustopic with id '+str(oid)+'not found')
    return server_data("Deletion successful","message")

''' 
PRAGMA Code to handle business reviews (for aggregate display)
''' 
def get_business_reviews(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "get")
        bus = Business.objects.get(id=oid)
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    except: 
        return server_error('Business with id '+str(oid)+'not found')
    
    discussions = Review.objects.filter(business =bus).order_by('-date')

    data = dict()
    data['reviews'] = get_discussions_data(discussions,user)
    return server_data(data,"businessReviews")



''' 
PRAGMA Code to handle business types
''' 
def get_business_types(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "get")
        bus = Business.objects.get(id=oid)
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    except: 
        return server_error('Business with id '+str(oid)+'not found')
        
    bustypes = BusinessType.objects.filter(business=bus)
    data = serial.get_bustypes_data(bustypes,user)
    return server_data(data,"businessType")


'''Associates a type with a business '''
def add_business_type(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "add")
        typeid = get_request_get_or_error('typeID', request)
        bus = Business.objects.get(id=oid)
        bustype = Type.objects.get(id=typeid)
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    except: 
        return server_error('Retrieving business and type failed (IDs: '+str(oid)+ ' and ' + str(typeid))
    
    if BusinessType.objects.filter(business=bus,Type=bustype).count() == 0:
        BusinessType.objects.create(business=bus,bustype=bustype,creator=user)
    
    bustypes = BusinessType.objects.filter(business=bus)
    data = serial.get_bustypes_data(bustypes,user)
    return server_data(data,"businessType")

'''Disassociates a type with a business '''
def remove_business_type(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "remove")
        BusinessType.objects.filter(id=oid).delete()
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    except:
        return server_error('BusType with id '+str(oid)+'not found')
    return server_data("Deletion successful","message")


def get_topics(request):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "get")
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    
    
    data = serial.get_topics_data(Topic.objects.all(),user,detail=True)
    return server_data(data,"topic")


def get_topics_parent(request):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "get")
        parent_id = get_request_get_or_error('parent', request)
        if parent_id!='':
            parent_topic = Topic.objects.get(id=parent_id)
        else:
            parent_topic = Topic.objects.get(descr='Main')
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    
    
    data = serial.get_topic_data(parent_topic,user,detail=True)
    
    
    return server_data(data,"topic")


def get_topic(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "get")
        topic = Topic.objects.get(id=oid)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    except Topic.DoesNotExist:
        return server_error("Topic with ID "+str(oid) + " not found")
    
    data = serial.get_topic_data(topic,user,detail=True)
    
    
    return server_data(data,"topic")

''' Get types of business (e.g. sandwich, etc. '''
def get_types(request):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "get")
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    data = serial.get_types_data(Type.objects.all().order_by('descr'),user)
    return server_data(data,"type")


def get_type(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "get")
        typeofbusiness = Type.objects.get(id=oid)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    except Type.DoesNotExist:
        return server_error("Type with ID "+str(oid) + " not found")
     
    data = serial.get_type_data(typeofbusiness)
    return server_data(data,"type")

def add_type(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "add")
        descr = get_request_post_or_error('topicDescr', request)
        if Type.objects.filter(descr=descr):
            typeofbusiness = Type.objects.get(descr=descr)
        else:
            typeofbusiness = Type.objects.create(descr=descr,creator=user)    
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    except:
        return server_error("Type could not be created")
     
    data = serial.get_type_data(typeofbusiness)
    return server_data(data,"type")



def subscribe_topic(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "edit")
        topic = Topic.objects.get(id=oid)
        weight = get_request_get_or_error('importance', request)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    except Topic.DoesNotExist:
        return server_error("Topic with ID "+str(oid) + " not found")
     
    logger.debug('trying to subscribe')
    try:
        logger.debug('Creating a user subscription with user' + str(user)+ " weight " + str(weight) + " to  the topic " + str(topic)) 
        
        if UserTopic.objects.filter(user=user,topic=topic).count() > 0:
            UserTopic.objects.filter(user=user,topic=topic).delete()
        UserTopic.objects.create(user=user,topic=topic,importance=weight)
        UserCache.objects.filter(user=user).delete()
        Recommendation.objects.filter(user=user).delete()
    except UserTopic.DoesNotExist:
        logger.debug('error could not subscribe')
        return server_error("Could not subscribe user. ")
    except Exception as e:
        logger.debug('exception')
        logger.debug(e.value)

    data = serial.get_topic_data(topic,user,detail=True)
    return server_data(data, "subscription")


def unsubscribe_topic(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "edit")
        topic = Topic.objects.get(id=oid)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    except Topic.DoesNotExist:
        return server_error("Topic with ID "+str(oid) + " not found")
     
    try:
        UserTopic.objects.filter(user=user,topic=topic).delete()
    except :
        return server_error("Error occurred. Could not unsubscribe user.")
    data = serial.get_topic_data(topic,user,detail=True)
    return server_data(data)



'''
PRAGMA Code to handle photos
'''
def get_all_photos(request):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "get")
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)

    allphotos= Photo.objects.all()
    data = serial.get_photos_data(allphotos,user,order_by='date')
    return server_data(data)


def get_photos(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "get")
        phototype = get_request_get_or_error('type', request)  
        order_by = get_request_get_or_error('order_by', request)  
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)

    
    if phototype=="business":
        try:
            bus = Business.objects.get(id=oid)
        except:
            return server_error("No business with ID"+str(oid)+" found")
        allphotos= Photo.objects.filter(business=bus)           
    else:
        allphotos= Photo.objects.filter(user=user,business=None)
        
    data = serial.get_photos_data(allphotos,user,order_by=order_by)
    return server_data(data)


def get_photo(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "get")
        photo = Photo.objects.get(id=oid)
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)       
    except Photo.DoesNotExist: 
        return server_error('Photo with id '+str(oid)+' not found.')
    
    data = serial.get_photo_data(photo,user)
    return server_data(data)

def edit_photo(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "edit")
        photo = Photo.objects.get(id=oid)
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)       
    except Photo.DoesNotExist: 
        return server_error('Photo with id '+str(oid)+' not found.')
    
    if 'photoCaption' in request.POST:
        photo.caption = request.POST['photoCaption']
    if 'photoTitle' in request.POST:
        photo.title = request.POST['photoTitle']
        
    photo.save(isUpload=False,isTextMod=True)
    
    data = serial.get_photo_data(photo,user)
    return server_data(data)

def rate_photo(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "rate")
        rating = int(get_request_get_or_error('rating', request))
        photo = Photo.objects.get(id=oid)
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    except Photo.DoesNotExist: 
        return server_error('Photo with id '+str(oid)+' not found.')
    
    if rating < 0:
        rating = 0.0
    elif rating > 1:
        rating = 1.0
        
    #XXX TODO make sure rating is an int
    #remove existing rating
    if PhotoRating.objects.filter(user=user,photo=photo).count()> 0:
        PhotoRating.objects.filter(user=user,photo=photo).delete()
    PhotoRating.objects.create(rating = rating,user=user,photo=photo)
    data = serial.get_photo_data(photo,user)
    return server_data(data)
    
 
def add_photo(request):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "add")
        caption = get_request_post_or_error('photoCaption', request)
        title = get_request_post_or_error('photoTitle', request)
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
        
    if 'businessID' not in request.GET:
        b = None
        defaultUserPhoto = True

    else:
        defaultUserPhoto = False

        bid = request.GET['businessID']
        try:
            b = Business.objects.get(id=bid)
        except:
            return server_error("Could not retrieve business with ID "+str(bid)+ " for add_photo")

    
    if 'image' in request.FILES:
        img = request.FILES['image']
        photo = photos.add_photo_by_upload(img,b,request.user,defaultUserPhoto,caption,title)
    elif 'url' in request.POST:
        url = request.POST['url']
        if url != '':
            photo = photos.add_photo_by_url(url, b, request.user, defaultUserPhoto,caption,title)
    else:
        return server_error("No photo specified in request.FILES or URL in request.POST")
    data = serial.get_photo_data(photo,user)
    return server_data(data)

def remove_photo(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "remove")
        Photo.objects.filter(id=oid).delete()
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)      
    except Photo.DoesNotExist: 
        return server_error('Photo with id '+str(oid)+' not found. Deletion failed')
    return server_data("Deletion of photo id= " +str(oid)+ " successful")

''' 
PRAMGA Code to handle discussions 
'''
#the comments are the "reviews" and "comments" (that are replies to the business topic or the review. Discussions with no parent are eligible to the be
# top review for a topic and will be displayed on the business details page
def get_comments(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "get")
        #bustopicID = get_request_get_or_error('busTopicID',request)
        bustopic = BusinessTopic.objects.get(id=oid)
    except Exception as e:
        return server_error(str(e))
    discussions = Comment.objects.filter(businesstopic =bustopic).order_by('-date')
    
    data = dict()
    data['busTopicInfo'] = serial.get_bustopic_data(bustopic, user, True)
    data['comments'] = get_discussions_data(discussions,user)
    logger.debug(data)
    return server_data(data,"comments")


def get_main_review_history(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "view")
        bustopic = BusinessTopic.objects.get(id=oid)
    except Exception as e:
        return server_error(str(e))
    
    
    data = get_bustopic_history(bustopic)
    logger.debug(data)
    return server_data(data,"history")

def add_main_review_history(request):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "view")
        busID = get_request_get_or_error('businessID', request)
        topicID = get_request_get_or_error('topicID', request)
        bus = Business.objects.get(id=busID)
        topic = Topic.objects.get(id=topicID)
        content = get_request_post_or_error('content', request)
        
    except Exception as e:
        return server_error(str(e))
    
    bustopic = add_topic_to_bus(bus, topic, user)
    

    create_article(bustopic,title=str(bus.name) + ' ' + str(topic.descr),
    user_message='User ' + str(user) + ' created the article on ' + str(topic),
    content=content,
    request=request,
    article_kwargs={'owner': user,
                    'group': None,
                    'group_read': True,
                    'group_write': True,
                    'other_read': True,
                    'other_write':True,
                    }
    )
    
    bustopic.save()
    data = get_bustopic_history(bustopic)
    logger.debug(data)
    return server_data(data,"history")



def edit_main_review(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "edit")
        #bustopicID = get_request_get_or_error('busTopicID',request)
        content = get_request_post_or_error('content', request)
        bustopic = BusinessTopic.objects.get(id=oid)
    except Exception as e:
        return server_error(str(e))
    
    logger.debug('Modifying bustopic review')
    logger.debug('new review is '+ str(content))
    edit_article(bustopic,title=None,content=content,summary='Mod by user ' + str(user), request=request)
                
    bustopic.save()
    UserCache.objects.filter(business=bustopic.business).delete()
    logger.debug('done !')
    
    discussions = Comment.objects.filter(businesstopic =bustopic).order_by('-date')
    
    data = dict()
    data['busTopicInfo'] = serial.get_bustopic_data(bustopic, user, True)
    data['comments'] = get_discussions_data(discussions,user)
    logger.debug(data)
    return server_data(data,"comments")


def get_comment(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "get")
        discussion = Discussion.objects.get(id=oid)
    except Exception as e:
        return server_error(str(e))
    
    data = dict()
    data['comment'] = get_discussion_data(discussion,user)
    return server_data(data,"comment")

def get_review(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "get")
        business = Business.objects.get(id=oid)
    except Exception as e:
        return server_error(str(e))

    data = get_review_data(business,user)
    logger.debug(data)
    return server_data(data,"review")


def add_comment(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "add")
        topicIDs = get_request_postlist_or_warn('topicIDs', request)
        topics = Topic.objects.filter(id__in=topicIDs)
        commentType = get_request_post_or_error('commentType',request)
        replyTo = int(get_request_post_or_warn('replyToID', request))
        commentContent = get_request_post_or_error('content', request)
        proposedChange = get_request_post_or_error('proposedChange', request)

    except Exception as e:
        logger.debug('error in add_comment ' + str(e))
        return server_error(str(e))
    except Exception as e:
        return server_error(str(e))
    
    comment = None 
    if commentType == "review":
        business = Business.objects.get(id=oid)#('businessID', request)   
        comment = add_review_to_business(business,commentContent,user)
    else:
        try:
            bustopic = BusinessTopic.objects.get(id=oid)
            business = bustopic.business
            comment = add_comment_to_businesstopic(bustopic,commentContent,proposedChange,user, replyTo,request)
        except Exception as e:
            logger.debug("In adding comment error is " + str(e))
    logger.debug('Review is ' + str(commentContent) +  " reply to ID  is " + str(replyTo))

    serialized = get_discussion_data(comment, user)
    return server_data(serialized,"comment")

def rate_comment(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "rate")
        comment = Discussion.objects.get(id=oid)
        rating = int(get_request_get_or_error('rating', request))
    except Exception as e:
        return server_error(str(e))
    
    rate_comment_internal(comment=comment,user=user,rating=rating)
    serialized = get_discussion_data(comment, user)
    return server_data(serialized,"comment")

    
    
''' 
PRAGMA Code to handle social
'''

def get_user(request):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "get")
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(str(e))
    user_data = serial.get_user_details(user,auth=True)
    return server_data(user_data,"userDetails")


def get_users(request):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "get")
    except Exception as e:
        return server_error(str(e))
    user_data = dict()
    users = []
    for asuser in AllsortzUser.objects.all().prefetch_related('user'):
      users.append(asuser.user)
    user_data['users'] = serial.get_users_details(users,user)
    return server_data(user_data,"userDetails")



def update_user(request):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "get")
        uname = get_request_post_or_error('userName', request)
        password = get_request_post_or_warn('userPassword', request)
        email = get_request_post_or_error('userEmail', request)
        deviceID=get_request_get_or_error('deviceID', request)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(str(e))
    
    logger.debug('Submitted post ' + str(request.POST)) 
    if User.objects.filter(username=uname).count()> 0:
        if User.objects.get(username=uname) != user:
            return server_error('Username ' + str(uname) + ' taken')
    if User.objects.filter(email=email).count() > 0:
        if User.objects.get(email=email) != user:
            return server_error('Email ' +str(email) + ' already in use')
    
    try:
        auth.register_asuser(user=user,newUname=uname,password=password,email=email,deviceID=deviceID)
    except  auth.RegistrationFailed as e:
        return server_error(str(e))
    
    logger.debug('RETURNING user data for ' + str(user))
    return server_data(serial.get_user_details(user,auth=True),"userDetails")

def update_user_picture(request):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "edit")
        image = request.FILES['file']
        deviceID=get_request_get_or_error('deviceID', request)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(str(e))
    
    try:
        print('upload photo ' + str(image))
        bp = add_photo_by_upload(image,None,user,True,"test caption","test title")
        print('adding photo' + str(image))
        user.asuser.profile_photo =  bp;
        user.asuser.save()
    except Exception as e:
        print('error!\n' + str(e))
        return server_error(str(e))
    return server_data(serial.get_user_details(user,auth=True),"userPicture")

'''
PRAGMA Code to handle queries
''' 

def get_queries(request):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "get")
        querytype = get_request_get_or_error('type', request)
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(str(e))
      
    if querytype=='yours':
        queries = Query.objects.filter(creator=user)
    elif querytype=='popular': 
        queries = Query.objects.filter(is_default=True)
    else:
        queries = Query.objects.filter(creator=user)
    data = serial.get_queries_data(queries,user)
    return server_data(data,"query")
    
    
def get_query(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "get")
        query = Query.objects.get(id=oid)
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    except:
        return server_error("Query with ID "+str(oid)+" not found")

    data = serial.get_query_data(query,user)
    return server_data(data,"query")
 
     
def get_query_base(request):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "get")
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)

    topics =dict()# serial.get_topics_data(Topic.objects.all(),user)
    types = serial.get_types_data(Type.objects.all().order_by('descr'),user)
    data = dict()
    data['topics'] = topics;
    data['types'] = types;
    return server_data(data,"query")
 

    

    
def add_query(request):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "add")
        query = Query()
        query.name = get_request_post_or_error('queryName',request)
        query.creator = user#get_json_or_error('queryName',request)
        query.proximity = get_request_post_or_error('proximityWeight',request)
        query.price = get_request_post_or_error('priceWeight',request)
        query.value = get_request_post_or_error('valueWeight',request)
        query.score = get_request_post_or_error('scoreWeight',request)
        query.userHasVisited = get_request_post_or_error('userHasVisited',request)
        query.text = get_request_post_or_error('searchText',request)
        query.networked = get_request_post_or_error('networked',request)
        query.deal = get_request_post_or_error('deal',request)
        query.is_default = False# get_json_or_error('deal',request)
        query.save()
        if 'querytopics' not in request.POST:
            return server_error("bustopics did not provide a list")
        bustopicList = request.POST.getlist('queryBustopics')
        for c in bustopicList:
            if Topic.objects.filter(id=c).count() == 0:
                return server_error("Invalid bustopic provided")
            cat = Topic.objects.get(id=c)
            QueryTopic.objects.create(query=query,topic=cat)
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    except:
        return server_error("Could not save the object")
    data = serial.get_query_data(query,user)
    return server_data(data)

def remove_query(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "remove")
        Query.objects.filter(id=oid).delete()
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    except:
        return server_error("Query with ID "+str(oid)+" not found. Deletion was not successful")
    return server_data("Deletion successful")

 
def edit_query(request):
    return server_error("unimplemented")
 
 
def clear_caches(): 
    BusinessCache.objects.all().delete()
    Recommendation.objects.all().delete()
    UserCache.objects.all().delete()

def internal_populate_database():
    Rating.objects.all().delete()
    Business.objects.filter(state='NJ').delete()
    BusinessMeta.objects.all().delete()
    #Page.objects.all().delete()
    Photo.objects.all().delete()
    BusinessTopic.objects.all().delete()
    Topic.objects.all().delete()
    Type.objects.all().delete()
    user = get_default_user()
    Recommendation.objects.all().delete()
    BusinessTopicRating.objects.all().delete()
    
    clear_caches()
    
    prepop.prepop_types(user)
    prepop.prepop_topics(user)
    prepop.prepop_businesses(user)
    prepop.prepop_queries(user)
    
    prepop.prepop_users()
#    prepop.prepop_business_ratings()
    prepop.prepop_topic_ratings()
 
def prepopulate_database(request):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "superuser")
       
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)

    if 'clear' in request.GET:
        Rating.objects.all().delete()
        Business.objects.all().delete()
        #Page.objects.all().delete()
        Photo.objects.all().delete()
        BusinessTopic.objects.all().delete()
        Topic.objects.all().delete()
        Type.objects.all().delete()
    
    prepop.prepop_types(user)
    prepop.prepop_topics(user)
    prepop.prepop_businesses(user)
    prepop.prepop_queries(user)    
    prepop.prepop_users()
    prepop.prepop_topic_ratings()

    
    return server_data('Prepop successful')

        
        
