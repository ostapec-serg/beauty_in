from odoo import fields, models


class BeautySpecialty(models.Model):
    _name = 'beauty.in.beauty.specialty'
    _description = 'Beauty Specialties'

    name = fields.Char()
    desc = fields.Text(string="Description")
    master_ids = fields.Many2many(
        comodel_name='hr.employee',
        relation="employee_specialty_rel",
        column1="specialty_id", column2="emp_id",
        domain=[('employee_type', '=', 'master')],
    )
