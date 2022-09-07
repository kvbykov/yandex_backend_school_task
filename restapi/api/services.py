from django.core.exceptions import ValidationError
from django.http import JsonResponse
from .models import Unit, History
from .validators import validate_uuid
from .validators import validate_all_params
from datetime import datetime, timedelta


# ====================== NODES AND DELETE ====================== #

def get_dict_from_unit(unit: Unit) -> dict:
    """Generates nested dictionary for JSON representation"""
    is_category = unit.type == 'CATEGORY'
    response = {'type': unit.type,
                'name': unit.name,
                'id': unit.id,
                'parentId': unit.parent.id if unit.parent else None,
                'price': unit.price,
                'date': unit.date.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
                'children': [get_dict_from_unit(child) for child in unit.unit_set.all()] if is_category else None,
                }
    return response


def get_requested_object(uuid: str) -> Unit | JsonResponse:
    """
    Checks if given uuid is valid
    Checks if there is an object with given uuid
    Returns json with error message or Unit instance
    """
    try:
        validate_uuid(uuid)
    except ValidationError as e:
        return JsonResponse({"code": 400, "message": e.message},
                            status=400,
                            json_dumps_params={'ensure_ascii': False})
    try:
        unit = Unit.objects.get(pk=uuid)
    except Unit.DoesNotExist:
        return JsonResponse({"code": 404, "message": "Item not found"},
                            status=404,
                            json_dumps_params={'ensure_ascii': False})
    return unit


# ====================== IMPORT UNITS ====================== #


def create_unit_instance(item: dict, date: str) -> Unit:
    values = {'pk': item['id'],
              'name': item['name'],
              'price': item['price'] if 'price' in item else None,
              'date': date,
              'parent': None if item['parentId'] is None else Unit.objects.get(pk=item['parentId']),
              'type': item['type'].upper(),
              }
    item = Unit(**values)
    return item


def get_update_data(items: list) -> tuple[set[str], set[str]]:
    """
    Returns two sets of strings:
    'affected_categories_ids' is required for updating 'date' field
    of categories with added/updated child

    'updated_or_added_ids' is required for adding new rows in History table
    """
    affected_categories_ids = set()
    updated_or_added_ids = set()
    for item in items:
        if item["parentId"] is not None:
            affected_categories_ids.add(item["parentId"])
        updated_or_added_ids.add(item["id"])
    return affected_categories_ids, updated_or_added_ids


def update_dates(affected_categories_ids: set[str], date: str):
    def traverse_and_update(category):
        if category.parent and category not in updated:
            updated.add(category)
            category.date = date
            category.save()
            category = category.parent
            traverse_and_update(category)
        else:
            updated.add(category)
            category.date = date
            category.save()

    updated = set()
    for category_id in affected_categories_ids:
        category = Unit.objects.get(pk=category_id)
        traverse_and_update(category)
    return None


def update_prices():
    def traverse_and_update(unit, offer_count=0, sum_price=0):
        if unit.type == 'OFFER':
            price = unit.price
            return price, 1
        else:
            children = unit.unit_set.all()
            if children:
                for child in children:
                    cost, offers = traverse_and_update(child)
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
        traverse_and_update(root_unit)


def save_history(item_id: str):
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


# ====================== SALES ====================== #

def get_date_range(request_date: str) -> tuple[str]:
    range_end = datetime.strptime(request_date, '%Y-%m-%dT%H:%M:%S.000Z')
    range_start = range_end - timedelta(days=1)
    return range_start, range_end


# ====================== STATS ====================== #

def get_datetime_object(date_str: str) -> datetime:
    return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.000Z')


def get_dict_from_history(history: History) -> dict:
    response = {"id": history.unit_id,
                "name": history.name,
                "date": history.date,
                "parentId": history.parentId,
                "price": history.price,
                "type": "OFFER"
                }
    return response
