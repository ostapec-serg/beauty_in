from dateutil.relativedelta import relativedelta

from odoo import fields, models
from odoo.addons.beauty_in import constants as const


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    state = fields.Selection(
        selection=const.MASTER_STATE_LIST,
        default="draft", string="Status"
    )
    specialty_ids = fields.Many2many(
        comodel_name="beauty.in.beauty.specialty",
        relation="employee_specialty_rel",
        column1="emp_id", column2="specialty_id",

    )
    appointment_history_ids = fields.One2many(
        comodel_name="beauty.in.appointment",
        inverse_name="master_id",
        domain=[("appointment_date", '<', fields.Date.today())]
    )
    today_appointment_ids = fields.One2many(
        comodel_name="beauty.in.appointment",
        inverse_name="master_id",
        domain=[("appointment_date", '=', fields.Date.today())]
    )
    employee_type = fields.Selection(
        selection=const.EMPLOYEE_LIST,
        default='master'
    )
    appointment_ids = fields.One2many(
        comodel_name="beauty.in.appointment",
        inverse_name="master_id",
        compute='_compute_master_appointment_ids'
    )

    def _compute_master_appointment_ids(self):
        """
        Compute all appointment_ids(month)
        """
        today = fields.Datetime.today().date()
        for rec in self:
            appointment_ids = self.env[
                'beauty.in.appointment'
            ].search([
                ('master_id', '=', rec.id),
                ('appointment_date', '<=', today),
                ('appointment_date', '>=', today - relativedelta(month=1)),
                ('is_done', '=', True)
            ])
            rec.appointment_ids = appointment_ids
