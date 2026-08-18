
import os
from dotenv import load_dotenv

load_dotenv()

# Cargo forte: título que só existe mesmo em vaga de estágio/dev/dados, sem
# possibilidade real de ser outra área.
KEYWORDS_CARGO_FORTE = [
    "Estágio em TI",
    "Estágio de TI",
    "Estágio em Desenvolvimento",
    "Estágio de Desenvolvimento",
    "Estagiário de TI",
    "Estagiária de TI",
    "Estágio em Engenharia de Software",
    "Estágio Frontend",
    "Estágio Backend",
    "Estágio Full Stack",
    "Estágio em Programação",
    "Estágio React",
    "Estágio Python",
    "Estágio .NET",
    "Estágio C#",
    "Estágio em Dados",
    "Estágio em Análise de Dados",
    "Estágio de BI",
    "Software Engineer Intern",
    "Web Development Intern",
    "Desenvolvedor Júnior",
    "Desenvolvedor Jr",
    "Desenvolvedora Júnior",
    "Desenvolvedora Jr",
    "Desenvolvedor Frontend Júnior",
    "Desenvolvedor Backend Júnior",
    "Desenvolvedor Full Stack Júnior",
    "Analista de Dados Júnior",
    "Analista de Dados Jr",
    "Analista BI Jr",
]

# Cargo ambíguo: título que exige qualificador (estágio, jr, dev, dados, etc.)
# para confirmar o alinhamento com o perfil.
KEYWORDS_CARGO_AMBIGUO = [
    "Desenvolvedor",
    "Desenvolvedora",
    "Developer",
    "Dev",
    "Engenheiro de Software",
    "Software Engineer",
    "Frontend",
    "Front-End",
    "Backend",
    "Back-End",
    "Fullstack",
    "Full-Stack",
    "Full Stack",
    "Programador",
    "Programadora",
    "Analista de Dados",
    "Analista BI",
    "Analista de BI",
    "Data Analyst",
    "Business Intelligence",
    "Data Analytics",
]

# Termo que precisa aparecer junto no título quando o cargo for ambíguo.
QUALIFICADORES_DADOS = [
    "estagio",
    "estagiario",
    "estagiaria",
    "intern",
    "trainee",
    "junior",
    "jr",
    "desenvolvimento",
    "software",
    "ti",
    "web",
    "fullstack",
    "frontend",
    "backend",
    "react",
    "next",
    "typescript",
    "node",
    "c#",
    "dotnet",
    ".net",
    "python",
    "dados",
    "data",
    "sql",
    "bi",
    "analytics",
]

# Ferramenta que aparece como núcleo do título.
FERRAMENTAS_TITULO = [
    "React",
    "React.js",
    "Next.js",
    "NextJS",
    "TypeScript",
    "JavaScript",
    "Node",
    "Node.js",
    "NodeJS",
    "C#",
    ".NET",
    "Dotnet",
    "Python",
    "SQL",
    "PostgreSQL",
    "SQLite",
    "Tailwind",
    "Docker",
    "Power BI",
]

# Palavra de cargo que confirma que a vaga de ferramenta é de dev/dados.
QUALIFICADORES_CARGO = [
    "estagio",
    "estagiario",
    "intern",
    "trainee",
    "desenvolvedor",
    "developer",
    "dev",
    "programador",
    "analista",
    "engenheiro",
    "junior",
    "jr",
]

KEYWORDS = KEYWORDS_CARGO_FORTE + KEYWORDS_CARGO_AMBIGUO

TERMOS_CARGO_EXTRA = [
    "estagio ti",
    "estagio desenvolvimento",
    "estagio software",
    "estagio react",
    "estagio python",
    "estagio dados",
    "desenvolvedor junior",
    "analista de dados junior",
]

TERMOS_CARGO = sorted(set(k.lower() for k in KEYWORDS) | set(TERMOS_CARGO_EXTRA))

TERMOS_FERRAMENTA = [
    "react",
    "typescript",
    "node",
    "c#",
    "dotnet",
    "python",
    "sql",
    "power bi",
    "docker",
]

TERMOS_BUSCA = TERMOS_CARGO + TERMOS_FERRAMENTA

TERMOS_POR_CICLO = 10

# Onde vaga HIBRIDA ou PRESENCIAL é aceita (mais "Remoto").
CIDADES = [
    "Remoto",
    "Fortaleza",
    "Caucaia",
    "Eusébio",
    "Maracanaú",
    "Ceará",
]

# MEDIDO: "Data Analyst @ Lisboa" e "Analista de Datos @ Madrid" reprovavam
# na localização, não no cargo — CIDADES acima é whitelist só de cidade
# brasileira, e a expansão de LOCATIONS_LINKEDIN pra Argentina/Chile (ver
# abaixo) passou a trazer vaga presencial/híbrida em Portugal/Espanha de
# vez em quando junto. Lista SEPARADA (não misturada em CIDADES, que
# continua só-Brasil de propósito — ver decisão registrada na criação do
# config_intl.py) com toggle próprio, pra dar pra ligar/desligar esse eixo
# sem mexer no resto do filtro. Canônica aqui porque config_intl.py já
# importa de config.py (não o contrário) — o pipeline internacional reusa
# essa mesma lista em vez de manter uma cópia (risco de divergir, mesmo
# motivo da unificação de _contem_termo/_tem_termo).
CIDADES_EUROPA_IBERICA = [
    "Portugal",
    "Lisboa",
    "Porto",
    "Braga",
    "Espanha",
    "España",
    "Spain",
    "Madrid",
    "Barcelona",
    "Valencia",
]

# Toggle independente do ATIVAR_EIXO_IBERICO de config_intl.py — são dois
# eixos diferentes (esse aqui é do pipeline BR/main.py, aquele é do
# pipeline internacional/main_intl.py), cada um com seu próprio liga/
# desliga, mesmo compartilhando a mesma lista de cidades acima.
#
# DESLIGADO: do mercado internacional, só interessa vaga remota — vaga
# presencial/híbrida em Lisboa/Madrid (o que esse eixo notifica, marcada
# "exploratória") não é o que o usuário quer. CIDADES_EUROPA_IBERICA
# continua definida (não precisa apagar) pra caso o eixo volte a ser
# ligado depois — só o toggle muda.
ATIVAR_EIXO_IBERICO_BR = False

# LinkedInScraper é a única fonte do pipeline BR que também alcança vaga
# fora do Brasil (as outras são portais brasileiros) — mas até aqui rodava
# só com location=Brasil fixo no código (scrapers/linkedin.py:88), então
# essa "porta pra fora" nunca era usada.
#
# Mercado "casa": busca modalidade completa (presencial/híbrida + remoto),
# porque o usuário mora aqui e vaga local de verdade interessa.
LOCATIONS_LINKEDIN = ["Brasil"]

# Mercados adicionais: só busca REMOTA (f_WT=2) — vaga presencial/híbrida
# num país onde o usuário não mora não serve, então nem faz sentido gastar
# a passada nacional ali (era puro desperdício: Argentina/Chile já rodavam
# as duas passadas antes, mas a nacional nunca batia em CIDADES mesmo,
# que é só cidade brasileira). Espanhol ou português — mesmo critério do
# pipeline internacional. Lista reaproveita exatamente os países já usados
# e testados ao vivo no endpoint do LinkedIn em config_intl.py
# (LOCATIONS_INTL) — evita arriscar nome de país nunca testado (grafia
# errada ou região que o LinkedIn não resolve como location de verdade,
# como já visto com "LATAM"/"Latin America").
# Mercados adicionais: desativados no pipeline Brasil (foco 100% nacional).
LOCATIONS_LINKEDIN_REMOTO_APENAS = []

# MEDIDO: a passada nacional acima (location="Brasil") varre o país inteiro
# e só sobra o que bate em CIDADES depois do filtro — pra termo concorrido
# em SP/RJ/MG (a maioria), as 3 páginas (30 resultados) nunca chegam numa
# vaga de cidade menor do Nordeste, porque o volume dos polos maiores
# ocupa tudo antes. Testado ao vivo: página 1 de "analista de dados" em
# Brasil inteiro veio 100% São Paulo/Curitiba/Brasília, nenhuma do
# Nordeste. Busca ESPECÍFICA por cidade não depende de volume nacional —
# o próprio location= do LinkedIn já restringe o resultado à cidade, então
# funciona mesmo quando SP/RJ dominam o termo. "Remoto" (item de CIDADES)
# não é local de busca de verdade — sai da lista, já coberto pela passada
# remoto=True de LOCATIONS_LINKEDIN acima.
LOCATIONS_LINKEDIN_CIDADES_PRESENCIAL = [c for c in CIDADES if c != "Remoto"]

# Mercado que a vaga remota precisa aceitar pra contar.
# Foco exclusivo em vagas remotas no Brasil.
MERCADOS_REMOTO_ACEITOS = ["Brasil"]

INTERVALO_MINUTOS = int(os.getenv("INTERVALO_MINUTOS", 180))

# Digest ranqueado: vaga com Job.pontuar_relevancia() >= este
# limiar notifica na hora (score 7, 8, 9, 10); abaixo disso, vai pro digest diário.
LIMIAR_DIGEST_IMEDIATO = 7

# Hora UTC a partir da qual o digest diário pode sair (uma vez por perfil,
# por dia — ver _enviar_digest_diario em main.py). A regra é "ainda não
# enviei hoje E já passou desta hora", então o digest sai no PRIMEIRO ciclo
# do dia UTC que TERMINAR depois dela — não numa janela exata de 1 hora,
# que era o que impedia o disparo de acontecer (o ciclo dura ~80 min e
# nunca terminava dentro da janela).
#
# 9 UTC: o ciclo que começa às 09:00 UTC termina por volta das 10:20 UTC =
# 07:20 em Brasília (UTC-3). Escolhido pela usuária: chega de manhã, com a
# lista do dia anterior pronta pra revisar, em vez de de madrugada.
#
# Era 0 (= ~22h20 de Brasília), mas esse valor nunca foi uma escolha de
# verdade — ficou assim desde que o recurso foi escrito e nunca chegou a
# funcionar, então nunca houve como perceber que horário dava na prática.
#
# Se o ciclo das 09:00 falhar num dia, o das 12:00 (13:20 UTC) manda — a
# regra é "já passou de 9", não "é exatamente 9", então qualquer ciclo
# seguinte do mesmo dia UTC serve de recuperação.
DIGEST_HORA_UTC = 9

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Caminho ancorado na RAIZ do projeto, não na pasta deste arquivo.
#
# MEDIDO: o commit b8227b0 ("Reorganiza raiz: ... -> core/") moveu este
# config.py da raiz pra core/. Como DB_PATH era relativo a __file__, o
# banco se mudou junto, em silêncio: data/jobs.db virou core/data/jobs.db.
# Efeito real, confirmado em disco e no jobradar.log:
#   - data/jobs.db (1.080 vagas, versionado) ficou órfão;
#   - core/data/jobs.db nasceu vazio, então iniciar_db() passou a abortar
#     por BancoVazioSuspeito em toda execução local;
#   - no GitHub Actions a pasta core/data/ não existe no repositório, então
#     o banco era recriado do zero a cada run — toda vaga virava "nova"
#     (renotificação a cada 3h), o rodízio de termos travava no offset 0
#     (só os 10 primeiros de 44 termos eram buscados), a fila do digest era
#     descartada e o heartbeat saía a cada ciclo em vez de 1x/dia;
#   - o passo "git add data/jobs.db" do workflow não via mudança nenhuma
#     ("Nada novo pra commitar"), então o estado nunca mais persistiu.
#
# _RAIZ_PROJETO sobe um nível a partir de core/, então o caminho deixa de
# depender de onde este arquivo mora — mover config.py de novo não move
# mais o banco junto. Coberto por tests/test_db_path.py, pra uma
# reorganização futura quebrar o teste em vez da produção.
#
# JOBRADAR_DB_PATH existe pra apontar um banco descartável em teste/
# experimento sem risco de escrever no banco real.
_RAIZ_PROJETO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.getenv("JOBRADAR_DB_PATH") or os.path.join(_RAIZ_PROJETO, "data", "jobs.db")