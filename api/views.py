#from allsortz.search import get_all_nearbyfrom api.business_operations import add_business_server, edit_business_server
from api.business_serializer import ReadJSONError, get_single_bus_data_ios, \
    get_request_get_or_error, get_request_post_or_error, get_bus_data_ios, \
    get_request_post_or_warn, get_request_postlist_or_warn
from api.models import Photo, PhotoRating, BusinessDiscussion, PhotoDiscussion, \
    Discussion, Business, Topic, DiscussionRating, BusinessRating, Type, \
    BusinessType, Rating, BusinessMeta, BusinessTopic, BusinessTopicDiscussion, \
    BusinessTopicRating, UserTopic
from api.photos import add_photo_by_url
from django.contrib.auth.models import User
from django.http import HttpResponse
from geopy import geocoders
from queries.models import Query, QueryTopic
from queries.views import perform_query_from_param, perform_query_from_obj
from wiki.models import Page
import api.authenticate as auth
import api.json_serializer as serial
import api.photos as photos
import api.prepop as prepop
import logging
import simplejson as json





logger = logging.getLogger(__name__)
            
def get_default_user():
    try:
        user = User.objects.get(username='matt')
    except:
        user = User(first_name='Matt', email='matty@allsortz.com', username='zouf')
        user.set_password("testing")
        user.save()
        
    return user


def get_user(request):
    return get_default_user()

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
        bus = Business.objects.get(id=oid)
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    except: 
        return server_error('Business with id '+str(oid)+'not found')
    bus_data = get_single_bus_data_ios(bus,user,detail=True)
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
    bus_data = get_single_bus_data_ios(bus,user)
    return server_data(bus_data)
    
def add_business(request):
    try:
        print('add business')
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "add")
        bus = Business()
        name=get_request_post_or_warn('businessName', request)
        addr=get_request_post_or_warn('businessStreet', request)
        city = get_request_post_or_warn('businessCity', request)
        state = get_request_post_or_warn('businessState', request)
        phone =  get_request_post_or_warn('businessPhone', request)
        url =  get_request_post_or_warn('businessURL', request)
        types = get_request_postlist_or_warn('selectedTypes',request)
        photoURL = get_request_post_or_warn('photoURL',request)
        bus = add_business_server(name=name,addr=addr,city=city,state=state,phone=phone,url=url,types=types)
    
        if photoURL != '':
            add_photo_by_url(phurl=photoURL,business=bus,user=user, default=True,caption="Picture of "+str(bus.name), title=str(bus.name))
        print(request.POST)
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value) 

    
    bus_data = get_single_bus_data_ios(bus,user,detail=True)
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
        types = get_request_postlist_or_warn('selectedTypes',request)
        bus = edit_business_server(bus=bus,name=name,addr=addr,city=city,state=state,phone=phone,url=url,types=types)
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)   
    except:
        return server_error("Getting business with id "+str(oid)+" failed")
    
    #bus.dist = distance.distance(user.current_location,(bus.lat,bus.lon)).miles
    bus_data = get_single_bus_data_ios(bus,user)
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
   
def search_businesses(request):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "get")
    except:
        return server_error('Failure to authenticate')  
    searchText = get_request_post_or_warn('searchText', request)  
    #topics = get_request_post_or_warn('selectedTopics',request)
    searchLocation = get_request_post_or_warn('searchLocation', request)
    distanceWeight = get_request_post_or_warn('dw', request)
    types = get_request_postlist_or_warn('selectedTypes', request)
    print('searching with types ' + str(types))
    print('searching with text' + str(searchText))
    print('searching with search Location ' + str(searchLocation) + ' and a weight of ' + str(distanceWeight))
    
    if searchText == '':
        print('is null')
        businesses = Business.objects.all()
    else:
        unique_businesses = dict()
        (lat,lng) = user.current_location
        qset = Business.search.geoanchor('latit','lonit', lat,lng).query(searchText)
        logger.info("Searching for "+str(searchText))
        for b in qset:
            searchWeight = b._sphinx['weight']
            #print('businesss ' + str(b) + ' has weight ' + str(searchWeight))
            unique_businesses[b.id] = b._get_current_object()
        topics = Topic.search.query(searchText)
        for t in topics:
            searchWeight = t._sphinx['weight']
            #print('tag ' + str(t) + ' has weight ' + str(searchWeight))
            businesstopics = BusinessTopic.objects.filter(topic = t._get_current_object())
            for bt in businesstopics:
                #businesses.append(bt.business)
                unique_businesses[bt.business.id] = bt.business

        types = Type.search.query(searchText)
        for t in types:
            print('type ' + str(t) + ' has weight ' + str(searchWeight))
            businesstypes = BusinessType.objects.filter(bustype = t._get_current_object())
            for bt in businesstypes:
                #businesses.append(bt.business)
                #print('append ' + str(bt.business))
                unique_businesses[bt.business.id] = bt.business
                
        businesses = []
        for (_,v) in unique_businesses.items():
            #print(v)
            businesses.append(v)
    
    unique_types = dict()
    for tid in types:
        unique_types[tid] =True
    
    
    print('Searching for types ' + str(unique_types))
    businesses_matching_type = []
    for b in businesses:     
        #print(b.businesstype_set)
        btypes = b.businesstype_set.all()
        for bt in btypes:
            print(bt.bustype.id)
            if bt.bustype.id in unique_types:
                
                businesses_matching_type.append(b)

    
    print('result is ' + str(businesses_matching_type))
    print('Performing serialization...')
    serialized_businesses = get_bus_data_ios(businesses_matching_type, user,detail=False)
    print('Serialization complete...')
    
    return server_data(serialized_businesses,"business")

 
 
def get_businesses(request):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "get")
    except:
        return server_error('Failure to authenticate')
    
    
    
    weights = dict()
    #Weights for sorting. 
    #score weight
    if 'sw' in request.GET:
        weights['sw'] = request.GET['sw']
    else:
        weights['sw'] = 1
    
    #distance weight
    if 'dw' in request.GET:
        weights['sdw'] = request.GET['dw']
    else:
        weights['dw'] = 1
        
    #price weight
    if 'pw' in request.GET:
        weights['pw'] = request.GET['pw']
    else:
        weights['pw'] = 1
        
    #value weight
    if 'vw' in request.GET:
        weights['vw'] = request.GET['vw']
    else:
        weights['vw'] = 1

    #topics to sort by
    if 'topics' in request.GET:  
        topics = request.get['topics']
    else:
        topics = None

    #topics to sort by
    if 'text' in request.GET:  
        searchText = request.get['text']
    else:
        searchText = None

    if 'lat' in request.GET and 'lng' in request.GET:
        lat = request.GET['lat']
        lng = request.GET['lng']
    else:
        g = geocoders.Google()
        _, (lat, lng) = g.geocode("Princeton, NJ")  
    
        
    businesses = perform_query_from_param(user, (lat, lng),weights,topics,searchText)
    print('Performing serialization...')
    businesses = Business.objects.all()
    top_businesses = get_bus_data_ios(businesses ,user,detail=False)
    print('Serialization complete...')
    return server_data(top_businesses,"business")


'''
PRAGMA Code to handle business bustopics
'''


def get_business_topics(request,oid):
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
        rating = int(get_request_get_or_error('rating', request))
        bustopic = BusinessTopic.objects.get(id=oid)
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    except: 
        return server_error('bustopic with id '+str(oid)+'not found')
    
    if rating < 0:
        rating = 0.0
    elif rating > 1:
        rating = 1.0
    
    #remove existing rating
    if BusinessTopicRating.objects.filter(businesstopic=bustopic,user=user).count() > 0:
        BusinessTopicRating.objects.filter(businesstopic=bustopic,user=user).delete()
    BusinessTopicRating.objects.create(businesstopic=bustopic, rating=rating,user=user) 
    
    data = serial.get_bustopic_data(bustopic,user)
    return server_data(data)


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
        pg = Page(name=bustopic.topic.descr,bustopic=bustopic)
        pg.save()
    data = serial.get_bustopic_data(bustopic,user)
    return server_data(data,"BusinessTopic")

'''Disassociates a topic with a business '''
def remove_business_topic(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "remove")
        bustopic = BusinessTopic.objects.get(id=oid)
        pg = Page.objects.get(bustopic=bustopic)
        pg.delete()
        bustopic.delete()
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    except:
        return server_error('bustopic with id '+str(oid)+'not found')
    return server_data("Deletion successful","message")

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
    data = serial.get_topics_data(Topic.objects.all(),user)
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
    data = serial.get_topic_data(parent_topic,user)
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
     
    data = serial.get_topic_data(topic,user)
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
     
    print('trying to subscribe')
    try:
        print('Creating a user subscription with user' + str(user)+ " weight " + str(weight) + " to  the topic " + str(topic)) 
        
        if UserTopic.objects.filter(user=user,topic=topic).count() > 0:
            UserTopic.objects.filter(user=user,topic=topic).delete()
        UserTopic.objects.create(user=user,topic=topic,importance=weight)
    except UserTopic.DoesNotExist:
        print('error could not subscribe')
        return server_error("Could not subscribe user. ")
    except Exception as e:
        print('exception')
        print(e.value)
    data = serial.get_topic_data(topic,user)
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
    data = serial.get_topic_data(topic,user)
    return server_data(data)

'''
PRAGMA Code to handle comments
'''

def get_comments(request):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "get")
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    return server_error('unimplemented')

def get_comment(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "get")
        comment = Discussion.objects.get(id=oid)
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    
    data = serial.get_comment_data(comment,user)
    return server_data(data)

def rate_comment(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "rate")
        rating = int(get_request_get_or_error('rating', request))
        comment = Discussion.objects.get(id=oid)
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    except: 
        return server_error('Comment with id '+str(oid)+'not found')

    if rating < 0:
        rating = 0.0
    elif rating > 1:
        rating = 1.0
    
    #XXX TODO make sure rating is an int
    #remove existing rating
    if DiscussionRating.objects.filter(user=user,comment=comment).count() > 0:
        DiscussionRating.objects.filter(user=user,comment=comment).delete()
    DiscussionRating.objects.create(user=user,rating=rating,comment=comment)
    data = serial.get_comment_data(comment,user)
    return server_data(data)

def add_comment(request):
    try: 
        user = auth.authenticate_api_request(request)
        oid = get_request_get_or_error('commentBaseID', request)  
        commentType = get_request_get_or_error('type', request)  
        content = get_request_post_or_error('commentContent', request)  
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)

    try:
        if 'replyTo' in request.GET:
            replyToID = request.GET['replyTo']
            replyComment = Discussion.objects.get(id=replyToID)
        else:
            replyComment = None
    except:
        return server_error("No comment found with id "+str(replyToID))
    
    if commentType == 'business':
        try:
            bus = Business.objects.get(id=oid)
        except:
            return server_error("Business with ID "+str(oid)+ " does not exist")
        comment = BusinessDiscussion.objects.create(user=user,reply_to=replyComment,content=content,business=bus)
    elif commentType == 'businesstopic':
        try:
            btopic = BusinessTopic.objects.get(id=oid)
        except:
            return server_error("bustopic with ID "+str(oid)+ " does not exist")
        comment = BusinessTopicDiscussion.objects.create(user=user,reply_to=replyComment,content=content,businesstopic=btopic)
    elif commentType == 'photo':
        try:
            photo = Photo.objects.get(id=oid)
        except:
            return server_error("Photo with ID "+str(oid)+ " does not exist")
        comment = PhotoDiscussion.objects.create(user=user,reply_to=replyComment,content=content,photo=photo)  
    else:
        return server_error("Invalid commentType "+str(commentType))
    data = serial.get_comment_data(comment,user)
    return server_data(data)

def edit_comment(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "edit")
        content = get_request_post_or_error('commentContent', request)  
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    
    comment = BusinessTopicDiscussion.objects.create(id=oid,content=content)
    data = serial.get_comment_data(comment,user)
    return server_data(data)
    
def remove_comment(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "user")
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    
    try:
        Discussion.objects.filter(id=oid).delete()
    except: 
        return server_error('Comment with id '+str(oid)+' not found. Deletion failed')
    
    return server_data("Deletion successful")


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
        return server_error(e.value)
      
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

 
def edit_query(requst):
    return server_error("unimplemented")
 
def internal_populate_database():
    Rating.objects.all().delete()
    Business.objects.all().delete()
    BusinessMeta.objects.all().delete()
    Page.objects.all().delete()
    Photo.objects.all().delete()
    BusinessTopic.objects.all().delete()
    Topic.objects.all().delete()
    Type.objects.all().delete()
    user = get_default_user()
    
    prepop.prepop_types(user)
    prepop.prepop_topics(user)

    prepop.prepop_businesses(user)
    prepop.prepop_queries(user)
    
    prepop.prepop_users()
    prepop.prepop_ratings()
 
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
        Page.objects.all().delete()
        Photo.objects.all().delete()
        BusinessTopic.objects.all().delete()
        Topic.objects.all().delete()
        Type.objects.all().delete()
    
    prepop.prepop_types(user)
    prepop.prepop_topics(user)
    prepop.prepop_businesses(user)
    prepop.prepop_queries(user)
    
    prepop.prepop_users()
    prepop.prepop_ratings()
    
    return server_data('Prepop successful')

        
        
