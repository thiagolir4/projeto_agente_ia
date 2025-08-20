# Frontend - Projeto Agente IA

## Visão Geral

Frontend Next.js para o sistema de agentes IA, permitindo upload de dados CSV, processamento com IA e chat interativo.

## 🚀 Funcionalidades

### 1. Upload e Processamento de Dados

- **Upload de CSV**: Interface drag & drop para arquivos CSV
- **Preview**: Visualização dos dados antes do processamento
- **Limpeza Automática**: Processamento automático de dados
- **Indexação em Vetores**: Preparação para busca semântica

### 2. Chat com Agentes IA

- **DataAgent**: Análise de dados com respostas em tabelas Markdown
- **InsightAgent**: Geração de insights executivos
- **Gestão de Sessões**: Isolamento de dados por usuário/sessão

### 3. Visualização de Dados

- **DataTable**: Tabela responsiva com paginação local
- **Renderização Markdown**: Suporte completo a tabelas Markdown
- **Interface Responsiva**: Design adaptável para diferentes dispositivos

## 🛠️ Tecnologias

- **Next.js 15**: Framework React com App Router
- **TypeScript**: Tipagem estática para melhor desenvolvimento
- **Tailwind CSS**: Framework CSS utilitário
- **React Markdown**: Renderização de conteúdo Markdown

## 📁 Estrutura do Projeto

```
src/
├── app/                    # Páginas da aplicação
│   ├── upload/            # Upload e processamento de CSV
│   ├── chat/              # Chat com agentes IA
│   ├── finance/           # Consulta financeira (preparado)
│   └── layout.tsx         # Layout principal
├── components/             # Componentes reutilizáveis
│   ├── DataTable.tsx      # Tabela com paginação
│   ├── ChatBox.tsx        # Interface de chat
│   ├── FileUploader.tsx   # Upload e processamento
│   └── Navbar.tsx         # Navegação
└── lib/                   # Utilitários e serviços
    └── api.ts             # Serviços da API
```

## 🚀 Instalação

### 1. Dependências

```bash
npm install
npm install react-markdown
```

### 2. Variáveis de Ambiente

```bash
cp env.local.example .env.local
# Edite .env.local com suas configurações
```

### 3. Executar

```bash
npm run dev
```

## 🔧 Configuração

### Variáveis de Ambiente

- `NEXT_PUBLIC_API_BASE`: URL base da API backend (padrão: http://localhost:8000)

### Tailwind CSS

O projeto já está configurado com Tailwind CSS. Para personalizar:

```bash
npm install @tailwindcss/typography
```

## 📱 Páginas

### `/upload`

- Upload de arquivos CSV
- Preview dos dados
- Processamento automático
- Indexação em vetores

### `/chat`

- Chat com agentes IA
- Requer Session ID
- Renderização de tabelas Markdown
- Geração de insights

### `/finance`

- Preparado para consultas financeiras
- Será implementado no próximo prompt

## 🔄 Fluxo de Uso

1. **Upload**: Faça upload de um arquivo CSV
2. **Processamento**: Execute limpeza automática
3. **Indexação**: Digite um Session ID e indexe em vetores
4. **Chat**: Use o chat para consultar os dados
5. **Insights**: Gere análises executivas automaticamente

## 🎯 Critérios de Aceite

✅ **Upload CSV**: Funcional e com preview  
✅ **Limpeza**: Processamento automático implementado  
✅ **Indexação**: Sistema de vetores funcional  
✅ **Chat**: Tabelas Markdown renderizadas corretamente  
✅ **Interface**: Responsiva e intuitiva

## 🧪 Testes

### Teste Manual

1. Acesse `/upload`
2. Faça upload de um CSV
3. Execute limpeza e indexação
4. Vá para `/chat` com o Session ID
5. Faça perguntas sobre os dados
6. Verifique se as tabelas Markdown são renderizadas

### Verificação de Funcionalidades

- [ ] Upload de CSV funciona
- [ ] Preview dos dados é exibido
- [ ] Limpeza automática executa
- [ ] Indexação em vetores funciona
- [ ] Chat responde com tabelas Markdown
- [ ] Botão de insights gera análises
- [ ] Interface é responsiva

## 🚧 Próximos Passos

1. **Integração Financeira**: Conectar com APIs de dados financeiros
2. **Autenticação**: Sistema de login e usuários
3. **Histórico**: Armazenamento de conversas
4. **Exportação**: Download de análises em PDF/Excel
5. **Notificações**: Alertas em tempo real

## 📞 Suporte

Para dúvidas ou problemas:

1. Verifique se o backend está rodando
2. Confirme as variáveis de ambiente
3. Verifique o console do navegador
4. Teste os endpoints da API diretamente

## 📄 Licença

Este projeto faz parte do sistema Projeto Agente IA.

