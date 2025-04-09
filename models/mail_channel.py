# -*- coding: utf-8 -*-

from odoo import models, _
from odoo.tools import html2plaintext, plaintext2html

COMMAND_AI = '/ai'

class MailChannel(models.Model):
    _inherit = 'mail.channel'


    def execute_command_ai(self, **kwargs):
        msg = _('Oops! Algo deu errado!')

        partner = self.env.user.partner_id
        body = kwargs.get('body', '').strip()

        try:
            if not body or body == COMMAND_AI or not body.startswith(COMMAND_AI):
                msg = _('Pergunte algo para a IA digitando "/ai " seguido da sua pergunta. Por exemplo "/ai Como posso criar um novo usuário?"')
            else:
                msg = self._execute_command_ai(
                    partner=partner,
                    prompt=html2plaintext(body[len(COMMAND_AI):]).strip()
                )
        except Exception as e:
            msg = _('Desculpe, ocorreu um erro ao processar sua solicitação. Por favor, tente novamente mais tarde. Erro: %s') % str(e)

        # Envia mensagem como SuperUser (K.A.R.E.N.)
        odoobot_id = self.env['ir.model.data']._xmlid_to_res_id("base.partner_root")
        self.with_context(mail_create_nosubscribe=True).sudo().message_post(
            body=msg,
            author_id=odoobot_id,
            message_type='comment',
            subtype_xmlid='mail.mt_comment'
        )


    def _execute_command_ai(self, partner, prompt):
        """Executa o comando /ai"""
        if not prompt:
            return _('Por favor, digite sua pergunta após o comando /ai')

        try:
            if partner.odoogpt_chat_method == 'completion':
                response = self.env['odoogpt.openai.utils'].completition_create(
                    prompt=self._build_prompt_completion(prompt)
                )
            else:  # default to chat-completion
                response = self.env['odoogpt.openai.utils'].chat_completion_create(
                    messages=self._build_prompt_chat_completion(prompt)
                )
            
            return plaintext2html(response)
        except Exception as e:
            return _('Desculpe, ocorreu um erro ao processar sua solicitação. Por favor, tente novamente mais tarde. Erro: %s') % str(e)

    def _build_prompt_completion(self, prompt):
        """Build the message to send to OpenAI Completition api"""
        return '{0}{1}{2}'.format(
            self.env.user.odoogpt_openai_prompt_prefix or '',
            prompt,
            self.env.user.odoogpt_openai_prompt_suffix or ''
        )
    _build_prompt = _build_prompt_completion    # unnecessary backward compatibility

    def _build_prompt_chat_completion(self, prompt):
        """Build the message to send to OpenAI Completition api"""
        return [
            {'role': 'system', 'content': self.env.user.odoogpt_chat_system_message},
            {'role': 'user', 'content': prompt},
        ]



    # UTILS

    def _ping_partners(self, partners):
        return '&nbsp;'.join("""<a href=\"{0}#model=res.partner&amp;id={1}\" class=\"o_mail_redirect\" data-oe-id=\"{1}\" data-oe-model=\"res.partner\" target=\"_blank\">@{2}</a>""".format(
            partner.get_base_url(), partner.id, partner.name
        ) for partner in partners)