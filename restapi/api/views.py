import datetime
import json

from django.shortcuts import render
from django.http import HttpResponse, Http404, JsonResponse, HttpResponseNotFound
from .models import Offer, Category, History
import ast
from django.core import serializers


# ====================== index ====================== #

def index(request):
    offers = list(Offer.objects.all())
    categories = list(Category.objects.all())
    response = f'{offers} \n {categories}'
    return HttpResponse(response)


# ====================== nodes ====================== #

def get_price_cache(unit, cache, offer_count=0, sum_price=0):
    if isinstance(unit, Offer):
        price = unit.price
        cache[unit.id] = price
        return price, 1
    else:
        children = list(unit.category_set.all()) + list(unit.offer_set.all())
        if children:
            for child in children:
                cost, offers = get_price_cache(child, cache)
                sum_price += cost
                offer_count += offers
            cache[unit.id] = sum_price // offer_count
        else:
            cache[unit.id] = None
        return sum_price, offer_count


def serialize(unit):
    cache = {}
    get_price_cache(unit, cache)
    if isinstance(unit, Offer):
        return {'type': 'OFFER',
                'name': str(unit.name),
                'id': unit.id,
                'parentId': str(unit.parentId.id) if unit.parentId else None,
                'price': cache[unit.id],
                'date': unit.date.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
                'children': None,
                }
    elif isinstance(unit, Category):
        children = list(unit.category_set.all()) + list(unit.offer_set.all())
        price = cache[unit.id]
        return {'type': 'CATEGORY',
                'name': str(unit.name),
                'id': unit.id,
                'parentId': str(unit.parentId.id) if unit.parentId else None,
                'price': None if price == 0 else price,
                'date': unit.date.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
                'children': [serialize(unit) for unit in children],
                }


def nodes(request, uuid):
    unit = None
    try:
        unit = Offer.objects.get(pk=uuid)
    except Offer.DoesNotExist:
        pass
    try:
        unit = Category.objects.get(pk=uuid)
    except Category.DoesNotExist:
        pass
    if unit is None:
        return HttpResponseNotFound('Not Found')
    response = serialize(unit)
    return JsonResponse(response, json_dumps_params={'ensure_ascii': False})


# ====================== delete ====================== #

def delete(request, uuid):
    unit = None
    try:
        unit = Offer.objects.get(pk=uuid)
    except Offer.DoesNotExist:
        pass
    try:
        unit = Category.objects.get(pk=uuid)
    except Category.DoesNotExist:
        pass
    if unit is None:
        response = {"code": 404,
                    "message": "Item not found"
                    }
    else:
        unit.delete()
        response = {'code': 200,
                    'message': 'Successfully deleted'
                    }
    return JsonResponse(response)


# ====================== imports ====================== #

def add_history(item):
    values = {'name': item.name,
              'date': item.date,
              'price': item.price,
              'parentId': item.parentId.id if item.parentId else None,
              }
    if isinstance(item, Category):
        values['category'] = Category.objects.get(pk=item.id)
    else:
        values['offer'] = Offer.objects.get(pk=item.id)
    obj = History(**values)
    obj.save()
    return None


def update_dates(item, date):
    if item.parentId:
        item = Category.objects.get(pk=item.parentId.id)
        item.date = date
        item.save()
        update_dates(item, date)
    else:
        item.date = date
        item.save()
    return None


def parse_json(item, date):
    values = {'pk': item['id'],
              'name': item['name'],
              'price': item['price'] if 'price' in item else None,
              'date': date,
              'parentId': None if item['parentId'] is None else Category.objects.get(pk=item['parentId']),
              }
    match item['type']:
        case 'CATEGORY':
            obj = Category(**values)
        case 'OFFER':
            obj = Offer(**values)
    return obj


def imports(request):
    body = json.loads(request.body.decode())
    date = body['updateDate']
    items = body['items']
    for item in items:
        item = parse_json(item, date)
        item.save()
        update_dates(item, date)
        add_history(item)
    response = {'code': 200,
                'message': 'Successfully imported all objects',
                }
    return JsonResponse(response)


# ====================== sales ====================== #

def sales(request, date):
    date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.000Z')
    yesterday = date - datetime.timedelta(days=1)
    response = {"items": []}
    for obj in Offer.objects.all():
        if yesterday <= obj.date.replace(tzinfo=None):
            response_obj = {'type': 'OFFER',
                            'name': str(obj.name),
                            'id': obj.id,
                            'parentId': str(obj.parentId.id) if obj.parentId else None,
                            'price': obj.price,
                            'date': obj.date.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
                            'children': None,
                            }
            response['items'].append(response_obj)
    return JsonResponse(response, json_dumps_params={'ensure_ascii': False})


# ====================== stats ====================== #

def stats(request, uuid):
    query = request.GET
    start = datetime.datetime.strptime(query['dateStart'], '%Y-%m-%dT%H:%M:%S.000Z')
    end = datetime.datetime.strptime(query['dateEnd'], '%Y-%m-%dT%H:%M:%S.000Z')
    item = None
    try:
        item = Category.objects.get(pk=uuid)
    except Category.DoesNotExist:
        pass
    try:
        item = Offer.objects.get(pk=uuid)
    except Offer.DoesNotExist:
        pass
    if item is None:
        pass

