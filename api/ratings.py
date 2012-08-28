'''
Created on Aug 1, 2012

@author: zouf
#'''
#from django.db.models.aggregates import Sum, Count
#import ios_interface 

from api.models import PhotoRating, DiscussionRating, BusinessRating, \
    BusinessTopicRating
from django.db.models.aggregates import Count, Sum, Avg

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
    
def getBusTopicRatings(bustopic):
    if BusinessTopicRating.objects.all().count() == 0:
        return 0
    

    ratingFilter = BusinessTopicRating.objects.filter(businesstopic=bustopic).aggregate(Avg('rating'))
    avg = ratingFilter['rating__avg']
    #numNeg = DiscussionRating.objects.filter(rating=0).count()
    return avg

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
    
