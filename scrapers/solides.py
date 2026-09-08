
import re
import time

from playwright.sync_api import sync_playwright

from core.job import Job, extrair_data_publicacao
from core.logger import get_logger
from scrapers.base import BaseScraper

logger = get_logger()

_MODALIDADES = {"remoto", "híbrido", "hibrido", "presencial"}
MAX_PAGINAS = 3


def _slug(termo: str) -> str:
    s = termo.strip().lower()
    s = s.replace("c#", "csharp").replace(".net", "dotnet")
    s = re.sub(r"[^a-z0-9áàâãéèêíïóôõöúçñ\s-]", "", s)
    return re.sub(r"\s+", "-", s)


def _extrair_vagas_do_html(html: str) -> list[Job]:
    """Extrai vagas diretamente do payload Flight do Next.js App Router embutido no HTML."""
    payloads = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)', html)
    if not payloads:
        return []
    full = "".join(payloads).replace('\\"', '"').replace('\\n', "\n")

    matches = list(re.finditer(r'"id":"([^"]+)","title":"([^"]+)"', full))
    vagas: list[Job] = []

    for i, m in enumerate(matches):
        vid = m.group(1)
        titulo = m.group(2)
        start = m.start()
        next_start = matches[i + 1].start() if i + 1 < len(matches) else start + 2500
        chunk = full[start:next_start]

        redir = re.findall(r'"redirectUrl":"([^"]+)"', chunk)
        link = redir[0] if redir else f"https://vagas.solides.com.br/vaga/{vid}"

        empresa_m = re.findall(r'"(?:companyName|tradeName)":"([^"]+)"', chunk)
        empresa = empresa_m[0] if empresa_m else "Não informado"

        city_m = re.findall(r'"city":\{"name":"([^"]+)"', chunk)
        state_m = re.findall(r'"state":\{"code":"([^"]+)"', chunk)
        partes = []
        if city_m:
            partes.append(city_m[0])
        if state_m:
            partes.append(state_m[0])
        local = " - ".join(partes) if partes else "Brasil"

        modalidade = ""
        workplace_m = re.findall(r'"workplace":\{"name":"([^"]+)"', chunk)
        if workplace_m:
            modalidade = workplace_m[0]
        else:
            texto_lower = f"{titulo} {local}".lower()
            if "remoto" in texto_lower or "remote" in texto_lower:
                modalidade = "Remoto"
            elif "hibrido" in texto_lower or "híbrido" in texto_lower:
                modalidade = "Híbrido"
            elif "presencial" in texto_lower:
                modalidade = "Presencial"

        created_m = re.findall(r'"createdAt":"([^"]+)"', chunk)
        publicado_em = created_m[0] if created_m else ""

        vagas.append(
            Job(
                titulo=titulo,
                empresa=empresa,
                local=local,
                link=link,
                site="Solides",
                publicado_em=publicado_em,
                modalidade=modalidade,
            )
        )
    return vagas


class SolidesScraper(BaseScraper):
    """Busca vagas no portal https://vagas.solides.com.br (layout Next.js App Router)."""

    def __init__(self, termos_busca: list[str]):
        self.termos_busca = termos_busca

    def buscar_vagas(self) -> list[Job]:
        vagas: list[Job] = []
        for termo in self.termos_busca:
            vagas.extend(self._buscar_termo(termo))

        logger.info(f"[Solides] {len(vagas)} vaga(s) encontrada(s) no total")
        return vagas

    def _buscar_termo(self, termo: str) -> list[Job]:
        logger.info(f"[Solides] Buscando: {termo}")
        vagas: list[Job] = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                )
            )
            page.add_init_script(
                "Object.defineProperty(navigator, 'webdriver', { get: () => undefined })"
            )

            try:
                for pagina in range(1, MAX_PAGINAS + 1):
                    url = f"https://vagas.solides.com.br/vagas/{_slug(termo)}?page={pagina}"
                    try:
                        page.goto(url, timeout=45000, wait_until="domcontentloaded")
                        time.sleep(2)
                    except Exception as e:
                        logger.warning(f"[Solides] Timeout/erro ao navegar para página {pagina} de '{termo}': {e}")
                        break

                    html = page.content()
                    vagas_da_pagina = _extrair_vagas_do_html(html)

                    # Fallback DOM caso o formato do Flight Stream mude
                    if not vagas_da_pagina:
                        cards = page.query_selector_all("li:has(h2 a), div[class*='rounded']:has(h2)")
                        for card in cards:
                            try:
                                t_el = card.query_selector("h2 a, h2, a[href*='/vaga/']")
                                if not t_el:
                                    continue
                                t = t_el.inner_text().strip()
                                l = t_el.get_attribute("href") or ""
                                if l.startswith("/"):
                                    l = f"https://vagas.solides.com.br{l}"
                                vagas_da_pagina.append(
                                    Job(
                                        titulo=t,
                                        empresa="Não informado",
                                        local="Brasil",
                                        link=l,
                                        site="Solides",
                                        publicado_em="",
                                        modalidade="",
                                    )
                                )
                            except Exception:
                                continue

                    if not vagas_da_pagina:
                        break

                    vagas.extend(vagas_da_pagina)

                    # Se a página retornou menos de 10 vagas, não há próxima página
                    if len(vagas_da_pagina) < 10:
                        break

            except Exception as e:
                logger.error(f"[Solides] Erro ao buscar '{termo}': {e}")
            finally:
                browser.close()

        return vagas
