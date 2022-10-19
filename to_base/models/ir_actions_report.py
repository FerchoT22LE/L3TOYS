from odoo import api, models, _


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    @api.model
    def _build_wkhtmltopdf_args(
            self,
            paperformat_id,
            landscape,
            specific_paperformat_args=None,
            set_viewport_size=False):
        command_args = super(IrActionsReport, self)._build_wkhtmltopdf_args(
            paperformat_id=paperformat_id,
            landscape=landscape,
            specific_paperformat_args=specific_paperformat_args,
            set_viewport_size=set_viewport_size)
        # when call get_pdf() for some reports like Balance Sheet, General Ledger, ...,
        # the result can miss header and footer and throw this WARNING: "Received createRequest signal on a disposed ResourceObject's NetworkAccessManager".
        # Refer to this issue: https://github.com/wkhtmltopdf/wkhtmltopdf/issues/1613
        # To avoid it, increase this parameter '--javascript-delay' to 2s for more time waiting.
        # Ticket: https://viindoo.com/web#cids=1&id=6362&menu_id=89&model=helpdesk.ticket&view_type=form
        command_args.extend(['--javascript-delay', '2000'])
        return command_args
