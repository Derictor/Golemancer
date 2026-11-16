# Golemancer - Forjado de Golens

**Versão:** 1.0.0  
**Autor:** Kilo  
**Jogo:** Thea 2: The Shattering  
**Idioma:** Português (PT-BR)

---

## Sobre o Mod

Golemancer adiciona uma classe única ao jogo: **Yuri Mizuki**, o Criador de Golens. Yuri é um humano artífice e ferreiro que despertou a capacidade de soprar memória em matéria inanimada, criando **golems vivos** a partir de pedra, metal, madeira, ossos, comida e ervas.

Cada golem é um filho, um companheiro de batalha e uma extensão da forja de Yuri. Não se vendem golens: batiza-se.

---

## Conteúdo

### 1 Classe Única
- **Yuri Mizuki** — Humano, Artesão + Inventor. Ficha prioriza Inteligência, Sabedoria e Misticismo.

### 20 Golens (4 níveis)

**T1 — Inferiores (servos baratos, peso 0.55):**
1. Choque — Pedra + Argila — Tanque de barreira, Fiel
2. Cascalho — Pedra + Osso — Batedor quebrado, Agressivo
3. Galho — Madeira — Batedor florestal, Curioso
4. Lâmp-Âmbar — Âmbar + Quartzo — Lanterna viva, Tímido
5. Massa-Mãe — Grãos + Nozes — Golem-fermento, Maternal
6. Seixo — Pedra Pura + Arenito — Golem de estimação, Carinhoso

**T2 — Feitores (peso 0.70):**
7. Ferro-Vido — Ferro + Pedra + Carvão — Escudeiro, Protetivo
8. Raiz — Madeira de Dríade + Madeira — Suporte noturno, Sereno
9. Ossada — Osso + Osso Monstro + Argila — Anti-fera, Territorial
10. Cristal — Quartzo + Âmbar — Ressoante mental, Ecoico
11. Pão-do-Campo — Comida Cozida + Grãos + Gelee de Besouro — Ração viva, Faminto

**T3 — Superiores (peso 0.95):**
12. Muralha — Granito + Pedra Armada + Ferro — Muralha impassível, Leal Absoluto
13. Viúva-de-Cedro — Madeira Sagrada + Madeira Anciã — Luto, Luto Eterno
14. Vejo — Gema + Diamante + Pedra-da-Lua — Curinga de resistência, Vaidoso
15. Agulha — Ervas + Cogumelos + Especiarias — Médico de campo, Meticuloso
16. Ferreiro — Ferro + Carvão + Aço — Arma viva, Exigente

**T4 — Únicos (1 por campanha, peso 1.15, estéreis):**
17. Guardião da Mina — Ferro + Granito + Essência de Pedra + Couro de Golem — Muralha sagrada
18. Dragão de Osso — Ossos de Dragão + Runas + Osso Encantado + Essência da Morte — Mago de essência
19. Ceva — Ervas + Algas + Ovos + Essência da Vida — Curandeiro amaldiçoado, Empático
20. Cinzel — Aço + Composto Metálico + Mithril + Pele Alquímica — Mestre-forjador, Orgulhoso

### 4 Golens de Evento (não forjáveis normalmente)
- Estalo — Obsidiana + Igneo + Carvão — Imprevisível
- Terra Viva — Argila + Pele Alquímica + Núcleo da Terra — Paciente
- Fantasma de Forja — Essência Esquecida + Centelheiro do Vazio + Matéria Prístina — Vazio
- Gêmeo-Âmbar — Âmbar + Malaquita + Núcleo da Terra — Par com HP compartilhado

### 2 Half-Descendentes
- Half-Argila — Humano com Int 5, Sab 4, Mis 2
- Half-Brasa — Humano com Sab 4, Mis 2, Int 5

### 9 Itens de Equipamento
Lâmina de Forja, Martelo-Mestre, Malha de Cota-Viva, Escudo-Pedra, Alvo de Âmbar, Pão-Vivo, Erva da Forja, Armadilha de Lambri, Pingente do Nome.

### 5 Eventos Únicos
1. A Oficina no Vale (recrutamento de Yuri)
2. A Forja Viva (oficina itinerante)
3. O Sopro de Argila (reprodução mágica)
4. Batismo de Golem (d100 para T4 Únicos)
5. O Filho que Não Quer Nome, A Ferramenta que Engoliu o Ferreiro, O Peso do Pão, A Ceva Chora, O Pedido do Cinzel

---

## Sistemas

### Níveis de Golem
- **T1 Inferior:** 1 turno de forja, até 4 vivos simultâneos
- **T2 Feitor:** 2 turnos, exige oficina, até 3 vivos
- **T3 Superior:** 3 turnos, exige forja + oficina, até 2 vivos
- **T4 Único:** 4 turnos + evento Batismo, 1 por campanha

### Gênero e Reprodução Mágica
- 4 gêneros: Masculino, Feminino, Neutro, Ambíguo
- Escolhido no Batismo ou via Pingente do Nome
- Reprodução: evento "O Sopro de Argila" requer 2 golens (1 macho + 1 fêmea), 4 Argila ou Madeira, 1 Essência
- O bebê nasce com TAG-GROWING_UP e amadurece em 25-45 turnos (mesmo sistema de crianças humanas)
- Únicos T4 são estéreis

### Corrupção de Forja
- Cada forja acumula corrupção em Yuri (TAG-YM_CORRUPCAO_FORJA)
- Limiar 10: Yuri não pode forjar até limpar (1 turno na forja + 2 Ervas/dia)
- Limiar 20: Golens ficam Irritados (−1 moral/turno)
- Limiar 30: Yuri é corrompido e se torna NPC hostil

### Árvore de Tecnologia
Todas as receitas são desbloqueadas via ITEM_TECH (árvore de tecnologia do jogo), seguindo a progressão:
T1 → T2 → T3 (via UpgradeRecipe com EssenceBonus)

---

## Instalação

1. Copie a pasta `Golemancer` para:
   `D:\SteamLibrary\steamapps\common\Thea 2 The Shattering\Thea2_Data\StreamingAssets\Mods\`
2. Inicie o jogo e ative o mod na tela de mods.
3. Inicie uma nova campanha — Yuri aparecerá no evento "A Oficina no Vale" (turno 5+).

---

## Estrutura de Arquivos

```
Golemancer/
├── info.txt                          # Manifesto do mod
├── LEIA-ME.md                        # Este arquivo
├── DATABASE_SUBRACE.xml              # Subraces (Yuri + 20 golens + 2 halves)
├── DATABASE_TAGS_QUEST.xml           # Tags do mod
├── DATABASE_SKILLS_1_NATURAL.xml     # Skills naturais
├── DATABASE_SKILLS_PACKS.xml         # Skill packs
├── DATABASE_SUBSKILLS_CHALLENGES_SUPPORT.xml   # Subskills de suporte
├── DATABASE_SUBSKILLS_CHALLENGES_DEFENCE.xml   # Subskills de defesa
├── DATABASE_ITEMS_CARGOS.xml         # Cargos de item
├── DATABASE_TRAIT_CARDS.xml          # Traço de perfil
├── DATABASE_DES_LOCALIZATION.xml     # Textos PT-BR
├── DATABASE_DES_NAMES.xml            # Nomes de personagens
├── DATABASE_RECIPES_ITEMS.xml        # Receitas de fabricação
├── DATABASE_TECH_ITEM.xml            # Árvore de tecnologia
├── YM_UniqueRecruitment.cs           # Script: recrutamento único
├── YM_ForjarProle.cs                 # Script: criação de descendentes
├── YM_ForjaViva.xml                  # Módulo de história (9 eventos)
└── Images/Interface/                 # Artes (cards, rosters, ícones, eventos)
```

---

## Créditos

Baseado nos sistemas de modding oficiais de Thea 2: The Shattering. Inspirado nos mods existentes: FantasticCreaturesPlus, Vampiros do Pacto Rubro, Pugilista do Caos.

---

*"A magia não é um dom. É uma dívida com uma estrela morta. E ela sempre cobra."*
— Arquimaga Vitreia
