<div align="center">

# 📡 JobRadar
### Monitor Automatizado de Vagas em TI, Desenvolvimento & Dados

![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-Scraping-2EAD33?style=for-the-badge&logo=playwright&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Banco%20versionado-07405E?style=for-the-badge&logo=sqlite&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Cron%203h-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)
![Tests](https://img.shields.io/badge/testes-245%20passing-success?style=for-the-badge)
![Status](https://img.shields.io/badge/status-em%20produ%C3%A7%C3%A3o-success?style=for-the-badge)

**Perfil Atual:** Samuel Gadelha Farias (Engenharia de Telecomunicações - UFC / Desenvolvedor Full Stack & Data Analytics)  
**Projeto Original por:** Liliam Kezia Oliveira Souza  

</div>

---

## 💎 O que é o JobRadar?

O **JobRadar** é um robô autônomo e inteligente para monitoramento contínuo de oportunidades de trabalho. Ele substitui a busca manual diária vasculhando agregadores e plataformas de recrutamento brasileiras, filtrando as oportunidades com regras de confiança, ranqueando a relevância de cada vaga e enviando alertas diretamente no **Telegram** — com **custo zero de servidor**, rodando 100% gratuito via **GitHub Actions**.

### 🌐 Fontes Monitoradas & Cadência de Busca:
- **Alta Frequência (A cada 3 horas):**
  - **LinkedIn** (~8,5% de rendimento, maior volume de vagas qualificadas).
  - **Gupy** (~2,6% de rendimento, alta estabilidade).
- **Baixa Frequência (Garimpo diário - 1x ao dia):**
  - **Catho** (varredura complementar).
  - **Sólides** (extração otimizada para o portal Next.js).
  - **Indeed** (garimpo complementar).
  - **99Jobs** (vagas e programas corporativos).
  - **GeekHunter** (vagas exclusivas de tecnologia).

---

## 🏗️ Arquitetura Técnica & Regras de Negócio

1. **Filtro em 3 Níveis de Confiança:**
   - *Cargo Forte:* Títulos inequívocos de Estágio, Dev Jr e Análise de Dados passam sozinhos (ex: `"Estágio em TI"`, `"Desenvolvedor Full Stack Jr"`).
   - *Cargo Ambíguo + Qualificador:* Títulos amplos (ex: `"Desenvolvedor"`) só são aprovados se contiverem um qualificador de nível/domínio junto (ex: `"Desenvolvedor React Jr"`).
   - *Ferramenta + Cargo:* Ferramentas soltas (ex: `"Python"`, `"React"`) só contam se vierem acompanhadas de palavra de cargo (ex: `"Desenvolvedor Python"`).
2. **Sistema de Score de Relevância (0 a 10):**
   - **+3** se o título for um cargo forte.
   - **+2** se o título for um cargo ambíguo com qualificador.
   - **+2** se contiver ferramentas da sua stack.
   - **+2** (bônus) para nível **Estágio/Trainee** ou **Júnior**.
   - **-2** (deságio) para vagas Pleno, Sênior, Especialista ou Liderança.
   - **+2** (nota máxima de localização) para vagas **Remotas**.
3. **Resiliência e Zero Spam:**
   - **Deduplicação:** Evita enviar a mesma vaga mais de uma vez usando hash único de link e combinação título + empresa.
   - **Digest Diário:** Vagas com relevância alta (Score ≥ 7) notificam na hora; vagas secundárias entram em um resumo diário agrupado pela manhã.
   - **Alerta de Saúde:** Avisa no Telegram se houver falhas críticas nos scrapers ativos daquele ciclo.

---

## 📁 Estrutura do Repositório

```text
job-radar/
├── README.md                 ← Documentação completa e guia de uso
├── PLANO_ADAPTACAO_JOB_RADAR.md ← Especificação inicial do perfil
├── requirements.txt          ← Dependências (playwright, pytest, python-dotenv)
├── main.py                   ← Motor de busca, agendador e controle do ciclo
├── core/
│   ├── config.py             ← Regras de filtro BR (cargos, qualificadores, cidades, buscas)
│   ├── config_intl.py        ← Configurações internacionais (remoto fora do BR)
│   ├── job.py                ← Classe Job, cálculo de relevância, senioridade e escopo
│   ├── perfis.py             ← Definição dos perfis (Brasil vs Internacional) e fontes
│   └── logger.py             ← Logs formatados do sistema
├── database/
│   └── database.py           ← Banco SQLite (vagas vistas, dedup, fila de digest)
├── scrapers/                 ← Módulos de extração de vagas (LinkedIn, Gupy, Catho, etc.)
├── notifier/
│   └── telegram.py           ← Formatação de mensagens e botões interativos do Telegram
├── tests/                    ← Suíte de 245 testes automatizados (pytest)
├── data/
│   └── jobs.db               ← Banco SQLite versionado (histórico de dedup)
└── .github/workflows/
    ├── jobradar.yml          ← Cron do GitHub Actions (roda a cada 3h na nuvem)
    └── testes.yml            ← CI (roda a suíte de testes a cada push)
```

---

## 🛠️ Guia Passo a Passo: Como Adaptar o JobRadar para o Seu Perfil

Quer usar este projeto para você ou adaptá-lo para a sua área profissional (Frontend, Backend, Dados, QA, UX/UI, Produto, etc.)? Siga este passo a passo:

### 1️⃣ Fazer um Fork do Repositório
1. No canto superior direito desta página do GitHub, clique no botão **Fork** para criar uma cópia do projeto na sua conta do GitHub.
2. Clone o repositório forked para o seu computador:
   ```powershell
   git clone https://github.com/SEU_USUARIO/job-radar.git
   cd job-radar
   ```

---

### 2️⃣ Criar seu Bot e Obter Credenciais no Telegram
O robô usa a API do Telegram para te enviar mensagens privadas instantâneas. Você precisa de duas informações: `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID`.

1. **Criar o Bot:**
   - Abra o Telegram e pesquise por [@BotFather](https://t.me/BotFather).
   - Envie o comando `/newbot`.
   - Escolha um nome para o seu robô (ex: `Meu Radar de Vagas`) e um username único terminado em `bot` (ex: `meu_radar_pessoal_bot`).
   - O BotFather vai te responder com uma mensagem contendo o **Token de Acesso à API HTTP** (ex: `7123456789:ABCDefGhIJklMNopQRstUVwxYZ`). Guarde esse valor.
2. **Ativar o Bot:**
   - Abra a conversa com o bot que você acabou de criar no Telegram e clique em **Começar** (ou envie `/start`). *(Se não enviar start, o bot não terá permissão para te mandar mensagens).*
3. **Descobrir o seu Chat ID:**
   - No Telegram, procure pelo bot [@userinfobot](https://t.me/userinfobot) e envie `/start`.
   - Ele responderá com o seu número de identificação (`Id:` ex: `123456789`). Guarde esse número.

---

### 3️⃣ Configurar o Seu Perfil em `core/config.py`
Abra o arquivo [`core/config.py`](file:///c:/Users/Samuel/Desktop/job-radar-samuel/core/config.py) no seu editor de código. É aqui que você define o seu foco:

1. **Cargos Fortes (`KEYWORDS_CARGO_FORTE`):**
   - Títulos de vaga que são exatamente o que você busca e que devem ser aceitos de imediato:
   ```python
   KEYWORDS_CARGO_FORTE = [
       "Estágio em Desenvolvimento",
       "Estágio Frontend",
       "Desenvolvedor Júnior",
       "Desenvolvedor React Jr",
       # Adicione os seus cargos foco aqui...
   ]
   ```
2. **Cargos Ambíguos (`KEYWORDS_CARGO_AMBIGUO`) e Qualificadores (`QUALIFICADORES_DADOS`):**
   - Nomes genéricos que só devem passar se vierem acompanhados de uma tecnologia ou nível:
   ```python
   KEYWORDS_CARGO_AMBIGUO = ["Desenvolvedor", "Developer", "Frontend", "Programador"]
   QUALIFICADORES_DADOS = ["junior", "jr", "estagio", "trainee", "react", "node"]
   ```
3. **Ferramentas e Stack Técnica (`FERRAMENTAS_TITULO`):**
   - Tecnologias do seu domínio que somam pontos na pontuação da vaga:
   ```python
   FERRAMENTAS_TITULO = ["React", "TypeScript", "Node.js", "Python", "SQL", "Docker", "Tailwind"]
   ```
4. **Palavras de Exclusão (`PALAVRAS_EXCLUSAO`):**
   - Termos que eliminam a vaga imediatamente para você não receber ruído:
   ```python
   PALAVRAS_EXCLUSAO = [
       "senior", "sr", "pleno", "pl", "tech lead", "gerente", "especialista",
       "suporte", "helpdesk", "vendas", "comercial", "telemarketing"
   ]
   ```
5. **Cidades e Regiões Aceitas (`CIDADES`):**
   - Onde você aceita trabalhar presencial ou híbrido (sempre mantenha `"Remoto"` na lista):
   ```python
   CIDADES = [
       "Remoto",
       "Fortaleza",
       "São Paulo",
       "Ceará",
   ]
   ```
6. **Termos de Consulta (`TERMOS_CARGO_EXTRA` e `TERMOS_FERRAMENTA`):**
   - As palavras-chave que o robô digitará nos campos de busca dos sites (LinkedIn, Gupy, etc.):
   ```python
   TERMOS_CARGO_EXTRA = [
       "estagio ti",
       "estagio desenvolvimento",
       "desenvolvedor junior",
   ]
   ```

---

### 4️⃣ Testar Localmente no seu Computador
1. Crie um ambiente virtual e instale as dependências:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate          # Linux/Mac: source venv/bin/activate
   pip install -r requirements.txt
   python -m playwright install chromium
   ```
2. Crie um arquivo `.env` na raiz do projeto:
   ```env
   TELEGRAM_BOT_TOKEN=seu_token_do_botfather_aqui
   TELEGRAM_CHAT_ID=seu_id_numerico_aqui
   ```
3. Execute uma busca de teste:
   ```powershell
   python main.py --perfil brasil --once
   ```
   *Se configurado corretamente, o robô buscará as vagas e enviará uma mensagem de confirmação e as vagas encontradas direto no seu Telegram!*

---

### 5️⃣ Ativar a Execução Automática e Gratuita na Nuvem (GitHub Actions)
Depois de testar localmente, envie as alterações para o seu GitHub e ative o agendamento em nuvem a cada 3 horas:

1. **Subir as alterações:**
   ```powershell
   git add .
   git commit -m "feat: adapta radar para o meu perfil profissional"
   git push origin main
   ```
2. **Cadastrar as Chaves Secretas no GitHub:**
   - No seu repositório no GitHub, clique em **Settings** > **Secrets and variables** > **Actions** > **New repository secret**.
   - Adicione o secret:
     - **Name:** `TELEGRAM_BOT_TOKEN`
     - **Secret:** *(Cole o token do seu bot)*
   - Clique em **Add secret** e repita para o chat ID:
     - **Name:** `TELEGRAM_CHAT_ID`
     - **Secret:** *(Cole o seu chat ID numérico)*
3. **Liberar Permissão de Escrita para o Workflow Salvar o Histórico:**
   - No repositório, acesse **Settings** > **Actions** > **General**.
   - Role até a seção **Workflow permissions**.
   - Selecione a opção **"Read and write permissions"** e clique em **Save**.
   *(Isso é fundamental para que o robô consiga commitar o arquivo `jobs.db` atualizado a cada ciclo, evitando te enviar vagas repetidas).*
4. **Disparar um Teste Manual na Nuvem:**
   - Vá na aba **Actions** do GitHub.
   - Selecione o workflow **JobRadar**.
   - Clique em **Run workflow** > **Run workflow**.

Pronto! Seu robô agora trabalhará sozinho na nuvem 24 horas por dia, 7 dias por semana, sem você precisar deixar o computador ligado.

---

## 🤖 Guia de Referência para Assistentes de IA (Instruções para outros Chats)

> **Instrução para Assistentes / IAs futuras:**
> Se o usuário pedir para você modificar ou ajustar o **JobRadar**, consulte estas diretrizes antes de alterar o código:
> 
> 1. **Filtros e Regras:** Toda adição de novos cargos, qualificadores, ferramentas ou cidades deve ser feita no arquivo `core/config.py`.
> 2. **Cálculo de Relevância:** A lógica de pontuação fica no método `pontuar_relevancia()` em `core/job.py`.
> 3. **Senioridade:** Alvos prioritários de senioridade são definidos em `_NIVEIS_SENIORIDADE_ALVO` no arquivo `core/job.py`.
> 4. **Fontes Ativas e Cadências:** Fontes são configuradas em `_SCRAPERS_BR` em `core/perfis.py`. Fontes com instabilidade em IPs de datacenter não devem ser configuradas como alta frequência para evitar falso alarme de saúde no Telegram.
> 5. **Suíte de Testes:** Sempre que alterar regras de filtro em `core/config.py` ou `core/job.py`, execute obrigatoriamente `pytest tests/ -v`.

