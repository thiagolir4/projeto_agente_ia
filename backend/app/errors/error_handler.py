class ImportErrorHandler:
    """
    Classe responsável por centralizar e exibir mensagens de erro de forma amigável.
    """

    @staticmethod
    def link_invalido(url: str):
        print(f"❌ O link fornecido não é válido para importação: {url}")
        print("   ➡️ Informe um link público do Google Sheets no formato:")
        print("   https://docs.google.com/spreadsheets/d/<ID>/edit?gid=<GID>")

    @staticmethod
    def arquivo_invalido(caminho: str):
        print(f"❌ O arquivo informado não é válido ou não existe: {caminho}")
        print("   ➡️ Verifique se o caminho está correto e se é um arquivo .csv")

    @staticmethod
    def erro_conexao(detalhe: str = ""):
        print("❌ Erro ao conectar-se à internet ou ao Google Sheets.")
        if detalhe:
            print(f"   Detalhe: {detalhe}")
        print("   ➡️ Verifique sua conexão e tente novamente.")

    @staticmethod
    def erro_mongo(detalhe: str = ""):
        print("❌ Erro ao inserir dados no MongoDB.")
        if detalhe:
            print(f"   Detalhe: {detalhe}")
        print("   ➡️ Verifique a conexão com o banco e as credenciais.")

    @staticmethod
    def erro_generico(e: Exception):
        print("❌ Ocorreu um erro inesperado durante a importação.")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Detalhe: {e}")
