{
    'name': 'Office Asset Management',
    'version': '17.0.1.1.0',
    'category': 'Operations/Inventory',
    'summary': 'Manage company assets, employee assignments, and borrowing workflows',
    'description': """
        Custom Odoo ERP module to track office assets, assign items to employees,
        and manage borrowing/returning lifecycles with automated sequences and audit logs.
    """,
    'author': 'Shakila N',
    'depends': ['base', 'hr', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/asset_sequence.xml',
        'views/asset_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}