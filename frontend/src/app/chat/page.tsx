"use client";

import { useState } from "react";
import ChatBox from "@/components/ChatBox";

export default function ChatPage() {
  const [sessionId, setSessionId] = useState("");
  const [isStarted, setIsStarted] = useState(false);

  const handleStartChat = () => {
    if (sessionId.trim()) {
      setIsStarted(true);
    }
  };

  const handleReset = () => {
    setIsStarted(false);
    setSessionId("");
  };

  if (!isStarted) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-2xl mx-auto p-6">
          <div className="bg-white rounded-lg shadow-lg p-8">
            <div className="text-center mb-8">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Chat com Agentes IA
              </h1>
              <p className="text-gray-600">
                Conecte-se com seus dados indexados através de conversa natural
              </p>
            </div>

            <div className="space-y-6">
              <div>
                <label
                  htmlFor="session-id"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Session ID *
                </label>
                <input
                  id="session-id"
                  type="text"
                  value={sessionId}
                  onChange={(e) => setSessionId(e.target.value)}
                  placeholder="Digite o Session ID usado na indexação (ex: sessao_001)"
                  className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  onKeyPress={(e) => e.key === "Enter" && handleStartChat()}
                />
                <p className="text-sm text-gray-500 mt-2">
                  Este ID deve ser o mesmo usado ao indexar seus dados em
                  vetores.
                </p>
              </div>

              <button
                onClick={handleStartChat}
                disabled={!sessionId.trim()}
                className="w-full px-6 py-3 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                🚀 Iniciar Chat
              </button>

              <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
                <h3 className="text-sm font-medium text-blue-900 mb-2">
                  💡 Como usar:
                </h3>
                <ol className="text-sm text-blue-800 space-y-1 list-decimal list-inside">
                  <li>
                    Primeiro, faça upload e indexe seus dados na página de
                    Upload
                  </li>
                  <li>Anote o Session ID usado na indexação</li>
                  <li>Digite o Session ID aqui e inicie o chat</li>
                  <li>Faça perguntas sobre seus dados em linguagem natural</li>
                  <li>
                    Use o botão &quot;Gerar Insights&quot; para análises
                    executivas
                  </li>
                </ol>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Chat com Agentes IA
            </h1>
            <p className="text-gray-600">Sessão: {sessionId}</p>
          </div>
          <button
            onClick={handleReset}
            className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
          >
            🔄 Nova Sessão
          </button>
        </div>

        <div className="h-[800px]">
          <ChatBox sessionId={sessionId} />
        </div>
      </div>
    </div>
  );
}
