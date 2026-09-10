# 🎯 Plano de Adaptação do JobRadar para Estágio em TI / Desenvolvimento

Este documento descreve o plano detalhado de refatoração e calibração do projeto **JobRadar** para buscar vagas de **Estágio em TI, Desenvolvimento de Software e Engenharia**, adaptado especificamente para o perfil de **Samuel Gadelha Farias** (Engenharia de Telecomunicações UFC / Desenvolvedor Full Stack).

---

## 👤 Perfil do Usuário Alvo
- **Nome:** Samuel Gadelha Farias
- **Portfólio:** https://samuelfarias.vercel.app/
- **Formação:** Graduação em Engenharia de Telecomunicações (UFC)
- **Foco de Vagas:** Estágio / Trainee / Júnior em Desenvolvimento de Software (Full Stack, Frontend, Backend, Engenharia de Software).
- **Tech Stack Principal:** TypeScript, React, Next.js, Node.js, NestJS, TailwindCSS, PostgreSQL, Prisma, Supabase, Docker, Python, REST APIs / Clean Architecture.
- **Localização Prioritária:** Fortaleza/CE, Caucaia/CE, Eusébio/CE, Maracanaú/CE e vagas **Remotas / Home Office** (Brasil e Internacional).

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
    "typescript", "javascript", "react", "react.js", "next.js", "nextjs", 
    "node", "node.js", "nodejs", "nest", "nestjs", "tailwind", "tailwindcss",
    "postgresql", "postgres", "prisma", "supabase", "docker", "python", "sql", 
    "mysql", "sqlite", "git", "rest api"
]

# Termos que ELIMINAM a vaga imediatamente (para não receber vagas sênior/pleno ou stacks indesejadas)
PALAVRAS_EXCLUSAO = [
    "senior", "sr", "sr.", "pleno", "pl", "pl.", 
    "lead", "tech lead", "gerente", "manager", 
    "especialista", "architect", "arquiteto", "principal",
    "c#", ".net", "dotnet", "csharp", "blazor", "asp.net"
]

# Regiões e modalidades desejadas
CIDADES_ALVO = [
    "fortaleza", "caucaia", "eusebio", "maracanau", "ceara", "ce", 
    "remote", "remoto", "home office", "home-office", "qualquer lugar"
]

# Termos de consulta para varredura no LinkedIn e scrapers
TERMOS_BUSCA_LINKEDIN = [
    "estagio desenvolvimento",
    "estagio software",
    "estagio react",
    "estagio typescript",
    "estagio frontend",
    "estagio backend",
    "estagio fullstack",
    "estagio node",
    "estagio python",
    "desenvolvedor junior",
    "desenvolvedor fullstack junior",
    "desenvolvedor frontend junior",
    "desenvolvedor backend junior",
    "estagiario TI"
]