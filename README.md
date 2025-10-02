# Python Blaster: Code & Clear

<div align="center">

```
\  |  /  \  |  /  \  |  /  \  |  /
 \ | /    \ | /    \ | /    \ | /
  \|/  T i m a 0 7 0 7  \ | /  \|/
  /|\  ===============   /|\   /|\
 / | \    P Y T H O N   / | \ / | \
/  |  \  B L A S T E R /  |  \  |  \
```

**Аркадная головоломка с фигурами, викториной по Python и Code-Battle редактором.**  
Минималистичный дизайн, плавные частицы, достижения, JSON-каталоги задач и вопросов, режим **НУБ/ПРО** и окно **Архив**.

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python)](https://www.python.org/)
[![Pygame](https://img.shields.io/badge/Pygame-2.x-0E4B5A?logo=pygame)](https://www.pygame.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](#license)
[![Made by](https://img.shields.io/badge/Made%20by-Tima0707-blueviolet)](#credits)

**[English version below ⬇️](#english-version)**
</div>

---

## Оглавление

- [Особенности](#особенности)
- [Скриншоты / демо](#скриншоты--демо)
- [Установка и запуск](#установка-и-запуск)
- [Управление](#управление)
- [Игровые режимы](#игровые-режимы)
- [Структура проекта](#структура-проекта)
- [Данные и форматы JSON](#данные-и-форматы-json)
  - [Вопросы викторины (`data/questions.json`)](#вопросы-викторины-dataquestionsjson)
  - [Каталог задач Code-Battle (`data/code_battles_catalog.json`)](#каталог-задач-code-battle-datacode_battles_catalogjson)
  - [Лог сыгранных баттлов (`data/code_battles.json`)](#лог-сыгранных-баттлов-datacode_battlesjson)
- [Алгоритм сложности и «возможность проиграть»](#алгоритм-сложности-и-возможность-проиграть)
- [Архитектура (Mermaid)](#архитектура-mermaid)
- [FAQ / Траблшутинг](#faq--траблшутинг)
- [Roadmap](#roadmap)
- [Лицензия](#лицензия)
- [Благодарности](#благодарности)
- [Приложение: готовые задачи для каталога](#приложение-готовые-задачи-для-каталога)

---

## Особенности

- 🎯 **Геймплей 8×8**: перетаскивай фигуры, заполняй линии, зарабатывай очки.
- 🧠 **Викторина по Python**: каждые N линий — рандомный вопрос (4 варианта).
- 💻 **Code-Battle (ПРО)**: встраиваемый редактор кода с подсветкой, таймером и автодополнением.  
  ▸ **Шаблоны пустые** — решение игрок пишет сам.  
  ▸ **Верный код и объяснение доступны только в «Архиве»**.
- 🏆 **Достижения и рекорды**: прогресс и статистика сохраняются в JSON.
- 🎛️ **Режим НУБ/ПРО**: мини-кнопка **НУБ/ПРО** справа от «Начать игру».  
  ▸ *НУБ*: только викторина. ▸ *ПРО*: викторина + code-battle.
- 🗂️ **Архив**: окно со **всеми задачами** каталога (код-решения + объяснения). Кнопка — **в правом нижнем углу** главного меню.
- ✨ **Минималистичный UI и частицы**: легкие анимации, притягивание фигур, «ghost»-контуры.

---

## Скриншоты / демо

> Добавь свои изображения в `docs/` и раскомментируй:

<!--
<div align="center">
  <img src="docs/screenshot-menu.png" width="720" alt="Главное меню">
  <img src="docs/screenshot-game.png" width="720" alt="Игровое поле">
  <img src="docs/screenshot-battle.png" width="720" alt="Code-Battle">
  <img src="docs/screenshot-archive.png" width="720" alt="Архив">
</div>
-->

---

## Установка и запуск

```bash
# 1) Клонируй
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>

# 2) Виртуальное окружение (опционально)
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 3) Зависимости
pip install pygame

# 4) Запуск
python main.py
```

> Python 3.9+ рекомендуется.

---

## Управление

- 🎲 **Игровое поле**: **мышь** — перетаскивание фигур.
- 🧩 **События** (после каждой 5-й линии):
  - *НУБ*: вопрос викторины.
  - *ПРО*: 50/50 — викторина или code-battle.
- ❓ **Викторина**: клавиши **1–4** — выбор ответа.
- 💻 **Code-Battle**:
  - **Tab** — отступ (4 пробела)
  - **Ctrl+Enter** — отправить решение
  - **Стрелки/Home/End** — курсор
- ⎋ **ESC** — в главное меню.

---

## Игровые режимы

- **НУБ** — только вопросы, без редактора кода.  
- **ПРО** — вопросы + code-battle.  
Переключение — мини-кнопка **НУБ/ПРО** справа от «Начать игру».

---

## Структура проекта

```
.
├── main.py                          # Вся логика игры (однофайловая сборка)
├── data/
│   ├── questions.json               # Вопросы викторины
│   ├── code_battles_catalog.json    # Каталог задач code-battle + решения/объяснения
│   ├── code_battles.json            # Лог сыгранных баттлов (создаётся автоматически)
│   └── game_data.json               # Статистика/рекорды (создаётся автоматически)
└── docs/
    └── screenshot-*.png             # Скриншоты (необязательно)
```

---

## Данные и форматы JSON

### Вопросы викторины (`data/questions.json`)

- Всегда **ровно 4 варианта**.  
- Поле `correct` — **индекс верного ответа** (0..3).  
- В игре варианты **перемешиваются**, индекс корректируется автоматически.

Пример:

```json
{
  "questions": [
    {
      "question": "Переведите число 255 в шестнадцатеричную систему:",
      "options": ["FF", "FE", "100", "255"],
      "correct": 0,
      "explanation": "255(10) = FF(16) (15*16 + 15)."
    },
    {
      "question": "Что выведет print(len('Python'))?",
      "options": ["6", "5", "7", "Ошибка"],
      "correct": 0,
      "explanation": "Длина строки 'Python' равна 6."
    }
  ]
}
```

### Каталог задач Code-Battle (`data/code_battles_catalog.json`)

- Содержит **все задачи** для режима code-battle и **для окна «Архив»**.
- В игре решение не показывается — используется `template`, `test_cases`, `hints`.
- В Архиве выводятся `solution` и `explanation`.

Пример элемента:

```json
{
  "name": "Палиндром",
  "description": "Проверьте, является ли строка палиндромом (игнорируйте пробелы и регистр)",
  "template": "def is_palindrome(s):\n    # Напишите ваш код здесь\n    pass",
  "test_cases": [
    {"input": ["racecar"], "expected": true},
    {"input": ["hello"], "expected": false},
    {"input": ["A man a plan a canal Panama"], "expected": true},
    {"input": [""], "expected": true}
  ],
  "difficulty": "medium",
  "time_limit": 180,
  "reward": 300,
  "hints": ["Нормализуйте строку", "Сравните с перевёрнутой"],
  "solution": "def is_palindrome(s):\n    s = ''.join(c.lower() for c in s if c.isalnum())\n    return s == s[::-1]",
  "explanation": "Фильтруем не буквенно-цифровые, приводим к нижнему, сравниваем с разворотом."
}
```

> В JSON нет кортежей — `input` задаём списком (`[]`). В коде аргументы распаковываются как `function(*input)`.

### Лог сыгранных баттлов (`data/code_battles.json`)

- Автособирается **после завершения** code-battle.  
- Нужен для аналитики (в Архиве показывается **каталог**, а не лог).

Структура:

```json
{
  "items": [
    {
      "date": "2025-01-01T12:34:56",
      "challenge_name": "Сумма двух чисел",
      "challenge_desc": "Напишите функцию...",
      "code": "def add(a, b): ...",
      "success": true,
      "message": "Все тесты пройдены!",
      "reward": 200,
      "time_spent_sec": 73
    }
  ]
}
```

---

## Алгоритм сложности и «возможность проиграть»

- Фигуры делятся на **простые / средние / сложные**.  
  С ростом `score` уменьшается доля простых (`easy → normal → hard`).
- Оценка хода учитывает **соседство** и **потенциальные линии** — бесконечных «сладких» мест нет.
- **Проигрыш** — когда **ни одну** из трёх фигур **нельзя поставить** (проверяется каждый кадр).

---

## Архитектура (Mermaid)

```mermaid
classDiagram
    class GameData
    class QuizEngine
    class CodeBattleCatalog
    class CodeBattleArchive
    class CodeBattle
    class GameBoard
    class Shape
    class ParticleSystem
    class MainMenu
    class ArchiveScreen
    class Game

    Game --> GameBoard
    Game --> QuizEngine
    Game --> CodeBattle
    Game --> ParticleSystem
    Game --> GameData
    Game --> CodeBattleArchive
    Game --> CodeBattleCatalog

    CodeBattle --> CodeBattleCatalog
    ArchiveScreen --> CodeBattleCatalog

    GameBoard --> Shape
    ParticleSystem --> Shape
    MainMenu --> GameData
```

---

## FAQ / Траблшутинг

**Текст на кнопках не видно** — замени шрифт `consolas` на системный: `pygame.font.SysFont(None, size)`.  
**Pygame не запускается** — `pip install pygame`, проверь Python 3.9+.  
**Вопросы не подхватываются** — проверь JSON и что у каждого вопроса **4 варианта**.  
**Code-Battle показывает ответ** — в игре решения **не выводятся**, смотри **Архив**.

---

## Roadmap

- Онлайн-лидерборд.
- Подбор фигур с учётом «дыр» на поле.
- Дополнительные темы оформления.
- Импорт/экспорт прогресса.

---

## Лицензия

MIT — см. `LICENSE` (при необходимости добавь в репозиторий).

---

## Благодарности

Автор и вдохновение: **Tima0707** 💙  
Сообщество Pygame и Python.

---

## Приложение: готовые задачи для каталога

Добавь элементы в массив `items` файла `data/code_battles_catalog.json`.

```json
{
  "name": "Сумма цифр числа",
  "description": "Верните сумму цифр неотрицательного целого n",
  "template": "def digit_sum(n):\n    # Напишите ваш код здесь\n    pass",
  "test_cases": [
    {"input": [0], "expected": 0},
    {"input": [7], "expected": 7},
    {"input": [123], "expected": 6},
    {"input": [9999], "expected": 36}
  ],
  "difficulty": "easy",
  "time_limit": 120,
  "reward": 250,
  "hints": ["Преобразуйте в строку или используйте // и %", "Аккуратно суммируйте"],
  "solution": "def digit_sum(n):\n    s = 0\n    while n > 0:\n        s += n % 10\n        n //= 10\n    return s",
  "explanation": "Классический разбор на цифры через деление на 10; O(d), где d — число цифр."
}
```

```json
{
  "name": "Удалить гласные",
  "description": "Верните строку без гласных (англ. aeiou, регистр игнорируйте)",
  "template": "def remove_vowels(s):\n    # Напишите ваш код здесь\n    pass",
  "test_cases": [
    {"input": ["hello"], "expected": "hll"},
    {"input": ["PYTHON"], "expected": "PYTHN"},
    {"input": ["AEiou"], "expected": ""},
    {"input": ["ChatGPT"], "expected": "ChtGPT"}
  ],
  "difficulty": "medium",
  "time_limit": 150,
  "reward": 300,
  "hints": ["Создайте множество гласных", "Фильтруйте символы циклом/генератором"],
  "solution": "def remove_vowels(s):\n    v = set('aeiouAEIOU')\n    return ''.join(ch for ch in s if ch not in v)",
  "explanation": "Множество даёт O(1) проверку принадлежности; генератор строит новую строку."
}
```

---

# English Version

## Table of Contents

- [Features](#features)
- [Screenshots / Demo](#screenshots--demo)
- [Install & Run](#install--run)
- [Controls](#controls)
- [Game Modes](#game-modes)
- [Project Structure](#project-structure)
- [Data & JSON Formats](#data--json-formats)
- [Difficulty & Game Over](#difficulty--game-over)
- [Architecture (Mermaid)](#architecture-mermaid)
- [FAQ](#faq)
- [Roadmap](#roadmap-1)
- [License](#license)
- [Credits](#credits)

---

## Features

- 🎯 **8×8 puzzle board** — drag-n-drop shapes, clear lines, score points.
- 🧠 **Python quiz** every N lines — always 4 options, shuffled in-game.
- 💻 **Code-Battle (PRO)** — embedded code editor with syntax highlight, timer, autocomplete.  
  ▸ **Templates are empty** — players must write the solution.  
  ▸ **Correct code + explanation live only in the Archive**.
- 🏆 **Achievements & highscores** — persisted in JSON.
- 🎛️ **NUB/PRO toggle** — compact button to the **right** of “Start Game”.  
  ▸ *NUB*: quiz only. ▸ *PRO*: quiz + code-battle.
- 🗂️ **Archive** window — shows **all tasks** from the catalog with solutions & explanations. Button at **bottom-right** of main menu.
- ✨ **Minimal UI & particles**, ghost outlines and snapping.

---

## Screenshots / Demo

> Put images into `docs/` and uncomment the block above.

---

## Install & Run

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>

python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install pygame
python main.py
```

---

## Controls

- Mouse — drag shapes.  
- `R` — reroll shapes.  
- Events every 5 lines:
  - NUB: quiz.
  - PRO: 50/50 quiz or code-battle.
- Quiz: keys `1–4`.  
- Code-Battle: `Tab`, `Ctrl+Enter`, `H`, arrows/Home/End.  
- `ESC` — main menu.

---

## Game Modes

- **NUB** — quiz only.  
- **PRO** — quiz + code-battle.  
Switch via compact **NUB/PRO** button (to the right of “Start Game”).

---

## Project Structure

See the Russian section above — same layout.

---

## Data & JSON Formats

- `data/questions.json` — multiple-choice quiz (4 options, `correct` is 0..3).  
- `data/code_battles_catalog.json` — **catalog** of all code-battle tasks; used by both gameplay and the **Archive** (solutions + explanations).  
- `data/code_battles.json` — log of finished battles (for analytics).

---

## Difficulty & Game Over

- Shapes are grouped as **simple / medium / complex**; probabilities shift with score.  
- Move scoring considers **adjacency** and **potential lines**.  
- **Game over** when none of the three shapes can be placed.

---

## Architecture (Mermaid)

See the diagram in the Russian section.

---

## FAQ

- If text is invisible on buttons — prefer `pygame.font.SysFont(None, size)`.  
- Ensure Python 3.9+ and `pip install pygame`.  
- Quiz: make sure each question has **exactly 4 options**.  
- Solutions are **not shown** during Code-Battle — check **Archive** window.

---

## Roadmap

- Online leaderboard.  
- Smarter shape generator with hole detection.  
- Themes.  
- Progress import/export.

---

## License

MIT.

---

## Credits

Author & inspiration: **Tima0707** 💙  
Pygame & Python community.

