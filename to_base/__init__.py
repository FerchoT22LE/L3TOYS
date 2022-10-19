import importlib
import logging
import os
import ast

import odoo

from odoo import api, modules, tools, SUPERUSER_ID
from odoo.tools import config, pycompat
from odoo.tests import common
from odoo.modules import module

from odoo.addons.base.models.res_currency import CurrencyRate

_logger = logging.getLogger(__name__)

from . import controllers
from . import models
from . import wizard

get_resource_path = module.get_resource_path
get_module_path = module.get_module_path
module_manifest = module.module_manifest
get_module_icon = module.get_module_icon
load_information_from_description_file = module.load_information_from_description_file
get_db_name = common.get_db_name


def _get_branding_module(branding_module='viin_brand'):
    """
    Wrapper for others to override
    """
    return branding_module


def _get_db_name_plus():
    db = get_db_name()
    if db:
        # Force POST value that is set as 8069 by dynamic value
        # to avoid dead test of Odoo
        global common
        common.PORT = odoo.tools.config['http_port']

    return db


def test_installable(module, mod_path=None):
    """
    :param module: The name of the module (sale, purchase, ...)
    :param mod_path: Physical path of module, if not providedThe name of the module (sale, purchase, ...)
    """
    if module == 'general_settings':
        module = 'base'
    if not mod_path:
        mod_path = get_module_path(module, downloaded=True)
    manifest_file = module_manifest(mod_path)
    if manifest_file:
        info = {
            'installable': True,
        }
        f = tools.file_open(manifest_file, mode='rb')
        try:
            info.update(ast.literal_eval(pycompat.to_text(f.read())))
        finally:
            f.close()
        return info
    return {}


viin_brand_manifest = test_installable(_get_branding_module())


def check_viin_brand_module_icon(module):
    """
    Ensure module icon with
        either '/viin_brand_originmodulename/static/description/icon.png'
        or '/viin_brand/static/img/apps/originmodulename.png'
        exists.
    """
    branding_module = _get_branding_module()
    brand_originmodulename = '%s_%s' % (branding_module, module if module not in ('general_settings', 'modules') else 'base')

    # load manifest of the overriding modules
    viin_brand_originmodulename_manifest = test_installable(brand_originmodulename)

    # /viin_brand/static/img/apps_icon_override/originmodulename.png
    originmodulename_iconpath = os.path.join(branding_module, 'static', 'img', 'apps', '%s.png' % (module if module not in ('general_settings', 'modules') else module == 'general_settings' and 'settings' or 'modules'))

    # /viin_brand_originmodulename'/static/description/icon.png
    iconpath = os.path.join(brand_originmodulename, 'static', 'description', 'icon.png')

    module_icon = False
    for adp in odoo.addons.__path__:
        if viin_brand_originmodulename_manifest.get('installable', False) and os.path.exists(os.path.join(adp, iconpath)):
            module_icon = iconpath
            break
        elif viin_brand_manifest.get('installable', False) and os.path.exists(os.path.join(adp, originmodulename_iconpath)):
            module_icon = originmodulename_iconpath
            break
    return module_icon


def get_viin_brand_resource_path(mod, *args):
    # Odoo hard coded its own favicon in several places
    # this override to attempt to get Viindoo's favicon if it
    # exists in branding_module/static/img/favicon.ico
    if mod == 'web' and 'static/img/favicon.ico' in args:
        branding_module = _get_branding_module()
        for adp in odoo.addons.__path__:
            if viin_brand_manifest.get('installable', False):
                viindoo_favicon_path = get_resource_path(branding_module, *args)
                if viindoo_favicon_path:
                    return viindoo_favicon_path
    # fall back to the default one
    return get_resource_path(mod, *args)


def get_viin_brand_module_icon(mod):
    """
    This overrides default module icon with
        either '/viin_brand_originmodulename/static/description/icon.png'
        or '/viin_brand/static/img/apps/originmodulename.png'
        where originmodulename is the name of the module whose icon will be overridden
    provided that either of the viin_brand_originmodulename or viin_brand is installable
    """
    module_icon = check_viin_brand_module_icon(mod)
    if module_icon:
        return module_icon
    else:
        return get_module_icon(mod)


def _get_brand_module_website(module):
    """
    This overrides default module website with '/branding_module/apriori.py'
    where apriori contains dict:
    modules_website = {
        'account': 'account's website',
        'sale': 'sale's website,
    }
    :return module website in apriori.py if exists else False
    """
    branding_module = _get_branding_module()
    for adp in odoo.addons.__path__:
        if viin_brand_manifest.get('installable', False):
            try:
                modules_website = importlib.import_module('odoo.addons.%s.apriori' % branding_module).modules_website
                if module in modules_website:
                    return modules_website[module]
            except:
                pass
    return False


def _load_information_from_description_file_plus(module, mod_path=None):
    info = load_information_from_description_file(module, mod_path=mod_path)
    if info:
        module_website = _get_brand_module_website(module)
        if module_website:
            info['website'] = module_website
    return info


def _test_if_loaded_in_server_wide():
    config_options = config.options
    if 'to_base' in config_options.get('server_wide_modules', '').split(','):
        return True
    else:
        return False


if not _test_if_loaded_in_server_wide():
    _logger.warning("The module `to_base` should be loaded in server wide mode using `--load`"
                 " option when starting Odoo server (e.g. --load=base,web,to_base)."
                 " Otherwise, some of its functions may not work properly.")


def _disable_currency_rate_unique_name_per_day():
    # Remove unique_name_per_day constraint in res.currency.rate model in base module
    # It doesn't delete constraint on database server
    for el in CurrencyRate._sql_constraints:
        if el[0] == 'unique_name_per_day':
            _logger.info("Removing the default currency rate's SQL constraint `unique_name_per_day`")
            CurrencyRate._sql_constraints.remove(el)
            break


def _update_brand_web_icon_data(env):
    # Generic trick necessary for search() calls to avoid hidden menus which contains 'base.group_no_one'
    menus = env['ir.ui.menu'].with_context({'ir.ui.menu.full_list': True}).search([('web_icon', '!=', False)])
    for m in menus:
        web_icon = m.web_icon
        paths = web_icon.split(',')
        if len(paths) == 2:
            module = paths[0]
            module_name = paths[1].split('/')[-1][:-4]
            if module_name == 'board' or module_name == 'modules' or module_name == 'settings':
                module = module_name
                web_icon = '%s,static/description/icon.png' % module

            module_icon = check_viin_brand_module_icon(module)
            if module_icon:
                web_icon_data = m._compute_web_icon_data(web_icon)
                if web_icon_data != m.web_icon_data:
                    m.write({'web_icon_data': web_icon_data})


def _update_favicon(env):
    branding_module = _get_branding_module()
    for adp in odoo.addons.__path__:
        if viin_brand_manifest.get('installable', False):
            img_path = module.get_resource_path(branding_module, 'static/img/favicon.ico')
            if img_path:
                res_company_obj = env['res.company']
                data = res_company_obj._get_default_favicon()
                res_company_obj.with_context(active_test=False).search([]).write({'favicon': data})


def pre_init_hook(cr):
    common.get_db_name = _get_db_name_plus
    module.get_resource_path = get_viin_brand_resource_path
    modules.get_resource_path = get_viin_brand_resource_path
    module.get_module_icon = get_viin_brand_module_icon


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _update_brand_web_icon_data(env)
    _update_favicon(env)


def uninstall_hook(cr, registry):
    common.get_db_name = get_db_name
    module.get_resource_path = get_viin_brand_resource_path
    modules.get_resource_path = get_viin_brand_resource_path
    module.get_module_icon = get_module_icon
    module.load_information_from_description_file = load_information_from_description_file
    modules.load_information_from_description_file = load_information_from_description_file


def post_load():
    _disable_currency_rate_unique_name_per_day()
    module.get_module_icon = get_viin_brand_module_icon
    module.get_resource_path = get_viin_brand_resource_path
    modules.get_resource_path = get_viin_brand_resource_path
    common.get_db_name = _get_db_name_plus
    module.load_information_from_description_file = _load_information_from_description_file_plus
    modules.load_information_from_description_file = _load_information_from_description_file_plus
