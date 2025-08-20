"use client";

import React, { useState } from "react";
import {
  apiUploadCSV,
  apiPreview,
  apiCleaningRun,
  apiVectorsIndex,
  UploadResponse,
  PreviewResponse,
  CleaningResponse,
  VectorsResponse,
} from "@/lib/api";
import DataTable from "./DataTable";

export default function FileUploader() {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isCleaning, setIsCleaning] = useState(false);
  const [isIndexing, setIsIndexing] = useState(false);
  const [uploadResult, setUploadResult] = useState<UploadResponse | null>(null);
  const [previewData, setPreviewData] = useState<PreviewResponse | null>(null);
  const [cleaningResult, setCleaningResult] = useState<CleaningResponse | null>(
    null
  );
  const [indexingResult, setIndexingResult] = useState<VectorsResponse | null>(
    null
  );
  const [sessionId, setSessionId] = useState("");
  const [error, setError] = useState<string>("");

  // Selecionar arquivo
  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile && selectedFile.type === "text/csv") {
      setFile(selectedFile);
      setError("");
      setUploadResult(null);
      setPreviewData(null);
      setCleaningResult(null);
      setIndexingResult(null);
    } else if (selectedFile) {
      setError("Por favor, selecione um arquivo CSV válido.");
      setFile(null);
    }
  };

  // Upload do arquivo
  const handleUpload = async () => {
    if (!file) return;

    setIsUploading(true);
    setError("");

    try {
      const result = await apiUploadCSV(file);
      console.log("Upload result:", result); // Debug
      
      if (result && result.success && result.data) {
        setUploadResult(result);
        // Buscar preview automaticamente
        await fetchPreview(result.data.dataset_id);
      } else {
        throw new Error("Resposta inválida do servidor");
      }
    } catch (error) {
      console.error("Upload error:", error); // Debug
      setError(
        `Erro no upload: ${
          error instanceof Error ? error.message : "Erro desconhecido"
        }`
      );
      setUploadResult(null);
    } finally {
      setIsUploading(false);
    }
  };

  // Buscar preview
  const fetchPreview = async (datasetId: string) => {
    try {
      const preview = await apiPreview(datasetId, 20);
      setPreviewData(preview);
    } catch (error) {
      console.error("Erro ao buscar preview:", error);
    }
  };

  // Executar limpeza
  const handleCleaning = async () => {
    if (!uploadResult?.data.dataset_id) return;

    setIsCleaning(true);
    setError("");

    try {
      const result = await apiCleaningRun(uploadResult.data.dataset_id);
      setCleaningResult(result);
    } catch (error) {
      setError(
        `Erro na limpeza: ${
          error instanceof Error ? error.message : "Erro desconhecido"
        }`
      );
    } finally {
      setIsCleaning(false);
    }
  };

  // Indexar em vetores
  const handleIndexing = async () => {
    if (!uploadResult?.data.dataset_id || !sessionId.trim()) {
      setError("Por favor, insira um Session ID válido.");
      return;
    }

    setIsIndexing(true);
    setError("");

    try {
      const result = await apiVectorsIndex(
        uploadResult.data.dataset_id,
        sessionId.trim()
      );
      setIndexingResult(result);
    } catch (error) {
      setError(
        `Erro na indexação: ${
          error instanceof Error ? error.message : "Erro desconhecido"
        }`
      );
    } finally {
      setIsIndexing(false);
    }
  };

  // Limpar formulário
  const handleReset = () => {
    setFile(null);
    setUploadResult(null);
    setPreviewData(null);
    setCleaningResult(null);
    setIndexingResult(null);
    setSessionId("");
    setError("");
    // Limpar input de arquivo
    const fileInput = document.getElementById("file-input") as HTMLInputElement;
    if (fileInput) fileInput.value = "";
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Upload e Processamento de Dados
        </h1>
        <p className="text-gray-600">
          Faça upload de um arquivo CSV e processe com IA
        </p>
      </div>

      {/* Upload de Arquivo */}
      <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          1. Upload do Arquivo
        </h2>

        <div className="space-y-4">
          <div>
            <label
              htmlFor="file-input"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Selecionar arquivo CSV
            </label>
            <input
              id="file-input"
              type="file"
              accept=".csv"
              onChange={handleFileSelect}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            />
          </div>

          {file && (
            <div className="p-3 bg-blue-50 rounded-md">
              <p className="text-sm text-blue-800">
                <strong>Arquivo selecionado:</strong> {file.name} (
                {(file.size / 1024).toFixed(1)} KB)
              </p>
            </div>
          )}

          <button
            onClick={handleUpload}
            disabled={!file || isUploading}
            className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isUploading ? "⏳ Fazendo upload..." : "📤 Fazer Upload"}
          </button>
        </div>
      </div>

      {/* Resultado do Upload */}
      {uploadResult && uploadResult.data && (
        <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            2. Resultado do Upload
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div className="p-4 bg-green-50 rounded-md">
              <p className="text-sm font-medium text-green-800">Dataset ID</p>
              <p className="text-lg font-bold text-green-900">
                {uploadResult.data.dataset_id || "N/A"}
              </p>
            </div>
            <div className="p-4 bg-blue-50 rounded-md">
              <p className="text-sm font-medium text-blue-800">Registros</p>
              <p className="text-lg font-bold text-blue-900">
                {uploadResult.data.row_count ? uploadResult.data.row_count.toLocaleString() : "N/A"}
              </p>
            </div>
            <div className="p-4 bg-purple-50 rounded-md">
              <p className="text-sm font-medium text-purple-800">Colunas</p>
              <p className="text-lg font-bold text-purple-900">
                {uploadResult.data.columns ? uploadResult.data.columns.length : "N/A"}
              </p>
            </div>
          </div>

          {/* Preview dos dados */}
          {previewData && (
            <div className="mt-6">
              <h3 className="text-lg font-medium text-gray-900 mb-3">
                Preview dos Dados
              </h3>
              <DataTable
                data={previewData.data.preview}
                columns={previewData.data.columns}
                pageSize={10}
              />
            </div>
          )}
        </div>
      )}

      {/* Limpeza de Dados */}
      {uploadResult && uploadResult.data && (
        <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            3. Limpeza de Dados
          </h2>

          <button
            onClick={handleCleaning}
            disabled={isCleaning}
            className="w-full px-4 py-2 bg-yellow-600 text-white rounded-md hover:bg-yellow-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isCleaning ? "⏳ Limpando dados..." : "🧹 Limpar Dados"}
          </button>

          {cleaningResult && (
            <div className="mt-4 p-4 bg-green-50 rounded-md">
              <p className="text-sm text-green-800">
                <strong>Limpeza concluída!</strong>{" "}
                {cleaningResult.data.cleaned_rows} de{" "}
                {cleaningResult.data.original_rows} registros processados.
              </p>
            </div>
          )}
        </div>
      )}

      {/* Indexação em Vetores */}
      {uploadResult && uploadResult.data && (
        <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            4. Indexação em Vetores
          </h2>

          <div className="space-y-4">
            <div>
              <label
                htmlFor="session-id"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Session ID (obrigatório para indexação)
              </label>
              <input
                id="session-id"
                type="text"
                value={sessionId}
                onChange={(e) => setSessionId(e.target.value)}
                placeholder="Ex: sessao_001"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <p className="text-xs text-gray-500 mt-1">
                Este ID será usado para identificar os dados no chat e busca por
                vetores.
              </p>
            </div>

            <button
              onClick={handleIndexing}
              disabled={!sessionId.trim() || isIndexing}
              className="w-full px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isIndexing ? "⏳ Indexando..." : "🔍 Indexar em Vetores"}
            </button>

            {indexingResult && (
              <div className="mt-4 p-4 bg-green-50 rounded-md">
                <p className="text-sm text-green-800">
                  <strong>Indexação concluída!</strong>{" "}
                  {indexingResult.data.indexed_rows} registros indexados para
                  sessão {indexingResult.data.session_id}.
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Botão de Reset */}
      {uploadResult && (
        <div className="text-center">
          <button
            onClick={handleReset}
            className="px-6 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
          >
            🔄 Processar Novo Arquivo
          </button>
        </div>
      )}

      {/* Mensagens de Erro */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <p className="text-sm text-red-800">❌ {error}</p>
        </div>
      )}

      {/* Instruções */}
      <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
        <h3 className="text-lg font-medium text-blue-900 mb-2">
          📋 Instruções
        </h3>
        <ol className="text-sm text-blue-800 space-y-1 list-decimal list-inside">
          <li>Selecione um arquivo CSV válido</li>
          <li>Faça upload e aguarde o processamento</li>
          <li>Visualize o preview dos dados</li>
          <li>Execute a limpeza automática dos dados</li>
          <li>Digite um Session ID e indexe em vetores</li>
          <li>Use o chat para consultar os dados indexados</li>
        </ol>
      </div>
    </div>
  );
}
