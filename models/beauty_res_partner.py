from odoo import fields, models, _


class HrEmployee(models.Model):
    _inherit = 'res.partner'

    appointment_ids = fields.One2many(
        comodel_name="beauty.in.appointment",
        inverse_name="partner_id"
    )
