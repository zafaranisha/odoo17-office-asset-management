from odoo import models, fields, api
from odoo.exceptions import ValidationError


class OfficeAsset(models.Model):
    _name = 'office.asset'
    _description = 'Office Asset Item'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'code asc'

    name = fields.Char(string='Asset Name', required=True, tracking=True)
    code = fields.Char(string='Asset Code', required=True, copy=False, readonly=True, default='New')
    category = fields.Selection([
        ('laptop', 'Laptop / PC'),
        ('peripheral', 'Peripheral (Monitor, Mouse, Keyboard)'),
        ('furniture', 'Office Furniture'),
        ('other', 'Other Equipment'),
    ], string='Category', default='laptop', required=True, tracking=True)
    
    purchase_date = fields.Date(string='Purchase Date', default=fields.Date.context_today)
    purchase_value = fields.Float(string='Purchase Value (IDR)', tracking=True)
    
    # Relasi Many2one ke modul bawaan Karyawan (hr.employee)
    employee_id = fields.Many2one('hr.employee', string='Assigned Employee', tracking=True)
    borrow_date = fields.Date(string='Borrow Date', tracking=True)
    
    state = fields.Selection([
        ('available', 'Available'),
        ('borrowed', 'Borrowed'),
        ('maintenance', 'Under Maintenance'),
    ], string='Status', default='available', required=True, tracking=True)
    
    notes = fields.Text(string='Condition & Notes')

    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Asset Code must be unique!')
    ]

    # Override method create() untuk generate kode aset otomatis
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', 'New') == 'New':
                vals['code'] = self.env['ir.sequence'].next_by_code('office.asset.seq') or 'New'
        return super().create(vals_list)

    def action_borrow(self):
        for record in self:
            if not record.employee_id:
                raise ValidationError("Please select an Assigned Employee before borrowing this asset.")
            record.state = 'borrowed'
            if not record.borrow_date:
                record.borrow_date = fields.Date.context_today(self)

    def action_return(self):
        for record in self:
            record.state = 'available'
            record.employee_id = False
            record.borrow_date = False

    def action_maintenance(self):
        for record in self:
            record.state = 'maintenance'


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    asset_ids = fields.One2many(
        'office.asset',
        'employee_id',
        string='Assigned Assets'
    )
    total_asset_value = fields.Float(
        string='Total Borrowed Asset Value (IDR)',
        compute='_compute_total_asset_value',
        store=True
    )

    # Computed field: otomatis menjumlahkan nilai aset yang berstatus 'borrowed'
    @api.depends('asset_ids.purchase_value', 'asset_ids.state')
    def _compute_total_asset_value(self):
        for employee in self:
            borrowed_assets = employee.asset_ids.filtered(lambda a: a.state == 'borrowed')
            employee.total_asset_value = sum(borrowed_assets.mapped('purchase_value'))