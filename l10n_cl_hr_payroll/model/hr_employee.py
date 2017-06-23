from odoo import models, fields, api


UPDATE_PARTNER_FIELDS = ['name', 'user_id', 'address_home_id']


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    firstname = fields.Char("Firstname")
    last_name = fields.Char("Last Name")
    middle_name = fields.Char("Middle Name", help='Employees middle name')
    mothers_name = fields.Char("Mothers Name", help='Employees mothers name')





    @api.multi
    @api.onchange('firstname', 'mothers_name', 'middle_name' , 'last_name')
    def get_name(self):
        for employee in self:
            if employee.firstname and employee.last_name:
                employee.name = u" ".join((p for p in (self.last_name, self.mothers_name, self.firstname, self.middle_name) if p))



    @api.model
    def _get_computed_name(self, last_name, firstname):
        """Compute the 'name' field according to splitted data.
        You can override this method to change the order of lastname and
        firstname the computed name"""
        return u" ".join((p for p in (last_name, mothers_name, firstname, middle_name) if p))


