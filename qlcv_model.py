# -*- coding: utf-8 -*-
from odoo import models, fields,api
from datetime import datetime

class Document(models.Model):
     _name = 'doc.task'
     _description = 'Document'
     _inherit = ['mail.thread']
     name = fields.Char('Name',required=True)
     number = fields.Char('Number')
     sign_date = fields.Datetime('Sign Date')
     sent_date = fields.Datetime('Sent Date')
     arrived_date = fields.Datetime('Arrived Date',default=datetime.today())
     # composer_id = fields.Many2one('hr.employee' , 'Composer')
     # approver_id = fields.Many2one('hr.employee' , 'Approver')
     # sender_id = fields.Many2one('hr.employee' , 'Sender')
     organization = fields.Many2one('res.partner','Organization',required=True)
     department_id = fields.Many2one('hr.department' , 'Department')
     type = fields.Char('Type',required=True, default='Arrived', readonly=True)
     otherinfor = fields.Text('Notes')
     # type_id = fields.Many2one('doc.type','Type',required=True)
     file_id = fields.Binary('File',required=True)
     state = fields.Selection([
          ('draft','Draft'),
          # ('published','Published'),
          ('sent','Email Sent'),
          ('done','Done'),
          ('cancel','Cancelled'),
     ],string='Document Status', readonly=True, copy=False, store=True, default='draft')

     @api.multi
     def action_convert(self):
          for doc in self:
               doc.state = 'done'

     @api.multi
     def action_document_send(self):

              '''
              This function opens a window to compose an email, with the edi sale template message loaded by default
              '''

              self.ensure_one()
              ir_model_data = self.env['ir.model.data']
              try:
                   template_id = ir_model_data.get_object_reference('sale', 'email_template_edi_sale')[1]
              except ValueError:
                   template_id = False
              try:
                   compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
              except ValueError:
                   compose_form_id = False
              ctx = dict()
              ctx.update({
                   'default_model': 'doc.task',
                   'default_res_id': self.ids[0],
                   'default_use_template': bool(template_id),
                   'default_template_id': template_id,
                   'default_composition_mode': 'comment',
                   'mark_so_as_sent': True,
                   'custom_layout': "sale.mail_template_data_notification_email_sale_order"
              })
              return {
                   'type': 'ir.actions.act_window',
                   'view_type': 'form',
                   'view_mode': 'form',
                   'res_model': 'mail.compose.message',
                   'views': [(compose_form_id, 'form')],
                   'view_id': compose_form_id,
                   'target': 'new',
                   'context': ctx,
              }
              for doc in self:
                  doc.state = 'sent'

     @api.multi
     def action_cancel(self):
         for doc in self:
             doc.state = 'cancel'

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
          ('email','Email Sent'),
          ('published', 'Published'),
          ('sent', 'Sent'),
          ('done', 'Done'),
          ('cancel', 'Cancelled'),
     ], string='Document Status', readonly=True, copy=False, store=True, default='draft')

     @api.multi
     def action_resend(self):
          for doc in self:
               doc.state = 'email'

     @api.multi
     def action_document_send(self):
          for doc in self:
               doc.state = 'email'

     @api.multi
     def action_confirm(self):
          for doc in self:
              if doc.state == 'email':
                   doc.state = 'published'
              elif doc.state == 'published':
                   doc.state = 'sent'
              elif doc.state == 'sent':
                   doc.state = 'done'

     @api.multi
     def action_cancel(self):
          for doc in self:
               doc.state = 'cancel'

# class File(models.Model):
#      _name='file.doc'
#      _description = 'File'
#      file = fields.Binary('File', required=True)

     @api.multi
     def import_file(self, cr, uid, ids, context=None):
          fileobj = TemporaryFile('w+')
          fileobj.write(base64.decodestring(data))
          # your treatment
          return True

class Tag(models.Model):
     _name = 'tag.doc'
     _description = 'Document Tag'
     tag_name = fields.Char('Tag Name')
# @api.multi
# def send_mail_template(self):
#      # Now let us find the e-mail template
#      template = self.env.ref('mail_template_demo.example_email_template')
#      self.env['mail.template'].browse(template.id).send_mail(self.id)
