import ast
import base64
import contextlib
import io

from odoo import api, fields, models
from odoo import tools
from odoo.modules.module import module_manifest, get_module_path

from odoo.addons.base.wizard.base_export_language import NEW_LANG_KEY


class BaseLanguageExport(models.TransientModel):
    _inherit = 'base.language.export'

    only_export_modules_infos_translation = fields.Boolean(string='Only export modules infos translation',
                                                    help="If this option is selected, the system will only export modules infos translation(name, summary and description)")

    def act_getfile(self):
        this = self[0]

        if not this.only_export_modules_infos_translation:
            return super(BaseLanguageExport, self).act_getfile()

        lang = this.lang if this.lang != NEW_LANG_KEY else False
        mods = sorted(this.mapped('modules.name')) or ['all']

        with contextlib.closing(io.BytesIO()) as buf:
            translations = []
            for mod in mods:
                translations.extend(self._retrieve_trans_from_manifest(mod, lang))
            writer = tools.TranslationFileWriter(buf, fileformat=this.format, lang=lang)
            writer.write_rows(translations)

            out = base64.encodebytes(buf.getvalue())

        filename = 'new'
        if lang:
            filename = mods[0] + '_' + tools.get_iso_codes(lang)

        extension = this.format
        if not lang and extension == 'po':
            extension = 'pot'
        name = "%s.%s" % (filename, extension)
        this.write({'state': 'get', 'data': out, 'name': name})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'base.language.export',
            'view_mode': 'form',
            'res_id': this.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

    @api.model
    def _retrieve_trans_from_manifest(self, module_name, lang):
        """ Retrieve translated records per module from manifest.

        :param module_name: module name
        :param lang: language code to retrieve the translations
                     retrieve source terms only if not set
        """
        module_path = get_module_path(module_name)
        manifest_file = module_manifest(module_path)

        key_trans = ['name', 'description', 'summary']

        result = []
        if manifest_file:
            manifest_file = open(manifest_file, "r")
            manifest_info = ast.literal_eval(manifest_file.read())
            for key in key_trans:
                if manifest_info.get(key, ''):
                    trans_detail = (
                        'base',
                        'model',
                        'ir.module.module,' + ('shortdesc' if key == 'name' else key),
                        'base.module_' + module_name,
                        manifest_info[key],
                        manifest_info.get(key + '_' + lang, '') if lang else '',
                        ()
                        )
                    result.append(trans_detail)
            manifest_file.close()
        return result
