# BigCousin

Um bot para Discord inspirado no Backloggd, focado em avaliação e organização de jogos diretamente dentro do Discord.

## Funcionalidades

- **Biblioteca pessoal** — Adicione jogos usando a API RAWG
- **Avaliações** — Dê notas de 1 a 10 para seus jogos
- **Reviews** — Escreva reviews detalhadas
- **Backlog** — Gerencie sua lista de jogos para jogar
- **Favoritos** — Marque seus jogos preferidos
- **Perfil** — Visualize estatísticas, jogos recentes e mais

## Stack

| Tecnologia | Versão |
|-----------|--------|
| Python | 3.11+ |
| discord.py | 2.4+ |
| SQLAlchemy | 2.0+ (assíncrono) |
| SQLite (aiosqlite) | — |
| RAWG API | v1 |

## Estrutura do Projeto

```
BigCousin/
├── main.py               # Entry point do bot
├── commands/             # Comandos Slash (Cogs)
│   ├── profile.py        # /profile
│   ├── games.py          # /addgame, /games
│   ├── rate.py           # /rate
│   ├── review.py         # /review
│   ├── backlog.py        # /backlog add|remove|list
│   └── favorite.py       # /favorite
├── database/             # Camada de dados
│   ├── models.py         # Modelos ORM (User, Game, Rating, Review, Backlog, Favorite)
│   └── connection.py     # Engine e sessão assíncrona
├── services/             # Lógica de negócio
│   ├── rawg_api.py       # Cliente RAWG com cache
│   ├── user_service.py
│   ├── game_service.py
│   ├── rating_service.py
│   ├── review_service.py
│   ├── backlog_service.py
│   └── favorite_service.py
├── utils/                # Utilitários
│   ├── embeds.py         # Templates de embed
│   ├── paginator.py      # Paginação com botões
│   ├── autocomplete.py   # Autocomplete para comandos
│   ├── errors.py         # Tratamento de erros
│   └── __init__.py
├── assets/               # Recursos visuais
├── data/                 # Banco SQLite (criado em runtime)
├── .env.example
├── requirements.txt
└── README.md
```

## Pré-requisitos

- Python 3.11 ou superior
- Uma aplicação no [Discord Developer Portal](https://discord.com/developers/applications)
- Uma chave de API da [RAWG](https://rawg.io/apidocs)

## Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/bigcousin.git
cd bigcousin
```

### 2. Crie um ambiente virtual

```bash
python -m venv venv
```

- Windows:
  ```bash
  venv\Scripts\activate
  ```
- Linux/macOS:
  ```bash
  source venv/bin/activate
  ```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Copie o arquivo de exemplo e edite com suas credenciais:

```bash
cp .env.example .env
```

Conteúdo do `.env`:

```
DISCORD_TOKEN=seu_token_do_discord_aqui
RAWG_API_KEY=sua_chave_da_rawg_api_aqui
```

**Obtendo o token do Discord:**
1. Acesse [Discord Developer Portal](https://discord.com/developers/applications)
2. Crie uma nova aplicação
3. Vá em "Bot" → "Add Bot"
4. Em "TOKEN", clique em "Reset Token" e copie o valor
5. Ative as intents necessárias: `MESSAGE CONTENT INTENT`
6. Em "OAuth2" → "URL Generator", marque `bot` e `applications.commands`
7. Marque permissões: `Send Messages`, `Embed Links`, `Use Slash Commands`
8. Use a URL gerada para convidar o bot ao seu servidor

**Obtendo a chave RAWG:**
1. Acesse [RAWG API](https://rawg.io/apidocs)
2. Crie uma conta e vá em "Get API Key"
3. Copie a chave gerada

### 5. Execute

```bash
python main.py
```

## Comandos

| Comando | Descrição |
|---------|-----------|
| `/profile` | Mostra seu perfil com estatísticas, favoritos e backlog |
| `/addgame <nome>` | Adiciona um jogo à sua biblioteca (com autocomplete) |
| `/games` | Lista todos os jogos da sua biblioteca |
| `/rate <jogo> <nota>` | Avalia um jogo (nota de 1 a 10) |
| `/review <jogo> <texto>` | Escreve uma review para um jogo |
| `/backlog add <jogo>` | Adiciona um jogo ao backlog |
| `/backlog remove <jogo>` | Remove um jogo do backlog |
| `/backlog list` | Lista o backlog |
| `/favorite <jogo>` | Alterna favorito de um jogo |

## Funcionalidades Futuras

- Ranking global de usuários
- Curtidas e comentários em reviews
- Recomendações baseadas em gêneros
- Integração com Steam
- Badges e conquistas
- Analytics e estatísticas avançadas
- Suporte a PostgreSQL

## Licença

MIT
