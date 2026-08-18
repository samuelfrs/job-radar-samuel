# 🎯 Plano de Adaptação do JobRadar para Estágio em TI / Desenvolvimento

Este documento descreve o plano detalhado de refatoração e calibração do projeto **JobRadar** para buscar vagas de **Estágio em TI, Desenvolvimento de Software e Engenharia**, adaptado especificamente para o perfil de **Samuel Gadelha Farias** (Engenharia de Telecomunicações UFC / Desenvolvedor Full Stack).

---

## 👤 Perfil do Usuário Alvo
- **Nome:** Samuel Gadelha Farias
- **Formação:** Graduação em Engenharia de Telecomunicações (UFC)
- **Foco de Vagas:** Estágio / Trainee / Júnior em Desenvolvimento de Software (Frontend, Backend, Full Stack, Engenharia de Software).
- **Tech Stack Principal:** React.js, Next.js, TypeScript, Node.js, C#, .NET Core, Python, Tailwind CSS, SQL (PostgreSQL, SQLite), Ruby on Rails, Linux, Docker.
- **Localização Prioritária:** Fortaleza/CE, Caucaia/CE e vagas **Remotas / Home Office** (Brasil e Internacional).

---

## 📂 Arquivos a Modificar no Repositório

### 1. `config.py` (Configuração Principal para o Brasil)
Substituir as regras originais de Dados/BI pelas regras de Desenvolvimento e Estágio:

```python
# --- TERMOS DE BUSCA E FILTRAGEM (PERFIL DESENVOLVIMENTO / ESTÁGIO) ---

# Cargos que aprovam a vaga sozinhos se encontrados no título
CARGOS_FORTES = [
    "estagio", "estag", "estagiario", "estagiaria", 
    "intern", "internship", "trainee"
]

# Cargos ambíguos que exigem um qualificador de estágio/nível junto
CARGOS_AMBIGUOS = [
    "desenvolvedor", "desenvolvedora", "developer", "dev",
    "engenheiro de software", "software engineer",
    "frontend", "front-end", "backend", "back-end", 
    "fullstack", "full-stack", "full stack", "web"
]

# Qualificadores necessários quando o cargo for ambíguo
QUALIFICADORES = [
    "estagio", "estagiario", "intern", "trainee", "junior", "jr"
]

# Ferramentas e tecnologias que somam pontos no Score de Relevância
FERRAMENTAS = [
    "react", "react.js", "next.js", "nextjs", "typescript", "javascript", 
    "node", "node.js", "nodejs", "c#", ".net", "dotnet", "net core", 
    "python", "ruby", "rails", "sql", "postgresql", "sqlite", 
    "tailwind", "docker", "linux", "git", "rest api"
]

# Termos que ELIMINAM a vaga imediatamente (para não receber vagas sênior/pleno)
PALAVRAS_EXCLUSAO = [
    "senior", "sr", "sr.", "pleno", "pl", "pl.", 
    "lead", "tech lead", "gerente", "manager", 
    "especialista", "architect", "arqueto", "principal"
]

# Regiões e modalidades desejadas
CIDADES_ALVO = [
    "fortaleza", "caucaia", "ceara", "ce", 
    "remote", "remoto", "home office", "home-office", "qualquer lugar"
]

# Termos de consulta para varredura no LinkedIn e scrapers
TERMOS_BUSCA_LINKEDIN = [
    "estagio desenvolvimento",
    "estagio software",
    "estagio react",
    "estagio frontend",
    "estagio backend",
    "estagio fullstack",
    "estagio python",
    "estagio dotnet",
    "estagiario TI"
]