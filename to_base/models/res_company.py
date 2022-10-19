import base64

import odoo

from odoo import fields, models, tools
from odoo.modules.module import get_resource_path

from ..__init__ import viin_brand_manifest, _get_branding_module


class Company(models.Model):
    _inherit = 'res.company'

    def _get_default_favicon(self, original=False):
        # use viindoo's favicon if it exists in branding_module/static/img/favicon.ico
        branding_module = _get_branding_module()
        for adp in odoo.addons.__path__:
            if viin_brand_manifest.get('installable', False):
                viindoo_favicon_path = get_resource_path(branding_module, 'static/img/favicon.ico')
                if viindoo_favicon_path:
                    with tools.file_open(viindoo_favicon_path, 'rb') as f:
                        return base64.b64encode(f.read())
        return super(Company, self)._get_default_favicon(original)

    font = fields.Selection(selection_add=[('Times New Roman', 'Times New Roman')])
    favicon = fields.Binary(string="Company Favicon", help="This field holds the image used to display a favicon for a given company.", default=_get_default_favicon)
