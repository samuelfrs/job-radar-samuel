"""Perfis de mercado (Brasil / Internacional) do JobRadar.

Antes disso existiam DOIS programas quase idênticos — main.py e
main_intl.py — cada um com sua própria cópia do ciclo de busca (buscar →
filtrar → checar dedup → notificar antes de salvar → funil por fonte →
alerta de saúde → heartbeat). O que diverge de verdade entre os dois
mercados é só DADO: fontes, termos de busca, cidades aceitas, regra de
cargo. A lógica de execução em si é a mesma — daí valer a pena descrever
cada mercado como um objeto (`Perfil`) e ter um único motor (main.py) que
roda qualquer um dos dois, escolhido em tempo de execução via `--perfil`.

Cada `Perfil` tem uma `chave` curta (usada tanto no argumento --perfil
quanto como sufixo nas chaves da tabela `metadados` — rodízio de termos,
cadência de baixa frequência e heartbeat ficam isolados por perfil, mesmo
os dois perfis rodando na mesma execução do workflow e escrevendo no mesmo
jobs.db).
"""

from dataclasses import dataclass, field

from core.config import (
    KEYWORDS,
    KEYWORDS_CARGO_FORTE,
    KEYWORDS_CARGO_AMBIGUO,
    QUALIFICADORES_DADOS,
    FERRAMENTAS_TITULO,
    QUALIFICADORES_CARGO,
    PALAVRAS_EXCLUSAO,
    CIDADES,
    CIDADES_EUROPA_IBERICA,
    ATIVAR_EIXO_IBERICO_BR,
    MERCADOS_REMOTO_ACEITOS,
    TERMOS_BUSCA,
    TERMOS_POR_CICLO,
)
from core.config_intl import (
    KEYWORDS_INTL,
    TERMOS_BUSCA_INTL,
    TERMOS_POR_CICLO_INTL,
    LOCATIONS_INTL,
    DOMINIOS_INDEED_INTL,
    CIDADES_INTL,
    ATIVAR_EIXO_IBERICO,
    MERCADOS_REMOTO_ACEITOS_INTL,
    IDIOMAS_EXIGIDOS_INTL,
)
from core.job import RegrasFiltro
from scrapers.geekhunter import GeekHunterScraper
from scrapers.glassdoor import GlassdoorScraper
from scrapers.gupy import GupyScraper
from scrapers.indeed import IndeedScraper
from scrapers.indeed_intl import IndeedIntlScraper
from scrapers.jobs99 import Jobs99Scraper
from scrapers.linkedin import LinkedInScraper
from scrapers.linkedin_intl import LinkedInIntlScraper
from scrapers.solides import SolidesScraper

# "alta" roda TODO ciclo; "baixa" roda só na primeira execução de cada dia
# (ver _fontes_baixa_frequencia_ja_rodaram_hoje em main.py). Existe pra
# fonte de baixo rendimento não pesar no custo de todo ciclo.
FREQUENCIA_ALTA = "alta"
FREQUENCIA_BAIXA = "baixa"


@dataclass
class DefinicaoScraper:
    """Uma fonte dentro de um perfil.

    `kwargs_extras`: além de `termos_busca` (que todo scraper recebe), fonte
    internacional precisa de argumento próprio — `locations=` no
    LinkedInIntlScraper, `dominios=` no IndeedIntlScraper. Fonte do perfil
    BR não precisa de nada extra (LinkedInScraper já traz seus países
    default de config.py), então fica com kwargs_extras vazio.
    """
    classe: type
    frequencia: str
    kwargs_extras: dict = field(default_factory=dict)


@dataclass
class Perfil:
    chave: str  # "brasil" / "internacional" — valor do --perfil e sufixo de chave em metadados
    nome: str  # nome de exibição nos logs/Telegram, ex: "Internacional"
    palavras_monitoradas: list[str]
    paises_pesquisados: list[str] | None  # só o perfil internacional imprime isso no banner
    regras: RegrasFiltro
    regras_eixo_secundario: RegrasFiltro | None
    eixo_secundario_ativo: bool
    eixo_secundario_rotulo: str  # usado só no texto do log ("Nova vaga exploratória (<rótulo>)")
    termos_busca: list[str]
    termos_por_ciclo: int
    definicao_scrapers: list[DefinicaoScraper]
    max_scrapers_concorrentes: int = 4


# Regra primária: cidade brasileira (Nordeste) ou "Remoto" com mercado
# Brasil/LATAM/Portugal/Espanha aceito (ver Job.escopo_remoto).
_REGRAS_BR = RegrasFiltro(
    keywords_forte=KEYWORDS_CARGO_FORTE,
    keywords_ambiguo=KEYWORDS_CARGO_AMBIGUO,
    qualificadores_dados=QUALIFICADORES_DADOS,
    ferramentas_titulo=FERRAMENTAS_TITULO,
    qualificadores_cargo=QUALIFICADORES_CARGO,
    cidades=CIDADES,
    mercados_remoto_aceitos=MERCADOS_REMOTO_ACEITOS,
    palavras_exclusao=PALAVRAS_EXCLUSAO,
)

# Eixo secundário (Ibéria): mesma regra de cargo, cidade europeia em vez de
# brasileira. DESLIGADO — ver ATIVAR_EIXO_IBERICO_BR em config.py: usuário só
# quer vaga remota do mercado internacional, não presencial/híbrida em
# Lisboa/Madrid. Continua definido (não apagado) pra religar fácil depois.
_REGRAS_BR_IBERIA = RegrasFiltro(
    keywords_forte=KEYWORDS_CARGO_FORTE,
    keywords_ambiguo=KEYWORDS_CARGO_AMBIGUO,
    qualificadores_dados=QUALIFICADORES_DADOS,
    ferramentas_titulo=FERRAMENTAS_TITULO,
    qualificadores_cargo=QUALIFICADORES_CARGO,
    cidades=CIDADES_EUROPA_IBERICA,
    palavras_exclusao=PALAVRAS_EXCLUSAO,
)

# Revelo não entrou: o portal de vagas exige login pra navegar, não dá pra
# fazer scraping público de forma confiável.
#
# Trampos SAIU depois de investigar por que rendia 0 notificação em 6 dias
# (~71 vagas brutas/ciclo com 99Jobs). Testei o parâmetro de busca (term=)
# direto na API do site com "analista de dados" e "business intelligence" —
# os dois devolveram a MESMA lista de vagas (Diretor de Arte, SDR,
# Atendimento Publicitário...), nenhuma de dados. A busca do site não
# filtra nada, é sempre o feed genérico recente; a categoria própria
# "Análise e Gestão de Dados" do site tem só 4 vagas no total, contra 226
# de "Emprego" geral (majoritariamente marketing/criação/comercial). O
# vazio vinha da FONTE (site não é de tecnologia/dados) — código do
# scraper continua em scrapers/trampos.py se algum dia mudar.
#
# 99Jobs FICOU: mesma investigação, resultado diferente. A busca por
# "analista de dados" no site retorna vaga de verdade relevante ("Analista
# de Dados Sênior" etc.) — só que presencial/híbrida em São Paulo, fora da
# lista CIDADES e sem sinal de remoto. O vazio aí vem do FILTRO de
# localização (a mesma limitação que afeta o sistema todo), não da fonte —
# remover jogaria fora uma fonte que funciona.
#
# Cadência por fonte: medido em jobradar.log + jobs.db (vagas notificadas /
# vagas brutas retornadas, somado por fonte). Gupy e LinkedIn confirmam o
# que foi medido à parte (Gupy ~2,6%); Catho, GeekHunter e 99Jobs ficam
# abaixo de 1%.
#
# WeWorkRemotelyIntlScraper reaproveitado aqui (não duplicado): é agregador
# de vaga 100% remota que cobre o mercado "remoto internacional" que
# nenhuma das 8 fontes brasileiras alcança — mesmo scraper usado no perfil
# internacional, sem nada daquele perfil hardcoded. Sem medição própria
# ainda pra essa combinação (fonte + termos em português) — FREQUENCIA_BAIXA
# até medir rendimento real.
_SCRAPERS_BR = [
    DefinicaoScraper(GupyScraper, FREQUENCIA_ALTA),        # ~2,6% de rendimento
    DefinicaoScraper(LinkedInScraper, FREQUENCIA_ALTA),     # ~8,5% — a melhor fonte de longe
    DefinicaoScraper(GlassdoorScraper, FREQUENCIA_ALTA),    # Nova fonte com alto volume de vagas
    DefinicaoScraper(SolidesScraper, FREQUENCIA_ALTA),      # ~1,1%
    DefinicaoScraper(IndeedScraper, FREQUENCIA_ALTA),       # ~1,1%
    DefinicaoScraper(GeekHunterScraper, FREQUENCIA_BAIXA),  # <1%
    DefinicaoScraper(Jobs99Scraper, FREQUENCIA_BAIXA),      # <1%, fonte confirmada funcionando
]

PERFIL_BR = Perfil(
    chave="brasil",
    nome="Brasil",
    palavras_monitoradas=KEYWORDS,
    paises_pesquisados=None,
    regras=_REGRAS_BR,
    regras_eixo_secundario=_REGRAS_BR_IBERIA,
    eixo_secundario_ativo=ATIVAR_EIXO_IBERICO_BR,
    eixo_secundario_rotulo="Ibéria",
    termos_busca=TERMOS_BUSCA,
    termos_por_ciclo=TERMOS_POR_CICLO,
    definicao_scrapers=_SCRAPERS_BR,
    max_scrapers_concorrentes=4,
)


# Regra primária: só remoto ("Remote"/"Remoto" em CIDADES_INTL), mercado
# LATAM/Portugal/Espanha aceito. Sem cargo ambíguo/ferramenta ainda nesse
# perfil — simples de propósito por ser o mais novo dos dois.
#
# idiomas_exigidos: sem mercado declarado, exige espanhol/português/LATAM
# no título (ver IDIOMAS_EXIGIDOS_INTL e comentário em RegrasFiltro) — a
# busca já tentava garantir isso via termo, mas nunca era reconferido na
# vaga em si.
_REGRAS_INTL = RegrasFiltro(
    keywords_forte=KEYWORDS_INTL,
    keywords_ambiguo=[],
    qualificadores_dados=[],
    ferramentas_titulo=[],
    qualificadores_cargo=[],
    cidades=CIDADES_INTL,
    mercados_remoto_aceitos=MERCADOS_REMOTO_ACEITOS_INTL,
    idiomas_exigidos=IDIOMAS_EXIGIDOS_INTL,
    palavras_exclusao=PALAVRAS_EXCLUSAO,
)

# Eixo secundário (Ibéria): vaga presencial/híbrida em Portugal/Espanha,
# achada de propósito (LOCATIONS_INTL busca lá) mas que CIDADES_INTL (só
# remoto) rejeitaria. DESLIGADO — mesmo motivo do eixo BR acima.
_REGRAS_INTL_IBERIA = RegrasFiltro(
    keywords_forte=KEYWORDS_INTL,
    keywords_ambiguo=[],
    qualificadores_dados=[],
    ferramentas_titulo=[],
    qualificadores_cargo=[],
    cidades=CIDADES_EUROPA_IBERICA,
    palavras_exclusao=PALAVRAS_EXCLUSAO,
)

# Pipeline internacional
_SCRAPERS_INTL = [
    DefinicaoScraper(LinkedInIntlScraper, FREQUENCIA_ALTA, {"locations": LOCATIONS_INTL}),
    DefinicaoScraper(IndeedIntlScraper, FREQUENCIA_ALTA, {"dominios": DOMINIOS_INDEED_INTL}),
]

PERFIL_INTL = Perfil(
    chave="internacional",
    nome="Internacional",
    palavras_monitoradas=KEYWORDS_INTL,
    paises_pesquisados=LOCATIONS_INTL,
    regras=_REGRAS_INTL,
    regras_eixo_secundario=_REGRAS_INTL_IBERIA,
    eixo_secundario_ativo=ATIVAR_EIXO_IBERICO,
    eixo_secundario_rotulo="Ibéria",
    termos_busca=TERMOS_BUSCA_INTL,
    termos_por_ciclo=TERMOS_POR_CICLO_INTL,
    definicao_scrapers=_SCRAPERS_INTL,
    max_scrapers_concorrentes=3,
)

PERFIS = {
    PERFIL_BR.chave: PERFIL_BR,
    PERFIL_INTL.chave: PERFIL_INTL,
}
