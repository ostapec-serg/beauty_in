from odoo import fields, models, api
from odoo.exceptions import UserError
from odoo.addons.beauty_in import constants as const


class BeautyInAddAppointmentWizard(models.TransientModel):
    _name = 'beauty.in.add.appointment.wizard'
    _description = 'Add New Appointment'

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        required=True
    )
    master_id = fields.Many2one(
        comodel_name="hr.employee",
        domain=[('employee_type', '=', 'master')],
        store=True, required=True
    )
    service = fields.Many2one(
        comodel_name="beauty.in.service",
        store=True, required=True
    )
    location_id = fields.Many2one(
        comodel_name="beauty.in.location",
        required=True
    )
    appointment_start_dtime = fields.Datetime(
        required=True,
        string="Appointment start date and time"
    )
    appointment_duration = fields.Selection(
        selection=const.APPOINTMENT_DURATION,
        default="30",
    )
    is_visible = fields.Boolean()

    def add_appointment(self):
        """
        Quick add appointment
        :raise UserError: If appointment created in the past
        """
        self.ensure_one()
        if self.appointment_start_dtime.date() >= fields.Datetime.now().date():
            self.env["beauty.in.appointment"].create({
                'partner_id': self.partner_id.id,
                'master_id': self.master_id.id,
                'appointment_start_dtime': self.appointment_start_dtime,
                'service': self.service,
                'location_id': self.location_id
            })
        else:
            raise UserError(
                f"You can't create appointment in the past!!!"
                f"You choose - {self.appointment_start_dtime.date()}"
                f"Choose another date!!!"
            )

    @api.onchange('appointment_start_dtime')
    def _check_date(self):
        if self.appointment_start_dtime:
            if self.appointment_start_dtime.date() >= fields.Datetime.now().date():
                self.is_visible = True
            else:
                self.is_visible = False
