#from allsortz.search import get_all_nearby
import  api.authenticate as auth 
from api.models import Photo, PhotoRating, BusinessDiscussion, \
    CategoryDiscussion, PhotoDiscussion, Discussion, Business, \
    BusinessCategory, CategoryRating, Tag, DiscussionRating, BusinessRating
from api.utility import get_bus_data_ios, get_single_bus_data_ios, ReadJSONError, \
    get_json_post_or_error, get_json_get_or_error
from django.contrib.auth.models import User
from django.http import HttpResponse
from geopy import geocoders, distance
from queries.models import Query, QueryTag
from queries.views import perform_query_from_param, perform_query_from_obj
from wiki.models import Page
import api.photos as photos
import api.prepop as prepop
import api.serializer as serial
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

def server_data(data):
    response_data = dict()
    response_data['success'] = True
    response_data['result'] = data
    return HttpResponse(json.dumps(response_data), mimetype="application/json")    

'''
Code to handle businesses
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
        rating = get_json_get_or_error('rating', request)
        bus = Business.objects.get(id=oid)
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    except: 
        return server_error('Business with id '+str(oid)+'not found')    
        
    if BusinessRating.objects.filter(business=bus,user=user).count() > 0:
        BusinessRating.objects.filter(business=bus,user=user).delete()
    BusinessRating.objects.create(business=bus, rating=rating,user=user) 
    bus.dist = distance.distance(user.current_location,(bus.lat,bus.lon)).miles
    bus_data = get_single_bus_data_ios(bus,user)
    return server_data(bus_data)
    
def add_business(request):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "add")
        bus = Business()
        name=get_json_post_or_error('businessName', request)
        addr=get_json_post_or_error('streetAddr', request)
        city = get_json_post_or_error('businessCity', request)
        state = get_json_post_or_error('businessState', request)
        phone =  get_json_post_or_error('businessPhone', request)
        
        #already exists
        if Business.objects.filter(name=name,address=addr,city=city,state=state).count() ==  0:
            bus = Business(name=name,address=addr,city=city,state=state)
            bus.save()
        elif Business.objects.filter(name=name,address=addr,city=city,state=state).count() > 1: #too many
            Business.objects.filter(name=name,address=addr,city=city,state=state).delete()
            Business.objects.create(name=name,address=addr,city=city,state=state,phone=phone)
        else:
            bus = Business.objects.get(name=name,address=addr,city=city,state=state)                    
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value) 
    bus.dist = distance.distance(user.current_location,(bus.lat,bus.lon)).miles
    bus_data = get_single_bus_data_ios(bus,user)
    return server_data(bus_data)

def edit_business(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "edit")
        bus = Business.objects.get(id = oid)
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)   
    except:
        return server_error("Getting business with id "+str(oid)+" failed")
    
    print(request.POST)
    if 'businessName' in request.POST:
        print('mod that stuff!')
        bus.name = request.POST['businessName']
    
    if 'streetAddr'  in request.POST:
        bus.addr = request.POST['streetAddr']
    
    if 'businessCity'  in request.POST:
        bus.city = request.POST['businessCity']

    if 'businessPhone'  in request.POST:
        return server_error("Phone not implemented")
    
    if 'businessState' in request.POST:
        bus.state = request.POST['businessState']
        
    print(bus.name)
    bus.save()
    print(bus.name)
    bus.dist = distance.distance(user.current_location,(bus.lat,bus.lon)).miles
    bus_data = get_single_bus_data_ios(bus,user)
    return server_data(bus_data)

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
    return server_data("Deletion of business "+str(name)+ " was a success")

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
    print('before serial')
    top_businesses = get_bus_data_ios(businesses ,user)
    print('after serial')

    return server_data(top_businesses)


'''
Code to handle business categories
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

def rate_business_category(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "rate")
        rating = get_json_get_or_error('rating', request)
        category = BusinessCategory.objects.get(id=oid)
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    except: 
        return server_error('Category with id '+str(oid)+'not found')
    
    CategoryRating.objects.create(user=user,tag=category,rating=rating)
    
    data = serial.get_category_data(category,user)
    return server_data(data)

def add_business_category(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "add")
        tagid = get_json_get_or_error('tagID', request)
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
    data = serial.get_category_data(category,user)
    return server_data(data)

def remove_business_category(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "remove")
        BusinessCategory.objects.filter(id=oid).delete()
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    except:
        return server_error('Category with id '+str(oid)+'not found')
    return server_data("Deletion successful")

def get_tags(request):
    try:
        user = auth.authenticate_api_request(request)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    data = serial.get_tags_data(Tag.objects.all(),user)
    return server_data(data)


'''
Code to handle comments
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
        rating = get_json_get_or_error('rating', request)
        comment = Discussion.objects.get(id=oid)
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)
    except: 
        return server_error('Comment with id '+str(oid)+'not found')

    DiscussionRating.objects.create(user=user,rating=rating,comment=comment)
    data = serial.get_comment_data(comment,user)
    return server_data(data)

def add_comment(request):
    try: 
        user = auth.authenticate_api_request(request)
        oid = get_json_get_or_error('commentBaseID', request)  
        commentType = get_json_get_or_error('type', request)  
        content = get_json_post_or_error('commentContent', request)  
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
        content = get_json_post_or_error('commentContent', request)  
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
Code to handle photos
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
        phototype = get_json_get_or_error('type', request)  
        order_by = get_json_get_or_error('order_by', request)  
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
        auth.authorize_user(user,request,"get")
        photo = Photo.objects.get(id=oid)
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)       
    except Photo.DoesNotExist: 
        return server_error('Photo with id '+str(oid)+' not found. Deletion failed')
    
    data = serial.get_photo_data(photo,user)
    return server_data(data)

def rate_photo(request,oid):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "rate")
        rating = get_json_get_or_error('rating', request)
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)


    photo = Photo.objects.get(id=oid)            
    PhotoRating.objects.create(rating = rating,user=user,photo=photo)
    data = serial.get_photo_data(photo,user)
    return server_data(data)
    
 
def add_photo(request):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "add")
        caption = get_json_post_or_error('photoCaption', request)
        title = get_json_post_or_error('photoTitle', request)
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
Code to handle queries
''' 

def get_queries(request):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "get")
        querytype = get_json_get_or_error('type', request)
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
    return server_data(data)
    
    
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
    return server_data(data)
 

    
def add_query(request):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "add")
        query = Query()
        query.name = get_json_post_or_error('queryName',request)
        query.creator = user#get_json_or_error('queryName',request)
        query.proximity = get_json_post_or_error('proximityWeight',request)
        query.price = get_json_post_or_error('priceWeight',request)
        query.value = get_json_post_or_error('valueWeight',request)
        query.score = get_json_post_or_error('scoreWeight',request)
        query.userHasVisited = get_json_post_or_error('userHasVisited',request)
        query.text = get_json_post_or_error('searchText',request)
        query.networked = get_json_post_or_error('networked',request)
        query.deal = get_json_post_or_error('deal',request)
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
 
def prepopulate(request):
    try:
        user = auth.authenticate_api_request(request)
        auth.authorize_user(user, request, "superuser")
       
    except ReadJSONError as e:
        return server_error(e.value)
    except (auth.AuthenticationFailed, auth.AuthorizationError) as e:
        return server_error(e.value)

    if 'clear' in request.GET:
        Business.objects.all().delete()
        Page.objects.all().delete()
        Photo.objects.all().delete()
        BusinessCategory.objects.all().delete()
        Tag.objects.all().delete()
    
    prepop.prepop_businesses(user)
    prepop.prepop_sorts(user)
    prepop.prepop_queries(user)
    return server_data('Prepop successful')

        
        
