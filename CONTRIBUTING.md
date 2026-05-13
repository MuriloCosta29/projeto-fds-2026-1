# Guia de Contribuição — CESAR School Status

Obrigado por contribuir com o **CESAR School Status**! Este guia explica como configurar o ambiente localmente e como contribuir com o projeto.

---

## Como Rodar o Projeto Localmente

### Pré-requisitos

Antes de começar, você precisa ter instalado:

- [Python 3.11+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/)
- [Google Chrome](https://www.google.com/chrome/) (para rodar os testes E2E)

---

### 1. Clonar o repositório

```bash
git clone https://github.com/seu-usuario/projeto-fds-2026-1.git
cd projeto-fds-2026-1
```

---

### 2. Criar e ativar o ambiente virtual

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
python -m venv .venv
source .venv/bin/activate
```

Você saberá que o ambiente está ativo quando aparecer `(.venv)` no início do terminal.

---

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

Caso o arquivo `requirements.txt` não esteja atualizado, instale manualmente:

```bash
pip install django selenium webdriver-manager whitenoise dj-database-url
```

---

### 4. Configurar o banco de dados

O projeto usa **SQLite** localmente. Para criar as tabelas, rode:

```bash
python manage.py migrate
```

---

### 5. Criar o usuário administrador (TI)

Para acessar as funcionalidades de TI (registrar incidentes, gerenciar, cadastrar alunos), crie um superusuário:

```bash
python manage.py createsuperuser
```

Preencha os campos solicitados:
```
Username: (escolha um nome de usuário)
Email: (seu email)
Password: (sua senha)
```

---

### 6. Rodar o servidor

```bash
python manage.py runserver
```

Acesse o sistema em: [http://localhost:8000](http://localhost:8000)

---

### 7. Rodar os testes E2E

Os testes usam **Selenium** e rodam em modo headless (sem abrir o Chrome) por padrão.

```bash
python manage.py test
```

**Para ver o Chrome abrindo durante os testes**, abra o `test_selenium.py` e comente a linha do headless:

```python
# options.add_argument("--headless")  ← comente essa linha
```

> ⚠️ Lembre de descomentar o `--headless` depois, para o CI funcionar corretamente.

---

### Estrutura do Projeto

```
projeto-fds-2026-1/
├── monitor/               # App principal
│   ├── models.py          # Modelo de Incidente
│   ├── views.py           # Views do sistema
│   ├── urls.py            # Rotas do app
│   ├── backends.py        # Autenticação por email
│   └── templates/         # HTMLs do sistema
├── setup/                 # Configurações do Django
│   └── settings.py
├── static/                # CSS e arquivos estáticos
├── test_selenium.py       # Testes E2E (Selenium)
├── requirements.txt       # Dependências do projeto
└── manage.py
```

---

### Problemas comuns

**`ModuleNotFoundError: No module named 'whitenoise'`**
```bash
pip install whitenoise
```

**`ModuleNotFoundError: No module named 'dj_database_url'`**
```bash
pip install dj-database-url
```

**ChromeDriver com erro de versão**
O projeto usa `webdriver-manager` que instala automaticamente a versão correta. Certifique-se de que o Google Chrome está atualizado.

**`where python` não retorna nada**
O Python não está no PATH. Use diretamente o executável do venv:
```bash
.venv\Scripts\python.exe manage.py runserver
```

---

## Como Contribuir

### 1. Crie uma Branch

Para nova funcionalidade:
```bash
git checkout -b feature/sua-feature
```

Para correção de bug:
```bash
git checkout -b fix/seu-fix
```

---

### 2. Faça suas Alterações

- Escreva código limpo e bem documentado
- Siga as convenções do Python (PEP 8)
- Adicione testes E2E para novas funcionalidades
- Certifique-se de que todos os testes passam antes de commitar

---

### 3. Commit suas Alterações

```bash
git add .
git commit -m "feat: descrição clara da sua alteração"
```

**Convenções de commit:**

| Tipo | Quando usar |
|---|---|
| `feat:` | Nova funcionalidade |
| `fix:` | Correção de bug |
| `docs:` | Alterações na documentação |
| `style:` | Formatação, espaçamento, etc |
| `refactor:` | Refatoração de código |
| `test:` | Adição ou modificação de testes |
| `revert:` | Reverter para versão anterior |
| `ci:` | Alterações no pipeline de CI |

---

### 4. Push para o GitHub

```bash
git push origin feature/sua-feature
```

---

### 5. Abra um Pull Request

- Vá para o repositório no GitHub
- Clique em **"Pull Requests"** → **"New Pull Request"**
- Selecione sua branch
- Descreva suas alterações de forma clara
- Aguarde a revisão

---

## Diretrizes de Código

### Python/Django

- Siga a [PEP 8](https://peps.python.org/pep-0008/)
- Use nomes descritivos para variáveis e funções em português (padrão do projeto)
- Mantenha as views pequenas e focadas
- Proteja rotas sensíveis com `@login_required`

### HTML/CSS

- Use indentação de 4 espaços
- Mantenha o padrão visual laranja do projeto
- Use classes CSS semânticas e consistentes com o restante do sistema

### Testes E2E (Selenium)

- Crie uma classe por história de usuário
- Use `setUp` para criar dados e limpar cookies
- Use `tearDown` para deletar usuários e incidentes criados no teste
- Use a função `clicar()` para todos os cliques em botões (compatível com CI)
- Mantenha o `--headless` ativo para o CI

---

## Reportando Bugs

Ao reportar bugs, inclua:

1. Descrição clara do problema
2. Passos para reproduzir o bug
3. Comportamento esperado vs comportamento atual
4. Screenshots (se aplicável)
5. Ambiente (SO, versão do Python, navegador)

---

## Sugestões de Funcionalidades

Ao sugerir novas funcionalidades:

1. Explique o problema que a funcionalidade resolve
2. Descreva a solução proposta
3. Considere o impacto para alunos e equipe de TI
4. Adicione contexto adicional se necessário

---

## Recursos Úteis

- [Documentação do Django](https://docs.djangoproject.com/)
- [Python PEP 8](https://peps.python.org/pep-0008/)
- [Selenium Documentation](https://selenium-python.readthedocs.io/)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

## Precisa de Ajuda?

- Abra uma [Issue](https://github.com/seu-usuario/projeto-fds-2026-1/issues)
- Entre em contato com os mantenedores do projeto

Obrigado por contribuir! 🚀