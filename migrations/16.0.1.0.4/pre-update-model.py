def migrate(cr, version):
    if not version:
        return

    # Atualiza o modelo para todos os usuários que estão usando o modelo antigo
    cr.execute("""
        UPDATE res_users 
        SET odoogpt_openai_model = 'gpt-4o-mini' 
        WHERE odoogpt_openai_model = 'text-davinci-003'
    """)

    # Atualiza o modelo para todas as empresas que estão usando o modelo antigo
    cr.execute("""
        UPDATE res_company 
        SET odoogpt_openai_model = 'gpt-4o-mini' 
        WHERE odoogpt_openai_model = 'text-davinci-003'
    """) 