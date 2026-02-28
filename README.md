# Vehicle Management API

Serviço principal de gerenciamento de veículos - Tech Challenge Fase 4 (FIAP/SOAT)

## Descrição

Este é o **serviço principal**, responsável por:

- ✅ Cadastrar veículos para venda (marca, modelo, ano, cor, preço)
- ✅ Editar dados do veículo
- ✅ Listar veículos (ordenados por preço)
- ✅ Autenticação JWT (registro e login de usuários)

## Arquitetura

Este serviço opera com **dois bancos de dados PostgreSQL separados**:

- **tech_challenge**: Dados de veículos (transacional)
- **tech_challenge_auth**: Dados de usuários (autenticação)

A comunicação com o **serviço de vendas** é feita via **requisições HTTP síncronas**.

```
┌─────────────────────┐         HTTP          ┌──────────────────────┐
│  Vehicle Management │ ◄──────────────────►  │  Vehicle Sales API   │
│    API (porta 8000) │                       │    (porta 8001)      │
└─────────┬───────────┘                       └──────────┬───────────┘
          │                                              │
          │                                              │
          ▼                                              ▼
┌─────────────────────┐                       ┌──────────────────────┐
│   PostgreSQL        │                       │   PostgreSQL         │
│   tech_challenge    │                       │   vehicle_sales      │
│   tech_challenge_auth│                      │   (porta 5433)       │
│   (porta 5432)      │                       └──────────────────────┘
└─────────────────────┘
```

## Stack Tecnológica

- **Linguagem:** Python 3.12
- **Framework:** FastAPI
- **Banco de Dados:** PostgreSQL (2 bancos separados)
- **ORM:** SQLAlchemy (Async)
- **Autenticação:** JWT (python-jose) + BCrypt (passlib)
- **Gerenciamento de Dependências:** Poetry
- **Infraestrutura:** Docker & Docker Compose
- **CI/CD:** GitHub Actions

## Como Rodar Localmente

### Pré-requisitos

- Docker e Docker Compose instalados

### Com Docker Compose

1. Construa e inicie o serviço:
   ```bash
   docker-compose up --build
   ```

2. A API estará disponível em: `http://localhost:8000`
3. Documentação Swagger: `http://localhost:8000/docs`

### Desenvolvimento Local (sem Docker)

1. Instale o Poetry:
   ```bash
   pip install poetry
   ```

2. Instale as dependências:
   ```bash
   poetry install
   ```

3. Execute a aplicação:
   ```bash
   poetry run uvicorn app.main:app --reload --port 8000
   ```

   *Nota: Rodando localmente, a aplicação usará SQLite (`vehicles.db` e `auth.db`).*

## Endpoints

### Veículos

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/v1/vehicles/` | Cadastrar veículo para venda |
| GET | `/api/v1/vehicles/` | Listar veículos (ordenados por preço) |
| GET | `/api/v1/vehicles/{id}` | Buscar veículo por ID |
| PUT | `/api/v1/vehicles/{id}` | Editar dados do veículo |
| DELETE | `/api/v1/vehicles/{id}` | Remover veículo |

### Autenticação

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/auth/register` | Registrar novo usuário |
| POST | `/auth/login` | Autenticar e obter token JWT |
| GET | `/auth/me` | Dados do usuário autenticado |

## Exemplos de Uso

### Cadastrar Veículo

```bash
curl -X POST http://localhost:8000/api/v1/vehicles/ \
  -H "Content-Type: application/json" \
  -d '{
    "marca": "Toyota",
    "modelo": "Corolla",
    "ano": 2023,
    "cor": "Preto",
    "preco": 95000.00
  }'
```

**Resposta:**
```json
{
  "id": 1,
  "marca": "Toyota",
  "modelo": "Corolla",
  "ano": 2023,
  "cor": "Preto",
  "preco": 95000.00,
  "status": "DISPONIVEL",
  "data_cadastro": "2024-01-15T10:30:00"
}
```

### Editar Veículo

```bash
curl -X PUT http://localhost:8000/api/v1/vehicles/1 \
  -H "Content-Type: application/json" \
  -d '{
    "preco": 89000.00,
    "cor": "Cinza"
  }'
```

### Registrar Usuário

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@example.com",
    "password": "senhaSegura123",
    "full_name": "Nome Completo"
  }'
```

### Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@example.com",
    "password": "senhaSegura123"
  }'
```

**Resposta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## Testes

### Executar Testes

```bash
poetry run pytest tests/ -v
```

### Executar Testes com Cobertura

```bash
poetry run pytest tests/ -v --cov=app --cov-report=html --cov-report=term
```

O relatório de cobertura HTML será gerado em `htmlcov/index.html`.

### Requisito de Cobertura

O CI/CD está configurado para **falhar se a cobertura for menor que 80%**.

## Infraestrutura Kubernetes

O projeto inclui manifests Kubernetes prontos para deploy em `k8s/`:

- **`k8s/deployment.yaml`**: Deployment com 2 réplicas, health checks (readiness/liveness), limites de recursos e variáveis de ambiente via Secrets
- **`k8s/service.yaml`**: Service do tipo LoadBalancer expondo a porta 8000

### Aplicar Manifests

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

### Verificar Status

```bash
kubectl get pods -n tech-challenge -l app=vehicle-management-api
kubectl get svc -n tech-challenge -l app=vehicle-management-api
```

## CI/CD

O pipeline de CI/CD (GitHub Actions) executa:

1. **Lint & Test**: Executa testes com validação de cobertura mínima de 80%
2. **Build Docker**: Constrói a imagem Docker
3. **Security Scan**: Analisa vulnerabilidades com Trivy
4. **Deploy**: Aplica os manifests Kubernetes (`k8s/deployment.yaml` e `k8s/service.yaml`) em merges para `main`

### Gatilho de Deploy

O deploy é executado automaticamente em **merges para a branch `main`** (via Pull Request).

## Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `DATABASE_URL` | URL do banco PostgreSQL (veículos) | `sqlite+aiosqlite:///./vehicles.db` |
| `AUTH_DATABASE_URL` | URL do banco PostgreSQL (auth) | `sqlite+aiosqlite:///./auth.db` |
| `SALES_SERVICE_URL` | URL do serviço de vendas | `http://localhost:8001` |
| `SECRET_KEY` | Chave secreta para JWT | `development-secret-key` |

## Estrutura do Projeto

```
vehicle-management-api/
├── app/
│   ├── core/
│   │   ├── config.py          # Configurações
│   │   ├── security.py        # JWT, BCrypt
│   │   └── deps.py            # Dependencies (auth)
│   ├── models/
│   │   ├── vehicle.py         # Model Vehicle
│   │   └── user.py            # Model User (auth separado)
│   ├── routers/
│   │   ├── vehicles.py        # CRUD veículos
│   │   └── auth.py            # Registro, Login
│   ├── schemas/
│   │   └── schemas.py         # DTOs Pydantic
│   ├── services/
│   │   ├── vehicle_service.py # Lógica de veículos
│   │   └── user_service.py    # Lógica de auth
│   ├── database.py
│   └── main.py
├── tests/
│   ├── conftest.py
│   ├── test_main.py
│   ├── test_vehicles.py
│   └── test_auth.py
├── .github/workflows/ci.yml
├── k8s/
│   ├── deployment.yaml
│   └── service.yaml
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── README.md
```

## Licença

MIT
