'''
Created on Aug 1, 2012

@author: zouf
#'''
#from django.db.models.aggregates import Sum, Count
#import ios_interface 

from api.models import PhotoRating, DiscussionRating, BusinessRating, \
    BusinessTopicRating, UserCache
from django.db.models.aggregates import Count, Sum, Avg
import logging

logger = logging.getLogger(__name__)
HATE = 0
NEUTRAL = 1
LIKE = 2
LOVE = 3

def getCommentRatings(discussion):
    ratingFilter = DiscussionRating.objects.filter(discussion=discussion, rating__range=["1", "5"])
    ratingFilter = ratingFilter.aggregate(Count('rating'))
    numPos = ratingFilter['rating__count']
    numNeg = DiscussionRating.objects.filter(rating=0).count()
    return [numPos, numNeg]
    

def getPhotoRatings(photo):
    ratingFilter = PhotoRating.objects.filter(photo=photo, rating__range=["1", "5"])
    ratingFilter = ratingFilter.aggregate(Count('rating'))
    numPos = ratingFilter['rating__count']
    numNeg = DiscussionRating.objects.filter(rating=0).count()
    return [numPos, numNeg]



def getGlobalAverage():
    res = BusinessRating.objects.all().aggregate(Sum('rating'), Count('rating'))
    count = res['rating__count']
    if count != 0:
        return (float(res['rating__sum']) / float(res['rating__count']))
    return 0

def getBusAverageRating(b):
    #       if bid in businessCache:
    #         return businessCache[bid]
    ratingFilter = BusinessRating.objects.filter(business=b).aggregate(Sum('rating'), Count('rating'))
    sumRating = ratingFilter['rating__sum']
    countRating = ratingFilter['rating__count']

    avg = 0
    K = 5  # calcStdev()
    if countRating != 0:
        glb = getGlobalAverage()
        avg = (glb * K + float(sumRating)) / (K + float(countRating))  # ci_lowerbound(sumRating,countRating)
    #       businessCache[bid] = avg
    return avg
    #b = Business.objects.get(id=bid)
    #return b.average_rating


def getAverageForTopics(b,topics):
    return 0

def getBusinessRatings(b):
    hates = BusinessRating.objects.filter(rating=HATE).count()
    neutrals = BusinessRating.objects.filter(rating=NEUTRAL).count()
    likes = BusinessRating.objects.filter(rating=LIKE).count()
    loves = BusinessRating.objects.filter(rating=LOVE).count()
    avg = getBusAverageRating(b)
    return [hates,neutrals,likes,loves,avg]

def get_bustopic_adjective(bustopic, avg):
    if avg < .3:
        return 'Avoid it!'
    elif avg < .45:
        return 'Not so good.'
    elif avg < .55:
        return 'Decent'
    elif avg < .7:
        return 'Good!'
    else:
        return 'Stunning!'


def get_avg_bustopic_rating(bustopic):
    try:
        avg = bustopic.bustopicrating.rating__avg
        return ' ALREADY ON MODEL'
        return avg
    except:
        try:
            ratingFilter = BusinessTopicRating.objects.filter(businesstopic=bustopic).aggregate(Avg('rating'))
            avg= ratingFilter['rating__avg']
            print ' AVG IS ' + str(avg)
            if avg is None:
                return 0
            else:
                return avg
        except Exception as e:
            logger.debug('Exception ' + str(e))
            return 0

def get_user_bustopic_rating(bustopic,user):
    try:
        r = BusinessTopicRating.objects.get(businesstopic=bustopic,user=user).rating
        if r >= 1:
            r = 1
        elif r <= 0:
            r = 0
        return r
    except:
        return -1
    
    
def rate_businesstopic_internal(bustopic,rating,user):
    if rating < -1:
        rating = -1.0
    elif rating > 1:
        rating = 1.0
    
    logger.debug('blarg')
    #remove existing rating
    if BusinessTopicRating.objects.filter(businesstopic=bustopic,user=user).count() > 0:
        BusinessTopicRating.objects.filter(businesstopic=bustopic,user=user).delete()
    logger.debug('CREATING RAITNG FOR '
           +str(bustopic))
    UserCache.objects.filter(business=bustopic.business,user=user).delete()
    BusinessTopicRating.objects.create(businesstopic=bustopic, rating=rating,user=user) 
    
def rate_comment_internal(comment,rating,user):
    if rating < -1:
        rating = -1.0
    elif rating > 1:
        rating = 1.0
    
    
    #remove existing rating
    
    if DiscussionRating.objects.filter(discussion=comment,user=user).count() > 0:
        DiscussionRating.objects.filter(discussion=comment,user=user).delete()
    print('creating a rating for discussions ' + str(comment.id) + ' ' + str(rating)) 
    try:

        DiscussionRating.objects.create(discussion=comment, rating=rating,user=user) 
    except Exception as e:
        print(str(e))
        
    
