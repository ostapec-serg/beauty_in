from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = 'res.partner'

    appointment_history_ids = fields.One2many(
        comodel_name="beauty.in.appointment",
        inverse_name="partner_id",
        domain=[("appointment_date", '<', fields.Date.today())]
    )
    today_appointment_ids = fields.One2many(
        comodel_name="beauty.in.appointment",
        inverse_name="partner_id",
        domain=[("appointment_date", '=', fields.Date.today())]
    )
