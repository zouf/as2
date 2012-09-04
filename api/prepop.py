'''
Created on Apr 2, 2012

@author: Joey
'''
from api.business_operations import add_business_server
from api.models import Topic, Business, BusinessType, BusinessRating, \
    BusinessMeta, Type, BusinessTopicRating, BusinessTopic, UserTopic
from api.photos import add_photo_by_url
from api.topic_operations import add_topic_to_bus, add_topic
from as2 import settings
from django.contrib.auth.models import User
from gettext import lngettext
from numpy.oldnumeric.random_array import binomial
from queries.models import Query
from recommendation.models import Recommendation
from wiki.models import Page
import csv
import json
import logging
import random



logger = logging.getLogger(__name__)

cuisineLabels =  ["All cuisines","Afghan","African","American","Armenian","Asian","Australian","Bagels, Hotdog, Pretzels","Bakery","Bangladeshi","Barbecue","Beverages, Smoothies, Fruit Salads","Brazilian","Cafe, Coffee, Tea","Cajun","Caribbean","Chicken","Chilean","Chinese","Chinese, Japanese","Continental","Creole","Czech","Delicatessen","Donuts","Eastern European","Filipino","French","German","Greek","Hamburgers","Hawaiian, Polynesian","Ice Cream, Gelato, Yogurt, Ices","Indian","Indonesian","Iranian","Irish, English","Italian","Japanese","Jewish, Kosher","Korean","Latin","Mediterranean","Mexican","Middle Eastern","North African","Other","Pakistani","Pancakes, Waffles","Peruvian","Pizza","Polish","Portuguese","Russian","Sandwiches, Soups, Salads","Scandinavian","Seafood","Soul Food","Southwestern","Spanish","Steak","Tapas","Tex-Mex","Thai","Turkish","Vegetarian","Vietnamese, Cambodian, Malaysia"]
cuisineCodes = [-1,1,2,3,4,5,6,500,8,9,10,503,13,14,15,17,18,19,20,22,23,24,26,27,29,30,34,35,37,38,39,505,43,44,45,46,501,48,49,50,52,53,54,55,56,504,99,59,60,61,62,64,66,67,502,71,72,73,76,77,78,80,81,82,83,84,28]
gradeCats = ["A", "B", "C", "NotYet", "NoGrade", "GradePend"]
violationCrit = {"02A":1,"02B":1,"02C":1,"02D":1,"02E":1,"02F":1,"02G":1,"02H":1,"02I":1,"02J":1,"03A":1,"03B":1,"03C":1,"03D":1,"03E":1,"03F":1,"03G":1,"04A":1,"04B":1,"04C":1,"04D":1,"04E":1,"04F":1,"04G":1,"04H":1,"04I":1,"04J":1,"04K":1,"04L":1,"04M":1,"04N":1,"04O":1,"05A":1,"05B":1,"05C":1,"05D":1,"05E":1,"05F":1,"05G":1,"05H":1,"05I":1,"06A":1,"06B":1,"06C":1,"06D":1,"06E":1,"06F":1,"06G":1,"06H":1,"06I":1,"07A":1,"08A":0,"08B":0,"08C":0,"09A":0,"09B":0,"09C":0,"10A":0,"10B":0,"10C":0,"10D":0,"10E":0,"10F":0,"10G":0,"10H":0,"10I":0,"10J":0,"15A":0,"15B":0,"15C":0,"15D":0,"15E":0,"15F":0,"15G":0,"15H":0,"15I":0,"15J":0,"15K":0,"15L":0,"15M":0,"15N":0,"15O":0,"15P":0,"15Q":0,"15R":0,"15S":1,"15T":1,"16A":0,"16B":0,"16C":0,"16D":0,"16E":0,"16F":0,"18A":0,"18B":0,"18C":0,"18D":0,"18E":0,"18F":0,"18G":0,"18H":0,"20A":0,"20B":0,"20C":0,"20D":0,"20E":0,"20F":0,"22A":1,"22B":0,"22C":1,"22E":1,"99B":0}
violationDesc = {"02A":"Food not cooked to required minimum temperature.","02B":"Hot food item not held at or above 140&#186; F.","02C":"Hot food item that has been cooked and refrigerated is being held for service without first being reheated to 1 65&#186; F or above within 2 hours.","02D":"Precooked potentially hazardous food from commercial food processing establishment that is supposed to be heated, but is not heated to 140&#186; F within 2 hours.","02E":"Whole frozen poultry or poultry breasts, other than a single portion, is being cooked frozen or partially thawed.","02F":"Meat, fish or molluscan shellfish served raw or undercooked without prior notification to customer.","02G":"Cold food item held above 41&#186; F (smoked fish and reduced oxygen packaged foods above 38 &#186;F) except during necessary preparation.","02H":"Food not cooled by an approved method whereby the internal product temperature is reduced from 140&#186; F to 70&#186; F or less within 2 hours, and from 70&#186; F to 41&#186; F or less within 4 additional hours.","02I":"Food prepared from ingredients at ambient temperature not cooled to 41&#186; F or below within 4 hours.","02J":"Reduced oxygen packaged (ROP) foods not cooled by an approved method whereby the internal food temperature is reduced to 38&#186; F within two hours of cooking and if necessary further cooled to a temperature of 34&#186; F within six hours of reaching 38&#186; F.","03A":"Food from unapproved or unknown source or home canned. Reduced oxygen packaged (ROP) fish not frozen before processing; or ROP foods prepared on premises transported to another site.","03B":"Shellfish not from approved source, improperly tagged/labeled; tags not retained for 90 days.","03C":"Eggs found dirty/cracked; liquid, frozen or powdered eggs not pasteurized.","03D":"Canned food product observed swollen, leaking or rusted, and not segregated from other consumable food items .","03E":"Potable water supply inadequate. Water or ice not potable or from unapproved source.  Cross connection in potable water supply system observed.","03F":"Unpasteurized milk or milk product present.","03G":"Raw food not properly washed prior to serving.","04A":"Food Protection Certificate not held by supervisor of food operations.","04B":"Food worker prepares food or handles utensil when ill with a disease transmissible by food, or have exposed infected cut or burn on hand.","04C":"Food worker does not use proper utensil to eliminate bare hand contact with food that will not receive adequate additional heat treatment.","04D":"Food worker does not wash hands thoroughly after using the toilet, coughing, sneezing, smoking, eating, preparing raw foods or otherwise contaminating hands.","04E":"Toxic chemical improperly labeled, stored or used such that food contamination may occur.","04F":"Food, food preparation area, food storage area, area used by employees or patrons, contaminated by sewage or liquid waste.","04G":"Unprotected potentially hazardous food re-served.","04H":"Raw, cooked or prepared food is adulterated, contaminated, cross-contaminated, or not discarded in accordance with HACCP plan.","04I":"Unprotected food re-served.","04J":"Appropriately scaled metal stem-type thermometer or thermocouple not provided or used to evaluate temperatures of potentially hazardous foods during cooking, cooling, reheating and holding.","04K":"Evidence of rats or live rats present in facility&#39;s food and/or non-food areas.","04L":"Evidence of mice or live mice present in facility&#39;s food and/or non-food areas.","04M":"Live roaches present in facility&#39;s food and/or non-food areas.","04N":"Filth flies or food/refuse/sewage-associated (FRSA) flies present in facility's food and/or non-food areas. Filth flies include house flies, little house flies, blow flies, bottle flies and flesh flies. Food/refuse/sewage-associated flies include fruit flies, drain flies and Phorid flies.","04O":"Live animals other than fish in tank or service animal present in facility&#39;s food and/or non-food areas.","05A":"Sewage disposal system improper or unapproved.","05B":"Harmful, noxious gas or vapor detected. CO ~1 3 ppm.","05C":"Food contact surface improperly constructed or located. Unacceptable material used.","05D":"Hand washing facility not provided in or near food preparation area and toilet room. Hot and cold running water at adequate pressure to enable cleanliness of employees not provided at facility. Soap and an acceptable hand-drying device not provided. ","05E":"Toilet facility not provided for employees or for patrons when required.","05F":"Insufficient or no refrigerated or hot holding equipment to keep potentially hazardous foods at required temperatures.","05G":"Properly enclosed service/maintenance area not provided.","05H":"No facilities available to wash, rinse and sanitize utensils and/or equipment.","05I":"Refrigeration used to implement HACCP plan not equipped with an electronic system that continuously monitors time and temperature.","06A":"Personal cleanliness inadequate. Outer garment soiled with possible contaminant.  Effective hair restraint not worn in an area where food is prepared.","06B":"Tobacco use, eating, or drinking from open container in food preparation, food storage or dishwashing area observed.","06C":"Food not protected from potential source of contamination during storage, preparation, transportation, display or service.","06D":"Food contact surface not properly washed, rinsed and sanitized after each use and following any activity when contamination may have occurred.","06E":"Sanitized equipment or utensil, including in-use food dispensing utensil, improperly used or stored.","06F":"Wiping cloths soiled or not stored in sanitizing solution.","06G":"HACCP plan not approved or approved HACCP plan not maintained on premises.","06H":"Records and logs not maintained to demonstrate that HACCP plan has been properly implemented.","06I":"Food not labeled in accordance with HACCP plan.","07A":"Duties of an officer of the Department interfered with or obstructed.","08A":"Facility not vermin proof. Harborage or conditions conducive to attracting vermin to the premises and/or allowing vermin to exist.","08B":"Covered garbage receptacle not provided or inadequate, except that garbage receptacle may be uncovered during active use. Garbage storage area not properly constructed or maintained; grinder or compactor dirty.","08C":"Pesticide use not in accordance with label or applicable laws. Prohibited chemical used/stored. Open bait station used.","09A":"Canned food product observed dented and not segregated from other consumable food items.","09B":"Thawing procedures improper.","09C":"Food contact surface not properly maintained.","10A":"Toilet facility not maintained and provided with toilet paper, waste receptacle and self-closing door.","10B":"Plumbing not properly installed or maintained; anti-siphonage or backflow prevention device not provided where required; equipment or floor not properly drained; sewage disposal system in disrepair or not functioning properly.","10C":"Lighting inadequate; permanent lighting not provided in food preparation areas, ware washing areas, and storage rooms.","10D":"Mechanical or natural ventilation system not provided, improperly installed, in disrepair and/or fails to prevent excessive build-up of grease, heat, steam condensation vapors, odors, smoke, and fumes.","10E":"Accurate thermometer not provided in refrigerated or hot holding equipment.","10F":"Non-food contact surface improperly constructed. Unacceptable material used. Non-food contact surface or equipment improperly maintained and/or not properly sealed, raised, spaced or movable to allow accessibility for cleaning on all sides, above and underneath the unit.","10G":"Food service operation occurring in room used as living or sleeping quarters.","10H":"Proper sanitization not provided for utensil ware washing operation.","10I":"Single service item reused, improperly stored, dispensed; not used when required.","10J":"&quot;Wash hands&quot; sign not posted at hand wash facility.","15A":"Tobacco vending machine present where prohibited.","15B":"Tobacco vending machine placed less than 25 feet from entrance to premises.","15C":"Tobacco vending machine not visible to the operator, employee or agent.","15D":"Durable sign with license number, expiration date, and address and phone number not posted.","15E":"Out-of package sale of tobacco products observed.","15F":"Employee under the age of 18 selling tobacco products without direct supervision of an adult retail dealer or dealer.","15G":"Sale to minor observed.","15H":"Sign prohibiting sale of tobacco products to minors not conspicuously posted.","15I":"&quot;No Smoking&quot; and/or &quot;Smoking Permitted&quot; sign not conspicuously posted. Health warning not present on &quot;Smoking Permitted&quot;","15J":"Ashtray present in smoke-free area.","15K":"Operator failed to make good faith effort to inform smokers of the Smoke-free Act prohibition of smoking.","15L":"Smoke free workplace smoking policy inadequate, not posted, not provided to employees.","15M":"Use of tobacco product on school premises (at or below the 12th grade level) observed.","15N":"Smoking permitted and/or allowed in smoking prohibited area under the operator's control.","15O":"Sale of herbal cigarettes to minors observed.","15P":"No tobacco health warning and smoking cessation sign(s) are posted.","15Q":"Tobacco health warning and smoking cessation sign(s) are obstructed and/or not prominently displayed.","15R":"No large tobacco health warning and smoking cessation sign is posted where tobacco products are displayed; small sign(s) are not posted at each register or place of payment.","15S":"Flavored tobacco products sold or offered for sale.","15T":"Original label for tobacco products sold or offered for sale.","16A":"A food containing artificial trans fat, with 0.5 grams or more of trans fat per serving, is being stored, distributed, held for service, used in preparation of a menu item, or served.","16B":"The original nutritional fact labels and/or ingredient label for a cooking oil, shortening or margarine or food item sold in bulk, or acceptable manufacturer's documentation not maintained on site.","16C":"Caloric content not posted on menus, menu boards or food tags, in a food service establishment that is 1 of 15 or more outlets operating the same type of business nationally under common ownership or control, or as a franchise or doing business under the same name, for each menu item that is served in portions, the size and content of which are standardized.","16D":"Posted caloric content on the menu(s), menu board(s), food tag(s) or stanchions adjacent to menu boards for drive-through windows deficient, in that the size and/or font for posted calories is not as prominent as the name of the menu item or its price.","16E":"Caloric content range (minimum to maximum) not posted on menus and or menu boards for each flavor, variety and size of each menu item that is offered for sale in different flavors, varieties and sizes.","16F":"Specific caloric content or range thereof not posted on menus, menu boards or food tags for each menu item offered as a combination meal with multiple options that are listed as single items.","18A":"Current valid permit, registration or other authorization to operate establishment not available.","18B":"Document issued by the Board of Health, Commissioner or Department unlawfully reproduced or altered.","18C":"Notice of the Department of Board of Health mutilated, obstructed, or removed.","18D":"Failure to comply with an Order of the Board of Health, Commissioner, or Department.","18E":"Failure to report occurrences of suspected food borne illness to the Department.","18F":"Permit not conspicuously displayed.","18G":"Manufacture of frozen dessert not authorized on Food Service Establishment permit.","18H":"Failure of event sponsor to exclude vendor without a current valid permit or registration.","20A":"Food allergy information poster not conspicuously posted where food is being prepared or processed by food workers.","20B":"Food allergy information poster not posted in language understood by all food workers.","20C":"Food allergy poster does not contain text provided or approved by Department.","20D":"&quot;Choking first aid&quot; poster not posted. &quot;Alcohol and pregnancy&quot; warning sign not posted. Resuscitation equipment: exhaled air resuscitation masks (adult &amp; pediatric), latex gloves, sign not posted. Inspection report sign not posted.","20E":"Letter Grade or Grade Pending card not conspicuously posted and visible to passersby.","20F":"Current letter grade card not posted.","22A":"Nuisance created or allowed to exist. Facility not free from unsafe, hazardous, offensive or annoying conditions.","22B":"Toilet facility used by women does not have at least one covered garbage receptacle.","22C":"Bulb not shielded or shatterproof, in areas where there is extreme heat, temperature changes, or where accidental contact may occur.","22E":"ROP processing equipment not approved by DOHMH.","99B":"Other general violation."}
 

def get_default_user():
    try:
        user = User.objects.get(username='matt')
    except:
        user = User(first_name='Matt', email='matty@allsortz.com', username='zouf')
        user.set_password("testing")
        user.save()
        
    return user

def create_blank_user(n):
    try:
        user = User.objects.get(username='blank'+str(n))
    except:
        user = User(first_name='Blank', email='blank'+str(n)+'@allsortz.com', username='blank'+str(n))
        user.set_password("testing")
        user.save()
        
    return user

def create_user(username, uid):
    u = User(username=("u" + str(uid)), first_name=(username[0:20].encode("utf8")), password="")
    # u.set_password("test")
    return u


def prepop_topics(user=get_default_user()):
    reader = csv.reader(open(settings.BASE_DIR+'/prepop/topics.csv', 'U'), delimiter=',', quotechar='"')
    i = 0
    for row in reader:
        i+=1
        if i == 1:
            continue
       
        descr = row[0]
        icon = row[1]
        all_parents = row[2].split(', ')
        parents = []
        for p in all_parents:
            parents.append(p.strip(None))
        #print('Adding topic ' + str(descr) + ' parent is ' + str(parents))
        add_topic(descr,parents,icon)
    
        
def prepop_types(user):
    reader = csv.reader(open(settings.BASE_DIR+'/prepop/types.csv', 'U'), delimiter=',', quotechar='"')
    i = 0
    for row in reader:
        i+=1
        if i == 1:
            continue
       
        descr = row[0]
        icon = row[1]

        tset = Type.objects.filter(descr=descr)
        if tset.count() > 0:
            continue
        t = Type(descr=descr,creator=user,icon=icon)
        t.save()
        
        
        

    

def prepop_businesses(user=get_default_user()):
    if user == None:
        user = get_default_user()
    reader = csv.reader(open(settings.BASE_DIR+'/prepop/businesses.csv', 'U'), delimiter=',', quotechar='"')
    i = 0
    indices = {}
    tag_indices ={}
    for row in reader:
        i+=1
        if i == 1:
            bpoint = 0
            for hindex in xrange(0,len(row)):
                if row[hindex] == 'Main':
                    bpoint = hindex
                    break
                indices[row[hindex]] = hindex
            for tindex in xrange(bpoint,len(row)):
                tag_indices[row[tindex]] = tindex
                
            continue
    
        name = row[indices['Business']]
        addr =  row[indices['Address']]
        city =  row[indices['City']]
        state =  row[indices['State']]
        phurl =  row[indices['phurl']]
        types =  row[indices['Types']]
        serves_alcohol = row[ indices['Alcohol']]
        has_wifi =  row[indices['Wifi']]
        average_score =  row[indices['Score']]
        average_price =  row[indices['Price']]
        hours=  row[indices['Hours']]
        phone =  row[indices['Phone']]
        businessURL =  row[indices['URL']]
        
        if has_wifi == 'Yes':
            wifi = True
        else:
            wifi = False
        
        if serves_alcohol == 'Yes':
            serves = True
        else:
            serves = False
    

     
        b = add_business_server(name=name,addr=addr,state=state,city=city,phone=phone,
                            types='', hours=hours,wifi=wifi,serves=serves, url=businessURL, 
                            average_price=average_price)
        
        add_photo_by_url(phurl=phurl,business=b,user=user, default=True,caption="Photo of "+str(b.name), title=str(b.name))

        for t in types.split(','):
            t = t.strip(None)
            if Type.objects.filter(descr=t).count() > 0:
                typeofbus = Type.objects.get(descr=t)
            else:
                typeofbus = Type.objects.create(descr=t,creator=get_default_user(),icon="blankicon.png")
            BusinessType.objects.create(business=b,bustype=typeofbus)    
        
          
        for t,rindex in tag_indices.items():    
            topic = Topic.objects.get(descr=t)
            if row[rindex] != '':
                bustopic = add_topic_to_bus(b, topic, user)
                pg = Page.objects.get(bustopic=bustopic)
                pg.content = row[rindex]
                pg.save()
                print('Page content: ' + str(pg.content))
        
        

            
        
        
      
def prepop_queries(user):
    user = get_default_user()
    for t in Topic.objects.all():
        q = Query(name=t.descr,proximity=5,value=5,score=5,price=5,visited=False,deal=False,networked=False,text="",creator=user,is_default=True)
        q.save()


def prepop_topic_ratings():
    random.seed(666)
    
    
    NumBusiness = Business.objects.count()
    NumTopics = Topic.objects.count()
      
    user = get_default_user()
    print('User ' + str(user))
    i = 0
    center = random.randint(0, NumTopics-1)
    
    for t in Topic.objects.all():
        for b in Business.objects.all():
            print('Rating ' + str(b) + ' under the topic ' + str(t))
            #norm_given_rat = stats.norm(center,rating_given_sd)  #gaussian distribution for giving a rating
            prob_rat_given =  1 # norm_given_rat.pdf(i)  *  1/norm_given_rat.pdf(center)

            rat_given_rv = binomial(1, prob_rat_given, 1) #1 if rated, 0 otherwise
            if rat_given_rv[0] != 0:
                #norm_pos_rat = stats.norm(center,pos_rating_sd) #create a normal distribution
                prob_pos_rat =  0.5 #norm_pos_rat.pdf(i)  *  1/norm_pos_rat.pdf(center) #probability positive
                
                SIZE = 5
                #We'll ge tan array that is of lenght SIZE and the probability of the event being '1' is prob_pos_rat
                pos_rat_rv = binomial(1, prob_pos_rat, SIZE) #1 if positive, 0 negative
                

                #sum up the array and divide to get a rating between 0 and 1
                rating_scaled = 0                    
                SUM = 0.0
                for r in pos_rat_rv:
                    SUM += r
                rating_scaled = float(SUM)/float(SIZE)
                print('giving rating' + str(rating_scaled))
                try:
                    
                    bt = BusinessTopic.objects.get(business=b,topic=t)
                    BusinessTopicRating.objects.filter(businesstopic=bt,user=user).delete()
                #UserTopic.objects.create(user=user,topic=t,importance=1)
                    rat = BusinessTopicRating(businesstopic=bt, user=user, rating=float(rating_scaled))
                    rat.save()
                except:
                    pass
            #no rating        
            i=i+1
            


    

def parsePhoneNumber(phoneNum):
    if (len(phoneNum) == 10):
        areaCode = phoneNum[0: 3];
        prefix = phoneNum[3: 6];
        suffix = phoneNum[6: 10];
        return "(" + areaCode + ") " + prefix + "-" + suffix;
    else:
        return "";


def parseAddress(address):
    splitAddress = address.split('|')
    if len(splitAddress)> 0:
        street = splitAddress[0]
    else:
        street = ''
    if len(splitAddress) > 1:
        borough = splitAddress[1] 
    else:
        borough = ''
    if len(splitAddress) > 2:
        zipcode = splitAddress[2]
    else:
        zipcode = ''

    if borough == "1":
        borough = "Manhattan,";
    elif borough == "2":
        borough = "Bronx,";
    elif borough == "3":
        borough = "Brooklyn,";
    elif borough == "4":
        borough = "Queens,";
    elif borough == "5":
        borough = "Staten Island"
#    elif borough == "5":  # check to see if this is true
#        borough == "Staten Island"
    else:
        borough = "";
        
    if len(splitAddress)> 3:
        phone = parsePhoneNumber(splitAddress[3])
    else:
        phone = '';
    return (street, borough, zipcode, phone)
    

def format_inspdata(inspdate):
    splitDate = inspdate.split('|')
    if len(splitDate) > 0:
        month = splitDate[0]
    else:
        month = ''
    
    if len(splitDate) > 1:
        day = splitDate[1]
    else:
        day=''
    
    if len(splitDate) > 2:
        year = splitDate[2]
    else:
        year=''

    return ('{0}-{1}-{2}'.format(year,month,day))
    
def prepop_nyc_doh_ratings():
    
    fp = open(settings.DOH_DATASET_LOCATION)

    
    data = json.load(fp,encoding="utf-8")
    #pprint(objs)
    for key in data:
        print(key)
    #inspdate
    #cuisine
    #name
    #grade
    #score
    #camis
    #address
    #lat
    #violations
    #lng
    pos = 0
    cuisineDict = dict()
    for cid in cuisineCodes:

        cuisineDict[cid] = cuisineLabels[pos]       
        pos += 1
    
    pos = 0
    for name in data['name']:
        nm = name
        print(nm)
        lat = data['lat'][pos]
        lng = data['lng'][pos]
        if data['cuisine'][pos] in cuisineDict:
            restaurant_type= str(cuisineDict[data['cuisine'][pos]])
        else:
            restaurant_type = ''
        grade = str(data['grade'][pos])
        if pos % 400 == 0:
            print('\n----------')
            print(nm)

        all_violations= ''
        violationIDs = data['violations'][pos]
        for vid in violationIDs:
            if vid != '' and vid in violationDesc:
                all_violations = all_violations + str(violationDesc[vid])
                all_violations = all_violations + "\n"
        violationPoints = data['score'][pos]
        
        inspdate = format_inspdata(str(data['inspdate'][pos]))
        
        
        (street, borough, zipcode, phone) = parseAddress(data['address'][pos])
        if pos %400 == 0:
            print('Orig type ID ' + str(data['cuisine'][pos]))
            print(restaurant_type)
            print(all_violations)
            print(str(grade))
            print(str(violationPoints))
            print(str( (street, borough, zipcode, phone)))
            print(inspdate)
            print('---------------\n')
        b = add_business_server(name=nm,addr=street,state='NY',city=borough,phone=phone,
                    types=[restaurant_type], hours='',wifi=None,serves=None, url='', 
                    average_price=-1,health_letter_code=grade,health_violation_text=all_violations,health_points=int(violationPoints),inspdate=inspdate)
        #override with the loc data from DOH
        b.lat = lat
        b.lon = lng
        b.zipcode = zipcode
        b.save()

        pos += 1
            
        
def prepop_users():
    for i in xrange(1,20,1):
        create_blank_user(i)
