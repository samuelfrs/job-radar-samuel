"""Testes automatizados da camada de filtro (job.py) — roda no workflow do
GitHub Actions a cada push (ver .github/workflows/tests.yml).

MEDIDO: seis rodadas seguidas de "corrigir → surgir regressão" durante o
desenvolvimento desta sessão — UF ambígua batendo Estados Unidos em vez de
Brasil, "Porto Alegre" virando Portugal por substring, "Remote - Brazil/
LATAM" perdendo um dos dois mercados declarados, vocabulário de modalidade
("Remoto", "Não informado") virando candidato a país... Cada validação foi
feita manualmente (bash ad-hoc, fora do projeto) e não ficou — o mesmo tipo
de bug podia voltar a qualquer commit futuro sem ninguém notar até aparecer
em produção.

extrair_escopo_remoto() e Job.combina_com() são função pura: não abrem
browser, não tocam rede, não tocam banco — só transformam
(texto, texto) -> resultado. É o tipo de código mais barato de testar que
existe, e é exatamente a camada que mais bugs reais teve neste projeto.

Cada caso abaixo documenta um bug JÁ CORRIGIDO nesta base (não é cenário
hipotético) — o valor esperado foi conferido rodando o código real antes de
virar asserção, não deduzido lendo o comentário.
"""

import pytest

from core.job import Job, extrair_escopo_remoto
from core.perfis import PERFIL_BR, PERFIL_INTL


# ---------------------------------------------------------------------------
# extrair_escopo_remoto(local, modalidade) -> set[str]
# ---------------------------------------------------------------------------

CASOS_ESCOPO = [
    # --- UF ambígua BR x EUA: 6 siglas colidem (AL/MA/MT/MS/PA/SC) — ver
    # _SIGLAS_UF_AMBIGUAS em job.py. Sem desambiguar pela capital, essas 6
    # viravam "Estados Unidos" e a vaga brasileira era barrada.
    ("uf-ambigua-al-maceio", "Remoto (Maceió, AL)", "", {"Brasil"}),
    ("uf-ambigua-ma-sao-luis", "Remoto (São Luís, MA)", "", {"Brasil"}),
    ("uf-ambigua-mt-cuiaba", "Remoto (Cuiabá, MT)", "", {"Brasil"}),
    ("uf-ambigua-ms-campo-grande", "Remoto (Campo Grande, MS)", "", {"Brasil"}),
    ("uf-ambigua-pa-belem", "Remoto (Belém, PA)", "", {"Brasil"}),
    ("uf-ambigua-sc-florianopolis", "Remoto (Florianópolis, SC)", "", {"Brasil"}),
    # Mesma sigla ambígua, mas SEM capital brasileira reconhecida — tem que
    # continuar resolvendo Estados Unidos (a desambiguação não pode virar
    # "toda sigla de 2 letras é Brasil por padrão").
    ("uf-ambigua-sem-capital-br-continua-eua", "Remote (Anytown, AL)", "", {"Estados Unidos"}),
    # UF que não colide com sigla americana resolve direto, sem precisar
    # olhar a cidade.
    ("uf-nao-ambigua-resolve-direto", "Remoto (Recife, PE)", "", {"Brasil"}),

    # --- MEDIDO em produção (jobradar.log real): card do LinkedIn às vezes
    # separa cidade e UF com hífen em vez de vírgula ("São Paulo - SP") —
    # sem tratar isso, `resto` não quebrava em segmento nenhum e a UF nunca
    # era comparada contra _SIGLAS_UF_BRASIL (ver MEDIDO em job.py). Vaga
    # remota brasileira real virava "escopo desconhecido" e era descartada.
    ("hifen-sao-paulo-sem-parenteses", "São Paulo - SP", "Remoto", {"Brasil"}),
    ("hifen-fortaleza-sem-parenteses", "Fortaleza - CE", "Remoto", {"Brasil"}),
    # UF ambígua com separador hífen também precisa desambiguar pela
    # capital, igual ao caso com vírgula acima.
    ("hifen-uf-ambigua-sc-florianopolis", "Florianópolis - SC", "Remoto", {"Brasil"}),

    # --- "Porto Alegre"/"Santiago do Cacém" virando Portugal/Chile por
    # substring (a chave batia dentro do nome da cidade brasileira/
    # portuguesa maior). Casamento de cidade isolada agora é por IGUALDADE
    # do candidato inteiro, não substring.
    ("porto-alegre-com-uf-nao-vira-portugal", "Remoto (Porto Alegre, RS)", "", {"Brasil"}),
    ("porto-alegre-sem-uf-nao-vira-portugal", "Remoto (Porto Alegre)", "Remoto", {"Brasil"}),
    ("santiago-do-cacem-nao-vira-chile", "Remoto (Santiago do Cacém)", "Remoto", {"santiago do cacem"}),
    # Anti-regressão: "Porto"/"Santiago" SOZINHOS continuam resolvendo pro
    # país de verdade — o fix é sobre substring dentro de nome composto,
    # não sobre desativar o reconhecimento da cidade.
    ("porto-sozinho-continua-portugal", "Remoto (Porto)", "Remoto", {"Portugal"}),
    ("santiago-sozinho-continua-chile", "Remoto (Santiago)", "Remoto", {"Chile"}),

    # --- Multimercado: "Remote - Brazil/LATAM" resolvia só pro primeiro
    # match (Brasil, que o perfil internacional REJEITA de propósito) e
    # perdia o LATAM (que ele aceita) — vaga válida sendo descartada.
    ("multimercado-brazil-barra-latam", "Remote - Brazil/LATAM", "", {"Brasil", "LATAM"}),
    ("multimercado-latam-mais-brazil", "Remote - LATAM + Brazil", "", {"Brasil", "LATAM"}),

    # --- Modalidade virando escopo geográfico falso: sem separador textual
    # ("Remote — ...") mas com `modalidade` confirmando remoto, `local`
    # inteiro virava candidato — incluindo o próprio vocabulário de
    # modalidade ("Remoto") e o placeholder de campo vazio ("Não
    # informado"), que não são nome de país nenhum.
    ("modalidade-remoto-sem-complemento-sem-escopo", "Remoto", "Remoto", set()),
    ("placeholder-nao-informado-sem-escopo", "Não informado", "Remoto", set()),
    ("placeholder-nao-informado-com-remoto-sem-escopo", "Não informado (Remoto)", "Remoto", set()),
    ("home-office-sem-escopo", "Home Office", "Remoto", set()),

    # --- Formato de cidade/região da Ibéria e LATAM comum no LinkedIn:
    # "Greater X", "X, X provincia" (província repete o nome da capital),
    # CEP espanhol na frente, "X Metropolitan Area" — nenhum batia por
    # igualdade exata antes da limpeza de ruído.
    ("greater-buenos-aires", "Greater Buenos Aires", "Remoto", {"Argentina"}),
    ("madrid-provincia-duplicado", "Madrid, Madrid provincia", "Remoto", {"Espanha"}),
    ("cep-espanhol-na-frente", "08015, Barcelona, Barcelona provincia", "Remoto", {"Espanha"}),
    ("medellin-metropolitan-area", "Medellín Metropolitan Area", "Remoto", {"Colômbia"}),

    # --- Sigla de estado mexicano (formato "Cidade, SIGLA" igual ao
    # americano/brasileiro, mas nenhuma sigla mexicana estava cadastrada).
    ("sigla-mexico-nl-monterrey", "Monterrey, N.L.", "Remoto", {"México"}),
    ("sigla-mexico-cdmx", "Cuauhtémoc, CDMX", "Remoto", {"México"}),

    # --- Abrangência dentro do Brasil ("Barueri + 35 cidades") não é nome
    # de país estrangeiro — precisa cair em "sem restrição", não em
    # "escopo desconhecido" (que seria rejeitado pelo motivo errado).
    ("regiao-br-barueri-mais-cidades", "Remoto (Barueri + 35 cidades)", "", set()),

    # --- ANTI-REGRESSÃO CRÍTICA: vaga americana sem sigla de estado, só
    # texto livre ("Greater Seattle Area") tem que continuar caindo em
    # "escopo desconhecido" (não-vazio, rejeitável) — é o vazamento que
    # motivou boa parte do trabalho de escopo nesta sessão. NUNCA deveria
    # virar conjunto vazio (que combina_com() trata como "sem restrição,
    # aceita").
    ("greater-seattle-area-continua-barrada", "Greater Seattle Area", "Remoto", {"seattle"}),

    # --- Sem restrição explícita.
    ("anywhere-sem-restricao", "Remote (Anywhere)", "", set()),
    ("worldwide-sem-restricao", "Remote - Worldwide", "", set()),

    # --- País fora do dicionário fica "escopo desconhecido" (rejeitável),
    # não "sem restrição" — filtro de mercado é allowlist, não blocklist.
    ("pais-nao-mapeado-fica-desconhecido", "Remote - Vietnam", "", {"vietnam"}),

    # --- Formatos básicos por extenso, incluindo país depois da cidade.
    ("us-only-classico", "Remote — US only", "", {"Estados Unidos"}),
    ("brazil-based", "Remote, Brazil based", "", {"Brasil"}),
    ("pais-depois-da-cidade", "Remote - Florida, United States", "", {"Estados Unidos"}),
]


@pytest.mark.parametrize(
    "nome,local,modalidade,esperado",
    CASOS_ESCOPO,
    ids=[c[0] for c in CASOS_ESCOPO],
)
def test_extrair_escopo_remoto(nome, local, modalidade, esperado):
    assert extrair_escopo_remoto(local, modalidade) == esperado


# ---------------------------------------------------------------------------
# Job.combina_com(regras) -> bool — pipeline completo (cargo + cidade/
# modalidade + mercado + idioma), não só a extração de escopo isolada.
# ---------------------------------------------------------------------------

CASOS_COMBINA_COM = [
    # Anti-regressão crítica (mesmo caso do teste de escopo, agora
    # end-to-end): vaga americana sem sigla de estado tem que ser barrada
    # no perfil internacional (que só aceita LATAM/Ibéria).
    ("seattle-barrada-perfil-intl", "Senior Data Analyst", "Greater Seattle Area", "Remoto", PERFIL_INTL, False),
    # Remota sem mercado declarado: só passa se o TÍTULO afirmar idioma/
    # região (spanish/portuguese/latam/...) — regra adicionada depois que
    # "Senior Data Analyst" remoto sem relação nenhuma com o mercado
    # passava só por não ter nada que a rejeitasse.
    ("spanish-speaking-sem-mercado-passa", "Spanish Speaking Data Analyst", "Remote", "Remoto", PERFIL_INTL, True),
    ("data-analyst-latam-passa", "Data Analyst LATAM", "Remote", "Remoto", PERFIL_INTL, True),
    ("sem-idioma-sem-mercado-barrada", "Senior Data Analyst", "Remote", "Remoto", PERFIL_INTL, False),
    # Mercado CONFIRMADO no texto dispensa o sinal de idioma no título — o
    # país hispanofalante já é o próprio sinal.
    ("mercado-confirmado-dispensa-idioma-no-titulo", "Senior Data Analyst", "Remote - Espanha", "Remoto", PERFIL_INTL, True),

    # Perfil Brasil: cargo e cidade são checados em campos separados
    # (título vs. local) — cidade fora da lista aceita barra mesmo com
    # cargo batendo.
    ("cidade-fora-da-lista-barrada", "Estágio em TI", "Nova York", "Presencial", PERFIL_BR, False),
    ("cargo-fora-do-escopo-barrado", "Vendedor Externo", "Fortaleza, CE", "Presencial", PERFIL_BR, False),
    ("cargo-forte-cidade-aceita-passa", "Estágio em TI", "Fortaleza, CE", "Presencial", PERFIL_BR, True),
    # keywords_ambiguo (ex: "Desenvolvedor") só conta com qualificador
    # de dev/dados junto no título — sozinho é ruído de outra área.
    ("cargo-ambiguo-sem-qualificador-barrado", "Desenvolvedor", "Fortaleza, CE", "Presencial", PERFIL_BR, False),
    ("cargo-ambiguo-com-qualificador-passa", "Desenvolvedor React Jr", "Fortaleza, CE", "Presencial", PERFIL_BR, True),
]


@pytest.mark.parametrize(
    "nome,titulo,local,modalidade,perfil,esperado",
    CASOS_COMBINA_COM,
    ids=[c[0] for c in CASOS_COMBINA_COM],
)
def test_combina_com(nome, titulo, local, modalidade, perfil, esperado):
    job = Job(
        titulo=titulo, empresa="Teste", local=local, link=f"https://teste.invalido/{nome}",
        site="Teste", modalidade=modalidade,
    )
    assert job.combina_com(perfil.regras) == esperado


# ---------------------------------------------------------------------------
# Job.publicacao_antiga -- meses/anos = True, dias/semanas/vazio/absoluto
# sem ano = False. Ver MEDIDO na property (job.py): vaga real da Sólides
# ("há 7 meses") no jobs.db motivou o campo.
# ---------------------------------------------------------------------------

CASOS_PUBLICACAO_ANTIGA = [
    # Caso real, capturado no jobs.db em produção (Solides, "ANALISTA DE
    # DADOS / MIGRAÇÃO - PLENO") -- o caso que motivou o campo.
    ("caso-real-solides-7-meses", "há 7 meses", True),
    ("mes-singular", "há 1 mês", True),
    ("anos-plural", "há 2 anos", True),
    ("ano-singular", "há 1 ano", True),
    # Dias/semanas continuam "fresca" -- só mês/ano é sinal inequívoco.
    ("dias-nao-e-antiga", "há 3 dias", False),
    ("semanas-nao-e-antiga", "há 2 semanas", False),
    ("hoje-nao-e-antiga", "hoje", False),
    ("ontem-nao-e-antiga", "ontem", False),
    # Sem dado nenhum (fonte não expõe) -- não dá pra afirmar "antiga" por
    # ausência de informação.
    ("vazio-nao-e-antiga", "", False),
    # Formato absoluto SEM ano -- não dá pra calcular idade sem saber o
    # ano, então fica False de propósito (não arrisca adivinhar).
    ("absoluto-sem-ano-nao-e-antiga", "Publicada em 11/08", False),
]


@pytest.mark.parametrize(
    "nome,publicado_em,esperado",
    CASOS_PUBLICACAO_ANTIGA,
    ids=[c[0] for c in CASOS_PUBLICACAO_ANTIGA],
)
def test_publicacao_antiga(nome, publicado_em, esperado):
    job = Job(
        titulo="Analista de Dados", empresa="Teste", local="Recife, PE",
        link=f"https://teste.invalido/{nome}", site="Teste", modalidade="Presencial",
        publicado_em=publicado_em,
    )
    assert job.publicacao_antiga == esperado
