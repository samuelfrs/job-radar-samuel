import time
import urllib.parse

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

from core.job import Job
from core.logger import get_logger
from scrapers.base import BaseScraper

logger = get_logger()

_MODALIDADES = {"remoto", "híbrido", "hibrido", "presencial"}


class GlassdoorScraper(BaseScraper):
    """Busca vagas no portal do Glassdoor Brasil (https://www.glassdoor.com.br)."""

    def __init__(self, termos_busca: list[str]):
        self.termos_busca = termos_busca

    def buscar_vagas(self) -> list[Job]:
        vagas: list[Job] = []
        for termo in self.termos_busca:
            vagas.extend(self._buscar_termo(termo))

        logger.info(f"[Glassdoor] {len(vagas)} vaga(s) encontrada(s) no total")
        return vagas

    def _buscar_termo(self, termo: str) -> list[Job]:
        logger.info(f"[Glassdoor] Buscando: {termo}")
        vagas: list[Job] = []
        termo_url = urllib.parse.quote(termo)
        url = f"https://www.glassdoor.com.br/Job/jobs.htm?sc.keyword={termo_url}&locT=N&locId=36"

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                locale="pt-BR",
            )
            page = context.new_page()

            try:
                page.goto(url, timeout=35000, wait_until="domcontentloaded")
                try:
                    page.wait_for_selector('li[data-test="jobListing"]', timeout=12000)
                except PlaywrightTimeoutError:
                    logger.info(f"[Glassdoor] 0 resultados ou timeout para '{termo}'.")
                    return []

                time.sleep(1.5)  # tempo para renderização completa dos cards
                cards = page.query_selector_all('li[data-test="jobListing"]')

                for card in cards:
                    try:
                        title_el = (
                            card.query_selector('a[data-test="job-title"]')
                            or card.query_selector('a[id^="job-title"]')
                            or card.query_selector('a')
                        )
                        if not title_el:
                            continue

                        titulo = title_el.inner_text().strip()
                        if not titulo:
                            continue

                        link = title_el.get_attribute("href") or ""
                        if link and link.startswith("/"):
                            link = f"https://www.glassdoor.com.br{link}"

                        comp_el = (
                            card.query_selector('[data-test="employer-name"]')
                            or card.query_selector('[class*="EmployerName"]')
                            or card.query_selector('span[class*="Employer"]')
                        )
                        empresa = comp_el.inner_text().strip() if comp_el else "Não informado"
                        # Limpa ratings tipo "Nubank 4.4" -> "Nubank"
                        if " | " in empresa:
                            empresa = empresa.split(" | ")[0].strip()

                        loc_el = (
                            card.query_selector('[data-test="emp-location"]')
                            or card.query_selector('[data-test="job-location"]')
                            or card.query_selector('[class*="Location"]')
                        )
                        local = loc_el.inner_text().strip() if loc_el else "Brasil"

                        age_el = (
                            card.query_selector('[data-test="job-age"]')
                            or card.query_selector('[class*="JobAge"]')
                        )
                        publicado_em = age_el.inner_text().strip() if age_el else ""

                        # Detecta modalidade
                        modalidade = ""
                        texto_completo = f"{titulo} {local}".lower()
                        if "remoto" in texto_completo or "remote" in texto_completo:
                            modalidade = "Remoto"
                        elif "híbrido" in texto_completo or "hibrido" in texto_completo:
                            modalidade = "Híbrido"
                        elif "presencial" in texto_completo:
                            modalidade = "Presencial"

                        vagas.append(
                            Job(
                                titulo=titulo,
                                empresa=empresa,
                                local=local,
                                link=link,
                                site="Glassdoor",
                                publicado_em=publicado_em,
                                modalidade=modalidade,
                            )
                        )
                    except Exception as e:
                        logger.debug(f"[Glassdoor] Erro ao extrair card: {e}")
                        continue

            except Exception as e:
                logger.warning(f"[Glassdoor] Erro ao buscar '{termo}': {e}")
            finally:
                browser.close()

        logger.info(f"[Glassdoor] {len(vagas)} vaga(s) para '{termo}'")
        return vagas
