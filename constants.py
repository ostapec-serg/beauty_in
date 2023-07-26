import datetime

STATE_LIST = [
    ("draft", "Draft"),
    ("active", "Active"),
    ("done", "Done")
]

MASTER_STATE_LIST = [
    ("draft", "Draft"),
    ("active", "Active"),
    ("arch", "Arch")
]

GENDER_LIST = [
    ('man', 'Man'),
    ('woman', 'Woman'),
    ('else', 'Else')
]

EMPLOYEE_LIST = [
    ('master', 'Master'),
    ('administration', 'Administration'),
]

# Duration of one visit to doctor. -> hours, minutes, seconds.
VISIT_DURATION = datetime.timedelta(
    hours=00, minutes=30, seconds=00
)
APPOINTMENT_DURATION = [
    ("10", '10 min'),
    ("15", '15 min'),
    ("30", '30 min'),
    ("60", '60 min')
]

# Duration of one doctor shift. -> hours, minutes, second.
WORK_SHIFT_DURATION = [
    ("1", '1 hour'),
    ("2", '2 hours'),
    ("3", '3 hours'),
    ("4", '4 hours'),
    ("5", '5 hours'),
    ("6", '6 hours'),
    ("7", '7 hours'),
    ("8", '8 hours')
]

delta = datetime.timedelta(seconds=1)
