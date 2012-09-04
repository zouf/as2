'''
Created on Aug 16, 2012

@author: zouf
'''
from api.authenticate import get_default_user
from api.models import Type, Business, BusinessType, BusinessCache, BusinessMeta
import logging

logger = logging.getLogger(__name__)

def associate_business_type(b,t): 
    if BusinessType.objects.filter(business=b,bustype=t).count() > 0:
        return
    BusinessType.objects.create(business=b,bustype=t)
    return

def associate_business_with_types(bus,types):
    for tdescr in types:
        try:
            t = Type.objects.get(descr=tdescr) 
        except Type.MultipleObjectsReturned:
            logger.error("Multiple types returned")
            t = Type.objects.filter(descr=tdescr)[0] 
            pass
        except Type.DoesNotExist:
            print("Type " + str(tdescr) + " does not exist")
            t = Type(descr=tdescr,creator=get_default_user(),icon='none.png')
            t.save()
            #logger.error('Type does not exist")')
            pass
        associate_business_type(bus, t)  


def edit_business_server(bus,name,addr,city,state,phone,url,types):
    print("Editing business!\n")
    print(name)
    print(addr)
    print(city)
    print(state)
    print(phone)
    print(url)
    print(types)
    if name != '':
        bus.name = name
    if addr != '':
        bus.addr = addr
    if bus.city != '':
        bus.city = city
    if bus.state != '':
        bus.state = state
    if bus.phone != '':
        bus.phone = phone
    if bus.url != '':
        bus.url = url
        
    if types != '': 
        associate_business_with_types(bus,types)   
        
    BusinessCache.objects.filter(business=bus).delete()
    bus.save()
    return bus

def add_business_server(name,addr,city,state,phone,url,types,hours='',average_price=-1,serves=None,wifi=None,\
                        health_points=-1,health_violation_text='',health_letter_code='',inspdate=''):
#    print("Creating business!\n")
#    print(name)
#    print(addr)
#    print(city)
#    print(state)
#    print(phone)
#    print(url)
#    print(types)
    try:
        bset = Business.objects.filter(name=name,address=addr,city=city,state=state)    
        if bset.count() ==  0:
            bus = Business(name=name,address=addr,city=city,state=state,phone=phone,url=url)
            bus.save()
        elif bset.count() > 1: #too many
            bset.delete()
            bus = Business(name=name,address=addr,city=city,state=state,phone=phone,url=url)
            bus.save()
        else:
            bus = Business.objects.get(name=name,address=addr,city=city,state=state)
  
        bmset = BusinessMeta.objects.filter(business=bus).filter()
        if bmset.count() > 0:
            bmset.delete()
        bm = BusinessMeta(business=bus,hours=hours,average_price=average_price,serves=serves,wifi=wifi,health_points=health_points,
                            health_violation_text=health_violation_text,   health_letter_code = health_letter_code,inspdate=inspdate)
        bm.save()
        associate_business_with_types(bus,types)
        print('Creating ' + str(bus.name) + ' Done')
        return bus
    except Exception as e:
        logger.error("error creating businesses " + str(e))
        print("error creating  business" + str(e))
        return None