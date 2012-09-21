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
        if tdescr == '':
            continue
        try:
            t = Type.objects.get(descr=tdescr) 
        except Type.MultipleObjectsReturned:
            logger.error("Multiple types returned")
            t = Type.objects.filter(descr=tdescr)[0] 
            pass
        except Type.DoesNotExist:
            logger.debug("Type " + str(tdescr) + " does not exist")
            if tdescr != '':
                t = Type(descr=tdescr,creator=get_default_user(),icon='none.png')
                t.save()
            #logger.error('Type does not exist")')
            pass
        associate_business_type(bus, t)  

def associate_business_with_type_IDs(bus,types):
    for tid in types:
        try:
            t = Type.objects.get(id=tid) 
        except Type.DoesNotExist:
            logger.debug("with id " + str(tid) + " does not exist")
            #logger.error('Type does not exist")')
            pass
        associate_business_type(bus, t)  


def edit_business_server(bus,name,addr,city,state,phone,url,types,hours):
    logger.debug("Editing business!\n")
    logger.debug(name)
    logger.debug(addr)
    logger.debug(city)
    logger.debug(state)
    logger.debug(phone)
    logger.debug(url)
    logger.debug(types)
    logger.debug(hours)
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
        
        
    bm  = BusinessMeta.objects.get(business=bus)
    if hours != '':
        bm.hours = hours
    bm.save()
    
    
    if types != '': 
        associate_business_with_type_IDs(bus,types)   
        
    BusinessCache.objects.filter(business=bus).delete()
    bus.save()
    return bus

def add_business_server(name,addr,city,state,phone,url,types,hours='',average_price=-1,serves=None,wifi=None,\
                        health_points=-1,health_violation_text='',health_letter_code='',inspdate='2000-1-1'):
#    logger.debug("Creating business!\n")
#    logger.debug(name)
#    logger.debug(addr)
#    logger.debug(city)
#    logger.debug(state)
#    logger.debug(phone)
#    logger.debug(url)
#    logger.debug(types)
    try:
        bset = Business.objects.filter(name=name,address=addr,city=city,state=state,phone=phone,url=url)
        if bset.count() ==  0:
            bus = Business(name=name,address=addr,city=city,state=state,phone=phone,url=url)
            bus.save()
        elif bset.count() > 1: #too many
            bset.delete()
            bus = Business(name=name,address=addr,city=city,state=state,phone=phone,url=url)
            bus.save()
        else:
            logger.debug('getting existing business')
            bus = bset[0]
  
        bmset = BusinessMeta.objects.filter(business=bus)
        if bmset.count() > 0:
            bmset.delete()
        logger.debug('Create meta for ' + str(bus))
        bm = BusinessMeta(business=bus,hours=hours,average_price=average_price,serves=serves,wifi=wifi,health_points=health_points,
                            health_violation_text=health_violation_text,   health_letter_code = health_letter_code,inspdate=inspdate)
        bm.save()
        associate_business_with_types(bus,types)
        #logger.debug('Creating ' + str(bus.name) + ' Done')
        return bus
    except Exception as e:
        logger.error("error creating businesses " + str(e))
        logger.debug("error creating  business" + str(e))
        return None
