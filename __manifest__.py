# See LICENSE file for full copyright and licensing details.
{
    'name': 'Beauty',
    'version': '16.0.0.0.0',
    'category': 'Customization',
    'summary': 'Maintaining records of masters and customers',

    'author': 'Ostapets Sergii',
    'website': 'https://t.me/ostapec_serg',

    'depends': [
        'hr',
    ],

    'data': [
        'security/beauty_groups.xml',
        'security/ir.model.access.csv',
        'data/beauty_in_specialty_data.xml',
        'data/beauty_in_demo.xml',
        'views/beauty_in_menus.xml',
        'wizard/create_appointment.xml',
        'wizard/week_schedule.xml',
        'views/specialty_views.xml',
        'views/master_views.xml',
        'views/location_views.xml',
        'views/service_views.xml',
        'views/appointment_views.xml',
        'views/master_schedule_views.xml',
        'reports/master_report_templates.xml',
        'reports/report.xml',
    ],

    #   'demo': [
    #      'data/beauty_in_demo.xml',
    #   ],

    'images': [
        'static/description/icon.png',
    ],

    'currency': 'EUR',
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
