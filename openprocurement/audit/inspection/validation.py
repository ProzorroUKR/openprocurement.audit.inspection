# -*- coding: utf-8 -*-
from openprocurement.api.utils import update_logging_context, raise_operation_error, error_handler, forbidden, get_now
from openprocurement.api.validation import validate_data
from openprocurement.audit.inspection.models import Inspection


def validate_inspection_data(request):
    update_logging_context(request, {'INSPECTION_ID': '__new__'})
    return validate_data(request, Inspection)


def validate_patch_inspection_data(request):
    return validate_data(request, Inspection, partial=True)
