# 🤖 Sistema de Análise Inteligente de Dados

Um sistema que permite analisar dados de forma inteligente através de uma interface web simples e um assistente de IA conversacional.

## ✨ O que este sistema faz?

Este sistema foi criado para facilitar a análise de dados para pessoas que não têm conhecimento técnico avançado. Com ele você pode:

- 📊 **Importar dados** de arquivos CSV ou planilhas do Google Sheets
- 🤖 **Conversar com uma IA** que entende suas perguntas em linguagem natural
- 📈 **Visualizar dados** em tabelas organizadas
- 💡 **Obter insights** automaticamente dos seus dados

## 🔄 Como funciona?

1. 📤 **Você importa seus dados** (arquivos CSV ou links do Google Sheets)
2. 🗄️ **O sistema organiza tudo** no banco de dados
3. 💬 **Você faz perguntas** como "Quais são os produtos mais vendidos?"
4. 🧠 **A IA analisa e responde** de forma clara e objetiva

## 📋 O que você precisa para usar?

### Pré-requisitos básicos:

- 🐍 **Python 3.11 ou superior** (linguagem de programação)
- 🍃 **MongoDB** (banco de dados para armazenar seus dados)
- 🔑 **Chave da API OpenAI** (para o assistente de IA funcionar)

### Como obter o que precisa:

🐍 **Python**: Baixe em [python.org](https://www.python.org/downloads/)

🍃 **MongoDB**: Baixe em [mongodb.com](https://www.mongodb.com/try/download/community)

🔑 **Chave OpenAI**: Crie uma conta em [openai.com](https://openai.com) e gere uma API key

## 🚀 Instalação passo a passo

### 1. 📥 Baixe o projeto

```bash
git clone https://github.com/seu-usuario/projeto_agente_ia.git
cd projeto_agente_ia
```

### 2. 📦 Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. ⚙️ Configure as variáveis de ambiente

Crie um arquivo chamado `.env` na pasta principal do projeto com o seguinte conteúdo:

```
OPENAI_API_KEY=sua_chave_openai_aqui
MONGO_URI=mongodb://localhost:27017/
DB_NAME=dbGrupoOscar
```

### 4. 🍃 Inicie o MongoDB

**Windows:**

```bash
net start MongoDB
```

**Linux/Mac:**

```bash
sudo systemctl start mongod
```

### 5. ▶️ Execute a aplicação

```bash
python main.py
```

### 6. 🌐 Acesse no navegador

Abra seu navegador e vá para: `http://localhost:5000`

## 💻 Como usar o sistema

### 📊 Importando dados

1. Na página principal, você verá uma seção "Importação de CSV"
2. Você pode:
   - 🔗 **Colar um link** do Google Sheets
   - 📁 **Enviar um arquivo CSV** do seu computador
3. Clique em "Importar" e aguarde a importação

### 🤖 Conversando com a IA

1. Na seção "Chat com Agente IA", digite sua pergunta
2. Exemplos de perguntas que você pode fazer:
   - 📈 "Quantos registros temos no total?"
   - 🏆 "Quais são os top 5 produtos mais frequentes?"
   - 🏪 "Mostre as lojas com mais movimentações"
   - 👥 "Quantos usuários únicos existem?"
   - 💰 "Qual o valor total das devoluções?"

### 👁️ Visualizando dados

1. Na lista "Coleções existentes", clique no nome da sua coleção
2. Você verá uma tabela com todos os dados importados
3. Use a paginação para navegar entre os registros

## 💬 Exemplos de perguntas que você pode fazer

### 📊 Análise geral:

- 📈 "Quantos registros temos?"
- 📋 "Quais colunas existem nos dados?"
- 📝 "Mostre um resumo dos dados"

### 🛍️ Análise de produtos:

- 🏆 "Quais são os produtos mais vendidos?"
- 🔢 "Quantos tipos diferentes de produtos temos?"
- 📊 "Mostre os produtos com mais movimentações"

### 🏪 Análise de lojas:

- 🥇 "Qual loja tem mais movimentações?"
- 🏢 "Quantas lojas diferentes temos?"
- 📈 "Mostre o ranking das lojas por volume"

### 👥 Análise de usuários:

- 🔢 "Quantos usuários únicos temos?"
- 👤 "Quais usuários fazem mais movimentações?"
- ⭐ "Mostre os usuários mais ativos"

## 📁 Estrutura do projeto

```
projeto_agente_ia/
├── main.py                    # Arquivo principal da aplicação
├── requirements.txt           # Lista de dependências
├── backend/                   # Código do servidor
│   └── app/
│       ├── agents/           # Assistente de IA
│       ├── database/         # Configuração do banco
│       ├── modules/          # Funcionalidades principais
│       └── utils/            # Ferramentas auxiliares
└── frontend/                 # Interface web
    ├── templates/            # Páginas HTML
    └── static/               # Estilos CSS
```

## 🔧 Resolvendo problemas comuns

### ❌ Erro: "MongoDB não está rodando"

**✅ Solução:** Inicie o MongoDB:

- Windows: `net start MongoDB`
- Linux/Mac: `sudo systemctl start mongod`

### 🔑 Erro: "Chave da OpenAI inválida"

**✅ Solução:**

1. Verifique se a chave está correta no arquivo `.env`
2. Confirme se você tem créditos na conta OpenAI

### 📦 Erro: "Dependências não encontradas"

**✅ Solução:** Reinstale as dependências:

```bash
pip install -r requirements.txt --force-reinstall
```

### 🌐 Erro: "Porta 5000 já está em uso"

**✅ Solução:**

1. Feche outros programas que possam estar usando a porta 5000
2. Ou mude a porta no arquivo `main.py`

## 🛠️ Tecnologias utilizadas

- 🐍 **Python**: Linguagem principal
- 🌐 **Flask**: Framework para criar a interface web
- 🍃 **MongoDB**: Banco de dados para armazenar os dados
- 🤖 **OpenAI**: API para o assistente de IA
- 📊 **Pandas**: Para processar arquivos CSV
- 🎨 **Bootstrap**: Para o design da interface

## 📄 Licença

Este projeto está sob a licença MIT, o que significa que você pode usar, modificar e distribuir livremente.
