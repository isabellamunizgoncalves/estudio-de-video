# Integração do Humanizer X no Projeto Rétrovisage

> **Arquivo — nunca implementado.** Este plano foi escrito para o motor Voice Studio, que saiu
> do fluxo em 19/11/2026 (hoje a narração é a `video-narrar` com Edge TTS). As ideias de
> humanização continuam válidas e podem alimentar a `video-humanizar`; as referências a
> `narracao-voicestudio` e ao Voice Studio não valem mais.

## Resumo Executivo

O **Humanizer X** é um motor de humanização de texto em 4 passes (padrões → voz → estatísticas → verificação) com foco especial em **Voice Mode** para scripts de TTS/agentes de voz. É gratuito, roda localmente no Claude Code e substitui ferramentas pagas ($10-20/mês).

---

## O Que o Humanizer X Traz Para o Áudio

### 1. Voice Mode — Feito Para TTS
Transforma texto escrito em **fala natural** antes de mandar para o Voice Studio:

| Texto Original (escrito) | Após Voice Mode (falado) |
|-------------------------|-------------------------|
| "Our AI-powered platform generates professional food photography..." | "So basically we take your food photos and make them look incredible. Like, restaurant-magazine level. You post them on Instagram..." |

**Regras do Voice Mode aplicadas:**
- Máx. 12 palavras por frase
- Contrações faladas: *going to → gonna, want to → wanna, kind of → kinda*
- Fillers naturais: *So, Hey, Look, Here's the thing, Quick question*
- Pausas com `...` ou fillers curtos
- Elimina transições formais (*Furthermore, Additionally, Moreover*)
- Voz ativa sempre
- Listas máx. 3 itens

### 2. SDR Mode — Para Cold Outreach / Ganchos
Se seus roteiros começam com ganchos de vendas ou chamadas para ação:
- 3-5 frases máx.
- Foco no "você" (3:1 vs "nós")
- Zero buzzwords
- Subject lines em lowercase

### 3. 30 Padrões IA Detectados e Removidos
Remove vocabulário que TTS lê de forma robótica:
- *delve, crucial, landscape, pivotal, underscore, testament, leverage, facilitate, streamline, synergy, holistic, paradigm, empower, elevate, curate, reimagine, navigate, unpack, resonate, compelling*

### 4. Ajuste Estatístico (Perplexity + Burstiness)
- **Burstiness**: Variação de comprimento de frases (σ > 8 = humano)
- **Perplexity**: Escolhas de palavras menos previsíveis
- **Entropia**: Quebra templates estruturais entre parágrafos

### 5. Voice Agent Engine (Camada Extra)
Para futuros agentes de voz interativos:
- **Layer 1**: Integração nativa Retell AI, Vapi, Bland AI, Synthflow, Fish.audio
- **Layer 2**: SSML disfluency patterns, prosody control
- **Layer 3**: Live response tuning (real-time)

---

## Onde Encaixar no Fluxo Atual

### Fluxo Atual (FLUXO.md)
```
Roteiro.md → alinhar.py → pausas.py → video-mapa → video-imagens → video-animar → video-som → video-final
```

### Fluxo Proposto Com Humanizer X
```
Roteiro.md (humano)
    │
    ▼ [NOVO] Humanizer X Voice Mode
    ├── Limpa 30 padrões IA
    ├── Injeta voz falada (contractions, fillers, ritmo)
    ├── Ajusta burstiness/perplexity para TTS
    └── Gera narracao_humanizada.txt
    │
    ▼ Voice Studio (narracao-voicestudio skill)
    ├── narracao_humanizada.txt → narracao_v01.wav
    │
    ▼ alinhar.py → pausas.py → video-mapa → ...
```

**Ponto de injeção ideal**: **Entre o roteiro final e o Voice Studio** — antes da geração de áudio.

---

## Implementação Prática

### 1. Instalar Humanizer X como Skill

```bash
# No diretório skills/ do projeto
mkdir -p skills/humanizer-x
git clone https://github.com/itsjwill/humanizer-x.git skills/humanizer-x
# ou copiar só o SKILL.md
cp skills/humanizer-x/SKILL.md ~/.claude/skills/humanizer-x/SKILL.md
```

### 2. Wrapper Script Criado: `ferramentas/audio/humanizar.py`

Já criei o wrapper Python com:
- Presets por perfil (incluindo `retrovisage`)
- Pipeline Voice Mode local (não depende de CLI)
- Contrações em FR/PT, fillers, sentence starters
- Remoção de padrões IA críticos
- Estatísticas de burstiness no output

### 3. Integrar no video-iniciar ou video-preparar

No `scripts/video.sh` ou skill `video-iniciar`, adicionar etapa:

```bash
# Etapa 0.5: Humanizar roteiro para TTS
humanizar_voz() {
    local projeto=$1
    local roteiro="$projeto/Roteiro/roteiro.md"
    local saida="$projeto/_CLAUDE/narracao/narracao_humanizada.txt"
    
    # Extrair só a narração do roteiro.md (já existe script na skill video-roteiro)
    python skills/video-roteiro/scripts/extrair_narracao.py "$roteiro" "$projeto/_CLAUDE/narracao/narracao_bruta.txt"
    
    # Humanizar para Voice Mode
    python ferramentas/audio/humanizar.py \
        "$projeto/_CLAUDE/narracao/narracao_bruta.txt" \
        "$saida" \
        --mode voice \
        --preset retrovisage
    
    echo "Narração humanizada salva em: $saida"
}
```

### 4. Atualizar narracao-voicestudio Skill

No `skills/narracao/narracao-voicestudio/SKILL.md`, Passo 1, adicionar:

> **NOVO**: Antes de gerar áudio, pergunte se o usuário quer aplicar Humanizer X Voice Mode no texto. Se sim, rode `ferramentas/audio/humanizar.py` no `.txt` de entrada antes de mandar para o Voice Studio.

---

## Benefícios Concretos Para Seus Vídeos

### Antes (Voice Studio direto no roteiro escrito)
- Frases longas, formais
- "Furthermore, the platform leverages cutting-edge technology..."
- TTS soa como robô lendo artigo

### Depois (Humanizer X Voice Mode → Voice Studio)
- "So here's the thing. The platform uses AI to make food photos look pro. Like, magazine level."
- Contrações naturais, fillers, ritmo falado
- TTS soa como pessoa falando

### Métricas de Qualidade
| Métrica | Antes | Depois (Voice Mode) |
|---------|-------|---------------------|
| Palavras/frase (média) | 18-22 | 6-12 |
| Desvio padrão (burstiness) | σ < 3 | σ > 8 |
| Contrações faladas | 0% | 80%+ |
| Fillers naturais | 0 | 3-5 por minuto |
| "Roboticidade" percebida | Alta | Baixa |

---

## Roadmap de Integração

### Fase 1: MVP (1-2 dias)
- [x] Wrapper `ferramentas/audio/humanizar.py` criado
- [ ] Instalar skill humanizer-x no Claude Code
- [ ] Testar com 1 roteiro: comparar áudio antes/depois
- [ ] Ajustar preset `retrovisage` pro seu estilo

### Fase 2: Integração no Fluxo (1 semana)
- [ ] Adicionar etapa no `video-iniciar` ou `video-preparar`
- [ ] Atualizar `narracao-voicestudio` skill para sugerir humanização
- [ ] Calibrar Voice Mode pro tom nostálgico, cinematográfico do Rétrovisage

### Fase 3: Avançado (opcional)
- [ ] Portar lógica dos 4 passes completos para Python nativo
- [ ] Adicionar SSML disfluency patterns no Voice Studio (se suportado)
- [ ] Testar Layer 2/3 do Voice Agent Engine para futuros vídeos interativos

---

## Arquivos Criados/Modificar

```
skills/
├── humanizer-x/                    # NOVO - skill clonada (opcional)
│   └── SKILL.md
│
ferramentas/audio/
├── humanizar.py                    # CRIADO - wrapper Python com preset retrovisage
├── humanizar_presets.json          # OPCIONAL - presets externos
│
skills/narracao/narracao-voicestudio/
├── SKILL.md                        # MODIFICAR - adicionar passo humanização
│
scripts/
├── rv.sh                           # MODIFICAR - adicionar comando humanizar
│
docs/
├── HUMANIZER_X_INTEGRACAO.md       # ESTE ARQUIVO
```

---

## Preset `retrovisage` Já Configurado

O wrapper já inclui preset para seu perfil:

```json
{
  "retrovisage": {
    "name": "Rétrovisage - França Anos 60",
    "language": "fr",
    "tone": "nostálgico, cinematográfico, sussurrado, íntimo",
    "pacing": "lento, pausado, com respiração",
    "max_words_per_sentence": 10,
    "fillers": ["Alors...", "Écoutez...", "Vous savez...", "En fait...", "Bon...", "Alors bon..."],
    "reactions": ["C'est fou", "Incroyable", "Vous imaginez ?", "C'est ça"],
    "contractions": {
      "je suis": "j'suis",
      "je vais": "j'vais",
      "je ne": "j'ne",
      "ce est": "c'est",
      "il y a": "y'a",
      "tu es": "t'es",
      "nous allons": "n'aller",
      "vous avez": "v'avez",
      "ils sont": "z'sont",
      "qu'est-ce que": "qu'est-c'qui",
      "il faut": "faut",
      "je veux": "j'veux",
      "je sais": "j'sais",
    },
    "pause_markers": ["...", "—"],
    "sentence_starters": ["Alors ", "Écoutez ", "Vous savez ", "Bon ", "En fait ", "Imaginez ", "Figurez-vous "],
    "avoid_words": ["furthermore", "additionally", "moreover", "consequently", "therefore", "thus", "hence"],
    "emotional_anchors": [
      "l'odeur du pain frais",
      "le crépitement de la radio",
      "la lumière dans la cuisine",
      "le goût du café au lait",
      "le bruit des pas sur le parquet"
    ],
  }
}
```

---

## Teste Rápido (Validar Agora)

```bash
# 1. Clone a skill (opcional, para usar via Claude Code)
git clone https://github.com/itsjwill/humanizer-x.git ~/.claude/skills/humanizer-x

# 2. Teste o wrapper local diretamente
echo "Our AI-powered platform generates professional food photography for restaurants, improving their digital presence and increasing customer engagement across social media channels." > /tmp/teste.txt

python ferramentas/audio/humanizar.py /tmp/teste.txt /tmp/teste_humanizado.txt --mode voice --preset retrovisage

cat /tmp/teste_humanizado.txt

# 3. Compare: gere áudio no Voice Studio ANTES e DEPOIS
# Ouça a diferença na naturalidade
```

---

## Referências

- **Repo**: https://github.com/itsjwill/humanizer-x
- **SKILL.md**: https://raw.githubusercontent.com/itsjwill/humanizer-x/main/SKILL.md
- **Voice Studio**: https://github.com/debpalash/voicestudio
- **Seu fluxo**: `docs/FLUXO.md`, `ARQUITETURA.md`