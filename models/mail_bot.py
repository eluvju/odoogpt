# -*- coding: utf-8 -*-
from odoo import models, _
from odoo.tools import html2plaintext, plaintext2html

class MailBot(models.AbstractModel):
    _inherit = 'mail.bot'
    _name = 'mail.bot'
    _description = 'K.A.R.E.N. Bot'

    def _get_welcome_message(self):
        """Sobrescreve a mensagem de boas-vindas padrão"""
        return _("""Olá! 👋

Eu sou K.A.R.E.N. (Knowledge and Artificial Response Engine Navigator), sua assistente virtual inteligente. 🤖

Estou aqui para ajudar você com:
• Dúvidas sobre o Sistema
• Processos de negócio
• Fluxos de trabalho
• Dicas e melhores práticas
• Suporte técnico básico

Você pode me perguntar qualquer coisa diretamente ou usar o comando /ai em chats em grupo.

Como posso ajudar você hoje? 😊""")

    def _get_answer(self, record, body, values, command=None):
        """Override to handle custom AI responses"""
        # Se for uma mensagem direta para o K.A.R.E.N.
        if record._name == 'mail.channel' and self._is_direct_message_to_odoobot(record, values):
            # Usar o mesmo mecanismo do comando /ai, mas sem necessidade do comando
            if self.env.user.odoogpt_chat_method == 'completion':
                response = self.env['odoogpt.openai.utils'].completition_create(
                    prompt=self._build_prompt_completion(body)
                )
            else:  # default to chat-completion
                response = self.env['odoogpt.openai.utils'].chat_completion_create(
                    messages=self._build_prompt_chat_completion(body)
                )
            
            return plaintext2html(response)
        return super()._get_answer(record, body, values, command)

    def _is_direct_message_to_odoobot(self, record, values):
        """Verifica se é uma mensagem direta para o K.A.R.E.N."""
        if record._name != 'mail.channel':
            return False
        
        # Verifica se é um chat direto com o K.A.R.E.N.
        odoobot_id = self.env['ir.model.data']._xmlid_to_res_id("base.partner_root")
        channel_members = record.channel_partner_ids.ids
        return len(channel_members) == 2 and odoobot_id in channel_members and record.channel_type == 'chat'

    def _build_prompt_completion(self, prompt):
        """Constrói o prompt para a API de Completion"""
        return f"No Sistema: {prompt}{self.env.user.odoogpt_openai_prompt_suffix or ''}"

    def _build_prompt_chat_completion(self, prompt):
        """Constrói o prompt para a API de Chat Completion"""
        system_message = """Você é K.A.R.E.N. (Knowledge and Artificial Response Engine Navigator), 
uma assistente virtual inteligente especializada em ajudar usuários com o Sistema. 
Você deve fornecer respostas úteis sobre o sistema, processos de negócio e funcionalidades, 
sempre mantendo um tom profissional mas amigável."""

        return [
            {'role': 'system', 'content': system_message},
            {'role': 'user', 'content': prompt}
        ] 