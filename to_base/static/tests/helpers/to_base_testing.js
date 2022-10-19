odoo.define('to_base.MockServer', function(require) {
	var MockServer = require('web.MockServer');

	MockServer.include({
		/**
		 * @override
		 */
		_performRpc: function(route, args) {
			if (args.model === "res.config.settings" & route === '/web/dataset/call_kw/res.config.settings/get_viin_brand_module_icon') {
				return Promise.resolve('viin_brand/static/img/apps/settings.png');
			}
			return this._super.apply(this, arguments);
		},
	})
});
