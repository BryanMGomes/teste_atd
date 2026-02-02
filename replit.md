# Sistema de Avaliação de Satisfação - Secretaria

## Visão Geral
Aplicação web full-stack para recolha e análise de avaliações de satisfação, desenvolvida para o módulo UFCD 0787.

## Tecnologias
- **Backend:** Python 3, Flask
- **Base de Dados:** SQLite
- **Frontend:** HTML5, CSS3, JavaScript
- **Gráficos:** Chart.js

## Estrutura do Projeto
```
├── app.py                 # Aplicação Flask principal
├── satisfacao.db          # Base de dados SQLite (criada automaticamente)
├── templates/
│   ├── index.html         # Interface pública de avaliação
│   └── admin.html         # Painel de administração
├── static/
│   ├── css/
│   │   └── style.css      # Estilos da aplicação
│   └── js/
│       ├── main.js        # JavaScript da interface pública
│       └── admin.js       # JavaScript do painel admin
```

## Funcionalidades

### Interface Pública (/)
- 3 botões com emojis: Muito Satisfeito, Satisfeito, Insatisfeito
- Interface full-screen para tablets
- Feedback visual após avaliação
- Bloqueio de cliques consecutivos (3 segundos)
- Registo automático de: grau, data, hora, dia da semana

### Área de Administração (/admin_2026)
- Estatísticas com totais e percentagens
- Gráfico de barras (Chart.js)
- Gráfico circular (doughnut)
- Filtros por data
- Histórico com paginação
- Exportação CSV e TXT

## Base de Dados
Tabela `avaliacoes`:
- id (INTEGER PRIMARY KEY)
- grau_satisfacao (TEXT)
- data (TEXT)
- hora (TEXT)
- dia_semana (TEXT)
- created_at (TIMESTAMP)

## Execução
```bash
python app.py
```
A aplicação inicia em http://0.0.0.0:5000

## Data de Criação
Fevereiro 2026
