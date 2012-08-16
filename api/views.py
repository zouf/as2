#from allsortz.search import get_all_nearby
from api.business_operations import add_business_server, edit_business_server
from api.business_serializer import ReadJSONError, get_single_bus_data_ios, \
    get_request_get_or_error, get_request_post_or_error, get_bus_data_ios, \
    get_request_post_or_warn, get_request_postlist_or_warn
from api.models import Photo, PhotoRating, BusinessDiscussion, \
    CategoryDiscussion, PhotoDiscussion, Discussion, Business, BusinessCategory, \
    CategoryRating, Tag, DiscussionRating, BusinessRating, UserSubscription, \
    TypeOfBusiness, BusinessType, Rating
from django.contrib.auth.models import User
from django.http import HttpResponse
from geopy import geocoders, distance
from queries.models import Query, QueryTag
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

def server_data(data,requesttype=None):
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
    bus_data = get_single_bus_data_ios(bus,user)
    return server_data(bus_data)

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
    if rating < 1:
        rating = 1
    elif rating > 4:
        rating = 4
        
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
        bus = add_business_server(name=name,addr=addr,city=city,state=state,phone=phone,url=url,types=types)
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value) 
    except Exception as e:
        return server_error(e.value)
    
    bus_data = get_single_bus_data_ios(bus,user)
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
    return server_data(data) #server_data(top_businesses)
    
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

    #Tags to sort by
    if 'tags' in request.GET:  
        tags = request.get['tags']
    else:
        tags = None

    #Tags to sort by
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
    
        
    businesses = perform_query_from_param(user, (lat, lng),weights,tags,searchText)
    print('Performing serialization...')
    businesses = Business.objects.all()
    top_businesses = get_bus_data_ios(businesses ,user)
    print('Serialization complete...')

    return server_data(top_businesses)


'''
PRAGMA Code to handle business categories
'''


def get_business_categories(request,oid):
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
        
    categories = BusinessCategory.objects.filter(business=bus)
    
    data = serial.get_categories_data(categories,user)
    return server_data(data)

'''Associates a tag with a business '''
def get_business_category(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "get")
        category = BusinessCategory.objects.get(id=oid)
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    except: 
        return server_error('Category with id '+str(oid)+'not found')
    
    data = serial.get_category_data(category,user)
    return server_data(data)

'''Rates a business' tag-business relationship '''
def rate_business_category(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "rate")
        rating = int(get_request_get_or_error('rating', request))
        category = BusinessCategory.objects.get(id=oid)
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    except: 
        return server_error('Category with id '+str(oid)+'not found')
    
    if rating < 1:
        rating = 1
    elif rating > 4:
        rating = 4
    
    #XXX TODO make sure rating is an int
    #remove existing rating
    if CategoryRating.objects.filter(category=category,user=user).count() > 0:
        CategoryRating.objects.filter(category=category,user=user).delete()
    CategoryRating.objects.create(category=category, rating=rating,user=user) 
    
    data = serial.get_category_data(category,user)
    return server_data(data)


'''Associates a tag with a business '''
def add_business_category(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "add")
        tagid = get_request_get_or_error('tagID', request)
        bus = Business.objects.get(id=oid)
        tag = Tag.objects.get(id=tagid)
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    except: 
        return server_error('Retrieving business and category failed (IDs: '+str(oid)+ ' and ' + str(tagid))
    
    if BusinessCategory.objects.filter(business=bus,tag=tag).count() > 0:
        category = BusinessCategory.objects.get(business=bus, tag=tag)
    else:
        category = BusinessCategory.objects.create(business=bus,tag=tag,creator=user)
        pg = Page(name=category.tag.descr,category=category)
        pg.save()
    data = serial.get_category_data(category,user)
    return server_data(data,"businessCategory")

'''Disassociates a tag with a business '''
def remove_business_category(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "remove")
        bc = BusinessCategory.objects.get(id=oid)
        pg = Page.objects.get(category=bc)
        pg.delete()
        bc.delete()
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    except:
        return server_error('Category with id '+str(oid)+'not found')
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
        typeofbusiness = TypeOfBusiness.objects.get(id=typeid)
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    except: 
        return server_error('Retrieving business and type failed (IDs: '+str(oid)+ ' and ' + str(typeid))
    
    if BusinessType.objects.filter(business=bus,typeofbusiness=typeofbusiness).count() == 0:
        BusinessType.objects.create(business=bus,typeofbusiness=typeofbusiness,creator=user)
    
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


def get_tags(request):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "get")
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    data = serial.get_tags_data(Tag.objects.all(),user)
    return server_data(data,"tag")


def get_tag(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "get")
        tag = Tag.objects.get(id=oid)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    except Tag.DoesNotExist:
        return server_error("Tag with ID "+str(oid) + " not found")
     
    data = serial.get_tag_data(tag,user)
    return server_data(data,"tag")




''' Get types of business (e.g. sandwich, etc. '''
def get_types(request):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "get")
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    data = serial.get_types_data(TypeOfBusiness.objects.all(),user)
    return server_data(data,"type")


def get_type(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "get")
        typeofbusiness = TypeOfBusiness.objects.get(id=oid)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    except TypeOfBusiness.DoesNotExist:
        return server_error("Type with ID "+str(oid) + " not found")
     
    data = serial.get_type_data(typeofbusiness)
    return server_data(data,"type")

def add_type(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "add")
        descr = get_request_post_or_error('tagDescr', request)
        if TypeOfBusiness.objects.filter(descr=descr):
            typeofbusiness = TypeOfBusiness.objects.get(descr=descr)
        else:
            typeofbusiness = TypeOfBusiness.objects.create(descr=descr,creator=user)    
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    except:
        return server_error("Type could not be created")
     
    data = serial.get_type_data(typeofbusiness)
    return server_data(data,"type")



def subscribe_tag(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "edit")
        tag = Tag.objects.get(id=oid)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    except Tag.DoesNotExist:
        return server_error("Tag with ID "+str(oid) + " not found")
     
    try:
        UserSubscription.objects.create(user=user,tag=tag)
    except UserSubscription.DoesNotExist:
        return server_error("Could not subscribe user. ")
    data = serial.get_tag_data(tag,user)
    return server_data(data)


def unsubscribe_tag(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "edit")
        tag = Tag.objects.get(id=oid)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    except Tag.DoesNotExist:
        return server_error("Tag with ID "+str(oid) + " not found")
     
    try:
        UserSubscription.objects.filter(user=user,tag=tag).delete()
    except :
        return server_error("Error occurred. Could not unsubscribe user.")
    data = serial.get_tag_data(tag,user)
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
        rating = 0
    elif rating > 1:
        rating = 1
    
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
    elif commentType == 'category':
        try:
            btag = BusinessCategory.objects.get(id=oid)
        except:
            return server_error("Category with ID "+str(oid)+ " does not exist")
        comment = CategoryDiscussion.objects.create(user=user,reply_to=replyComment,content=content,businesstag=btag)
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
    
    comment = CategoryDiscussion.objects.create(id=oid,content=content)
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
        rating = 0
    elif rating > 1:
        rating = 1
        
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

    tags = serial.get_tags_data(Tag.objects.all(),user)
    types = serial.get_types_data(TypeOfBusiness.objects.all(),user)
    data = dict()
    data['tags'] = tags;
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
        if 'queryTags' not in request.POST:
            return server_error("Categories did not provide a list")
        categoryList = request.POST.getlist('queryCategories')
        for c in categoryList:
            if Tag.objects.filter(id=c).count() == 0:
                return server_error("Invalid Category provided")
            cat = Tag.objects.get(id=c)
            QueryTag.objects.create(query=query,tag=cat)
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
        BusinessCategory.objects.all().delete()
        Tag.objects.all().delete()
        TypeOfBusiness.objects.all().delete()
    
    prepop.prepop_types(user)
    prepop.prepop_businesses(user)
    prepop.prepop_sorts(user)
    prepop.prepop_queries(user)
    
    prepop.prepop_users()
    prepop.prepop_ratings()
    
    return server_data('Prepop successful')

        
        
