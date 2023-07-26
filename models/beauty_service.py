from odoo import fields, models


class BeautyService(models.Model):
    _name = 'beauty.in.service'
    _description = 'Beauty Services'

    name = fields.Char(required=True)
    price = fields.Float(required=True)
    average_service_time = fields.Integer()
    desc = fields.Text(string="Description")
    active = fields.Boolean(
        'Active', default=True,
        help="By unchecking the active field, you may hide a location without deleting it."
    )
