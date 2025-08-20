export default function Home() {
  return (
    <div className="space-y-8">
      <section className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Bem-vindo ao Projeto Agente IA
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Uma plataforma completa para análise de dados, chat com IA e upload de
          arquivos. Explore as funcionalidades através do menu de navegação.
        </p>
      </section>

      <section className="grid md:grid-cols-3 gap-6">
        <div className="card text-center">
          <div className="text-4xl mb-4">💬</div>
          <h3 className="text-xl font-semibold mb-2">Chat com IA</h3>
          <p className="text-gray-600">
            Converse com nossa IA para obter insights e respostas inteligentes.
          </p>
        </div>

        <div className="card text-center">
          <div className="text-4xl mb-4">📁</div>
          <h3 className="text-xl font-semibold mb-2">Upload de Arquivos</h3>
          <p className="text-gray-600">
            Faça upload de documentos para análise e processamento.
          </p>
        </div>

        <div className="card text-center">
          <div className="text-4xl mb-4">📊</div>
          <h3 className="text-xl font-semibold mb-2">Análise Financeira</h3>
          <p className="text-gray-600">
            Visualize e analise dados financeiros de forma intuitiva.
          </p>
        </div>
      </section>

      <section className="text-center">
        <h2 className="text-2xl font-semibold mb-4">Status da API</h2>
        <div className="inline-flex items-center px-4 py-2 bg-green-100 text-green-800 rounded-full">
          <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
          API Online
        </div>
      </section>
    </div>
  );
}
