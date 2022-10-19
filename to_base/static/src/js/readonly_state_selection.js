odoo.define('to_base.readonly_state_selection', function(require) {
	"use strict";

	var field_registry = require('web.field_registry');
	var StateSelectionWidget = require('web.basic_fields').StateSelectionWidget;

	/**
	* new widget `readonly_state_selection` that is as the same as the native
	* Odoo's widget `state_selection`` except its dropdown is shown always
	* no matter the record is writable or not.
	*/
	var ReadonlyStateSelectionWidget = StateSelectionWidget.extend({
		_render: function() {
			this._super.apply(this, arguments);
			// Ensure to show dropdown always no matter the record is writable or not
			this.$('a[data-toggle=dropdown]').toggleClass('disabled', false);
		},
	});
	field_registry.add('readonly_state_selection', ReadonlyStateSelectionWidget);
	return ReadonlyStateSelectionWidget;
});

