from django.conf import settings
from django.contrib.auth.models import User
from api.models import Business, BusinessRating
from recommendation.normalization import getNormFactors
import copy

import math
import numpy
import random
import sys
sys.path.append(settings.CLIB_DIR)
import fastnmf
import time



def get_folds(allBusinessRatings):
    folds = [[], [], [], [], []]
    numBusinessRatings = len(allBusinessRatings)
#    random.seed(666)
    fld = []
    for i in range(0, numBusinessRatings):
        fld.append(i % 5)
    random.shuffle(fld)

    for i in range(0, numBusinessRatings):
        ind = fld[i]
        folds[ind].append(allBusinessRatings.pop())
    return(folds)


def get_outfold_data(folds, thisFold, fp):
    outFoldDat = []
    for f in range(0, 5):
        if f != thisFold:
            for s in folds[f]:
                fp.write(str(s) + "\n")
                outFoldDat.append(s)

    fp.write("verify....\n\n\n\n\n\n\n\n")
    for v in outFoldDat:
        fp.write(str(v) + "\n")
    return outFoldDat


def get_p_q_best(k, steps, alpha):
    N = User.objects.count()
    M = Business.objects.count()
    print("Get BusinessRatings from DB")
    allBusinessRatings = BusinessRating.objects.all()
    print("Moving data to an array...")

    print(N)

    allRatMatrix, bid2arrID, uid2arrID, arrID2bid, arrID2uid = getAllRatMatrix(N, M, allBusinessRatings)
    print(len(allRatMatrix))
    print("Running nmf...")
    nP, nQ = run_nmf_internal(allRatMatrix, N, M, k, steps, alpha, 0)

    return nP, nQ, arrID2bid, arrID2uid


def getAllRatMatrix(N, M, allBusinessRatings):
    arrID2uid = numpy.zeros(N)
    arrID2bid = numpy.zeros(M)
    bid2arrID = dict()
    uid2arrID = dict()
    allRatMatrix = []
    i = 0
    j = 0
    c = 0
    for r in allBusinessRatings:
        if c % 100 == 0:
            print(c)
        c += 1
        NormFactor = getNormFactors(r.user.id, r.business.id)

        #Need to keep a mapping from the position in the
        # array to the actual business and user ID

        #arr2...  keeps mapping of array position to actual IDs in database
        #uid2 and bid2 keeps mapping of database IDs to the array IDS
        #this is used to get the normalization factor and can be used
        # later to get back recommendations

        bPos = 0
        if r.business.id in bid2arrID:
            bPos = bid2arrID[r.business.id]
        else:
            bPos = j
            bid2arrID[r.business.id] = bPos
            arrID2bid[j] = r.business.id
            j += 1

        uPos = 0
        if r.user.id in uid2arrID:
            uPos = uid2arrID[r.user.id]
        else:
            uPos = i
            uid2arrID[r.user.id] = uPos
            arrID2uid[i] = r.user.id
            i += 1
        #        fp2.write("BusinessRating is " + str(r.BusinessRating) + " after normalization " +  str(float(r.BusinessRating - NormFactor))+ "\n")

        allRatMatrix.append([uPos, bPos, float(r.BusinessRating - NormFactor)])
    return allRatMatrix, bid2arrID, uid2arrID, arrID2bid, arrID2uid


def run_nmf_mult_k(K, Steps, Alpha):
    N = User.objects.count()
    M = Business.objects.count()
    allBusinessRatings = BusinessRating.objects.all()
    user_BusinessRating_threshold = 0
    bus_BusinessRating_threshold =0
    resultFile = settings.RESULTS_DIR + "u" + str(user_BusinessRating_threshold) + "_b" + str(bus_BusinessRating_threshold) + "_s" + str(Steps) + "_k" + str(K[0]) + "-" + str(K[len(K) - 1])
    predictionFile = settings.RESULTS_DIR + "predictions_" + "u" + str(user_BusinessRating_threshold) + "_b" + str(bus_BusinessRating_threshold) + "_s" + str(Steps) + "_k" + str(K[0]) + "-" + str(K[len(K) - 1])
    print(resultFile)
    fp = open(resultFile, "w")
    pred_fp = open(predictionFile, "w")
    pred_fp.write("#K, f, Difference, Actual, Predicted")
    fp.write("#NumUsers = " + str(N + 1) + '\n')
    fp.write("#NumBusinesses = " + str(M + 1) + '\n')
    fp.write("#UserThresh = " + str(user_BusinessRating_threshold) + '\n')
    fp.write("#BusinessThresh = " + str(bus_BusinessRating_threshold) + '\n')
    fp.write("#NumBusinessRatings = " + str(allBusinessRatings.count()) + '\n')
    fp.write("#Steps = " + str(Steps) + '\n')
    fp.write("#Alpha = " + str(Alpha) + '\n')
    fp.write("#TimeStart = " + str(time.asctime()) + '\n')
    fp.write('#\n')
    fp.write('#K, AvgRSSRounded, AvgDistRounded, AvgRSSFloat, AvgDistFloat\n')
    fp.flush()
    print("Moving data to an array...")
    fp2 = open("/tmp/debug-BusinessRatings.txt", "w")
    allRatMatrix, bid2arrID, uid2arrID, arrID2bid, arrID2uid = getAllRatMatrix(N,M,allBusinessRatings)
    print("GeneBusinessRating Folds...")
    folds = get_folds(allRatMatrix)
    print("Fold Generation Complete...")
    for k in K:
        print("Running on K=" + str(k) + " Starting at time= " + time.asctime())
        sumDistRounded = 0
        sumRSSRounded = 0
        sumDistFloat = 0.0
        sumRSSFloat = 0.0
        ctr = 0
        for f in range(0, 5):
            outFold = []
            for iterF in range(0, 5):
                if iterF != f:
                    for subelement in folds[iterF]:
                        outFold.append((subelement))
        inFold = copy.deepcopy(folds[f])

        time_before = time.clock()
        nP, nQ = run_nmf_internal(outFold,N,M,k, Steps, Alpha, fp=fp2)
        del outFold
        elapsed = time.clock() - time_before;
        print("\tK="+str(k)+" Fold=" +str(f)+" TimeElapsed="+ str(elapsed/60) + " minutes")
        
        #for keeping track of rss, average distance for floats and rounded
        distFloat = 0.0
        rssFloat = 0.0
        rssRounded = 0
        distRounded = 0
        inFoldLen = len(inFold)
        for r in inFold:
            uid = r[0] 
            bid = r[1] 
           
            NormFactor = getNormFactors(arrID2uid[uid], arrID2bid[bid])
            r[2] = r[2] + NormFactor
            prediction = numpy.dot(nP[uid],nQ[bid]) + NormFactor
            
            roundR = round(r[2])
            roundP = round(prediction)
            
            floatR = float(r[2])
            floatP = float(prediction)
            if r[2] > 4:
                floatR = 4.0
                roundR = 4;
            elif r[2] < 1:
                roundR = 1;
                floatR = 1.0
                
            if prediction > 4:
                roundP = 4
                floatP = 4.0
            elif prediction < 1:
                roundP = 1
                floatP = 1.0


            #print("Username " + str(r.username))
            #print("Business " + str(r.business.name))
            #print("BusinessRating " + str(r.BusinessRating))
            #print("Prediction " + str(prediction))
                  
            rssFloat +=    math.pow(abs(floatP - floatR),2)
            distFloat +=   abs(floatP - floatR)
            rssRounded +=  math.pow(abs(roundP - roundR),2)
            distRounded += abs(roundP - roundR)
            #pred_fp.write(str(abs(floatP - floatR)) + ", " + str(floatR) + ", " + str(floatP) + ", " +str(k) + ", " + str(f) +  '\n');
            pred_fp.write(str(abs(floatP-floatR)) + " " + str(floatR) + " " + str(floatP) + " " + '\n');
            if ctr % 1000 == 0:
                pred_fp.flush()
            ctr += 1
        sumDistRounded +=  distRounded / inFoldLen
        sumRSSRounded += rssRounded/ inFoldLen
        sumDistFloat +=  distFloat / inFoldLen
        sumRSSFloat +=  rssFloat/ inFoldLen
        print("\t\t RSS_float="  + str(rssFloat/inFoldLen)   + " Distance_float=" + str(distFloat/inFoldLen))
        print("\t\t RSS_rounded="+ str(rssRounded/inFoldLen) + " Distance_rounded=" + str(distRounded/inFoldLen))
    result_1 = str(sumRSSRounded/5)+ ", " + str(sumDistRounded/5) 
    result_2 = str(sumRSSFloat/5)+ ", " + str(sumDistFloat/5) 
    fp.write(str(k) + ", " + result_1 + ", " + result_2 + '\n')
    fp.flush()
    print("\n\n\nK="+str(k) + "Rounded: " + result_1 + " Float: " + result_2)
    
    fp.write("#TimeEnd = "+str(time.asctime())+'\n')
    pred_fp.flush()
    fp.flush()
    fp.close()
    fp2.close()
    pred_fp.close()


def run_nmf_internal(R,N,M, K, Steps, Alpha, fp):
    # P = numpy.random.rand(N,K)
    #Q = numpy.random.rand(M,K)    
    P=[]
    Q=[]    
#    for r in R:
#      fp.write(str(r[2])+"\n")
    #print(R)
    #run_nmf_c(list& BusinessRatings, int N, int M, int K, int p_Steps, double p_Alpha, list& p_P, list &p_Q)
    fastnmf.run_nmf_from_python(R,N,M,K, Steps, Alpha, P,Q)
    return P, Q
    #nR = numpy.dot(nP, nQ.T)
    #return nR
