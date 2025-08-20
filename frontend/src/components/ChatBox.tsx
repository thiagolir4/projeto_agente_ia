"use client";

import React, { useState, useRef, useEffect } from "react";
import { apiChatData, apiChatInsight, ChatResponse } from "@/lib/api";
import ReactMarkdown from "react-markdown";

interface ChatBoxProps {
  sessionId: string;
  className?: string;
}

interface Message {
  id: string;
  type: "user" | "assistant";
  content: string;
  timestamp: Date;
}

export default function ChatBox({ sessionId, className = "" }: ChatBoxProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [lastDataResponse, setLastDataResponse] = useState<string>("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll para a última mensagem
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Adicionar mensagem
  const addMessage = (type: "user" | "assistant", content: string) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      type,
      content,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, newMessage]);
  };

  // Enviar prompt para análise de dados
  const handleSendPrompt = async () => {
    if (!inputValue.trim() || isLoading) return;

    const prompt = inputValue.trim();
    setInputValue("");
    setIsLoading(true);

    // Adicionar mensagem do usuário
    addMessage("user", prompt);

    try {
      const response: ChatResponse = await apiChatData({
        session_id: sessionId,
        prompt,
      });

      if (response.success && response.data.response) {
        addMessage("assistant", response.data.response);
        setLastDataResponse(response.data.response);
      } else {
        addMessage(
          "assistant",
          "❌ Erro ao processar a solicitação. Tente novamente."
        );
      }
    } catch (error) {
      console.error("Erro ao enviar prompt:", error);
      addMessage(
        "assistant",
        `❌ Erro: ${
          error instanceof Error ? error.message : "Erro desconhecido"
        }`
      );
    } finally {
      setIsLoading(false);
    }
  };

  // Gerar insights
  const handleGenerateInsights = async () => {
    if (!lastDataResponse || isLoading) return;

    setIsLoading(true);

    try {
      const response: ChatResponse = await apiChatInsight({
        session_id: sessionId,
        context: lastDataResponse,
      });

      if (response.success && response.data.insights) {
        addMessage(
          "assistant",
          `## 💡 Insights Gerados\n\n${response.data.insights}`
        );
      } else {
        addMessage("assistant", "❌ Erro ao gerar insights. Tente novamente.");
      }
    } catch (error) {
      console.error("Erro ao gerar insights:", error);
      addMessage(
        "assistant",
        `❌ Erro ao gerar insights: ${
          error instanceof Error ? error.message : "Erro desconhecido"
        }`
      );
    } finally {
      setIsLoading(false);
    }
  };

  // Limpar conversa
  const handleClearChat = () => {
    setMessages([]);
    setLastDataResponse("");
  };

  return (
    <div
      className={`flex flex-col h-full bg-white rounded-lg shadow-lg ${className}`}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            Chat com Agentes IA
          </h3>
          <p className="text-sm text-gray-500">Sessão: {sessionId}</p>
        </div>
        <button
          onClick={handleClearChat}
          className="px-3 py-1 text-sm text-gray-600 bg-gray-100 rounded-md hover:bg-gray-200"
        >
          Limpar Chat
        </button>
      </div>

      {/* Mensagens */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            <p className="text-lg font-medium">Bem-vindo ao Chat!</p>
            <p className="text-sm">
              Faça uma pergunta sobre seus dados para começar.
            </p>
            <p className="text-xs mt-2">
              Exemplo: &quot;Mostre os primeiros 10 registros&quot;
            </p>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${
                message.type === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-3xl rounded-lg px-4 py-2 ${
                  message.type === "user"
                    ? "bg-blue-600 text-white"
                    : "bg-gray-100 text-gray-900"
                }`}
              >
                {message.type === "user" ? (
                  <p>{message.content}</p>
                ) : (
                  <div className="prose prose-sm max-w-none">
                    <ReactMarkdown>{message.content}</ReactMarkdown>
                  </div>
                )}
                <div
                  className={`text-xs mt-1 ${
                    message.type === "user" ? "text-blue-200" : "text-gray-500"
                  }`}
                >
                  {message.timestamp.toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Botão de Insights */}
      {lastDataResponse && (
        <div className="px-4 py-2 border-t border-gray-200">
          <button
            onClick={handleGenerateInsights}
            disabled={isLoading}
            className="w-full px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            💡 Gerar Insights
          </button>
        </div>
      )}

      {/* Input */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex space-x-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && handleSendPrompt()}
            placeholder="Digite sua pergunta sobre os dados..."
            disabled={isLoading}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          />
          <button
            onClick={handleSendPrompt}
            disabled={isLoading || !inputValue.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? "⏳" : "Enviar"}
          </button>
        </div>
      </div>
    </div>
  );
}
