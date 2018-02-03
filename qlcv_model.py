# -*- coding: utf-8 -*-
from odoo import models, fields,api
from datetime import datetime

class Document(models.Model):
     _name = 'doc.task'
     _description = 'Document'
     _inherit = ['mail.thread']
     name = fields.Char('Name',required=True)
     # number = fields.Char('Number')
     sign_date = fields.Datetime('Sign Date')
     sent_date = fields.Datetime('Sent Date')
     arrived_date = fields.Datetime('Arrived Date',default=datetime.today())
     # composer_id = fields.Many2one('hr.employee' , 'Composer')
     # approver_id = fields.Many2one('hr.employee' , 'Approver')
     # sender_id = fields.Many2one('hr.employee' , 'Sender')
     customer = fields.Many2one('res.partner','Customer',required=True)
     department_id = fields.Many2one('hr.department' , 'Department')
     type = fields.Char('Type',required=True, default='Arrived', readonly=True)
     # notes = fields.Text('Note')
     # type_id = fields.Many2one('doc.type','Type',required=True)
     file = fields.Binary('File',required=True)
     state = fields.Selection([
          ('draft','Draft'),
          # ('published','Published'),
          # ('sent','Sent'),
          ('done','Done'),
     ],string='Document Status', readonly=True, copy=False, store=True, default='draft')

# class Department(models.Model):
#      _name = 'department.task'
#      _description = 'Department'
#      _inherit = ['mail.thread']
#      iden = fields.Char('ID',required=True)
#      name = fields.Char('Name',required=True)

# class Document_Type(models.Model):
#      _name = 'doc.type'
#      _description = 'Document Type'
#      name = fields.Char('Name',required=True)
#      des = fields.Char('Description')

class Document_Sent(models.Model):
     _inherit = 'doc.task'
     _name = 'doc.sent'
     type = fields.Char('Type', required=True, default='Sent', readonly=True)
     composer_id = fields.Many2one('hr.employee', 'Composer')
     approver_id = fields.Many2one('hr.employee', 'Approver')
     sender_id = fields.Many2one('hr.employee', 'Sender')
     state = fields.Selection([
          ('draft', 'Draft'),
          ('published', 'Published'),
          ('sent', 'Sent'),
          ('done', 'Done'),
     ], string='Document Status', readonly=True, copy=False, store=True, default='draft')

@api.multi
def import_file(self, cr, uid, ids, context=None):
    fileobj = TemporaryFile('w+')
    fileobj.write(base64.decodestring(data))
    # your treatment
    return True


@api.multi
def send_mail_template(self):
     # Now let us find the e-mail template
     template = self.env.ref('mail_template_demo.example_email_template')
     self.env['mail.template'].browse(template.id).send_mail(self.id)






