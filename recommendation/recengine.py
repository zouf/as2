#from celery.execute import send_task
from api.authenticate import get_default_user
from api.models import BusinessRating, Business, UserTopic, BusinessTopicRating, \
    BusinessTopic, Topic
from api.ratings import getBusAverageRating
from cProfile import runctx
from django.contrib.auth.models import User
from django.db.models.aggregates import Count, Sum, Avg
from recommendation.models import UserFactor, BusinessFactor, Recommendation
from recommendation.normalization import getNormFactors
import logging
import numpy as np


logger = logging.getLogger(__name__)

def get_recommendation_by_topic(business,user):
    logger.debug('Getting recommendation for ' + str(business))
    try:
        r = Recommendation.objects.get(business=business,user=user)
        return r.recommendation
    except:
        (runSum, runCt) = get_node_average(business,Topic.objects.get(descr='Main'),user)
        if runCt > 0:
            avg = float(runSum)/float(runCt)
            logger.debug('AVG for business ' + str(business) + ' is ' + str(avg))
            
            try:
                rec = Recommendation.objects.get(user=user,business=business).delete()
                rec.recommendation = avg;
                rec.save()
            except:
                Recommendation.objects.create(user=user,business=business,recommendation=avg)
            return avg
        return 0
            
        
    

#get average over whole tree
#We're treating the children and the parent with the same weight. This way leaves do not lose importance higher up in the tree
def get_node_average(business,topic,user):
    btset = BusinessTopic.objects.select_related('topic').filter(business=business,topic=topic)
    
    #for this node in the tree
    thisAvg= 0
    if btset.count()> 0:
        ratingFilter = BusinessTopicRating.objects.filter(businesstopic=btset[0], rating__range=["0", "4"])
        countFilter = ratingFilter.aggregate(Count('rating'))
        sumFilter = ratingFilter.aggregate(Sum('rating'))
        if countFilter['rating__count'] > 0:
            thisAvg =  sumFilter['rating__sum'] / countFilter['rating__count']
            #print('business' + str(business) + " topic " + str(topic)+ " average " + str(thisAvg))

            thisCount = 1
        else:
            thisAvg = 0
            thisCount = 0
    else:
        thisAvg = 0
        thisCount = 0
        
    #for all the children
    for edge in topic.children.all():
        (childSum, childCount) = get_node_average(business,edge.to_node,user)
        #print(str(childSum) + ' : childSum')
        #print(str(childCount) + ' : childCount')

        if childCount > 0:
            childAverage = childSum / childCount
            #print('Average for topic ' + str(edge.to_node) + ' is ' + str(childAverage))
            thisAvg += childAverage
            thisCount += 1
        
    return (thisAvg, thisCount)
        
    
    
       
def build_recommendations_by_topic():
    print('Deleting all predictions and rebuilding recommendations')
    Recommendation.objects.all().delete()
    for b in Business.objects.all():
        u = get_default_user()
        print('getting recommendationg for business ' + str(b) + ' for user ' + str(u))
        logger.debug('getting recommendationg for business ' + str(b) + ' for user ' + str(u))
        get_recommendation_by_topic(b,u)
    

def get_best_current_recommendation(business, user):

        #  my.factors <- me %*% m@fit@W
        #  barplot(my.factors)
        #  my.prediction <- my.factors %*% t(m@fit@W)
        #  items$title[order(my.prediction, decreasing=T)[1:10]]
        try:
            r = Recommendation.objects.get(user=user,business=business)
            return r.recommendation
        except:
            pass

        NumFactors = 42
        print(business.id)
        normalizationFactor = getNormFactors(user.id, business.id)
        businessAverage = getBusAverageRating(business)
        
        ufset = UserFactor.objects.filter(user=user)
        myFactors = np.zeros(NumFactors)

        for uf in ufset:
            factor = uf.latentFactor
            relation = uf.relation
            myFactors[factor] = relation

        if ufset.count() == 0:
            logger.debug("Getting business average since the user has no factors")
            print("Getting business average since the user has no factors")
            Recommendation.objects.create(user=user,business=business,recommendation=businessAverage)
            return businessAverage

        bfset = BusinessFactor.objects.filter(business=business)
        busFactors = np.zeros(NumFactors)
        for bf in bfset:
            factor = bf.latentFactor
            relation = bf.relation
            busFactors[factor] = relation
        
        if bfset.count() == 0:
            logger.debug("Getting business average since the business has no factors")
            print("Getting business average since the business has no factors")
            #cache the recommendations        
            Recommendation.objects.create(user=user,business=business,recommendation=businessAverage)
            return businessAverage 

        logger.debug("Getting recommendation from actual predictions")
        print("Getting recommendation from actual predictions")

        prediction = np.dot(myFactors, busFactors) + normalizationFactor
        rec = round(prediction * 2) / 2  # round to half

        if rec > 4.0:
            rec = 4.0
        elif rec < 1.0:
            rec = 1.0
        
        
        return rec

#
#class RecEngine:
#    best_recommendation_table = dict()
#    workerSpawned = False
#
#    def setBestRecTable(self, newTable):
#        print "Before"
#        self.best_recommendation_table = newTable
#        print self.best_recommendation_table
#        print "After"
#
#    def getBestRecTable(self):
#        return self.best_recommendation_table
#
##    def spawn_worker_task(self):
##        if not self.workerSpawned:
##            send_task("tasks.build_recommendations")
##            self.workerSpawned = True
#
#    def get_top_BusinessRatings(self, user,  numToPrint):
#        NumFactors = 42
#        ufset = UserFactor.objects.filter(user=user)
#        myFactors = np.zeros(NumFactors)
#
#        ratFilter = BusinessRating.objects.filter(username=user)
#
#        id2bus = {}
#        ct = 0
#        for bus in Business.objects.all():
#            id2bus[ct] = bus
#            ct = ct + 1
#
#        busrelations = np.zeros((Business.objects.all().count(), NumFactors))
#        for bc in id2bus.items():
#            bfset = BusinessFactor.objects.filter(business=bc[1])
#            for bf in bfset:
#                busrelations[bc[0], bf.latentFactor] = bf.relation
#
#        myFactors = np.zeros(NumFactors)
#        for k in range(0, NumFactors):
#            for r in ratFilter:
#                bfset = BusinessFactor.objects.filter(business=r.business).filter(latentFactor=k)
#                for bf in bfset:
#                    relation = bf.relation
#                    myFactors[k] += relation * r.BusinessRating
#
#        myBusinessRatings = np.dot(myFactors, np.transpose(busrelations))
#
#        dtype = [('index', int), ('BusinessRating', float)]
#
#        pairedBusinessRatings = []
#        for i in range(Business.objects.all().count()):
#            pairedBusinessRatings.append((i, myBusinessRatings[i]))
#
#        myPR = np.array(pairedBusinessRatings, dtype)
#
#        print(myPR)
#        myPR = np.sort(myPR, order=['BusinessRating'])
#        print(myPR)
#
#        top10 = []
#
#        end = 0
#        if len(myPR) < numToPrint:
#            end = len(myPR)
#        else:
#            end = numToPrint
#        for i in range(0, end):
#            #dont append stuff user has already rated
#            bus = id2bus[myPR[len(myPR) - i - 1]['index']]
#            queryrat = BusinessRating.objects.filter(username=user, business=bus)
#            if queryrat.count() == 0:  # hasn't been a BusinessRating yet
#                top10.append(id2bus[myPR[len(myPR) - i - 1]['index']])
#
#        return top10
#
#    # CALLED BY THE VIEW TO GET THE BES    T CURRENT RECOMMENDATION
#    
