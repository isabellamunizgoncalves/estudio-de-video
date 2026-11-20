# Regras comuns das skills rv-* (Rétrovisage)

Sequência completa do canal: `/video-roteiro` → `/video-humanizar` → `/video-iniciar` → narração (`video-narrar`) → `/video-preparar` → `/video-mapa` → `/video-imagens` → `/video-animar` → `/video-som` → `/video-final`. O contrato de arquivos entre as etapas está em `docs/FLUXO.md`.

Lidas uma vez por sessão por todas as skills de edição. Mudou uma regra geral? Mude aqui, não em cada skill.

## 0. Onde tudo mora
O fluxo roda no computador de Isabella, na raiz do repositório `meu-fluxo-de-edicao` (a pasta `youtube/`). Todos os caminhos abaixo são relativos a essa raiz.

| O quê | Onde |
|---|---|
| Skills | `skills/<etapa>/<skill>/` (roteiro, narracao, edicao) |
| Scripts | `ferramentas/` (Python do ambiente: `.venv-edicao/` na raiz, criado por `scripts/instalar-local.sh`) |
| Perfil | `perfis/retrovisage/` (identidade, estilo-*, catálogo) |
| Bibliotecas que crescem | `biblioteca/musica/`, `biblioteca/sfx/` (com `creditos.md` e índice) |
| Cada vídeo | `projects/<slug>/` (ex.: `projects/retrovisage-04/`), fora do git |

**Pastas de um vídeo** (criadas por `scripts/novo-projeto.sh <slug>`):

| Pasta | Quem grava | O que tem |
|---|---|---|
| `Roteiro/` | skills de roteiro | `roteiro.md` (estruturado), `roteiro.txt` (texto puro), `roteiro_humanizado.txt` (pronto para a voz) |
| `Narracao/` | `video-narrar` ou Isabella | `narracao_vNN.wav` bruta (+ ficha `.json` quando veio da skill) |
| `Imagens/`, `Musica/` | Isabella | o que ela sobe à mão |
| `_CLAUDE/` | skills de edição | estado (`projeto.json`), transcrição, narração ajustada, mapa, imagens prontas, renders, mix, entrega |

**Começo de toda sessão:**
1. Se `.venv-edicao/` (na raiz) e `~/.venv-edicao/` não existirem, rode `scripts/instalar-local.sh` em segundo plano.
2. O vídeo: se Isabella não disse qual, liste as pastas em `projects/` (menos `_templates`) e pergunte.

**Salvar = gravar em `projects/<slug>/` e atualizar o estado.** Os vídeos não vão para o git (áudio, imagem e render são pesados); o backup deles é por conta de Isabella.
- Mudança em skills, scripts, perfil ou biblioteca vai para o git: commit no repositório do fluxo, e push só quando ela pedir.
- Renders (`_CLAUDE/renders/`) se recriam a partir do estado: podem ser refeitos se sumirem.

## 1. Conversa e segurança
- Falar com Isabella em português, frases curtas, sem jargão sem explicar. Ela não edita com código.
- **Tudo automático** (preferência de Isabella, 04/11): o Claude faz o trabalho de cada etapa sozinho, escolhe a melhor opção e só depois mostra para ela conferir e aprovar (ou trocar por número). Não entregar listas de tarefas para ela executar.
- Nunca mover, renomear ou apagar o que ela subiu (roteiro, narração, imagens). Tudo o que o Claude gera fica em `_CLAUDE/`.
- Nunca sobrescrever um arquivo já entregue: versão nova (`_v01`, `_v02`…).
- Apagar, quando precisar: mover para `_CLAUDE/_lixeira/` e deixar ela decidir.
- Mudança nas skills, scripts ou perfil: só com o "sim" dela, e com commit (o git é o histórico para voltar).

## 2. Estado do vídeo sem ler inteiro
Cada vídeo tem `_CLAUDE/projeto.json`. Ler e mudar sempre pelo script de estado (`ferramentas/util/estado.py`):
- `estado.py <pasta> status`: onde o vídeo está;
- `estado.py <pasta> <bloco>`: resumo de um bloco (`--json` para o bloco inteiro; `--item <id>` para um item);
- `--set <caminho> <valor>`, `--etapa <etapa>=<status>`;
- `--pendencia <etapa> "<texto>"` e `--resolver <id>`.

Status: `pendente`, `em_andamento`, `aguardando_aprovacao`, `aguardando_isabella`, `concluido`, `nao_precisa`.
Ids estáveis (`c01` capítulo, `cn001` cena, `img014` imagem, `mus03` música, `sfx12` som): é por eles que ela pede ajustes.

## 3. Caderno de aprendizados (`_CLAUDE/aprendizados.md`)
Anotar na hora, durante a revisão de qualquer etapa, toda correção, elogio ou preferência que vale para outros vídeos:
- "zoom mais lento nas fotos", "essa música ficou perfeita": **anota**;
- "troca essa foto": **não anota** (é só deste vídeo);
- na dúvida, anota com "(talvez só deste vídeo)".

Formato: `- [ ] <etapa> · <o que foi pedido, com contexto> · <dd/mm>`. Depois de aplicado: `- [x] … → <onde entrou>`; só daquele vídeo: `- [-] …`. Nunca apagar linhas. Anotar não é mudar (seção 5).

## 4. Trechos, ponto salvo e fechar uma etapa
- O plano (`/video-mapa`) olha o vídeo inteiro. Animar e som podem ir por trecho, escolhido na hora ("o gancho", "até 5:00", "capítulo 2"). Uma cena pertence ao trecho em que começa. Cada trecho lê o que os anteriores fizeram, para não repetir fórmula.
- **Ponto salvo:** trecho ou etapa terminado, revisões aplicadas, entrega gerada e estado atualizado. Só aí sugerir `/clear` e `/video`.
- **Pendência:** pedido ainda não aplicado é anotado na hora pelo script de estado e aparece no status.
- **Fechar a etapa** (aprovada inteira): marcar `concluido`, dizer quantos aprendizados ficaram anotados, sugerir `/clear` e `/video`.

## 5. Aplicar os aprendizados (quando Isabella pedir)
1. Ler as linhas `- [ ]` do caderno.
2. Propor onde cada uma entra: gosto vai para o perfil (`estilo-*.md`, `identidade.md`, `catalogo.md`); ofício (vale para qualquer vídeo) vai para a skill da etapa; o que vale para todas vai para este arquivo.
3. Ela filtra. Gravar só o aprovado, mostrando antes o texto das mudanças maiores. Marcar cada linha. Commit no repositório do fluxo.

## 6. Revisão sempre por vídeo pronto
- Não há programa de edição: Isabella revisa assistindo. O Claude manda o vídeo pela conversa (ferramenta de envio de arquivo).
- Rascunho de revisão em **720p** (mais rápido); o final em 1920x1080, 30 qps.
- Ela pede citando o **minuto** ("no 3:40, troca a foto") ou o **número** ("cn014 mais devagar"). Converta o minuto para a cena pelo mapa.
- Cada ajuste é um render novo: junte vários pedidos antes de renderizar.

## 7. Licenças e créditos
- Toda imagem, música e efeito tem fonte e licença anotadas em `_CLAUDE/creditos.json` do vídeo. Sem licença clara, não entra.
- Foto francesa do século XX: domínio público só 70 anos depois da morte do fotógrafo. Preferir acervos que declaram a licença (Gallica, Wikimedia Commons, Europeana, Library of Congress) e anotar o que eles dizem.
- **Nunca imagem com marca d'água** (Pngtree e afins) nem logotipo de marca em destaque.
- Foto enviada por Isabella também precisa de fonte e licença anotadas antes de publicar.
- A `/video-final` gera o texto de créditos para a descrição do YouTube.

## 8. Modelo por etapa (sugestão)
| Etapa | Modelo | Esforço |
|---|---|---|
| /video, /video-iniciar, /video-imagens | o mais leve que funcione bem | baixo |
| /video-preparar, /video-final | intermediário | médio |
| /video-mapa, /video-animar | o mais capaz | alto |
| /video-som, aplicar aprendizados | o mais capaz | médio |

Trocar de modelo logo depois do `/clear` não custa nada.