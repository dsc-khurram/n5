flectra.define('hr_employee_basic_info.KanbanColumn', function (require) {
    
    var KanbanColumn = require('web.KanbanColumn');
    var core = require('web.core');
    var ListController = require('web.ListController');
    var rpc = require('web.rpc');
    var session = require('web.session');
    var _t = core._t;

    ListController.include({
        init: function () {
            this._super.apply(this, arguments);
        },
        renderButtons: function($node) {
        this._super.apply(this, arguments);
            if (this.$buttons) {
                this.$buttons.find('.o_list_button_confirm_employee_profile').click(this.proxy('action_confirm_employee_profile'));
            }
        },
        
        action_confirm_employee_profile: function () {
            var self =this
            var user = session.uid;
            rpc.query({
                model: 'custom.hr.employee.buttons',
                method: 'confirm_employee_profile_from_running_contract',
                args: [1],
            })
        }
    });

    KanbanColumn.include({
        init: function (parent, data, options, recordOptions) {
            this._super(parent, data, options, recordOptions);
            if (this.modelName === 'hr.employee') {
                this.draggable = false;
            }
        },
    });
    return KanbanColumn

})