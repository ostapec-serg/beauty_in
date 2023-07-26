import logging
from datetime import timedelta
import typing as tp

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

from odoo.addons.beauty_in import constants as const

_logger = logging.getLogger()


class BeautyInAppointment(models.Model):
    _name = 'beauty.in.appointment'
    _description = _("Appointments in 'Beauty in'")

    state = fields.Selection(
        selection=const.STATE_LIST,
        default="draft",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Client", required=True
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
    # For easier searching
    appointment_date = fields.Date(
        compute='_compute_appointment_date',
        store=True, index=True
    )
    # is_intern = fields.Boolean(compute="_compute_is_intern")
    appointment_start_dtime = fields.Datetime(
        string="Visit date and time",
        required=True
    )
    appointment_end_dtime = fields.Datetime(
        compute='_compute_appointment_end_dtime',
        store=True
    )
    appointment_duration = fields.Selection(
        selection=const.APPOINTMENT_DURATION,
        default="30"
    )
    day_name = fields.Char(
        string="Day of the week",
        compute="_compute_day_week",
    )
    schedule_id = fields.Many2one(
        comodel_name="beauty.in.master.schedule",
        ondelete="cascade"
    )
    note = fields.Text()
    is_done = fields.Boolean()
    active = fields.Boolean(
        'Active', default=True,
        help="By unchecking the active field, "
             "you may hide a location without deleting it."
    )

    @api.onchange('appointment_start_dtime')
    @api.depends('appointment_start_dtime')
    def _compute_appointment_date(self) -> tp.Any:
        """
        Compute visit date for easier searching
        """
        # TODO add auto date fill
        for rec in self:
            if rec.appointment_start_dtime:
                rec.appointment_date = rec.appointment_start_dtime.date()
            else:
                rec.appointment_date = False

    @api.onchange('appointment_start_dtime')
    @api.depends('appointment_start_dtime')
    def _compute_appointment_end_dtime(self) -> tp.Any:
        """
        Computing appointment end time depends on
        APPOINTMENT_DURATION constant
        """
        for rec in self:
            if rec.appointment_start_dtime:
                duration = timedelta(minutes=int(rec.appointment_duration))
                end = rec.appointment_start_dtime + duration
                rec.appointment_end_dtime = end
            else:
                rec.appointment_end_dtime = None

    @api.onchange('appointment_start_dtime')
    @api.depends('appointment_start_dtime')
    def _compute_day_week(self) -> tp.Any:
        """
        Compute dy of the week based on
        `appointment_start_dtime` field
        """
        for rec in self:
            if rec.appointment_start_dtime:
                rec.day_name = rec.appointment_start_dtime.strftime('%A')
            else:
                rec.day_name = None

    @api.model
    def create(self, vals_list: tp.Dict) -> tp.Dict:
        """ Creates new records for the model """
        self.is_available_time(vals_list)
        vals_list['state'] = "active"
        vals_list['schedule_id'] = self._get_schedule_id(vals_list)
        return super().create(vals_list)

    def unlink(self) -> tp.Any:
        """
        Deletes the records in ``self``.

        :raise ValidationError: if the record state == 'done'
        """
        for rec in self:
            if rec.is_done:
                raise ValidationError(
                    _("You can't delete appointments that already done!")
                )
        return super().unlink()

    def write(self, vals: tp.Dict) -> tp.Any:
        """
        Updates all records in ``self`` with the provided values.
        """
        is_done = vals.get('is_done')
        for rec in self:
            if vals.get('appointment_start_dtime'):
                vals['master_id'] = rec.id
                self.is_available_time(vals)
            if is_done:
                vals['state'] = 'done'
        return super().write(vals)

    def name_get(self) -> tp.List:
        """
        Build display name
        """
        return [
            (visit.id, f"{visit.appointment_start_dtime}/"
                       f"{visit.partner_id.name}") for visit in self
        ]

    def is_available_time(self, vals_list: tp.Dict) -> tp.Any:
        """
        Checking available appointment time
        """
        schedule = self._check_schedule_time(vals_list)
        appointment = self._check_appointment_time(vals_list)
        if schedule and appointment:
            return True

    def _check_schedule_time(self, vals_list: tp.Dict) -> tp.Any:
        """
        Checking available schedule time
        """
        delta = const.delta
        appointment_start_dtime = fields.Datetime.to_datetime(
            vals_list.get("appointment_start_dtime"))
        master_id = vals_list.get("master_id")
        duration = vals_list.get('appointment_duration')
        schedules = self.env[
            'beauty.in.master.schedule'
        ].search([
            ('master_id', '=', master_id),
            ('shift_date', '=', appointment_start_dtime.date())
        ])
        # Check if any schedule exist
        if not schedules:
            raise ValidationError(_("No schedule found!"))
        for schedule in schedules:
            # Checkin whether the specified time falls within the
            # doctor's work schedule
            work_start = schedule.shift_start_time
            work_end = schedule.shift_end_time
            start = appointment_start_dtime + delta
            end = start + self.get_duration_dt(duration) - delta
            if not work_start < (start or end) < work_end:
                _logger.warning(_("Specified time out of schedule"))
                raise ValidationError(
                    _("Specified time out "
                      "of schedule. Choose another time!")
                )
        return True

    def _check_appointment_time(self, vals_list: tp.Dict) -> tp.Any:
        """
        Checking available schedule time
        """
        delta = const.delta
        appointment_start_dtime = fields.Datetime.to_datetime(
            vals_list.get("appointment_start_dtime"))
        master_id = vals_list.get("master_id")
        duration = vals_list.get('appointment_duration')
        appointments = self.env[
            'beauty.in.appointment'
        ].search([
            ('master_id', '=', master_id),
            ('appointment_date', '=', appointment_start_dtime.date())])
        # Check if any appointments exist
        for visit in appointments:
            # Checkin whether the specified time does not
            # overlap with existing appointments
            visit_start = visit.appointment_start_dtime
            visit_end = visit.appointment_end_dtime
            start = appointment_start_dtime + delta
            end = start + self.get_duration_dt(duration) - delta
            if start < (visit_start or visit_end) < end:
                _logger.warning(_("Specified time is busy."
                                  "Choose another time!"))
                raise ValidationError(
                    _("Specified time is busy!"
                      " Choose another time!"
                      )
                )
        return True

    def _get_schedule_id(self, vals_list: tp.Dict) -> tp.Any:
        """
        Check if schedule exist for the current doctor
        And return id of that schedule

        :param vals_list: values for creating visit
        :raise ValidationError: if schedule not found
        """
        delta = const.delta
        appointment_start = fields.Datetime.to_datetime(
            vals_list.get("appointment_start_dtime")) - delta
        master_id = vals_list.get("master_id")
        schedules = self.env[
            'beauty.in.master.schedule'
        ].search([
            ('master_id', '=', master_id),
            ('shift_date', '=', appointment_start.date())
        ])
        for schedule in schedules:
            start = schedule.shift_start_time
            end = schedule.shift_end_time.time()
            if start.time() <= appointment_start.time() < end:
                return schedule.id
        raise ValidationError(
            _("No schedule found!")
        )

    def get_duration_dt(self, duration: tp.AnyStr):
        """
        Convert duration `str` to datetime delta duration
        """
        duration = timedelta(minutes=int(duration))
        return duration
