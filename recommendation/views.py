from api.models import Business
from django.conf import settings
from django.contrib.auth.models import User
from django.db import transaction
from recommendation.models import UserFactor, BusinessFactor, Recommendation
from recommendation.nmf import run_nmf_mult_k, get_p_q_best
import logging
import numpy


logger = logging.getLogger(__name__)
def build_predictions():
    k = 42
    Steps = 5000
    Alpha = 0.05
    print("Run Matrix Factorization to get predictions")
    print("Alpha: "+str(Alpha)+"\n")
    print("Steps: "+str(Steps)+"\n")
    print("K: "+str(k)+"\n")
    P, Q, arrID2bid, arrID2uid = get_p_q_best(k, Steps, Alpha)
    print("Done running Matrix Factorization")

    i = 0
    factors = []
    print("Creating user factors and saving them")
    for row in P:
        k = 0
        actualUID = arrID2uid[i]
        #this user hasn't rated anything
        if actualUID == 0:
            continue
        usr = User.objects.get(id=actualUID)
        for col in row:
            uf = UserFactor(user=usr, latentFactor=k, relation=col)
            factors.append(uf)
            k += 1
        i += 1
    UserFactor.objects.bulk_create(factors)

    i = 0
    factors = []
    print("Creating business factors and saving them")
    for row in Q:
        actualBID = arrID2bid[i]
        #this business hasn't been rated
        if actualBID == 0:
            continue
        bus = Business.objects.get(id=actualBID)
        k = 0
        for col in row:

            bf = BusinessFactor(business=bus, latentFactor=k, relation=col)
            factors.append(bf)
            k += 1
        i += 1
    BusinessFactor.objects.bulk_create(factors)
    print(factors)
    Predictions = numpy.dot(P,numpy.transpose(Q))
    if Predictions == 0:
        logger.debug('Predictions == 0. Returning')
        print('Predictions == 0. Returning')
        return
    print(Predictions)
    i = 0
    predictions = []
    for row in Predictions:
        print(len(row))
        j = 0
        bus = Business.objects.get(id=arrID2bid[j])
        for cell in row:
            usr = User.objects.get(id=arrID2uid[i])
            p = Recommendation(business=bus,recommendation=cell,username=usr)
            predictions.append(p)
            j+=1
        i+=1
    Recommendation.objects.bulk_create(predictions)
    transaction.commit();



def find_categories_best_k(k):
    Steps = 5000
    Alpha = 0.05
    #arrID2... are maps from the array indicies to the business and user id
    P, Q, arrID2bid, arrID2uid = get_p_q_best(k, Steps, Alpha)
    zipQ = zip(*Q)
    latentNum = 0
    for l in zipQ:  # {
        maxVal = max(l)
        cutOff = 0.1 * maxVal
        print "  Cutoff is: " + str(cutOff)

        relevantBus = []
        for i in xrange(0, len(l)):
            if l[i] > cutOff:
                # this business is relevant to this latent variable
                # save the id (index is id-1) to use in db look up later
                for elemI in xrange(0, len(relevantBus)):
                    if relevantBus[elemI][1] < l[i]:
                        relevantBus.insert(elemI, [arrID2bid[i], l[i]])
                if len(relevantBus) == 0:
                    relevantBus.append([arrID2bid[i], l[i]])

        otherList = []
        for r in relevantBus:
            print(r[1])
            otherList.append(r[0])
        print("\n")
        print("\n")
        print("\n")

        #print "    " + str(len(relevantBus)) + " businesses past cutoff"
        # For this latent variable, we now have all businesses IDs,
        # print out all of the labels associated with these businesses
        fp = open(settings.RESULTS_DIR + "latent_" + str(latentNum), 'w')
        buses = Business.objects.filter(pk__in=otherList)
        for b in buses:
            keywords = b.keywords.all()
            #print "      " + str(len(keywords)) + " keywords for business"
            nm = b.name
            fp.write(nm.encode("utf8") + "\n")
            fp.write(b.address.encode("utf8") + "\n")
            for k in keywords:
                fp.write(str(k) + "\n")
            fp.write("\n")

        fp.close()
        latentNum = latentNum + 1
    #}


def val_nmf(K, Steps):
    Alpha = 0.05
    run_nmf_mult_k(K, Steps, Alpha)


def validate_production_data():
    K = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 52, 54, 56, 58, 60]
    Steps = 5000
    Alpha = 0.05
    run_nmf_mult_k(K, Steps, Alpha)


#def simple_validate():
#    #pop_test_user_bus_data(numUsers=30, numBusinesses=20)
#    #generate_nmf_test(numFactors=6, density=.3)
#    print("here?")
#    K = [1, 3, 6, 9, 12]
#    Steps = 20000
#    Alpha = 0.001
#    run_nmf_mult_k(K, Steps, Alpha)
