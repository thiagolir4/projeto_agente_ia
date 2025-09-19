# 🤖 Agente IA - Análise de Dados MongoDB

Sistema inteligente para análise de dados com interface web, chat conversacional e integração com MongoDB.

## ✨ Funcionalidades

- 📊 **Importação de arquivos CSV** - Upload e processamento de dados
- 🤖 **Chat inteligente com IA** - Análise conversacional dos dados
- 📈 **Análise em tempo real** - Consultas diretas ao MongoDB
- ⚡ **Performance otimizada** - Cache e índices para velocidade
- 🎨 **Interface moderna** - Design responsivo e intuitivo
- 🔍 **Consultas inteligentes** - Interpretação natural de perguntas

## 🚀 Tecnologias

### Backend
- **Python 3.11** - Linguagem principal
- **Flask** - Framework web
- **MongoDB** - Banco de dados NoSQL
- **LangChain** - Framework para IA
- **OpenAI** - Modelo de linguagem
- **FAISS** - Busca vetorial
- **Pandas** - Manipulação de dados

### Frontend
- **HTML5/CSS3** - Interface web
- **JavaScript** - Interatividade
- **Bootstrap** - Design responsivo

## 📋 Pré-requisitos

- Python 3.11+
- MongoDB
- Chave da API OpenAI

## 🚀 Instalação e Execução

### 1. Clone o repositório
```bash
git clone https://github.com/thiagolir4/projeto_agente_ia.git
cd projeto_agente_ia
```

### 2. Instale as dependências
```bash
pip install -r backend/requirements.txt
```

### 3. Configure as variáveis de ambiente
```bash
# Crie um arquivo .env na raiz do projeto
OPENAI_API_KEY=sua_chave_openai_aqui
MONGO_URI=mongodb://localhost:27017/
DB_NAME=dbGrupoOscar
```

### 4. Inicie o MongoDB
```bash
# Windows
net start MongoDB

# Linux/Mac
sudo systemctl start mongod
```

### 5. Execute a aplicação
```bash
python main.py
```

### 6. Acesse a aplicação
- **Interface Web**: http://localhost:5000
- **MongoDB**: localhost:27017

## 🐳 Docker (Recomendado)

### 1. Execute com Docker Compose
```bash
docker-compose up -d
```

### 2. Acesse a aplicação
- **Interface Web**: http://localhost:5000

## 📊 Como Usar

### 1. **Importar Dados**
- Acesse a interface web
- Clique em "Escolher arquivo"
- Selecione um arquivo CSV
- Clique em "Importar para MongoDB"

### 2. **Chat com IA**
- Use a interface de chat
- Faça perguntas sobre os dados
- Exemplos:
  - "Quais são os top 5 SKUs mais frequentes?"
  - "Mostre as lojas com mais devoluções"
  - "Quantos usuários únicos existem?"

### 3. **Visualizar Dados**
- Clique em "Ver Coleção"
- Visualize os dados importados
- Navegue pelos registros

## 🔧 Configuração Avançada

### Variáveis de Ambiente
```bash
# MongoDB
MONGO_URI=mongodb://localhost:27017/
DB_NAME=dbGrupoOscar

# OpenAI
OPENAI_API_KEY=sua_chave_aqui

# Aplicação
FLASK_ENV=development
FLASK_DEBUG=True
```

### Índices MongoDB
O sistema cria automaticamente índices para otimizar consultas:
- SKU
- LOJA
- IDUSUARIO
- DATA_DEVOLUCAO
- TIPOMOVIMENTACAO
- DIFERENCA_VALOR

## 📁 Estrutura do Projeto

```
projeto_agente_ia/
├── main.py                    # Aplicação Flask principal
├── backend/
│   ├── app/
│   │   ├── agents/           # Agente IA
│   │   │   └── mongodb_agent.py
│   │   ├── database/         # Configuração MongoDB
│   │   │   └── db_config.py
│   │   ├── modules/          # Módulos de importação
│   │   │   └── importar_csv.py
│   │   ├── errors/           # Tratamento de erros
│   │   └── utils/            # Utilitários
│   └── requirements.txt      # Dependências Python
├── frontend/
│   ├── templates/            # Templates HTML
│   │   ├── index.html
│   │   └── colecao.html
│   └── static/              # CSS, JS, imagens
│       └── style.css
├── Dockerfile               # Imagem Docker
├── docker-compose.yml       # Orquestração
└── README.md               # Este arquivo
```

## 🎯 Exemplos de Uso

### Consultas Inteligentes
- "Quais são os top 10 SKUs mais frequentes?"
- "Mostre as lojas com mais devoluções em formato de tabela"
- "Quantos registros existem no banco?"
- "Quais usuários fazem mais devoluções?"

### Análise de Dados
- Frequência de SKUs
- Análise por loja
- Análise por usuário
- Análise temporal
- Valores de devolução

## 🐛 Troubleshooting

### Erro de conexão MongoDB
```bash
# Verificar se MongoDB está rodando
net start MongoDB  # Windows
sudo systemctl start mongod  # Linux
```

### Erro OpenAI API
- Verifique se a chave está correta
- Verifique se tem créditos na conta

### Erro de dependências
```bash
# Reinstalar dependências
pip install -r backend/requirements.txt --force-reinstall
```

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT.

## 👨‍💻 Autor

**Thiago Lira**
- GitHub: [@thiagolir4](https://github.com/thiagolir4)

## 🙏 Agradecimentos

- OpenAI pela API de linguagem
- MongoDB pela base de dados
- LangChain pelo framework de IA
- Flask pela simplicidade do backend

---

**⭐ Se este projeto te ajudou, considere dar uma estrela!**
