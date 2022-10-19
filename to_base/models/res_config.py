# -*- coding: utf-8 -*-

from odoo import models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    @api.model
    def get_viin_brand_module_icon(self, module):
        # we cannot import outside the class due to the import order in the module's __init__.py
        # i.e. models are imported prior to assigning the `get_viin_brand_module_icon()` to the `get_module_icon()`
        from odoo.modules.module import get_module_icon
        return get_module_icon(module)
