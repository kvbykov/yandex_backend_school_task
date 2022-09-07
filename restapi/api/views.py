import json
from django.db import transaction
from django.http import JsonResponse
from .models import Unit
from django.core.exceptions import ValidationError
from .services import get_dict_from_unit
from .services import get_datetime_object
from .services import get_dict_from_history
from .services import get_requested_object
from .services import get_date_range
from .services import create_unit_instance
from .services import update_dates
from .services import get_update_data
from .services import update_prices
from .services import save_history
from .validators import validate_date
from .validators import validate_all_params


def get_unit(request, uuid):
    unit_or_response = get_requested_object(uuid)
    if isinstance(unit_or_response, JsonResponse):
        return unit_or_response
    response = get_dict_from_unit(unit_or_response)
    return JsonResponse(response, json_dumps_params={'ensure_ascii': False})


@transaction.atomic
def delete(request, uuid):
    unit_or_response = get_requested_object(uuid)
    if isinstance(unit_or_response, JsonResponse):
        return unit_or_response
    unit_or_response.delete()
    return JsonResponse({"code": 200, "message": "Deleted"},
                        json_dumps_params={'ensure_ascii': False})


@transaction.atomic
def import_units(request):
    request_body = json.loads(request.body.decode())
    update_date = request_body["updateDate"]
    import_items = request_body["items"]

    affected_categories_ids, updated_or_added_ids = get_update_data(import_items)

    for import_item in import_items:
        try:
            validate_all_params(import_item, update_date)
            unit_instance = create_unit_instance(import_item, update_date)
        except ValidationError as e:
            transaction.set_rollback(True)
            return JsonResponse({"code": 400, "message": e.message},
                                status=400,
                                json_dumps_params={'ensure_ascii': False})
        unit_instance.save()

    update_dates(affected_categories_ids, update_date)
    update_prices()
    for item_id in updated_or_added_ids:
        save_history(item_id)
    return JsonResponse({"code": 200, "message": "Import or update went successful"},
                        json_dumps_params={'ensure_ascii': False})


def get_recently_updated(request, request_date):
    try:
        validate_date(request_date)
    except ValidationError as e:
        return JsonResponse({"code": 400, "message": e.message},
                            status=400,
                            json_dumps_params={'ensure_ascii': False})
    date_range = get_date_range(request_date)
    response = {"items": []}
    for unit in Unit.objects.filter(date__range=date_range).filter(type='OFFER'):
        dict_unit = get_dict_from_unit(unit)
        response['items'].append(dict_unit)
    return JsonResponse(response, json_dumps_params={'ensure_ascii': False})


def get_statistics(request, uuid):
    unit_or_response = get_requested_object(uuid)
    if isinstance(unit_or_response, JsonResponse):
        return unit_or_response
    unit = unit_or_response

    query = request.GET
    date_start = query["dateStart"]
    date_end = query["dateEnd"]

    try:
        validate_date(date_start)
        validate_date(date_end)
    except ValidationError as e:
        return JsonResponse({"code": 400, "message": e.message},
                            status=400,
                            json_dumps_params={'ensure_ascii': False})

    date_start = get_datetime_object(date_start)
    date_end = get_datetime_object(date_end)

    response = {"items": []}
    for history_unit in unit.history_set.all().filter(date__range=(date_start, date_end)):
        dict_unit = get_dict_from_history(history_unit)
        response["items"].append(dict_unit)
    return JsonResponse(response, json_dumps_params={'ensure_ascii': False})
