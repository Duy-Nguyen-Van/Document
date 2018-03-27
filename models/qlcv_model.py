# -*- coding: utf-8 -*-
from odoo import models, fields,api
from datetime import datetime
# import os
# import re
# import json
# import base64
# import logging
# import mimetypes
#
# from odoo import _
# from odoo import models, api, fields
# from odoo.tools import ustr
# from odoo.tools.mimetypes import guess_mimetype
# from odoo.exceptions import ValidationError, AccessError

from odoo.addons.muk_dms.models import dms_base

class Document(models.Model):
     _name = 'doc.task'
     _description = 'Document'
     _inherit = ['mail.thread','muk_dms.file']
     filename = fields.Char('Name',required=True)
     number = fields.Char('Number',required=True)
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
     # data = fields.Binary(
     #     string='File',
     #     )
     data = fields.Many2one('muk_dms.file','File')
     # filename = fields.Char(
     #     string="Filename",
     #     required=True)
     state = fields.Selection([
          ('draft','Draft'),
          ('sent','Email Sent'),
          ('done','Done'),
          ('cancel','Cancelled'),
     ],string='Document Status', readonly=True, copy=False, store=True, default='draft')
     tag = fields.Many2many('tag.doc', string='Tag')
     directory = fields.Many2one(
         'doc.direct',
         string="Directory",
         ondelete='restrict',
         auto_join=True,
         required=True)

     @api.multi
     def action_document_send(self):
         '''
         This function opens a window to compose an email, with the edi sale template message loaded by default
         '''
         self.ensure_one()
         attachment = {
             'name': ("%s" % self.name),
             'datas': self.data.content,
             'datas_fname': self.name,
             'res_model': 'doc.task',
             'type': 'binary'
         }
         id = self.env['ir.attachment'].create(attachment)
         email_template = self.env.ref('islabdocument.email_template_doc')
         email_template.attachment_ids = False
         email_template.attachment_ids = [(4,id.id)]
         ir_model_data = self.env['ir.model.data']
         try:
             template_id = ir_model_data.get_object_reference('islabdocument', 'email_template_doc')[1]
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

     @api.multi
     def action_convert(self):
          for doc in self:
               doc.state = 'done'
          print 'convert ok'

     @api.multi
     def action_cancel(self):
         for doc in self:
             doc.state = 'cancel'

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
     def action_document_send(self):
         '''
         This function opens a window to compose an email, with the edi sale template message loaded by default
         '''
         self.ensure_one()
         attachment = {
             'name': ("%s" % self.name),
             'datas': self.data.content,
             'datas_fname': self.name,
             'res_model': 'doc.sent',
             'type': 'binary'
         }
         id = self.env['ir.attachment'].create(attachment)
         email_template = self.env.ref('islabdocument.email_template_sent')
         email_template.attachment_ids = False
         email_template.attachment_ids = [(4, id.id)]
         ir_model_data = self.env['ir.model.data']
         try:
             template_id = ir_model_data.get_object_reference('islabdocument', 'email_template_sent')[1]
         except ValueError:
             template_id = False
         try:
             compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
         except ValueError:
             compose_form_id = False
         ctx = dict()
         ctx.update({
             'default_model': 'doc.sent',
             'default_res_id': self.ids[0],
             'default_use_template': bool(template_id),
             'default_template_id': template_id,
             'default_composition_mode': 'comment',
             'mark_so_as_sent': True,
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

class Tag(models.Model):
     _name = 'tag.doc'
     _description = 'Document Tag'
     name = fields.Char('Tag Name')

class MailComposeMessageArrived(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.multi
    def send_mail(self, auto_commit=False):
        if self._context.get('default_model') == 'doc.task' and self._context.get('default_res_id') and self._context.get('mark_so_as_sent'):
            order = self.env['doc.task'].browse([self._context['default_res_id']])
            if order.state == 'draft':
                order.state = 'sent'
            self = self.with_context(mail_post_autofollow=True)
        return super(MailComposeMessageArrived, self).send_mail(auto_commit=auto_commit)

class MailComposeMessageSent(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.multi
    def send_mail(self, auto_commit=False):
        if self._context.get('default_model') == 'doc.sent' and self._context.get('default_res_id') and self._context.get('mark_so_as_sent'):
            order = self.env['doc.sent'].browse([self._context['default_res_id']])
            if order.state == 'draft':
                order.state = 'email'
            self = self.with_context(mail_post_autofollow=True)
        return super(MailComposeMessageSent, self).send_mail(auto_commit=auto_commit)

class Doc_directory(models.Model):
    _name = 'doc.direct'
    _inherit = 'muk_dms.directory'
    files = fields.One2many(
        'doc.task',
        'directory',
        copy=False,
        string="Files")


