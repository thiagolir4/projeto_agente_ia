"use client";

import { useState } from "react";

export default function FinancePage() {
  const [tickers, setTickers] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleConsult = async () => {
    if (!tickers.trim()) return;

    setIsLoading(true);

    // TODO: Implementar consulta de dados financeiros
    // Por enquanto, apenas simula o carregamento
    setTimeout(() => {
      setIsLoading(false);
      alert(
        "Funcionalidade de consulta financeira será implementada no próximo prompt!"
      );
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto p-6">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Consulta Financeira
          </h1>
          <p className="text-gray-600">
            Consulte dados financeiros em tempo real
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="space-y-6">
            <div>
              <label
                htmlFor="tickers"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Tickers das Ações *
              </label>
              <input
                id="tickers"
                type="text"
                value={tickers}
                onChange={(e) => setTickers(e.target.value)}
                placeholder="Digite os tickers separados por vírgula (ex: AAPL, GOOGL, MSFT)"
                className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                onKeyPress={(e) => e.key === "Enter" && handleConsult()}
              />
              <p className="text-sm text-gray-500 mt-2">
                Separe múltiplos tickers com vírgulas. Use o formato padrão do
                mercado (ex: AAPL para Apple Inc.)
              </p>
            </div>

            <button
              onClick={handleConsult}
              disabled={!tickers.trim() || isLoading}
              className="w-full px-6 py-3 bg-green-600 text-white font-medium rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? "⏳ Consultando..." : "📊 Consultar Dados"}
            </button>

            <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
              <h3 className="text-sm font-medium text-yellow-900 mb-2">
                🚧 Em Desenvolvimento
              </h3>
              <p className="text-sm text-yellow-800">
                A funcionalidade de consulta financeira será implementada no
                próximo prompt. Esta página está preparada para receber a
                integração com APIs de dados financeiros.
              </p>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
              <h3 className="text-sm font-medium text-blue-900 mb-2">
                💡 Funcionalidades Planejadas
              </h3>
              <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
                <li>Consulta de preços em tempo real</li>
                <li>Histórico de preços e volumes</li>
                <li>Indicadores técnicos</li>
                <li>Análise de tendências</li>
                <li>Comparação entre ações</li>
                <li>Alertas de preço</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
