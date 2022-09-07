from uuid import UUID
from datetime import datetime
from django.core.exceptions import ValidationError
from .models import Unit


def validate_uuid(test_uuid: str, version=4) -> bool:
    try:
        uuid_object = UUID(test_uuid, version=version)
    except ValueError:
        raise ValidationError("Invalid UUID")


def validate_type(test_type: str):
    try:
        assert test_type == "OFFER" or test_type == "CATEGORY"
    except AssertionError:
        raise ValidationError("Invalid type (must be CATEGORY or OFFER)")


def validate_date(test_date: str):
    try:
        date_object = datetime.strptime(test_date, '%Y-%m-%dT%H:%M:%S.000Z')
    except ValueError:
        raise ValidationError("Invalid date (must be ISO8601 formatted)")


def validate_parent(test_parent_id: str):
    if test_parent_id is None:
        return None
    try:
        parent = Unit.objects.get(pk=test_parent_id)
    except Unit.DoesNotExist:
        raise ValidationError("ParentId refers non-existing object")
    try:
        assert parent.type == "CATEGORY"
    except AssertionError:
        raise ValidationError("ParentId must refer category object")


def validate_price(test_item: dict):
    item_type = test_item["type"]
    try:
        if item_type == "OFFER":
            price = test_item["price"]
            assert isinstance(price, int) and price >= 0
        else:
            assert "price" not in test_item
    except AssertionError:
        raise ValidationError("Invalid price")


def validate_name(test_name: str):
    try:
        assert test_name is not None
    except AssertionError:
        raise ValidationError('Name must not be null')


def validate_all_params(import_item: dict, date: str):
    missing = []
    for param in ("name", "id", "type"):
        if param not in import_item:
            missing.append(param)
    try:
        assert not missing
    except AssertionError:
        missing = ', '.join(missing)
        raise ValidationError(f'Missing required parameter(s): {missing}')

    validate_date(date)
    validate_uuid(import_item["id"])
    validate_type(import_item["type"])
    validate_name(import_item["name"])
    if "price" in import_item:
        validate_price(import_item)
    if "parentId" in import_item:
        validate_parent(import_item["parentId"])


