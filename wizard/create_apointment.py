from odoo import fields, models, api, _
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
    appointment_start_dtime = fields.Datetime(
        required=True,
        string="Appointment start date and time"
    )
    appointment_duration = fields.Selection(
        selection=const.APPOINTMENT_DURATION,
        default="30",
    )
    is_visible = fields.Boolean(default=True)

    def add_appointment(self):
        """
        Quick add appointment
        :raise UserError: If appointment created in the past
        """
        self.ensure_one()
        now = fields.Datetime.now().date()
        if self.appointment_start_dtime.date() >= now:
            self.env["beauty.in.appointment"].create({
                'partner_id': self.partner_id.id,
                'master_id': self.master_id.id,
                'appointment_start_dtime': self.appointment_start_dtime,
                'service': self.service.id,
                'appointment_duration': self.appointment_duration,
            })
        else:
            raise UserError(
                f"You can't create appointment in the past!!!"
                f"You choose - {self.appointment_start_dtime.date()}"
                f"Choose another date!!!"
            )
        message = _("Appointment added!\nAppointment date - ")
        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Create an Appointment"),
                'type': 'success',
                'message': f"{message}{self.appointment_start_dtime}",
                'fadeout': 'slow',
                'fadein': 'slow',
                'sticky': False,
                'next': {
                    'type': 'ir.actions.act_window_close'
                }
            }
        }
        return notification

    @api.onchange('appointment_start_dtime')
    def _check_date(self):
        now = fields.Datetime.now().date()
        if self.appointment_start_dtime:
            if self.appointment_start_dtime.date() >= now:
                self.is_visible = True
            else:
                self.is_visible = False
