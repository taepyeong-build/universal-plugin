# Korean & English Prose Craft + Anti-Slop Reference

Load this reference when drafting or line-editing to enforce W6 (Micro-Prose Craft & Rhythm) and W7 (Voice Authenticity & Anti-Slop).

---

## 1. Korean Prose Mastery (한국어 문체 공학)

### A. P0 Ban: True Double Passives (이중피동 금지)
Korean stacks a passive suffix (`-이/히/리/기-` or `되-`) with `-어지다` incorrectly. Always collapse to a single passive or active verb:

| Incorrect (Double Passive — P0) | Natural Korean Replacement |
| :--- | :--- |
| `보여진다`, `보여지고 있다` | `보인다`, `드러난다`, `(주체가) 본다` |
| `쓰여진다`, `쓰여졌다` | `쓰인다`, `쓰였다`, `사용한다` |
| `불려진다`, `불려졌다` | `불린다`, `불렸다` |
| `열려진다`, `닫혀진다` | `열린다`, `닫힌다` |
| `잊혀진다`, `믿겨진다` | `잊힌다`, `믿긴다` / `믿어진다` |
| `나뉘어지다`, `놓여지다`, `풀려지다` | `나뉘다`, `놓이다`, `풀리다` |
| `담겨지다`, `얽혀지다`, `쌓여지다`, `읽혀지다` | `담기다`, `얽히다`, `쌓이다`, `읽히다` |
| `되어지다`, `되어졌다` | `되다`, `되었다` (또는 능동 동사) |

*(Note: Single passives from active roots such as `만들어지다`, `밝혀지다`, `지켜지다`, `알려지다` are grammatically valid, though active verbs are often stronger.)*

### B. Korean Translationese (번역투 제거)

| Translationese Pattern | Why It Weakens Prose | Crisp Korean Rewrite |
| :--- | :--- | :--- |
| `~에 있어서` | Empty Japanese/English preposition calque | Replace with `~에서`, `~할 때`, or delete (`배포 과정에 있어서` → `배포 과정에서`) |
| `~에 의해(서)` | Forces unnatural passive voice | Make the agent the subject (`팀에 의해 승인되었다` → `팀이 승인했다`) |
| `~하는 것에 대해(서)` | Nominalizes verbs into heavy noun phrases | Direct object + verb (`지연이 발생하는 것에 대해 조사했다` → `지연 원인을 조사했다`) |
| `~적인` overuse | Vague adjective padding (`효율적인`, `효과적인`, `근본적인`) | Name the exact mechanism (`효율적인 캐시` → `응답 시간을 40% 줄이는 캐시`) |
| Unnecessary plural `~들` | English plural calque on mass/collective nouns | Drop `들` unless individuating (`많은 문제들을 야기한다` → `문제를 여러 건 일으킨다`) |
| Inanimate subjects (무생물 주어) | "이 지표는 우리에게 ~을 말해준다" | Shift to human/system perspective (`이 지표를 보면 ~을 알 수 있다`) |
| `의` chaining (`A의 B의 C의 D`) | Cognitive load explodes past 2 `의` per clause | Convert modifiers into verbs or compound nouns (`팀의 배포의 속도의 저하` → `팀 배포 속도가 느려진 원인`) |

### C. Nominalization → Active Verb Energy (명사화 해소)
Replace heavy `한자 명사 + 기능동사(진행하다/수행하다/실시하다/도출하다/가능하다)` with crisp action verbs:
- `검토를 진행하겠습니다` → `검토하겠습니다`
- `감사를 수행하는 것이 가능하다` → `감사할 수 있다`
- `개선의 도출을 실시했다` → `개선안을 도출했다` / `개선했다`
- `발생이 되고 있다` → `발생한다` / `생긴다`

### D. Korean Rhythm & Sentence-Ending Variation (호흡과 어미 변주)
- **End-Stop Monotony**: Never repeat the exact same ending (`~습니다`, `~이다`, `~한다`) 5+ times consecutively (P0). Even 3–4 consecutive identical endings flatten rhythm — alternate verb stems, rhetorical turns, or nominal/clause pacing while keeping consistent register (하십시오체 / 해요체 / 해라체).
- **Breath Length**: Target average 35–55 chars per Korean sentence, but **vary intentionally** (Burstiness CV `>= 0.35`): pair a 65-char analytical sentence with a 15-char punch sentence. Break sentences above 95 chars unless deliberately periodic.
- **Subject-Predicate Agreement (주어-서술어 호응)**: Verify that every long sentence's opening subject actually matches its final verb (avoid *"핵심 원인은 캐시 미스가 급증했기 때문이다"* → *"핵심 원인은 캐시 미스 급증이다"*).

---

## 2. English Classic Style Craft (*Williams / Zinsser / Orwell / Pinker*)

1. **Actors as Subjects, Actions as Verbs**:
   - Weak: *"The implementation of caching resulted in an improvement in latency."*
   - Strong: *"Caching cut latency by 42%."*
2. **Given-New Flow (Topic → Stress)**:
   - Open sentences with short, familiar context (Topic); place new, complex, emphatic information at the end (Stress).
3. **Concrete Anglo-Saxon / Direct Verbs Over Latinate Padding**:
   - Cut `utilize` → `use`, `facilitate` → `help/enable`, `leverage` → `use`, `in order to` → `to`, `due to the fact that` → `because`.
4. **Rhythm & Burstiness**:
   - Avoid uniform 16–22 word sentences. Mix 28-word reasoned clauses with crisp 6–10 word landing sentences. Flag sentences > 35 words unless structured with parallel clarity.

---

## 3. Bilingual AI-Slop Blacklist & Replacements

| Category | Korean AI-Slop Fingerprint | English AI-Slop Fingerprint | Expert Fix |
| :--- | :--- | :--- | :--- |
| **Throat-Clearing Openers** | `오늘날 급변하는...`, `디지털 전환 시대에...`, `~은 그 어느 때보다 중요합니다` | `In today's fast-paced world...`, `In the ever-evolving landscape...` | Delete the entire sentence; start with sentence #2 or the concrete conflict. |
| **Symmetrical Contrast Cliché** | `단순히 A가 아니라 B입니다`, `A를 넘어 B로` (repeated) | `It's not just X — it's Y`, `More than just X` | State B directly with its mechanism; use contrast at most once per piece if genuinely earned. |
| **Empty Authority Fillers** | `핵심은 바로 ~입니다`, `~라고 할 수 있습니다`, `필수적입니다`, `주목할 만한` | `It is important to note that`, `underscore`, `pivotal`, `testament to` | Delete the framing wrapper and let the concrete evidence carry authority. |
| **Buzzword Haze** | `혁신적인 솔루션`, `다양한 측면에서`, `패러다임의 전환`, `시너지 극대화` | `delve`, `tapestry`, `realm`, `nuanced`, `game-changer`, `seamlessly` | Replace with specific mechanism, bounded scope, or observable number. |
| **Hollow Wrap-Up** | `지금까지 ~을 살펴보았습니다`, `앞으로의 행보가 기대됩니다`, `지속적인 노력이 필요합니다` | `In conclusion, as we navigate...`, `Only time will tell`, `The future looks bright` | End on a concrete decision ask, falsifiable prediction, or resonant concrete image. |
| **Formatting Tics** | Every paragraph converted to `- **키워드:** 설명`; forced 3-item lists (`A, B, 그리고 C`); decorative emojis | Bold-lead bullet walls in prose; compulsive em-dash (`—`) overuse (> 1 per 150 words) | Use prose paragraphs for narrative/argument; reserve lists for genuine parallel sets. |
