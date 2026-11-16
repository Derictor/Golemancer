# GUIA DE ATUALIZACAO — GOLEMANCER (Thea 2: The Shattering)

Este documento serve de referência para quem quiser voltar a atualizar ou expandir este mod no futuro.

---

## 1. LOCALIZACAO DO MOD

Pasta: `D:\SteamLibrary\steamapps\common\Thea 2 The Shattering\Thea2_Data\StreamingAssets\Mods\Golemancer\`

---

## 2. ESTRUTURA DE PASTAS

```
Golemancer/
├── info.txt                          # Manifesto do mod (imagens, DBs, scripts, story modules)
├── LEIA-ME.md                        # Documentacao para jogador
├── YURI_MIZUKI_ESPECIFICACAO.md      # Especificacao tecnica original (design)
├── DATABASE_SUBRACE.xml              # Subraces (Yuri + todos os golens + halves)
├── DATABASE_TAGS_QUEST.xml           # Tags do mod (genero, itens, golens, sanidade)
├── DATABASE_SKILLS_1_NATURAL.xml     # Skills naturais de personagens/pets
├── DATABASE_SKILLS_PACKS.xml         # Pacotes de skills por classe/subrace
├── DATABASE_SUBSKILLS_CHALLENGES_SUPPORT.xml   # Subskills de suporte (passivas, atributos)
├── DATABASE_SUBSKILLS_CHALLENGES_DEFENCE.xml   # Subskills de defesa (shielding)
├── DATABASE_ITEMS_CARGOS.xml         # Cargos de item (equipavel no slot Companion)
├── DATABASE_TRAIT_CARDS.xml          # Traco de perfil da classe (Yuri)
├── DATABASE_DES_LOCALIZATION.xml     # Texto PT-BR (nomes e descricoes visiveis)
├── DATABASE_DES_NAMES.xml            # Nomes de personagens
├── DATABASE_RECIPES_ITEMS.xml        # Receitas de fabricacao (custo de materiais)
├── DATABASE_TECH_ITEM.xml            # Arvore de tecnologia (desbloqueios por tier)
├── YM_UniqueRecruitment.cs           # Script: recrutamento unico de Yuri (1 por campanha)
├── YM_ForjarProle.cs                 # Script: criacao de descendentes (Sopro de Argila)
├── YM_ForjaViva.xml                  # Story module: 9 eventos unicos
├── Images/Interface/                 # Todas as artes (cards, rosters, icones, eventos, cenas, HUD)
│   ├── Cards/        (1024x1536)
│   ├── Roster/       (256x256 RGBA transparente - foco no rosto)
│   ├── Classe/       (256x256 icones de classe)
│   ├── Skills/       (256x256 icones de habilidade)
│   ├── Items/        (256x256 icones de item)
│   ├── Events/       (700x1000 vertical + 1280x720 wide)
│   ├── Scenes/       (1536x1024 ilustracao de interacao)
│   ├── HUD/          (painéis, barras, slots, molduras)
│   └── Portraits/    (716x1000 retrato de Yuri)
├── tools/                            # Gerador procedural de arte
│   └── generate_art.py               # Script Python para gerar todas as imagens
└── .git/                             # Repositorio git (historico de versoes)
```

---

## 3. COMO ADICIONAR UM NOVO GOLEM

Passo a passo:

### 3.1. DATABASE_SUBRACE.xml
Adicionar um novo `<SUBRACE-...>` antes do fechamento `</SUBRACES>`:
- Definir `Race Value="RACE-CONCEPT"` (para golens)
- Adicionar `<SecondSubraceAttributes Amount="1" Tag="TAG-CONCEPT" />`
- Adicionar `<SecondSubraceAttributes Amount="1" Tag="TAG-YM_GOLEM_CORE" />`
- Definir atributos principais (MainSubraceAttributes) e secundarios (SecondSubraceAttributes)
- Adicionar `<CommonSubraceAttributes Chance="100"><CountedTag Amount="1" Tag="TAG-GENDER_OTHER" /></CommonSubraceAttributes>`
- Referenciar `SKILL_PACK-YM_GOLEM_<NOME>` em NaturalSkills e ClassSkills
- Referenciar GraphicMale/Female com o nome do roster

### 3.2. DATABASE_TAGS_QUEST.xml
Adicionar tag para o novo golem:
```xml
<TAG-YM_GOLEM_<NOME> Visible="FALSE">
  <DescriptionInfo Name="DES_YM_<NOME>" Description="DES_YM_<NOME>_DES" IconName="GOLEM_<NOME>_Roster" />
  <TagType Value="ItemType" />
  <Parent Value="TAG-YM_GOLEM_CORE" />
  <Parent Value="TAG-PET" />
</TAG-YM_GOLEM_<NOME>>
```

### 3.3. DATABASE_SKILLS_1_NATURAL.xml
Adicionar `<SKILL-YM_GOLEM_<NOME>>` com as subskills desejadas.

### 3.4. DATABASE_SKILLS_PACKS.xml
Adicionar `<SKILL_PACK-YM_GOLEM_<NOME>>` referenciando a skill acima.

### 3.5. DATABASE_SUBSKILLS_CHALLENGES_DEFENCE.xml
Adicionar `<SUBSKILL-YM_GOLEM_<NOME>>` com shielding apropriado ao tier.

### 3.6. DATABASE_ITEMS_CARGOS.xml
Adicionar `<ITEM_CARGO-YM_GOLEM_<NOME>>` com RequiredTag correspondente.

### 3.7. DATABASE_RECIPES_ITEMS.xml
Adicionar `<ITEM_REC-YM_<NOME>>` com:
- `WeightMultiplier` (0.55 T1, 0.70 T2, 0.95 T3, 1.15 T4)
- `ResearchCost` (1, 2, 3, 4)
- `MaterialRow` com recursos reais do jogo
- `Skills Value="SKILL_PACK-YM_GOLEM_<NOME>"`

### 3.8. DATABASE_TECH_ITEM.xml
Adicionar `<ITEM_TECH-YM_<NOME>_1>` com `ParentItemTech` apontando para o eixo de material correto.

### 3.9. DATABASE_DES_LOCALIZATION.xml
Adicionar `<Entry Key="DES_YM_<NOME>" Val="Nome" />` e `_DES` com descricao.

### 3.10. DATABASE_DES_NAMES.xml
Adicionar `<NAME_COLLECTION-GOLEM_<NOME>>` com nomes masculino/feminino.

### 3.11. info.txt
Adicionar `<IMAGE Name="GOLEM_<NOME>_Roster" Path="..." />` e `<IMAGE Name="GOLEM_<NOME>_Card" Path="..." />`.

### 3.12. Imagens
Gerar via `tools/generate_art.py` ou criar manualmente:
- Card: `Images/Interface/Cards/GOLEM_<NOME>_Card.png` (1024x1536)
- Roster: `Images/Interface/Roster/GOLEM_<NOME>_Roster.png` (256x256 RGBA transparente)

---

## 4. COMO ADICIONAR UM NOVO ITEM DE EQUIPAMENTO

Mesmo fluxo do golem, mas:
- `InventorySlot` diferente (RightHand, LeftHand, Armour, Jewellery, Tool)
- `WeightMultiplier` geralmente 0.55
- Subskill de defesa ou ataque no `DATABASE_SUBSKILLS_CHALLENGES_SUPPORT.xml`
- Tag com `Parent Value="TAG-MELEE_WEAPON"` (armas), `TAG-ARMOUR` (armaduras), `TAG-SHIELD` (escudos), `TAG-JEWELLERY` (joias), `TAG-TOOLS` (ferramentas)

---

## 5. COMO ADICIONAR UM NOVO EVENTO

1. Adicionar entrada em `YM_ForjaViva.xml` com `<Adventure name="..." uniqueID="X" ...>`
2. Definir `<nodes>` com `<FilterBlock>` para pre-condicoes e `<ModifierBlock>` para efeitos
3. Adicionar imagem em `Images/Interface/Events/`
4. Registrar em `info.txt` na secao `<IMAGE ... EventImage="true" />`
5. Adicionar entrada em `DATABASE_DES_LOCALIZATION.xml` para textos do evento

---

## 6. CONVENCOES DE NOMEACAO

| Elemento | Prefixo | Exemplo |
|----------|---------|---------|
| Subrace golem | `SUBRACE-GOLEM_` | `SUBRACE-GOLEM_CHOQUE` |
| Tag golem | `TAG-YM_GOLEM_` | `TAG-YM_GOLEM_CHOQUE` |
| Skill golem | `SKILL-YM_GOLEM_` | `SKILL-YM_GOLEM_CHOQUE` |
| Skill pack | `SKILL_PACK-YM_GOLEM_` | `SKILL_PACK-YM_GOLEM_CHOQUE` |
| Subskill defesa | `SUBSKILL-YM_GOLEM_` | `SUBSKILL-YM_GOLEM_CHOQUE` |
| Cargo item | `ITEM_CARGO-YM_GOLEM_` | `ITEM_CARGO-YM_GOLEM_CHOQUE` |
| Receita | `ITEM_REC-YM_` | `ITEM_REC-YM_CHOQUE` |
| Tech | `ITEM_TECH-YM_` | `ITEM_TECH-YM_CHOQUE_1` |
| Localizacao | `DES_YM_` | `DES_YM_CHOQUE` |
| Nome | `GOLEM_` | `GOLEM_CHOQUE` |
| Item Yuri | `ITEM_REC-YM_` | `ITEM_REC-YM_LAMINA_FORJA` |
| Tag item Yuri | `TAG-YM_ITEM_` | `TAG-YM_ITEM_LAMINA_FORJA` |
| Half-descendente | `HALF_` | `HALF_ARGILA`, `HALF_BRASA` |

---

## 7. SISTEMAS IMPLEMENTADOS

### Corrupção de Forja (TAG-YM_CORRUPCAO_FORJA)
- Cada forja acumula corrupção em Yuri (atributo WorldType)
- Limiar 10: Yuri não pode forjar até limpar (1 turno na forja + 2 Ervas/dia)
- Limiar 20: Golens ficam Irritados (−1 moral/turno)
- Limiar 30: Yuri é corrompido e se torna NPC hostil

### Sanidade (TAG-YM_SANIDADE / TAG-YM_CORRUPCAO_MENTAL)
- Perda: ao receber dano, perde Misticismo e Sabedoria (SKILL-YM_SANIDADE_LOSS)
- Recuperação: passiva que restaura com o tempo (SKILL-YM_SANIDADE_RECOVER)

### Reprodução Mágica ("O Sopro de Argila")
- Requer: 2 golens (1 macho + 1 fêmea), 4 Argila ou Madeira, 1 Essência
- Bebê nasce com TAG-GROWING_UP e amadurece em 25-45 turnos
- Únicos T4 são estéreis (TAG-YM_STERILE)
- FMO: `FMO_YM_ForjarProle` em `YM_ForjarProle.cs`

### Níveis de Golem (Tiers)
| Tier | Nome | Peso | Forja | Máx simultâneos |
|------|------|------|-------|-----------------|
| T1 | Inferior | 0.55 | 1 turno, acampamento | 4 |
| T2 | Feitor | 0.70 | 2 turnos, oficina | 3 |
| T3 | Superior | 0.95 | 3 turnos, forja+oficina | 2 |
| T4 | Único | 1.15 | 4 turnos + Batismo (evento) | 1 por campanha |

---

## 8. ARQUIVOS GIT E VERSIONAMENTO

O mod usa git para versionamento. Comandos úteis:

```bash
# Ver histórico
git log --oneline

# Ver mudanças não commitadas
git status

# Ver diff de um arquivo
git diff DATABASE_SUBRACE.xml

# Voltar para versão anterior
git checkout -- <arquivo>

# Commit de mudanças
git add .
git commit -m "descricao da mudança"
```

Commits importantes:
- `2383ea3` - Versão base completa
- `3730651` - Expansão v1.1 (novos golens, halves, itens, sanidade)
- `7c2046b` - Correções de arte e caminhos
- `c10f042` - Tradução completa PT-BR

---

## 9. GERACAO DE ARTE

O script `tools/generate_art.py` gera todas as imagens proceduralmente (Pillow). Para regenerar:

```bash
python tools/generate_art.py
```

Tamanhos padrão:
- Card: 1024x1536 RGB
- Roster: 256x256 RGBA (fundo transparente, foco no rosto)
- Ícones: 256x256 RGBA
- Evento Vertical: 700x1000 RGB
- Evento Wide: 1280x720 RGB
- Cena: 1536x1024 RGB
- HUD: variados RGBA

Estilo: Dark Fantasy (desaturado, ferro/gelo/osso, alto contraste, vinheta, granulação, poeira).

---

## 10. DICAS DE MANUTENCAO

1. **Sempre valide XMLs** após editar: abra no navegador ou use um validador XML
2. **Mantenha IDs consistentes** entre DATABASE_SUBRACE, DATABASE_TAGS_QUEST, DATABASE_RECIPES_ITEMS, info.txt
3. **Não renomeie TAGs** após o lançamento (quebra saves existentes)
4. **Adicione novos golens no final** do DATABASE_SUBRACE.xml antes de `</SUBRACES>`
5. **Teste no jogo** antes de commitar: inicie uma campanha e verifique se Yuri aparece
6. **Mantenha o LEIA-ME.md atualizado** com novo conteúdo

---

## 11. CONTATO / CREDITOS

Mod: Golemancer - Forjado de Golens
Classe: Yuri Mizuki, o Criador de Golens
Base: Thea 2: The Shattering
Inspirado nos mods: FantasticCreaturesPlus, Vampiros do Pacto Rubro, Pugilista do Caos

---

*"A magia não é um dom. É uma dívida com uma estrela morta. E ela sempre cobra."*
— Arquimaga Vitreia
