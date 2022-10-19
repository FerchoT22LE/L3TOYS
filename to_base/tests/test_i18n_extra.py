import glob
from os import path

from odoo.tests import TransactionCase
from odoo.modules import get_module_path


class TestI18nExtra(TransactionCase):

    def setUp(self):
        super(TestI18nExtra, self).setUp()

    def test_pot_exists(self):
        i18n_extra_path = path.join(get_module_path('to_base'), 'i18n_extra')
        self.assertFalse(glob.glob(i18n_extra_path + '/*.pot'))
