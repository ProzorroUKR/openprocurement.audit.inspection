from pyramid.events import ContextFound
from openprocurement.audit.api.auth import AuthenticationPolicy
from openprocurement.audit.inspection.design import add_design
from openprocurement.audit.inspection.utils import set_logging_context, extract_inspection, inspection_from_data
from logging import getLogger
from pkg_resources import get_distribution

PKG = get_distribution(__package__)
LOGGER = getLogger(PKG.project_name)


def includeme(config):
    LOGGER.info('init audit-inspection plugin')
    config.set_authentication_policy(AuthenticationPolicy(config.registry.settings['auth.file']))
    add_design()
    config.add_subscriber(set_logging_context, ContextFound)
    config.add_request_method(extract_inspection, 'inspection', reify=True)
    config.add_request_method(inspection_from_data)
    config.scan("openprocurement.audit.inspection.views")
