import glob
from os import path

from odoo import models, api, tools
from odoo.modules import get_module_path

class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    def _update_translations(self, filter_lang=None, overwrite=False):
        res = super(IrModuleModule, self)._update_translations(filter_lang=filter_lang, overwrite=overwrite)
        for r in self:
            if r.name == 'to_base':
                langs = self.env['res.lang'].search([]).mapped('code')
                modules = self.env['ir.module.module'].search([])
                modules._update_module_infos_translation(langs, r._cr)
        return res

    def _update_module_infos_translation(self, langs, cr, overwrite=False):
        if not isinstance(langs, list):
            langs = [langs]
        modules_name = self.mapped('name')
        for lang in langs:
            i18n_extra_path = path.join(get_module_path('to_base'), 'i18n_extra')
            i18n_extra_files = glob.glob(i18n_extra_path + '/*.po')
            for file_path in i18n_extra_files:
                module_name = path.basename(path.normpath(file_path)).split('_' + lang)[0]
                if module_name in modules_name:
                    tools.trans_load(cr, file_path, lang, verbose=False, create_empty_translation=False, overwrite=overwrite)

    @api.model_create_multi
    def create(self, vals):
        res = super(IrModuleModule, self).create(vals)
        langs = self.env['res.lang'].search([]).mapped('code')
        res._update_module_infos_translation(langs, self._cr)
        return res

    def write(self, vals):
        res = super(IrModuleModule, self).write(vals)

        if any(val in ['shortdesc', 'summary', 'description'] for val in vals):
            langs = self.env['res.lang'].search([]).mapped('code')
            self._update_module_infos_translation(langs, self._cr, overwrite=True)
        return res
