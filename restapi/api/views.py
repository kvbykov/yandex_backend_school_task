import datetime
import json

from django.http import HttpResponse, Http404, HttpResponseNotFound, JsonResponse
from .models import Unit, History


# ====================== index ====================== #

def index(request):
    ...


# ====================== nodes ====================== #

def serialize(unit):
    is_category = unit.type == 'CATEGORY'
    response = {'type': unit.type,
                'name': unit.name,
                'id': unit.id,
                'parentId': unit.parent.id if unit.parent else None,
                'price': unit.price,
                'date': unit.date.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
                'children': [serialize(child) for child in unit.unit_set.all()] if is_category else None,
                }
    return response


def nodes(request, uuid):
    try:
        unit = Unit.objects.get(pk=uuid)
    except Unit.DoesNotExist:
        return HttpResponseNotFound('{"code": 404, "message": "Item not found"}')
    response = serialize(unit)
    return JsonResponse(response, json_dumps_params={'ensure_ascii': False})


# ====================== delete ====================== #

def delete(request, uuid):
    try:
        unit = Unit.objects.get(pk=uuid)
    except Unit.DoesNotExist:
        return HttpResponseNotFound('{"code": 404, "message": "Item not found"}')
    unit.delete()
    return HttpResponse('{"code": 200, "message": "Deleted"}')


# ====================== imports ======================

def save_history(item_id):
    item = Unit.objects.get(pk=item_id)
    if item.type == 'OFFER':
        values = {'name': item.name,
                  'date': item.date,
                  'price': item.price,
                  'parentId': item.parent.id if item.parent else None,
                  'unit': item,
                  }
        obj = History(**values)
        obj.save()
    return None


def update_prices():
    def traverse(unit, offer_count=0, sum_price=0):
        if unit.type == 'OFFER':
            price = unit.price
            return price, 1
        else:
            children = unit.unit_set.all()
            if children:
                for child in children:
                    cost, offers = traverse(child)
                    sum_price += cost
                    offer_count += offers
                unit.price = sum_price // offer_count
                unit.save()
            else:
                unit.price = None
                unit.save()
            return sum_price, offer_count

    root_units = Unit.objects.filter(parent=None)

    for root_unit in root_units:
        traverse(root_unit)


def update_dates(affected_categories_ids, date):
    def traverse(category):
        if category.parent and category not in updated:
            updated.add(category)
            category.date = date
            category.save()
            category = category.parent
            traverse(category)
        else:
            updated.add(category)
            category.date = date
            category.save()

    updated = set()
    for category_id in affected_categories_ids:
        category = Unit.objects.get(pk=category_id)
        traverse(category)
    return None


def deserialize(item, date):
    values = {'pk': item['id'],
              'name': item['name'],
              'price': item['price'] if 'price' in item else None,
              'date': date,
              'parent': None if item['parentId'] is None else Unit.objects.get(pk=item['parentId']),
              'type': item['type'],
              }
    item = Unit(**values)
    return item


def imports(request):
    body = json.loads(request.body.decode())
    date = body['updateDate']
    items = body['items']
    affected_categories_ids = set()
    updated_or_added_ids = []
    for item in items:
        if item['parentId'] is not None:
            affected_categories_ids.add(item['parentId'])
        item = deserialize(item, date)
        item.save()
        updated_or_added_ids.append(item.id)
    update_dates(affected_categories_ids, date)
    update_prices()
    for unit_id in updated_or_added_ids:
        save_history(unit_id)
    response = {'code': 200,
                'message': 'Successfully imported all objects',
                }
    return JsonResponse(response)


# ====================== sales ====================== #

def sales(request, date):
    date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.000Z')
    yesterday = date - datetime.timedelta(days=1)
    response = {"items": []}
    for obj in Unit.objects.filter(type='OFFER'):
        if yesterday <= obj.date.replace(tzinfo=None):
            response_obj = {'type': 'OFFER',
                            'name': obj.name,
                            'id': obj.id,
                            'parentId': obj.parent.id if obj.parent else None,
                            'price': obj.price,
                            'date': obj.date.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
                            'children': None,
                            }
            response['items'].append(response_obj)
    return JsonResponse(response, json_dumps_params={'ensure_ascii': False})


# ====================== stats ====================== #

def stats(request, uuid):
    # query = request.GET
    # start = datetime.datetime.strptime(query['dateStart'], '%Y-%m-%dT%H:%M:%S.000Z')
    # end = datetime.datetime.strptime(query['dateEnd'], '%Y-%m-%dT%H:%M:%S.000Z')
    # item = None
    # try:
    #     item = Category.objects.get(pk=uuid)
    # except Category.DoesNotExist:
    #     pass
    # try:
    #     item = Offer.objects.get(pk=uuid)
    # except Offer.DoesNotExist:
    #     pass
    # if item is None:
    ...

def test_transactions(request):
    obj = Unit(id='069cb8d7-bbdd-47d3-ad8f-82ef4c269df1', name='TEST', price=228, type='')
