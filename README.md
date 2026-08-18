<div align="center">

# 📡 JobRadar — Samuel Gadelha Farias
### Monitor Automatizado de Vagas de Estágio em TI, Desenvolvimento & Análise de Dados

![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-Scraping-2EAD33?style=for-the-badge&logo=playwright&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Banco%20versionado-07405E?style=for-the-badge&logo=sqlite&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Cron%203h-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)
![Tests](https://img.shields.io/badge/testes-245%20passing-success?style=for-the-badge)
![Status](https://img.shields.io/badge/status-em%20produ%C3%A7%C3%A3o-success?style=for-the-badge)

**Perfil Alvo:** Samuel Gadelha Farias (Engenharia de Telecomunicações - UFC / Desenvolvedor Full Stack & Data Analytics)  
**Projeto Original por:** Liliam Kezia Oliveira Souza  

</div>

---

## 💎 Proposta de Valor e Perfil

O **JobRadar** é um sistema autônomo de monitoramento contínuo de vagas. Ele substitui a busca manual diária varrendo **8 fontes de recrutamento** (LinkedIn, Gupy, Catho, Indeed, Solides, 99Jobs, GeekHunter, WeWorkRemotely) a cada **3 horas**, filtrando com regras estritas de 3 níveis de confiança, pontuando a relevância de cada oportunidade e enviando alertas diretamente no **Telegram** — com custo zero de servidor (rodando via **GitHub Actions**).

### 👤 Perfil Configurado
- **Cargos Foco:** Estágio, Trainee e Desenvolvedor Júnior em **Desenvolvimento de Software** (Frontend, Backend, Full Stack, Engenharia de Software) e **Análise de Dados** (Data Analyst, BI, Analytics).
- **Tech Stack Prioritária:** React.js, Next.js, TypeScript, Node.js, C#, .NET Core, Python, Tailwind CSS, SQL (PostgreSQL, Supabase, SQLite), Docker, Linux, MATLAB, Power BI.
- **Localização:** Fortaleza/CE, Caucaia/CE, Eusébio/CE, Maracanaú/CE, Ceará e **Remoto / Home Office** (Brasil).
- **Pontuação Especial:** Vagas 100% **Remotas** recebem nota máxima de mercado (+2 no score) para destaque prioritário no Telegram.

---

## 🏗️ Arquitetura Técnica & Regras de Negócio

1. **Filtro em 3 Níveis de Confiança:**
   - *Cargo Forte:* Títulos inequívocos de Estágio, Dev Jr e Análise de Dados passam sozinhos (ex: "Estágio em TI", "Desenvolvedor Full Stack Jr").
   - *Cargo Ambíguo + Qualificador:* Títulos amplos (ex: "Desenvolvedor") só são aprovados se contiverem um qualificador de nível/domínio junto (ex: "Desenvolvedor React Jr").
   - *Ferramenta + Cargo:* Ferramentas soltas (ex: "Python", "React") só contam se vierem acompanhadas de palavra de cargo (ex: "Desenvolvedor Python").
2. **Sistema de Score de Relevância (0 a 10):**
   - **+3** se o título for um cargo forte.
   - **+2** se o título for um cargo ambíguo com qualificador.
   - **+2** se contiver ferramentas da stack.
   - **+2** (bônus) para nível **Estágio/Trainee** ou **Júnior**.
   - **-2** (deságio) para vagas Pleno, Sênior, Especialista ou Liderança.
   - **+2** (nota máxima de localização) para vagas **Remotas**.
3. **Resiliência e Zero Spam:**
   - **Deduplicação:** Evita enviar a mesma vaga mais de uma vez usando hash único de link e combinação título + empresa.
   - **Digest Diário:** Vagas com relevância alta notificam na hora; vagas secundárias entram em um resumo diário agrupado.

---

## 📁 Estrutura do Repositório

```text
job-radar/
├── README.md                 ← Documentação completa e guia de uso
├── PLANO_ADAPTACAO_JOB_RADAR.md ← Especificação inicial do perfil
├── requirements.txt          ← Dependências (playwright, pytest, requests, python-dotenv)
├── main.py                   ← Motor de busca e controle do ciclo
├── core/
│   ├── config.py             ← Regras de filtro BR (cargos, qualificadores, cidades, buscas)
│   ├── config_intl.py        ← Configurações internacionais (remoto fora do BR)
│   ├── job.py                ← Classe Job, cálculo de relevância, senioridade e escopo
│   ├── perfis.py             ← Definição dos perfis (Brasil vs Internacional)
│   └── logger.py             ← Logs formatados do sistema
├── database/
│   └── database.py           ← Banco SQLite (vagas vistas, dedup, fila de digest)
├── scrapers/                 ← Módulos de extração de vagas (Gupy, LinkedIn, Catho, etc.)
├── notifier/
│   └── telegram.py           ← Formatação de mensagens e botões do Telegram
├── tests/                    ← Suíte de 245 testes automatizados (pytest)
├── data/
│   └── jobs.db               ← Banco SQLite versionado (histórico de dedup)
└── .github/workflows/
    ├── jobradar.yml          ← Cron do GitHub Actions (roda a cada 3h na nuvem)
    └── testes.yml            ← CI (roda a suíte de testes a cada push)
```

---

## 💻 Como Rodar e Testar no seu Computador

### 1. Clonar o Repositório e Criar o Ambiente Virtual
```powershell
git clone <URL_DO_SEU_REPOSISITORIO>
cd job-radar
python -m venv venv
.\venv\Scripts\activate      # Linux/Mac: source venv/bin/activate
```

### 2. Instalar Dependências e Navegador do Playwright
```powershell
pip install -r requirements.txt
python -m playwright install chromium
```

### 3. Rodar os Testes Automatizados (245 Testes)
```powershell
pytest tests/ -v
```

### 4. Configurar Notificações do Telegram (Local)
Crie um arquivo `.env` na raiz do projeto:
```env
TELEGRAM_BOT_TOKEN=seu_bot_token_aqui
TELEGRAM_CHAT_ID=seu_chat_id_aqui
```

### 5. Executar uma Varredura Manual
```powershell
python main.py --perfil brasil --once
```

---

## ☁️ Como Ativar a Execução Gratuita na Nuvem (GitHub Actions)

O projeto já vem pronto para rodar sozinho na nuvem a cada **3 horas**:

1. Suba o código para o seu repositório no GitHub:
   ```powershell
   git add .
   git commit -m "feat: adapta radar para perfil Samuel Farias"
   git push origin main
   ```
2. No GitHub, acesse seu repositório > **Settings** > **Secrets and variables** > **Actions** > **New repository secret** e cadastre:
   - `TELEGRAM_BOT_TOKEN`: Token gerado pelo [@BotFather](https://t.me/BotFather).
   - `TELEGRAM_CHAT_ID`: ID obtido no [@userinfobot](https://t.me/userinfobot).
3. Vá em **Settings** > **Actions** > **General** > **Workflow permissions** e selecione **"Read and write permissions"** > **Save**.

---

## 🤖 Guia de Referência para Assistentes de IA (Instruções para outros Chats)

> **Instrução para Assistentes / IAs futuras:**
> Se o usuário pedir para você modificar ou ajustar o **JobRadar**, consulte estas diretrizes antes de alterar o código:
> 
> 1. **Filtros e Regras:** Toda adição de novos cargos, qualificadores, ferramentas ou cidades deve ser feita no arquivo `core/config.py`.
> 2. **Cálculo de Relevância:** A lógica de pontuação fica no método `pontuar_relevancia()` em `core/job.py`.
> 3. **Senioridade:** Alvos prioritários de senioridade são definidos em `_NIVEIS_SENIORIDADE_ALVO` no arquivo `core/job.py`.
> 4. **Suíte de Testes:** Sempre que alterar regras de filtro em `core/config.py` ou `core/job.py`, execute obrigatoriamente `pytest tests/ -v` para garantir que nenhuma regressão ocorra.

