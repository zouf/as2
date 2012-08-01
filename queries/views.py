'''
Created on Jul 31, 2012

@author: zouf
'''

from django.contrib.gis.geos.factory import fromstr
from django.contrib.gis.measure import D
from api.models import Business, BusinessRating
from recommendation.normalization import getBusAvg

MAX_RATING = 4.0
DISTANCE = 3



def order_by_BusinessRating(b1,b2):
    
    if b1['BusinessRating'] and b2['BusinessRating']:
        return cmp(b1['BusinessRating'], b2['BusinessRating'])
    elif b1['BusinessRating']:
        return cmp(b1['BusinessRating'], b2['recommendation'])
    elif b2['BusinessRating']:
        return cmp(b1['recommendation'],b2['BusinessRating'])
    else:     
        return cmp(b1['recommendation'], b2['recommendation'])
    
#def order_by_weight(b1,b2):
#
#    if b1['weight'] and b2['weight']:
#        return cmp(b2['weight'], b1['weight'])
#    elif b1['weight']:
#        return cmp(b2['weight'], b1['weight'])
#    elif b2['weight']:
#        return cmp(b2['weight'],b1['weight'])
#    else:     
#        return cmp(b2['weight'], b1['weight'])

def order_by_weight(b1,b2):
    if b1.weight and b2.weight:
        return cmp(b2.weight, b1.weight)
    elif b1.weight:
        return cmp(b2.weight, b1.weight)
    elif b2.weight:
        return cmp(b2.weight,b1.weight)
    else:     
        return cmp(b2.weight, b1.weight)

def get_nearby_businesses(mylat,mylng,distance=3):

    #current_pg_point = "point '({:.5f}, {:.5f})'".format(mylng, mylat)
    all_buses = Business.objects.all()
    pnt = fromstr('POINT('+str(mylng)+ ' '+str(mylat)+')', srid=4326)
    nearby_buses =  all_buses.filter(geom__distance_lte=(pnt, D(mi=DISTANCE)))
    with_distances = []
    print('before')
    for b in nearby_buses.distance(pnt):
        with_distances.append(b)
    print('after')
    return with_distances



def perform_query_from_obj(user,location,query):
    return query_internal(user=user,location=location,score=query.score,proximity=query.proximity, price=query.price, value=query.value, 
                          text=query.text,tags=query.tags,visited=query.visited,deal=query.deal,networked=query.networked)

def perform_query_from_param(user,location,weights,text,tags,visited = None, deal=None, networked=None):
    sw = weights['sw']
    dw = weights['dw']
    pw = weights['pw']
    vw = weights['vw']
    
    return query_internal(user=user,location=location,score=sw,proximity=dw, price=pw, value=vw, 
                          text=text,tags=tags,visited=visited,deal=deal,networked=networked)
    
def distance_weight(user,location,b):   
    return (DISTANCE - b.distance.mi) / DISTANCE

  
def score_weight(user,b):
    if user and BusinessRating.objects.filter(user=user, business=b).count() > 0:
        try:
            score = BusinessRating.objects.get(user=user, business=b).BusinessRating
        except BusinessRating.MultipleObjectsReturned:
            score = BusinessRating.objects.filter(user=user,business=b)[0].BusinessRating
    else:
        #TODO GET RECOMMENDATION HERE!!!!!!
        score =  getBusAvg(b.id)  
    return float(score) / float(MAX_RATING)
#XXX TODO IMPLEMENT
def price_weight(user,b):
    return 1

#XXX TODO IMPLEMENT
def value_weight(user,b):
    return 1



def query_internal(user,location,score,proximity,value,price,text,tags,visited,deal,networked):
    all_nearby = get_nearby_businesses(location[0],location[1],distance=DISTANCE)
   
    new_list = []
    for b in all_nearby:
        scoreWeight = 1.0#score_weight(user,b) 
        proxWeight = distance_weight(user,location,b)
        priceWeight = price_weight(user,b) #TODO GET PRICE
        valueWeight = value_weight(user,b) #TODO GET PRICE
        b.weight = scoreWeight + proxWeight + priceWeight + valueWeight
        new_list.append(b)
    new_list = sorted(new_list,cmp=order_by_weight) 
    return new_list
        
    
    
    
    
    
    
    