from datetime import timedelta, datetime, time

from odoo import fields, models, api, _ as _t
from odoo.addons.beauty_in import constants as const
from odoo.exceptions import ValidationError


class BeautyInWeekScheduleWizard(models.TransientModel):
    _name = 'beauty.in.week.schedule.wizard'
    _description = 'Add Week Schedule'

    week_start_date = fields.Date(required=True)
    shift_start_time = fields.Datetime(required=True)
    master_id = fields.Many2one(
        comodel_name="hr.employee",
        domain=[('employee_type', '=', 'master')],
        required=True,
        ondelete="cascade"
    )
    shift_duration = fields.Selection(
        selection=const.WORK_SHIFT_DURATION,
        required=True,
        default="8"
    )
    is_even_or_odd = fields.Selection(
        selection=[("all", "All"), ("even", "Even"), ("odd", "Odd")],
        default="all",
        string="Even or Odd",
        help="For even or odd days"
    )

    def add_schedule(self):
        """
        Create one week schedule for specified master
        """
        self.ensure_one()
        schedule_start_dt = fields.Datetime.to_datetime(
            self.shift_start_time
        )
        delta = timedelta(days=1)
        params = {
            "master_id": self.master_id.id,
            "shift_duration": self.shift_duration
        }
        schedule_count = 0
        for _ in range(0, 7):
            schedule_date = schedule_start_dt.date()
            if self.is_even_or_odd == 'even':
                if schedule_date.day % 2 == 0:
                    params["shift_date"] = schedule_date
                    params["shift_start_time"] = schedule_start_dt
            elif self.is_even_or_odd == 'odd':
                if schedule_date.day % 2 != 0:
                    params["shift_date"] = schedule_date
                    params["shift_start_time"] = schedule_start_dt
            else:
                params["shift_date"] = schedule_date
                params["shift_start_time"] = schedule_start_dt
            try:
                schedule_start_dt += delta
                self._create_schedule(params)
                schedule_count += 1
            except ValidationError:
                pass
        message = _t("Added schedules for days out of 7 - ")
        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _t("Week schedule"),
                'type': 'success',
                'message': f"{message}{schedule_count}",
                'fadeout': 'slow',
                'fadein': 'slow',
                'sticky': False,
                'next': {
                    'type': 'ir.actions.act_window_close'
                }
            }
        }
        return notification

    def _create_schedule(self, params: dict):
        """
        Create one week schedule for specified doctor
        """
        self.env['beauty.in.master.schedule'].create({
            "shift_date": params["shift_date"],
            "shift_duration": params["shift_duration"],
            "shift_start_time": params['shift_start_time'],
            "master_id": params['master_id'],
        })

    @api.onchange('week_start_date', 'shift_start_time')
    @api.depends('week_start_date', 'shift_start_time')
    def _shift_start_time(self):
        """
        Set work day start depends on week_start_date
        and shift_start_time fields
        """
        if not self.shift_start_time and self.week_start_date:
            shift_start_time = datetime.combine(
                self.week_start_date, time(0, 0, 0)
            )
            self.shift_start_time = shift_start_time
        elif self.shift_start_time and self.week_start_date:
            self.shift_start_time = datetime.combine(
                self.week_start_date, self.shift_start_time.time()
            )
        else:
            self.shift_start_time = None
