# FakeRadar AI — Servidor FastAPI

> Serviço Python FastAPI responsável por detecção de fake news, extração de alegações, checagem de fatos e pontuação de credibilidade usando NLP e LLM.

---

## 🚀 Como rodar o projeto

### 1. Instale as dependências

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Configure o ambiente

```bash
cp .env.example .env
# Preencha as chaves de API no arquivo .env
```

### 3. Execute o servidor

```bash
uvicorn app.main:app --reload --port 8000
```

### 4. Acesse a documentação interativa

Abra `http://localhost:8000/docs` no navegador (Swagger UI).

---

## 📦 Estrutura do Projeto

```
app/
	main.py           # Ponto de entrada FastAPI
	routers/          # Rotas (endpoints)
	services/         # Serviços (NLP, scraping, checagem, etc)
	models/           # Modelos Pydantic
	config/           # Configuração e env
requirements.txt    # Dependências
Dockerfile          # Docker produção
Dockerfile.dev      # Docker desenvolvimento
.env.example        # Exemplo de variáveis de ambiente
```

---

## 🛣️ Endpoints principais

- `GET /ai/health` — Verifica status do serviço
- `POST /ai/analyze` — Analisa artigo/texto, extrai alegações, checa fatos e retorna score de credibilidade

---

## 🧪 Testes

```bash
pytest
```

---

## 📝 Licença

MIT. Livre para uso acadêmico e comercial.
