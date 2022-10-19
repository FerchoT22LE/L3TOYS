odoo.define('viin_brand.settings', function(require) {
    "use strict";

    var BaseSettingRenderer = require('base.settings').Renderer;

    BaseSettingRenderer.include({
		_renderTabs: function () {
			var self = this;
			self._super.apply(self, arguments);

			_.each(self.modules, function(module){
				self._rpc({
					model: 'res.config.settings',
					method: 'get_viin_brand_module_icon',
					args: [module.key],
				})
				.then(function(result){
					if (result){
						module.imgurl = result;
						self.$('.tab[data-key="' + module.key + '"] > div').attr('style', `background : url("${module.imgurl}") no-repeat center;background-size:contain;`);
					}
				});
			});
    	},
	});
});
