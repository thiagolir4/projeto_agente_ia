import Link from "next/link";

export default function Home() {
  return (
    <div className="space-y-8">
      <section className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Bem-vindo ao Projeto Agente IA
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Uma plataforma completa para análise de dados, chat com IA e upload de
          arquivos. Explore as funcionalidades através dos cartões abaixo.
        </p>
      </section>

      <section className="grid md:grid-cols-3 gap-6">
        <Link
          href="/chat"
          className="card text-center hover:shadow-lg hover:scale-105 transition-all duration-200 cursor-pointer group bg-gradient-to-br from-purple-50 to-white hover:from-purple-100"
        >
          <div className="text-4xl mb-4 group-hover:scale-110 transition-transform duration-200">
            💬
          </div>
          <h3 className="text-xl font-semibold mb-2 text-purple-800">
            Chat com IA
          </h3>
          <p className="text-gray-600">
            Converse com nossa IA para obter insights e respostas inteligentes.
          </p>
          <div className="mt-4 text-sm text-purple-600 font-medium">
            Clique para começar →
          </div>
        </Link>

        <Link
          href="/upload"
          className="card text-center hover:shadow-lg hover:scale-105 transition-all duration-200 cursor-pointer group bg-gradient-to-br from-yellow-50 to-white hover:from-yellow-100"
        >
          <div className="text-4xl mb-4 group-hover:scale-110 transition-transform duration-200">
            📁
          </div>
          <h3 className="text-xl font-semibold mb-2 text-yellow-800">
            Upload de Arquivos
          </h3>
          <p className="text-gray-600">
            Faça upload de documentos para análise e processamento.
          </p>
          <div className="mt-4 text-sm text-yellow-600 font-medium">
            Clique para começar →
          </div>
        </Link>

        <Link
          href="/finance"
          className="card text-center hover:shadow-lg hover:scale-105 transition-all duration-200 cursor-pointer group bg-gradient-to-br from-green-50 to-white hover:from-green-100"
        >
          <div className="text-4xl mb-4 group-hover:scale-110 transition-transform duration-200">
            📊
          </div>
          <h3 className="text-xl font-semibold mb-2 text-green-800">
            Análise Financeira
          </h3>
          <p className="text-gray-600">
            Visualize e analise dados financeiros de forma intuitiva.
          </p>
          <div className="mt-4 text-sm text-green-600 font-medium">
            Clique para começar →
          </div>
        </Link>
      </section>
    </div>
  );
}
