#!/usr/bin/env python3
"""
Wrapper Humanizer X para Voice Mode - prepara texto de narração para TTS Voicebox.

Uso:
    python humanizar.py <entrada.txt> <saida.txt> [--mode voice] [--preset retrovisage]

Integração:
    - Chama a skill humanizer-x via Claude Code CLI (se disponível)
    - Ou aplica transformações Voice Mode locais (fallback)
    - Presets por perfil de estilo (frança-sec-xx, etc.)
"""
import argparse
import json
import os
import random
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Seed para reprodutibilidade
random.seed(42)

# ─── Presets por Perfil ───
PRESETS_DIR = Path(__file__).parent / "humanizar_presets.json"

DEFAULT_PRESETS = {
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
    },
    "default": {
        "name": "Default Voice Mode",
        "language": "pt",
        "tone": "natural, conversational",
        "pacing": "normal",
        "max_words_per_sentence": 12,
        "fillers": ["So...", "Look...", "Here's the thing...", "You know...", "Honestly..."],
        "reactions": ["No way", "That's wild", "Right?", "Makes sense"],
        "contractions": {
            "going to": "gonna",
            "want to": "wanna",
            "kind of": "kinda",
            "sort of": "sorta",
            "let me": "lemme",
            "give me": "gimme",
            "don't know": "dunno",
            "I am": "I'm",
            "I would": "I'd",
            "I have": "I've",
        },
        "pause_markers": ["...", "—"],
        "sentence_starters": ["So ", "Look ", "Here's the thing ", "You know ", "Honestly "],
        "avoid_words": ["furthermore", "additionally", "moreover", "consequently", "therefore", "thus", "hence"],
        "emotional_anchors": [],
    }
}

# ─── Padrões IA para Remover (Pass 1 - Voice Mode Relevante) ───
AI_PATTERNS_CRITICAL = [
    # Inglês
    r"\b(delve|crucial|landscape|pivotal|testament|underscore|leverage|facilitate|streamline|synergy|holistic|paradigm|empower|elevate|curate|reimagine|navigate|unpack|resonate|compelling|multifaceted|comprehensive|robust|vibrant|nuanced|intricate|tapestry|enduring|garner|showcase|highlight|emphasize|interplay|key|vital|significant|cutting.edge|groundbreaking|game.changer|revolutionary|transformative|unprecedented|seamless|effortless)\b",
    # Francês
    r"\b(crucial|pivot|témoignage|souligner|exploite[rst]?|facilite[rst]?|rationnalise[rst]?|synergie|holistique|paradigme|autonomise[rst]?|élev[eé]r?|organise[rst]?|réinvente[rst]?|navigue[rst]?|déball[eé]r?|résonne[rst]?|percutant|multiforme|exhaustif|robuste|vibrant|nuancé[e]?|complexe|tapisserie|durable|obtient?|présente[rst]?|mettre.en.valeur|insiste[rst]?|interaction|clé|vital|significatif|novateur|révolutionnaire|transformateu?r?|sans.précédent|fluide|sans.effort|pointe|rationnel|optimise[rst]?|maximise[rst]?|améliore[rst]?)\b",
]
AI_PATTERNS_HIGH = [
    r"—",  # em dash
    r"\b(not only|not just|not merely|ne.seulement|pas.seulement|non.seulement)\b.*?\b(but also|but|mais)\b",
    r"\b(stands? as|serves? as|marks?|represents?|boasts?|features?|offers?|constitutes?|functions? as|sert.de|fonctionne.comme|marque|représente|offre|constitue)\b",
    r"\b(great question|excellent point|absolutely|certainly|of course|bonne.question|excellent.point|absolument|certainnement|bien.sûr|évidemment)\b",
]

# ─── Funções de Transformação Voice Mode ───
def load_preset(preset_name: str) -> Dict:
    """Carrega preset do arquivo JSON ou usa default."""
    if PRESETS_DIR.exists():
        with open(PRESETS_DIR, encoding="utf-8") as f:
            presets = json.load(f)
        if preset_name in presets:
            return presets[preset_name]
    return DEFAULT_PRESETS.get(preset_name, DEFAULT_PRESETS["default"])

def apply_contractions(text: str, contractions: Dict[str, str]) -> str:
    """Aplica contrações faladas (case-insensitive)."""
    result = text
    for formal, spoken in contractions.items():
        # Word boundaries para não quebrar dentro de palavras
        pattern = re.compile(re.escape(formal), re.IGNORECASE)
        result = pattern.sub(spoken, result)
    return result

def split_long_sentences(text: str, max_words: int) -> str:
    """Divide frases longas em pedaços menores (heurística simples)."""
    # Primeiro, normaliza: garante espaço após pontuação
    text = re.sub(r'([.!?])([A-ZÀ-ÿ])', r'\1 \2', text)
    
    sentences = re.split(r'(?<=[.!?])\s+', text)
    result = []
    for sent in sentences:
        words = sent.split()
        if len(words) <= max_words:
            result.append(sent)
        else:
            # Divide no meio aproximadamente
            mid = len(words) // 2
            # Procura ponto de divisão natural (vírgula, conjunção, que)
            split_idx = mid
            connectors = ('e', 'et', 'mais', 'car', 'puis', 'que', 'qui', 'où', 'donc', 'or', 'ni', 'mais', 'porque', 'pois', 'assim', 'logo', 'então', 'porém', 'contudo', 'todavia', 'mas')
            for i in range(max(mid-5, 0), min(mid+5, len(words))):
                w = words[i].rstrip(',;:').lower()
                if w in connectors or words[i].endswith((',', ';', ':')):
                    split_idx = i + 1
                    break
            part1 = ' '.join(words[:split_idx]).rstrip(',;:')
            part2 = ' '.join(words[split_idx:])
            if part1 and not part1[-1] in '.!?':
                part1 += '.'
            if part2:
                part2 = part2[0].upper() + part2[1:]
            result.append(part1)
            result.append(part2)
    return ' '.join(result)

def add_fillers_and_starters(text: str, preset: Dict) -> str:
    """Adiciona fillers e sentence starters naturais - apenas nos limites de frase."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    if not sentences:
        return text
    
    fillers = preset.get("fillers", [])
    starters = preset.get("sentence_starters", [])
    reactions = preset.get("reactions", [])
    
    result = []
    for i, sent in enumerate(sentences):
        sent = sent.strip()
        if not sent:
            continue
        
        # Adiciona starter na primeira frase e a cada ~3 frases
        if i == 0 or (i > 0 and i % 3 == 0 and starters):
            starter = starters[i % len(starters)]
            sent = starter + sent[0].lower() + sent[1:] if sent else starter
        
        # Adiciona filler no INÍCIO de frases (probabilidade 30%)
        import random
        if fillers and i > 0 and random.random() < 0.3:
            filler = fillers[i % len(fillers)].rstrip('...')
            sent = filler + ' ' + sent
        
        # Adiciona reação no final de algumas frases (probabilidade 25%)
        if reactions and i > 0 and random.random() < 0.25:
            reaction = reactions[i % len(reactions)]
            sent = sent.rstrip('.!?') + f" {reaction}."
        
        result.append(sent)
    
    return ' '.join(result)

def add_pause_markers(text: str, markers: List[str]) -> str:
    """Adiciona marcadores de pausa naturais."""
    # Após vírgulas em frases longas
    sentences = re.split(r'(?<=[.!?])\s+', text)
    result = []
    for sent in sentences:
        # Substitui algumas vírgulas por pausa mais longa
        if ',' in sent and len(sent.split()) > 6:
            parts = sent.split(',', 1)
            marker = markers[0] if markers else '...'
            sent = parts[0] + marker + ' ' + parts[1]
        result.append(sent)
    return ' '.join(result)

def remove_ai_patterns(text: str) -> str:
    """Remove padrões IA críticos e high - substitui por alternativas simples em vez de apagar."""
    result = text
    
    # Substituições diretas para padrões críticos (português/inglês/francês)
    replacements = {
        # EN -> simples
        r'\bdelve\b': 'look into',
        r'\bcrucial\b': 'important',
        r'\blandscape\b': 'scene',
        r'\bpivotal\b': 'key',
        r'\btestament\b': 'proof',
        r'\bunderscore\b': 'show',
        r'\bleverage\b': 'use',
        r'\bfacilitate\b': 'help',
        r'\bstreamline\b': 'simplify',
        r'\bsynergy\b': 'working together',
        r'\bholistic\b': 'complete',
        r'\bparadigm\b': 'model',
        r'\bempower\b': 'enable',
        r'\belevate\b': 'raise',
        r'\bcurate\b': 'select',
        r'\breimagine\b': 'rethink',
        r'\bnavigate\b': 'handle',
        r'\bunpack\b': 'explain',
        r'\bresonate\b': 'connect',
        r'\bcompelling\b': 'strong',
        r'\bmultifaceted\b': 'complex',
        r'\bcomprehensive\b': 'full',
        r'\brobust\b': 'solid',
        r'\bvibrant\b': 'lively',
        r'\bnuanced\b': 'subtle',
        r'\bintricate\b': 'detailed',
        r'\btapestry\b': 'mix',
        r'\benduring\b': 'lasting',
        r'\bgarner\b': 'get',
        r'\bshowcase\b': 'show',
        r'\bhighlight\b': 'emphasize',
        r'\bemphasize\b': 'stress',
        r'\binterplay\b': 'interaction',
        r'\bkey\b': 'main',
        r'\bvital\b': 'essential',
        r'\bsignificant\b': 'major',
        r'\bcutting.edge\b': 'advanced',
        r'\bgroundbreaking\b': 'new',
        r'\bgame.changer\b': 'big change',
        r'\brevolutionary\b': 'radical',
        r'\btransformative\b': 'changing',
        r'\bunprecedented\b': 'never seen',
        r'\bseamless\b': 'smooth',
        r'\beffortless\b': 'easy',
        # FR -> simples
        r'\bcrucial\b': 'important',
        r'\bpivot\b': 'clé',
        r'\btémoignage\b': 'preuve',
        r'\bsouligne[rst]?\b': 'montre',
        r'\bexploite[rst]?\b': 'utilise',
        r'\bfacilite[rst]?\b': 'aide',
        r'\brationalise[rst]?\b': 'simplifie',
        r'\bsynergie\b': 'collaboration',
        r'\bholistique\b': 'global',
        r'\bparadigme\b': 'modèle',
        r'\bautonomise[rst]?\b': 'permet',
        r'\bélev[eé]r?\b': 'augmente',
        r'\borganise[rst]?\b': 'prépare',
        r'\bréinvente[rst]?\b': 'revoit',
        r'\bnavigue[rst]?\b': 'gère',
        r'\bdéball[eé]r?\b': 'explique',
        r'\brésonne[rst]?\b': 'touche',
        r'\bpercutant\b': 'fort',
        r'\bmultiforme\b': 'varié',
        r'\bexhaustif\b': 'complet',
        r'\brobuste\b': 'solide',
        r'\bvibrant\b': 'vivant',
        r'\bnuancé[e]?\b': 'subtil',
        r'\bcomplexe\b': 'complexe',
        r'\btapisserie\b': 'mélange',
        r'\bdurable\b': 'durable',
        r'\bobtient?\b': 'a',
        r'\bprésente[rst]?\b': 'montre',
        r'\bmettre.en.valeur\b': 'valorise',
        r'\binsiste[rst]?\b': 'insiste',
        r'\binteraction\b': 'échange',
        r'\bclé\b': 'principal',
        r'\bvital\b': 'essentiel',
        r'\bsignificatif\b': 'majeur',
        r'\bnovateur\b': 'nouveau',
        r'\brévolutionnaire\b': 'radical',
        r'\btransformateu?r?\b': 'qui change',
        r'\bsans.précédent\b': 'jamais vu',
        r'\bfluide\b': 'fluide',
        r'\bsans.effort\b': 'facile',
        r'\btechnologie de pointe\b': 'technologie avancée',
        r'\bde pointe\b': 'avancée',
        r'\bpointe\b': 'avancé',
        r'\boptimise[rst]?\b': 'améliore',
        r'\bmaximise[rst]?\b': 'augmente',
        r'\baméliore[rst]?\b': 'améliore',
    }
    
    for pattern, replacement in replacements.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    
    # Padrões HIGH - remove estruturas problemáticas
    for pattern in AI_PATTERNS_HIGH:
        result = re.sub(pattern, '', result, flags=re.IGNORECASE)
    
    # Limpeza: espaços duplos, pontuação estranha
    result = re.sub(r'\s+', ' ', result)
    result = re.sub(r'\s+([.!?])', r'\1', result)
    result = re.sub(r'\b\w{1,2}\b\s+\b\w{1,2}\b', '', result)  # remove palavras soltas muito curtas
    return result.strip()

def inject_emotional_anchors(text: str, anchors: List[str]) -> str:
    """Injeção opcional de ancoragem sensorial (usar com moderação)."""
    if not anchors:
        return text
    # Adiciona uma âncora a cada ~5 frases se o texto for longo
    sentences = re.split(r'(?<=[.!?])\s+', text)
    if len(sentences) < 5:
        return text
    
    result = []
    for i, sent in enumerate(sentences):
        result.append(sent)
        if i > 0 and i % 5 == 0 and anchors:
            anchor = anchors[(i // 5) % len(anchors)]
            result.append(f"({anchor})")
    return ' '.join(result)

def humanize_voice_mode(text: str, preset: Dict) -> str:
    """Pipeline completo Voice Mode."""
    # 1. Remove/substitui padrões IA
    text = remove_ai_patterns(text)
    
    # 2. Contrações faladas
    text = apply_contractions(text, preset.get("contractions", {}))
    
    # 3. Divide frases longas
    text = split_long_sentences(text, preset.get("max_words_per_sentence", 12))
    
    # 4. Adiciona fillers/starters/reactions
    text = add_fillers_and_starters(text, preset)
    
    # 5. Marcadores de pausa
    text = add_pause_markers(text, preset.get("pause_markers", ["..."]))
    
    # 6. Ancoragem emocional (opcional, leve)
    if preset.get("emotional_anchors"):
        text = inject_emotional_anchors(text, preset["emotional_anchors"])
    
    # 7. Limpeza final
    text = cleanup_text(text)
    
    return text.strip()

def cleanup_text(text: str) -> str:
    """Limpeza pós-processamento."""
    # Fix artigos/preposições duplicados ou errados
    fixes = [
        (r'\bde (avancée|avancé|nouveau|nouvelle|différent|différente|grand|grande|petit|petite|bon|bonne|mauvais|mauvaise)\b', r'\1'),
        (r'\bà (le|la|les)\b', lambda m: {'le': 'au', 'la': 'à la', 'les': 'aux'}[m.group(1)]),
        (r'\bde (le|la|les)\b', lambda m: {'le': 'du', 'la': 'de la', 'les': 'des'}[m.group(1)]),
        (r'\s+', ' '),
        (r'\s+([.!?])', r'\1'),
        (r'([.!?])\s*([A-ZÀ-ÿ])', r'\1 \2'),
    ]
    for pattern, repl in fixes:
        text = re.sub(pattern, repl, text)
    return text.strip()

def call_claude_skill(text: str, mode: str) -> Optional[str]:
    """Tenta chamar a skill humanizer-x via Claude Code CLI."""
    try:
        # Verifica se claude CLI existe
        if not shutil.which("claude"):
            return None
        
        # Tenta invocar skill (pode não funcionar direto via CLI)
        # Esta é uma aproximação - a skill roda dentro do Claude Code
        result = subprocess.run(
            ["claude", "--print", f"/humanizer-x --mode {mode}"],
            input=text.encode(),
            capture_output=True,
            timeout=60
        )
        if result.returncode == 0:
            return result.stdout.decode().strip()
    except Exception:
        pass
    return None

def main():
    parser = argparse.ArgumentParser(description="Humaniza texto para TTS Voicebox")
    parser.add_argument("entrada", help="Arquivo .txt de entrada (narração bruta)")
    parser.add_argument("saida", help="Arquivo .txt de saída (humanizado)")
    parser.add_argument("--mode", default="voice", choices=["voice", "casual", "professional", "academic", "creative", "sdr"])
    parser.add_argument("--preset", default="retrovisage", help="Nome do preset (ex: retrovisage)")
    parser.add_argument("--use-claude-skill", action="store_true", help="Tentar usar skill humanizer-x via Claude CLI")
    args = parser.parse_args()
    
    # Lê entrada
    with open(args.entrada, encoding="utf-8") as f:
        texto = f.read().strip()
    
    if not texto:
        print("Erro: arquivo de entrada vazio", file=sys.stderr)
        sys.exit(1)
    
    # Carrega preset
    preset = load_preset(args.preset)
    print(f"Usando preset: {preset['name']} ({preset['language']})")
    
    # Tenta skill Claude primeiro (se pedida)
    if args.use_claude_skill:
        resultado = call_claude_skill(texto, args.mode)
        if resultado:
            texto = resultado
            print("✓ Humanização via skill humanizer-x (Claude Code)")
        else:
            print("⚠ Skill não disponível, usando fallback local")
    
    # Fallback/local: aplica transformações Voice Mode
    if args.mode == "voice":
        texto = humanize_voice_mode(texto, preset)
        print("✓ Transformações Voice Mode aplicadas localmente")
    
    # Salva saída
    os.makedirs(os.path.dirname(os.path.abspath(args.saida)), exist_ok=True)
    with open(args.saida, "w", encoding="utf-8") as f:
        f.write(texto)
    
    print(f"✓ Salvo em: {args.saida}")
    
    # Stats
    orig_words = len(texto.split())
    sentences = re.split(r'[.!?]+', texto)
    sent_lengths = [len(s.split()) for s in sentences if s.strip()]
    if sent_lengths:
        import statistics
        avg_len = sum(sent_lengths) / len(sent_lengths)
        std_len = statistics.stdev(sent_lengths) if len(sent_lengths) > 1 else 0
        print(f"  Frases: {len(sent_lengths)} | Média: {avg_len:.1f} palavras | Desvio (burstiness): {std_len:.1f}")

if __name__ == "__main__":
    main()