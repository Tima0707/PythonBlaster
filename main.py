##                                       ____
##   _________  ||||||    ||\    /||    /    \     /======\   ========    /======\   ========
##  |=========|   ||      || \  / ||    |    |    /|      |\      / /    /|      |\     / /
##      ||        ||      ||  \/  ||    |====|   | |      | |    / /    | |      | |   / /
##      ||        ||      ||      ||    |    |   | |      | |   / /     | |      | |  / /
##      ||        ||      ||      ||             | |      | |  / /      | |      | | / /
##      ||        ||      ||      ||              \|      |/  / /        \|      |/ / /
##      ||      ||||||    ||      ||               \======/  /_/          \======/ /_/

#  git -https://github.com/Tima0707
#  tg  -@LEGENDA_KRUTOY




import pygame
import sys
import random
import json
import os
import time
import math
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime

from pygame.locals import (
    QUIT, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION,
    KEYDOWN, K_r, K_1, K_2, K_3, K_4, K_SPACE, K_ESCAPE,
    K_RETURN, K_BACKSPACE, K_TAB, K_HOME, K_END, K_UP, K_RIGHT, K_LEFT, K_DOWN
)

# -----------------------------
# Константы/параметры экрана
# -----------------------------
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 700
GRID_SIZE = 8
CELL_SIZE = 60
GRID_OFFSET_X = 600
GRID_OFFSET_Y = 100
PANEL_CELL_SIZE = 35
FPS = 60

# Палитра
BACKGROUND = (15, 20, 30)
GRID_COLOR = (40, 50, 70)
GRID_HIGHLIGHT = (70, 90, 120)
CELL_COLORS = [
    (41, 128, 185),  # Синий
    (39, 174, 96),   # Зеленый
    (142, 68, 173),  # Фиолетовый
    (230, 126, 34),  # Оранжевый
    (231, 76, 60),   # Красный
    (26, 188, 156),  # Бирюзовый
    (241, 196, 15),  # Желтый
]
TEXT_COLOR = (236, 240, 241)
HIGHLIGHT_COLOR = (52, 152, 219)
VALID_PLACEMENT_COLOR = (46, 204, 113)
INVALID_PLACEMENT_COLOR = (231, 76, 60)
GHOST_ALPHA = 150
PANEL_BG = (30, 40, 55)
BUTTON_COLOR = (41, 128, 185)
BUTTON_HOVER_COLOR = (52, 152, 219)
CORRECT_COLOR = (46, 204, 113)
WRONG_COLOR = (231, 76, 60)
MENU_BG = (20, 30, 48)
CODE_EDITOR_BG = (25, 35, 45)
CODE_EDITOR_TEXT = (220, 220, 220)
CODE_LINE_NUMBERS = (100, 100, 120)

# -----------------------------
# Система частиц
# -----------------------------
class Particle:
    def __init__(self, x, y, color, velocity=None, life=60, size=4, particle_type="circle"):
        self.x = x
        self.y = y
        self.color = color
        self.velocity = velocity or [random.uniform(-5, 5), random.uniform(-5, 5)]
        self.life = life
        self.max_life = life
        self.size = size
        self.type = particle_type
        self.gravity = 0.15
        self.decay = 0.95

    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.velocity[1] += self.gravity
        self.velocity[0] *= self.decay
        self.velocity[1] *= self.decay
        self.life -= 1
        self.size = max(1, self.size * 0.98)
        return self.life > 0

    def draw(self, surface):
        alpha = int(255 * (self.life / self.max_life))
        if self.type == "circle":
            color = (*self.color, alpha)
            s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, color, (self.size, self.size), self.size)
            surface.blit(s, (int(self.x - self.size), int(self.y - self.size)))
        elif self.type == "square":
            color = (*self.color, alpha)
            s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            s.fill(color)
            surface.blit(s, (int(self.x - self.size / 2), int(self.y - self.size / 2)))
        elif self.type == "star":
            color = (*self.color, alpha)
            s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            points = []
            for i in range(5):
                angle = i * 2 * math.pi / 5 - math.pi / 2
                points.append((self.size + self.size * 0.8 * math.cos(angle),
                               self.size + self.size * 0.8 * math.sin(angle)))
                angle += math.pi / 5
                points.append((self.size + self.size * 0.4 * math.cos(angle),
                               self.size + self.size * 0.4 * math.sin(angle)))
            pygame.draw.polygon(s, color, points)
            surface.blit(s, (int(self.x - self.size), int(self.y - self.size)))

class ParticleSystem:
    def __init__(self):
        self.particles = []
        self.effects = {
            "line_clear": {"count": 50, "colors": [(255, 255, 200), (255, 200, 100), (255, 150, 50)]},
            "shape_place": {"count": 25, "colors": [(100, 200, 255), (50, 150, 255), (0, 100, 200)]},
            "combo": {"count": 80, "colors": [(255, 50, 50), (255, 100, 100), (255, 150, 150)]},
            "code_success": {"count": 100, "colors": [(50, 255, 100), (100, 255, 150), (150, 255, 200)]},
            "game_over": {"count": 150, "colors": [(255, 50, 50), (255, 100, 100), (200, 50, 50)]}
        }

    def add_effect(self, effect_type, x, y, color=None):
        if effect_type in self.effects:
            effect = self.effects[effect_type]
            colors = [color] if color else effect["colors"]
            for _ in range(effect["count"]):
                particle_color = random.choice(colors)
                particle_type = random.choice(["circle", "square", "star"])
                size = random.uniform(3, 8)
                life = random.randint(60, 120)
                velocity = [random.uniform(-6, 6), random.uniform(-6, 6)]
                self.particles.append(Particle(x, y, particle_color, velocity, life, size, particle_type))

    def update(self):
        self.particles = [p for p in self.particles if p.update()]

    def draw(self, surface):
        for particle in self.particles:
            particle.draw(surface)

# -----------------------------
# Сохранение общей статистики
# -----------------------------
class GameData:
    def __init__(self):
        self.data_file = "data/game_data.json"
        self.default_data = {
            "high_score": 0,
            "achievements": {
                "first_game": False,
                "score_500": False,
                "score_1000": False,
                "score_2000": False,
                "clear_10_lines": False,
                "clear_25_lines": False,
                "answer_5_questions": False,
                "answer_10_questions": False,
                "complete_5_code_battles": False,
                "complete_10_code_battles": False
            },
            "games_played": 0,
            "total_lines_cleared": 0,
            "total_questions_answered": 0,
            "total_correct_answers": 0,
            "total_code_battles_completed": 0,
            "last_played": None,
            "game_sessions": []
        }
        self.data = json.loads(json.dumps(self.default_data))
        self.load_data()

    def load_data(self):
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    self._update_dict_recursive(self.data, loaded_data)
            else:
                self.save_data()
        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")
            self.data = json.loads(json.dumps(self.default_data))
            self.save_data()

    def _update_dict_recursive(self, target, source):
        for key, value in target.items():
            if key in source:
                if isinstance(value, dict) and isinstance(source[key], dict):
                    self._update_dict_recursive(value, source[key])
                else:
                    target[key] = source[key]

    def save_data(self):
        try:
            self.data["last_played"] = datetime.now().isoformat()
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения данных: {e}")

    def update_high_score(self, score):
        if score > self.data["high_score"]:
            self.data["high_score"] = score
            self.save_data()
            return True
        return False

    def update_achievements(self, game_stats):
        updated = False
        if game_stats["score"] >= 500 and not self.data["achievements"]["score_500"]:
            self.data["achievements"]["score_500"] = True; updated = True
        if game_stats["score"] >= 1000 and not self.data["achievements"]["score_1000"]:
            self.data["achievements"]["score_1000"] = True; updated = True
        if game_stats["score"] >= 2000 and not self.data["achievements"]["score_2000"]:
            self.data["achievements"]["score_2000"] = True; updated = True
        if game_stats["lines_cleared"] >= 10 and not self.data["achievements"]["clear_10_lines"]:
            self.data["achievements"]["clear_10_lines"] = True; updated = True
        if game_stats["lines_cleared"] >= 25 and not self.data["achievements"]["clear_25_lines"]:
            self.data["achievements"]["clear_25_lines"] = True; updated = True
        if self.data["total_questions_answered"] >= 5 and not self.data["achievements"]["answer_5_questions"]:
            self.data["achievements"]["answer_5_questions"] = True; updated = True
        if self.data["total_questions_answered"] >= 10 and not self.data["achievements"]["answer_10_questions"]:
            self.data["achievements"]["answer_10_questions"] = True; updated = True
        if self.data["total_code_battles_completed"] >= 5 and not self.data["achievements"]["complete_5_code_battles"]:
            self.data["achievements"]["complete_5_code_battles"] = True; updated = True
        if self.data["total_code_battles_completed"] >= 10 and not self.data["achievements"]["complete_10_code_battles"]:
            self.data["achievements"]["complete_10_code_battles"] = True; updated = True
        if not self.data["achievements"]["first_game"]:
            self.data["achievements"]["first_game"] = True; updated = True
        if updated: self.save_data()
        return updated

    def add_game_session(self, score, lines_cleared, questions_answered, correct_answers, code_battles_completed=0):
        session_data = {
            "date": datetime.now().isoformat(),
            "score": score,
            "lines_cleared": lines_cleared,
            "questions_answered": questions_answered,
            "correct_answers": correct_answers,
            "code_battles_completed": code_battles_completed
        }
        self.data["games_played"] += 1
        self.data["total_lines_cleared"] += lines_cleared
        self.data["total_questions_answered"] += questions_answered
        self.data["total_correct_answers"] += correct_answers
        self.data["total_code_battles_completed"] += code_battles_completed
        self.data["game_sessions"].append(session_data)
        if len(self.data["game_sessions"]) > 50:
            self.data["game_sessions"] = self.data["game_sessions"][-50:]
        self.update_high_score(score)
        self.update_achievements({
            "score": score,
            "lines_cleared": lines_cleared,
            "questions_answered": questions_answered,
            "correct_answers": correct_answers
        })
        self.save_data()

# -----------------------------
# Архив сыгранных баттлов (лог)
# -----------------------------
class CodeBattleArchive:
    def __init__(self, path="data/code_battles.json", limit=200):
        self.path = path
        self.limit = limit
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if not os.path.exists(self.path):
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump({"items": []}, f, ensure_ascii=False, indent=2)

    def _load(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
                data.setdefault("items", [])
                return data
        except Exception:
            return {"items": []}

    def _save(self, data):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("Ошибка сохранения архива код-баттлов:", e)

    def add(self, *, challenge_name, challenge_desc, code, success, message, reward, time_spent_sec):
        data = self._load()
        item = {
            "date": datetime.now().isoformat(timespec="seconds"),
            "challenge_name": challenge_name,
            "challenge_desc": challenge_desc,
            "code": code,
            "success": bool(success),
            "message": message,
            "reward": int(reward),
            "time_spent_sec": int(time_spent_sec)
        }
        data["items"].append(item)
        if len(data["items"]) > self.limit:
            data["items"] = data["items"][-self.limit:]
        self._save(data)

# -----------------------------
# Каталог задач код-баттла (с решениями/объяснениями)
# -----------------------------
class CodeBattleCatalog:
    """
    Загружает ВСЕ задачи код-баттла для Архива и для самой игры.
    Если есть файл data/code_battles_catalog.json — загрузим его,
    иначе используем встроенный дефолтный список.
    """
    def __init__(self, path="data/code_battles_catalog.json"):
        self.path = path
        self.items = self._load_or_default()

    def _load_or_default(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "items" in data:
                        return data["items"]
                    if isinstance(data, list):
                        return data
            except Exception as e:
                print("Ошибка загрузки каталога задач:", e)

        # Встроенные задачи (пустые шаблоны! решения только для архива)
        return [
            {
                "name": "Сумма двух чисел",
                "description": "Напишите функцию, которая возвращает сумму двух чисел",
                "template": "def add(a, b):\n    # Напишите ваш код здесь\n    pass",
                "test_cases": [
                    {"input": (1, 2), "expected": 3},
                    {"input": (5, 7), "expected": 12},
                    {"input": (-1, 1), "expected": 0},
                    {"input": (0, 0), "expected": 0}
                ],
                "difficulty": "easy",
                "time_limit": 120,
                "reward": 200,
                "hints": ["Используйте оператор +", "Верните результат сложения"],
                "solution": "def add(a, b):\n    return a + b",
                "explanation": "Сумма вычисляется оператором +. Никаких особых случаев."
            },
            {
                "name": "Факториал",
                "description": "Верните n! (произведение 1..n), 0! = 1",
                "template": "def factorial(n):\n    # Напишите ваш код здесь\n    pass",
                "test_cases": [
                    {"input": (0,), "expected": 1},
                    {"input": (1,), "expected": 1},
                    {"input": (5,), "expected": 120},
                    {"input": (7,), "expected": 5040}
                ],
                "difficulty": "medium",
                "time_limit": 180,
                "reward": 350,
                "hints": ["Итерация от 1 до n", "Начальное значение 1"],
                "solution": "def factorial(n):\n    res = 1\n    for i in range(2, n+1):\n        res *= i\n    return res",
                "explanation": "Итеративный вариант без рекурсии: быстрее и безопаснее по стеку."
            },
            {
                "name": "Палиндром",
                "description": "Проверьте, является ли строка палиндромом (игнорируйте пробелы и регистр)",
                "template": "def is_palindrome(s):\n    # Напишите ваш код здесь\n    pass",
                "test_cases": [
                    {"input": ("racecar",), "expected": True},
                    {"input": ("hello",), "expected": False},
                    {"input": ("A man a plan a canal Panama",), "expected": True},
                    {"input": ("",), "expected": True}
                ],
                "difficulty": "medium",
                "time_limit": 180,
                "reward": 300,
                "hints": ["Нормализуйте строку", "Сравните с перевёрнутой"],
                "solution": "def is_palindrome(s):\n    s = ''.join(c.lower() for c in s if c.isalnum())\n    return s == s[::-1]",
                "explanation": "Фильтруем не буквенно-цифровые, приводим к нижнему, сравниваем с разворотом."
            },
            {
                "name": "n-е число Фибоначчи",
                "description": "Верните n-е число Фибоначчи, F(0)=0, F(1)=1",
                "template": "def fibonacci(n):\n    # Напишите ваш код здесь\n    pass",
                "test_cases": [
                    {"input": (0,), "expected": 0},
                    {"input": (1,), "expected": 1},
                    {"input": (6,), "expected": 8},
                    {"input": (10,), "expected": 55}
                ],
                "difficulty": "hard",
                "time_limit": 240,
                "reward": 500,
                "hints": ["Итерация a,b", "Обновляйте пару (a,b)"],
                "solution": "def fibonacci(n):\n    if n < 2:\n        return n\n    a, b = 0, 1\n    for _ in range(2, n+1):\n        a, b = b, a + b\n    return b",
                "explanation": "Итеративно без рекурсии — линейно по времени и O(1) по памяти."
            },
            {
                "name": "Является ли число простым",
                "description": "Верните True, если n — простое число (n>=2)",
                "template": "def is_prime(n):\n    # Напишите ваш код здесь\n    pass",
                "test_cases": [
                    {"input": (2,), "expected": True},
                    {"input": (15,), "expected": False},
                    {"input": (17,), "expected": True},
                    {"input": (1,), "expected": False}
                ],
                "difficulty": "medium",
                "time_limit": 180,
                "reward": 350,
                "hints": ["Проверьте делители до sqrt(n)", "Граничные случаи"],
                "solution": "def is_prime(n):\n    if n < 2:\n        return False\n    i = 2\n    while i * i <= n:\n        if n % i == 0:\n            return False\n        i += 1\n    return True",
                "explanation": "Достаточно проверять делители до корня из n."
            },
            {
                "name": "Разворот слов",
                "description": "Дана строка, разверните порядок слов (сохраните сами слова)",
                "template": "def reverse_words(s):\n    # Напишите ваш код здесь\n    pass",
                "test_cases": [
                    {"input": ("hello world",), "expected": "world hello"},
                    {"input": ("a b c",), "expected": "c b a"},
                    {"input": ("Python",), "expected": "Python"},
                    {"input": ("  ab   cd ",), "expected": "cd ab"}
                ],
                "difficulty": "easy",
                "time_limit": 150,
                "reward": 250,
                "hints": ["split/strip", "join со списком в обратном порядке"],
                "solution": "def reverse_words(s):\n    words = s.split()\n    return ' '.join(words[::-1])",
                "explanation": "split() сам схлопнет пробелы; остаётся развернуть список слов."
            }
        ]

# -----------------------------
# Код-баттл (использует каталог, но не раскрывает решения!)
# -----------------------------
class CodeBattle:
    def __init__(self, catalog: CodeBattleCatalog):
        self.catalog = catalog
        # Для игры берём только публичные поля (без solution/explanation)
        self.challenges = [
            {
                "name": it["name"],
                "description": it["description"],
                "template": it["template"],       # ПУСТОЙ ШАБЛОН!
                "test_cases": it["test_cases"],
                "difficulty": it.get("difficulty", "medium"),
                "time_limit": it.get("time_limit", 180),
                "reward": it.get("reward", 300),
                "hints": it.get("hints", [])
            } for it in self.catalog.items
        ]

        self.current_challenge = None
        self.player_code = ""
        self.start_time = 0
        self.time_left = 0
        self.result = None
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_position = 0
        self.code_font = pygame.font.SysFont('consolas', 20)
        self.line_height = 25
        self.scroll_offset = 0
        self.show_autocomplete = False
        self.autocomplete_options = []
        self.autocomplete_index = 0
        self.current_hint = 0

        self.keywords = ["def", "return", "if", "else", "elif", "for", "while",
                         "in", "range", "len", "str", "int", "float", "list",
                         "dict", "True", "False", "None", "and", "or", "not"]

        self.submit_button_rect = pygame.Rect(0, 0, 200, 40)

    def start_battle(self):
        self.current_challenge = random.choice(self.challenges)
        self.player_code = self.current_challenge["template"]  # без готового решения!
        self.cursor_position = len(self.player_code)
        self.start_time = time.time()
        self.time_left = self.current_challenge["time_limit"]
        self.result = None
        self.scroll_offset = 0
        self.current_hint = 0
        return self.current_challenge

    def update_timer(self):
        if self.current_challenge and not self.result:
            elapsed = time.time() - self.start_time
            self.time_left = max(0, self.current_challenge["time_limit"] - elapsed)
            self.cursor_timer += 1
            if self.cursor_timer >= 30:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0
            if self.time_left <= 0:
                self.submit_solution()

    def handle_input(self, event):
        if not self.current_challenge or self.result:
            return False

        if event.type == KEYDOWN:
            if event.key == K_RETURN and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                self.submit_solution(); return True
            elif event.key == K_TAB:
                if self.show_autocomplete and self.autocomplete_options:
                    self.apply_autocomplete()
                else:
                    code_before = self.player_code[:self.cursor_position]
                    code_after = self.player_code[self.cursor_position:]
                    self.player_code = code_before + "    " + code_after
                    self.cursor_position += 4
                return True
            elif event.key == K_DOWN and self.show_autocomplete:
                self.autocomplete_index = (self.autocomplete_index + 1) % len(self.autocomplete_options); return True
            elif event.key == K_UP and self.show_autocomplete:
                self.autocomplete_index = (self.autocomplete_index - 1) % len(self.autocomplete_options); return True
            elif event.key == K_RETURN and self.show_autocomplete:
                self.apply_autocomplete(); return True
            elif event.key == K_RETURN:
                code_before = self.player_code[:self.cursor_position]
                code_after = self.player_code[self.cursor_position:]
                self.player_code = code_before + '\n' + code_after
                self.cursor_position += 1; return True
            elif event.key == K_BACKSPACE:
                if self.cursor_position > 0:
                    code_before = self.player_code[:self.cursor_position - 1]
                    code_after = self.player_code[self.cursor_position:]
                    self.player_code = code_before + code_after
                    self.cursor_position -= 1
                    self.check_autocomplete()
                return True
            elif event.key == K_LEFT:
                self.cursor_position = max(0, self.cursor_position - 1); self.show_autocomplete = False; return True
            elif event.key == K_RIGHT:
                self.cursor_position = min(len(self.player_code), self.cursor_position + 1); self.show_autocomplete = False; return True
            elif event.key == K_UP and not self.show_autocomplete:
                lines = self.player_code[:self.cursor_position].split('\n')
                if len(lines) > 1:
                    prev_len = len(lines[-2]); cur_len = len(lines[-1])
                    new_pos = self.cursor_position - cur_len - 1 - max(0, cur_len - prev_len)
                    self.cursor_position = max(0, new_pos)
                return True
            elif event.key == K_DOWN and not self.show_autocomplete:
                lines = self.player_code[:self.cursor_position].split('\n')
                remaining = self.player_code[self.cursor_position:].split('\n', 1)
                if len(remaining) > 1:
                    cur_len = len(lines[-1])
                    next_len = len(remaining[0])
                    new_pos = self.cursor_position + len(remaining[0]) + 1 + max(0, cur_len - next_len)
                    self.cursor_position = min(len(self.player_code), new_pos)
                return True
            elif event.key == K_HOME:
                lines = self.player_code[:self.cursor_position].split('\n')
                self.cursor_position -= len(lines[-1]); return True
            elif event.key == K_END:
                remaining = self.player_code[self.cursor_position:].split('\n', 1)
                if remaining: self.cursor_position += len(remaining[0]); return True
            elif event.unicode.isprintable():
                code_before = self.player_code[:self.cursor_position]
                code_after = self.player_code[self.cursor_position:]
                self.player_code = code_before + event.unicode + code_after
                self.cursor_position += 1
                self.check_autocomplete()
                return True

        elif event.type == MOUSEBUTTONDOWN:
            if self.submit_button_rect.collidepoint(event.pos):
                self.submit_solution(); return True
            code_rect = pygame.Rect(120, 200, SCREEN_WIDTH - 240, 300)
            if code_rect.collidepoint(event.pos):
                click_x, click_y = event.pos
                line_height = self.line_height
                line_num = min(len(self.player_code.split('\n')) - 1,
                               max(0, (click_y - 200) // line_height))
                lines = self.player_code.split('\n')
                line_text = lines[line_num] if line_num < len(lines) else ""
                char_pos = min(len(line_text), max(0, (click_x - 160) // 10))
                total_pos = sum(len(lines[i]) + 1 for i in range(line_num)) + char_pos
                self.cursor_position = min(total_pos, len(self.player_code))
                self.show_autocomplete = False
                return True
        return False

    def check_autocomplete(self):
        if self.cursor_position == 0:
            self.show_autocomplete = False; return
        current_text = self.player_code[:self.cursor_position]
        last_word = ""
        for i in range(self.cursor_position - 1, -1, -1):
            if i < len(current_text) and (current_text[i].isalnum() or current_text[i] == '_'):
                last_word = current_text[i] + last_word
            else:
                break
        if len(last_word) >= 2:
            self.autocomplete_options = [kw for kw in self.keywords if kw.startswith(last_word)]
            self.show_autocomplete = len(self.autocomplete_options) > 0
            self.autocomplete_index = 0
        else:
            self.show_autocomplete = False

    def apply_autocomplete(self):
        if not self.show_autocomplete or not self.autocomplete_options:
            return
        selected = self.autocomplete_options[self.autocomplete_index]
        current_text = self.player_code[:self.cursor_position]
        word_start = self.cursor_position
        for i in range(self.cursor_position - 1, -1, -1):
            if i < len(current_text) and not (current_text[i].isalnum() or current_text[i] == '_'):
                word_start = i + 1; break
            if i == 0:
                word_start = 0; break
        code_before = self.player_code[:word_start]
        code_after = self.player_code[self.cursor_position:]
        self.player_code = code_before + selected + code_after
        self.cursor_position = word_start + len(selected)
        self.show_autocomplete = False

    def next_hint(self):
        if self.current_challenge and "hints" in self.current_challenge:
            self.current_hint = (self.current_hint + 1) % len(self.current_challenge["hints"])

    def safe_execute(self, code, test_cases):
        safe_builtins = {
            'len': len, 'range': range, 'str': str, 'int': int, 'float': float,
            'bool': bool, 'list': list, 'tuple': tuple, 'dict': dict, 'set': set,
            'sum': sum, 'min': min, 'max': max, 'abs': abs, 'enumerate': enumerate
        }
        local_vars = {}
        try:
            exec(code, {"__builtins__": safe_builtins}, local_vars)
            function = None
            for var in local_vars.values():
                if callable(var):
                    function = var; break
            if not function:
                return False, "Функция не найдена"
            for i, test in enumerate(test_cases):
                try:
                    result = function(*test["input"])
                    if result != test["expected"]:
                        return False, f"Тест {i + 1} не пройден: ожидалось {test['expected']}, получено {result}"
                except Exception as e:
                    return False, f"Ошибка в тесте {i + 1}: {str(e)}"
            return True, "Все тесты пройдены!"
        except Exception as e:
            return False, f"Ошибка выполнения: {str(e)}"

    def submit_solution(self):
        if not self.current_challenge or self.result:
            return
        success, message = self.safe_execute(self.player_code, self.current_challenge["test_cases"])
        self.result = {
            "success": success,
            "message": message,
            "reward": self.current_challenge["reward"] if success else 0
        }
        return self.result

    # Рендер редактора и UI баттла
    def draw(self, surface, particle_system):
        if not self.current_challenge:
            return
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))

        battle_rect = pygame.Rect(100, 50, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 100)
        pygame.draw.rect(surface, CODE_EDITOR_BG, battle_rect, border_radius=15)
        pygame.draw.rect(surface, HIGHLIGHT_COLOR, battle_rect, 3, border_radius=15)

        title_font = pygame.font.SysFont('consolas', 32, bold=True)
        title = title_font.render("КОД-БАТТЛ!", True, HIGHLIGHT_COLOR)
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 70))

        challenge_font = pygame.font.SysFont('consolas', 24)
        name_text = challenge_font.render(f"Задача: {self.current_challenge['name']}", True, TEXT_COLOR)
        desc_text = self.code_font.render(self.current_challenge['description'], True, TEXT_COLOR)
        surface.blit(name_text, (120, 120))
        surface.blit(desc_text, (120, 150))

        time_text = challenge_font.render(f"Время: {int(self.time_left)} сек", True, TEXT_COLOR)
        reward_text = challenge_font.render(f"Награда: {self.current_challenge['reward']} очков", True, CORRECT_COLOR)
        surface.blit(time_text, (SCREEN_WIDTH - 300, 120))
        surface.blit(reward_text, (SCREEN_WIDTH - 300, 150))

        code_rect = pygame.Rect(120, 200, SCREEN_WIDTH - 240, 300)
        pygame.draw.rect(surface, (20, 25, 35), code_rect, border_radius=10)
        pygame.draw.rect(surface, GRID_HIGHLIGHT, code_rect, 2, border_radius=10)

        lines = self.player_code.split('\n')
        visible_lines = 12
        start_line = 0
        end_line = min(len(lines), start_line + visible_lines)

        for i in range(start_line, end_line):
            line_num = i + 1
            y_pos = 210 + (i - start_line) * self.line_height
            line_num_text = self.code_font.render(str(line_num), True, CODE_LINE_NUMBERS)
            surface.blit(line_num_text, (130, y_pos))

            line_text = lines[i]
            tokens = self.tokenize_line(line_text)
            x_offset = 160
            for token, token_type in tokens:
                color = self.get_token_color(token_type)
                token_surface = self.code_font.render(token, True, color)
                surface.blit(token_surface, (x_offset, y_pos))
                x_offset += token_surface.get_width()

        if self.cursor_visible and not self.result:
            cursor_line, cursor_col = self.get_cursor_position()
            if start_line <= cursor_line < end_line:
                cursor_x = 160 + self.code_font.size(lines[cursor_line][:cursor_col])[0]
                cursor_y = 210 + (cursor_line - start_line) * self.line_height
                pygame.draw.line(surface, CODE_EDITOR_TEXT,
                                 (cursor_x, cursor_y),
                                 (cursor_x, cursor_y + self.line_height), 2)

        if self.show_autocomplete and self.autocomplete_options:
            autocomplete_rect = pygame.Rect(160, 210 + self.line_height, 200,
                                            len(self.autocomplete_options) * self.line_height)
            pygame.draw.rect(surface, (40, 45, 60), autocomplete_rect)
            pygame.draw.rect(surface, GRID_HIGHLIGHT, autocomplete_rect, 1)
            for i, option in enumerate(self.autocomplete_options):
                color = HIGHLIGHT_COLOR if i == self.autocomplete_index else TEXT_COLOR
                option_text = self.code_font.render(option, True, color)
                surface.blit(option_text, (165, 215 + self.line_height + i * self.line_height))

        if "hints" in self.current_challenge:
            hint_rect = pygame.Rect(120, 520, SCREEN_WIDTH - 240, 60)
            pygame.draw.rect(surface, (30, 35, 45), hint_rect, border_radius=8)
            pygame.draw.rect(surface, GRID_HIGHLIGHT, hint_rect, 1, border_radius=8)
            hint_text = self.code_font.render(
                f"Подсказка: {self.current_challenge['hints'][self.current_hint]}",
                True, TEXT_COLOR
            )
            surface.blit(hint_text, (130, 540))

            hint_nav = self.code_font.render(
                f"({self.current_hint + 1}/{len(self.current_challenge['hints'])}) Нажмите H для следующей подсказки",
                True, CODE_LINE_NUMBERS
            )
            surface.blit(hint_nav, (130, 565))

        self.submit_button_rect = pygame.Rect(SCREEN_WIDTH - 320, 520, 200, 40)
        pygame.draw.rect(surface, BUTTON_COLOR, self.submit_button_rect, border_radius=8)
        pygame.draw.rect(surface, HIGHLIGHT_COLOR, self.submit_button_rect, 2, border_radius=8)
        submit_text = self.code_font.render("Отправить (Ctrl+Enter)", True, TEXT_COLOR)
        surface.blit(submit_text, (self.submit_button_rect.centerx - submit_text.get_width() // 2,
                                   self.submit_button_rect.centery - submit_text.get_height() // 2))

        if self.result:
            result_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 50, 400, 100)
            color = CORRECT_COLOR if self.result["success"] else WRONG_COLOR
            pygame.draw.rect(surface, PANEL_BG, result_rect, border_radius=10)
            pygame.draw.rect(surface, color, result_rect, 3, border_radius=10)
            result_font = pygame.font.SysFont('consolas', 24, bold=True)
            result_text = result_font.render("УСПЕХ!" if self.result["success"] else "НЕУДАЧА", True, color)
            message_text = self.code_font.render(self.result["message"], True, TEXT_COLOR)
            surface.blit(result_text, (SCREEN_WIDTH // 2 - result_text.get_width() // 2, SCREEN_HEIGHT // 2 - 30))
            surface.blit(message_text, (SCREEN_WIDTH // 2 - message_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
            if self.result["success"]:
                for _ in range(10):
                    x = random.randint(SCREEN_WIDTH // 2 - 100, SCREEN_WIDTH // 2 + 100)
                    y = random.randint(SCREEN_HEIGHT // 2 - 50, SCREEN_HEIGHT // 2 + 50)
                    particle_system.add_effect("code_success", x, y)

        instruct_font = pygame.font.SysFont('consolas', 18)
        if not self.result:
            for i, instruction in enumerate([
                "Tab - отступ (4 пробела)",
                "Ctrl+Enter - отправить решение",
                "H - следующая подсказка",
                "Стрелки - перемещение курсора"
            ]):
                text = instruct_font.render(instruction, True, TEXT_COLOR)
                surface.blit(text, (120, SCREEN_HEIGHT - 100 + i * 20))
        else:
            instruct_text = instruct_font.render("Нажмите любую клавишу чтобы продолжить", True, TEXT_COLOR)
            surface.blit(instruct_text, (SCREEN_WIDTH // 2 - instruct_text.get_width() // 2, SCREEN_HEIGHT - 70))

    def get_cursor_position(self):
        lines = self.player_code[:self.cursor_position].split('\n')
        line = len(lines) - 1
        col = len(lines[-1]) if lines else 0
        return line, col

    def tokenize_line(self, line):
        tokens = []
        current_token = ""
        in_string = False
        string_char = None
        in_comment = False

        for char in line:
            if in_comment:
                current_token += char
            elif in_string:
                current_token += char
                if char == string_char:
                    tokens.append((current_token, "string"))
                    current_token = ""
                    in_string = False
                    string_char = None
            else:
                if char in ['"', "'"]:
                    if current_token:
                        tokens.append((current_token, "normal"))
                        current_token = ""
                    in_string = True
                    string_char = char
                    current_token = char
                elif char == '#':
                    if current_token:
                        tokens.append((current_token, "normal"))
                        current_token = ""
                    in_comment = True
                    current_token = char
                elif char in ' \t\n()[]{}:,=+-*/%':
                    if current_token:
                        token_type = "keyword" if current_token in self.keywords else "normal"
                        tokens.append((current_token, token_type))
                        current_token = ""
                    tokens.append((char, "normal"))
                else:
                    current_token += char

        if current_token:
            if in_comment:
                tokens.append((current_token, "comment"))
            elif in_string:
                tokens.append((current_token, "string"))
            else:
                token_type = "keyword" if current_token in self.keywords else "normal"
                tokens.append((current_token, token_type))
        return tokens

    def get_token_color(self, token_type):
        colors = {
            "normal": CODE_EDITOR_TEXT,
            "keyword": (86, 156, 214),
            "string": (206, 145, 120),
            "comment": (106, 153, 85),
        }
        return colors.get(token_type, CODE_EDITOR_TEXT)

# -----------------------------
# Фигуры
# -----------------------------
class Shape:
    SIMPLE_SHAPES = [0, 1, 2, 4, 5, 6, 10, 11, 12, 13, 16, 17, 18, 19, 20, 21, 22, 23]
    MEDIUM_SHAPES = [3, 7, 8, 14, 15, 24, 25]
    COMPLEX_SHAPES = [9, 26, 27]

    SHAPES = [
        [[1, 1]],  # 0
        [[1, 1, 1]],  # 1
        [[1, 1, 1, 1]],  # 2
        [[1, 1, 1, 1, 1]],  # 3
        [[1], [1]],  # 4
        [[1], [1], [1]],  # 5
        [[1], [1], [1], [1]],  # 6
        [[1], [1], [1], [1], [1]],  # 7
        [[1, 1], [1, 1]],  # 8
        [[1, 1, 1], [1, 1, 1], [1, 1, 1]],  # 9
        [[1, 0], [1, 0], [1, 1]],  # 10
        [[0, 1], [0, 1], [1, 1]],  # 11
        [[1, 1], [1, 0], [1, 0]],  # 12
        [[1, 1], [0, 1], [0, 1]],  # 13
        [[1, 1, 1], [1, 0, 0]],  # 14
        [[1, 1, 1], [0, 0, 1]],  # 15
        [[1, 1, 1], [0, 1, 0]],  # 16
        [[0, 1, 0], [1, 1, 1]],  # 17
        [[1, 0], [1, 1], [1, 0]],  # 18
        [[0, 1], [1, 1], [0, 1]],  # 19
        [[1, 1, 0], [0, 1, 1]],  # 20
        [[0, 1, 1], [1, 1, 0]],  # 21
        [[1, 0], [1, 1], [0, 1]],  # 22
        [[0, 1], [1, 1], [1, 0]],  # 23
        [[1, 1], [1, 0]],  # 24
        [[1, 1], [0, 1]],  # 25
        [[1, 1, 1], [1, 0, 0], [1, 0, 0]],  # 26
        [[1, 1, 1], [0, 0, 1], [0, 0, 1]],  # 27
    ]

    def __init__(self, shape_type: Optional[int] = None, difficulty: str = "normal"):
        self.blocks: List[Tuple[int, int]] = []
        self.color = random.choice(CELL_COLORS)
        if shape_type is None:
            if difficulty == "easy":
                shape_type = random.choice(self.SIMPLE_SHAPES)
            elif difficulty == "hard":
                weights = [3] * len(self.SIMPLE_SHAPES) + [5] * len(self.MEDIUM_SHAPES) + [8] * len(self.COMPLEX_SHAPES)
                all_shapes = self.SIMPLE_SHAPES + self.MEDIUM_SHAPES + self.COMPLEX_SHAPES
                shape_type = random.choices(all_shapes, weights=weights, k=1)[0]
            else:
                shape_type = random.randint(0, len(self.SHAPES) - 1)
        pattern = self.SHAPES[shape_type]
        self.height = len(pattern)
        self.width = len(pattern[0]) if self.height > 0 else 0
        for y, row in enumerate(pattern):
            for x, cell in enumerate(row):
                if cell:
                    self.blocks.append((x, y))
        self.surface = self._create_surface(CELL_SIZE)
        self.panel_surface = self._create_surface(PANEL_CELL_SIZE)

    def _create_surface(self, cell_size: int) -> pygame.Surface:
        surf = pygame.Surface((self.width * cell_size, self.height * cell_size), pygame.SRCALPHA)
        for bx, by in self.blocks:
            rect = pygame.Rect(bx * cell_size, by * cell_size, cell_size - 2, cell_size - 2)
            pygame.draw.rect(surf, self.color, rect)
            pygame.draw.rect(surf, HIGHLIGHT_COLOR, rect, 2)
            highlight = pygame.Surface((cell_size // 3, cell_size // 3), pygame.SRCALPHA)
            highlight.fill((255, 255, 255, 50))
            surf.blit(highlight, (bx * cell_size + 2, by * cell_size + 2))
        return surf

    def draw(self, surface: pygame.Surface, x: int, y: int,
             alpha: int = 255, show_placement_hint: bool = False,
             valid_placement: bool = True, is_ghost: bool = False,
             in_panel: bool = False) -> None:
        draw_surface = self.panel_surface if in_panel else self.surface
        cell_size = PANEL_CELL_SIZE if in_panel else CELL_SIZE
        if show_placement_hint and not in_panel:
            hint = pygame.Surface((self.width * cell_size, self.height * cell_size), pygame.SRCALPHA)
            color = VALID_PLACEMENT_COLOR if valid_placement else INVALID_PLACEMENT_COLOR
            for bx, by in self.blocks:
                rect = pygame.Rect(bx * cell_size, by * cell_size, cell_size - 2, cell_size - 2)
                pygame.draw.rect(hint, color, rect)
                pygame.draw.rect(hint, HIGHLIGHT_COLOR, rect, 2)
            if alpha < 255:
                hint.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(hint, (x, y)); return
        if is_ghost and not in_panel:
            ghost = self.surface.copy()
            ghost.fill((255, 255, 255, GHOST_ALPHA), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(ghost, (x, y)); return
        if alpha < 255 and not in_panel:
            temp = self.surface.copy()
            temp.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(temp, (x, y)); return
        surface.blit(draw_surface, (x, y))

# -----------------------------
# Игровое поле
# -----------------------------
class GameBoard:
    def __init__(self):
        self.reset()

    def reset(self) -> None:
        self.grid: List[List[int]] = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.colors: List[List[Optional[Tuple[int, int, int]]]] = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.score = 0
        self.lines_cleared = 0

    def can_place_shape(self, shape: Shape, x: int, y: int) -> bool:
        for block_x, block_y in shape.blocks:
            grid_x, grid_y = x + block_x, y + block_y
            if (grid_x < 0 or grid_x >= GRID_SIZE or
                grid_y < 0 or grid_y >= GRID_SIZE or
                self.grid[grid_y][grid_x] != 0):
                return False
        return True

    def find_best_placement(self, shape: Shape) -> Optional[Tuple[int, int]]:
        best_x, best_y = -1, -1
        best_score = -1.0
        for y in range(GRID_SIZE - shape.height + 1):
            for x in range(GRID_SIZE - shape.width + 1):
                if self.can_place_shape(shape, x, y):
                    score = self.evaluate_placement(shape, x, y)
                    if score > best_score:
                        best_score = score
                        best_x, best_y = x, y
        if best_x == -1:
            return None
        return best_x, best_y

    def evaluate_placement(self, shape: Shape, x: int, y: int) -> float:
        score = 0.0
        for block_x, block_y in shape.blocks:
            grid_x, grid_y = x + block_x, y + block_y
            for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                nx, ny = grid_x + dx, grid_y + dy
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                    if self.grid[ny][nx] != 0:
                        score += 1.0
        score += (GRID_SIZE - y) * 0.5
        temp_grid = [row[:] for row in self.grid]
        for block_x, block_y in shape.blocks:
            gx, gy = x + block_x, y + block_y
            temp_grid[gy][gx] = 1
        lines = 0
        for row in temp_grid:
            if all(row): lines += 1
        for col in range(GRID_SIZE):
            if all(temp_grid[r][col] for r in range(GRID_SIZE)): lines += 1
        score += lines * 10.0
        return score

    def place_shape(self, shape: Shape, x: int, y: int, particle_system=None) -> bool:
        if not self.can_place_shape(shape, x, y):
            return False
        for block_x, block_y in shape.blocks:
            grid_x, grid_y = x + block_x, y + block_y
            self.grid[grid_y][grid_x] = 1
            self.colors[grid_y][grid_x] = shape.color
            if particle_system:
                center_x = GRID_OFFSET_X + grid_x * CELL_SIZE + CELL_SIZE // 2
                center_y = GRID_OFFSET_Y + grid_y * CELL_SIZE + CELL_SIZE // 2
                particle_system.add_effect("shape_place", center_x, center_y, shape.color)
        self.clear_lines(particle_system)
        return True

    def clear_lines(self, particle_system=None) -> int:
        lines_to_clear: List[Tuple[str, int]] = []
        for y in range(GRID_SIZE):
            if all(self.grid[y]): lines_to_clear.append(('horizontal', y))
        for x in range(GRID_SIZE):
            if all(self.grid[y][x] for y in range(GRID_SIZE)): lines_to_clear.append(('vertical', x))
        cleared = 0
        for line_type, index in lines_to_clear:
            if line_type == 'horizontal':
                for x in range(GRID_SIZE):
                    if particle_system and self.colors[index][x]:
                        center_x = GRID_OFFSET_X + x * CELL_SIZE + CELL_SIZE // 2
                        center_y = GRID_OFFSET_Y + index * CELL_SIZE + CELL_SIZE // 2
                        particle_system.add_effect("line_clear", center_x, center_y, self.colors[index][x])
                    self.grid[index][x] = 0
                    self.colors[index][x] = None
            else:
                for y in range(GRID_SIZE):
                    if particle_system and self.colors[y][index]:
                        center_x = GRID_OFFSET_X + index * CELL_SIZE + CELL_SIZE // 2
                        center_y = GRID_OFFSET_Y + y * CELL_SIZE + CELL_SIZE // 2
                        particle_system.add_effect("line_clear", center_x, center_y, self.colors[y][index])
                    self.grid[y][index] = 0
                    self.colors[y][index] = None
            cleared += 1
        if cleared > 0:
            self.lines_cleared += cleared
            self.score += cleared * 100
            if cleared >= 2:
                self.score += (cleared - 1) * 50
                if particle_system:
                    center_x = GRID_OFFSET_X + GRID_SIZE * CELL_SIZE // 2
                    center_y = GRID_OFFSET_Y + GRID_SIZE * CELL_SIZE // 2
                    particle_system.add_effect("combo", center_x, center_y)
        return cleared

    def is_game_over(self) -> bool:
        for shape in [Shape(i) for i in range(5)]:
            for y in range(GRID_SIZE):
                for x in range(GRID_SIZE):
                    if self.can_place_shape(shape, x, y):
                        return False
        return True

    def draw(self, surface: pygame.Surface) -> None:
        grid_bg = pygame.Rect(GRID_OFFSET_X - 10, GRID_OFFSET_Y - 10,
                              GRID_SIZE * CELL_SIZE + 20, GRID_SIZE * CELL_SIZE + 20)
        pygame.draw.rect(surface, PANEL_BG, grid_bg, border_radius=10)
        pygame.draw.rect(surface, GRID_HIGHLIGHT, grid_bg, 3, border_radius=10)
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                rect = pygame.Rect(GRID_OFFSET_X + x * CELL_SIZE,
                                   GRID_OFFSET_Y + y * CELL_SIZE,
                                   CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(surface, GRID_COLOR, rect, 1)
                if self.grid[y][x] != 0:
                    cell_rect = pygame.Rect(GRID_OFFSET_X + x * CELL_SIZE + 1,
                                            GRID_OFFSET_Y + y * CELL_SIZE + 1,
                                            CELL_SIZE - 2, CELL_SIZE - 2)
                    pygame.draw.rect(surface, self.colors[y][x], cell_rect, border_radius=4)
                    pygame.draw.rect(surface, HIGHLIGHT_COLOR, cell_rect, 2, border_radius=4)

# -----------------------------
# Вопросы (перемешивание вариантов)
# -----------------------------
class QuizEngine:
    def __init__(self):
        self.questions = []
        self.rng = random.Random()
        self.load_questions()

    def load_questions(self):
        try:
            with open('data/questions.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                raw = data.get("questions", [])
        except Exception as e:
            print(f"Ошибка загрузки вопросов: {e}")
            raw = [{
                "question": "Что выведет этот код: print('Hello' + 'World')?",
                "options": ["HelloWorld", "Hello World", "Hello+World", "Ошибка"],
                "correct": 0,
                "explanation": "В Python оператор + для строк выполняет конкатенацию."
            }]

        self.questions = []
        for q in raw:
            question = str(q.get("question", "")).strip()
            options = list(q.get("options", []))
            explanation = str(q.get("explanation", "")).strip()

            if not options:
                options = ["Вариант 1", "Вариант 2", "Вариант 3", "Вариант 4"]
                correct_idx = 0
            else:
                seen = set(); deduped = []
                for opt in options:
                    if opt not in seen:
                        seen.add(opt); deduped.append(opt)
                options = deduped
                try:
                    original_correct_idx = int(q.get("correct", 0))
                except Exception:
                    original_correct_idx = 0
                original_correct_idx = max(0, min(original_correct_idx, len(options) - 1))
                correct_text = options[original_correct_idx]

                if len(options) < 4:
                    i = 1
                    while len(options) < 4:
                        filler = f"Вариант {i}"
                        if filler not in options:
                            options.append(filler)
                        i += 1
                elif len(options) > 4:
                    others = [o for o in options if o != correct_text]
                    i = 1
                    while len(others) < 3:
                        filler = f"Вариант {i}"
                        if filler != correct_text and filler not in others:
                            others.append(filler)
                        i += 1
                    picked = self.rng.sample(others, 3)
                    options = [correct_text] + picked
                correct_idx = options.index(correct_text)

            self.questions.append({
                "question": question,
                "options": options,
                "correct": correct_idx,
                "explanation": explanation
            })
        print(f"Загружено и нормализовано вопросов: {len(self.questions)}")

    def get_random_question(self):
        if not self.questions:
            self.load_questions()
        base = self.rng.choice(self.questions)
        options = list(base["options"])
        correct_text = options[base["correct"]]
        self.rng.shuffle(options)
        correct_idx = options.index(correct_text)
        return {
            "question": base["question"],
            "options": options,
            "correct": correct_idx,
            "explanation": base.get("explanation", "")
        }

# -----------------------------
# UI: Кнопка
# -----------------------------
class Button:
    def __init__(self, x, y, width, height, text, action=None, font_size=24):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.is_hovered = False
        self.font = pygame.font.SysFont('consolas', font_size)

    def draw(self, surface):
        color = BUTTON_HOVER_COLOR if self.is_hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, HIGHLIGHT_COLOR, self.rect, 2, border_radius=8)
        text_surf = self.font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)

    def check_click(self, pos):
        if self.rect.collidepoint(pos) and self.action:
            return self.action
        return None

# -----------------------------
# Главное меню (ПРО/НУБ + Архив внизу справа)
# -----------------------------
class MainMenu:
    def __init__(self, screen, game_data):
        self.screen = screen
        self.game_data = game_data
        self.title_font = pygame.font.SysFont('consolas', 48, bold=True)
        self.font = pygame.font.SysFont('consolas', 32)
        self.small_font = pygame.font.SysFont('consolas', 24)

        button_width, button_height = 300, 60
        center_x = SCREEN_WIDTH // 2 - button_width // 2

        # Старт
        self.start_button = Button(center_x, 300, button_width, button_height, "Начать игру", "start")

        # МАЛЕНЬКАЯ кнопка ПРО/НУБ — справа от стартовой
        self.pro_mode = False
        pro_w, pro_h = 120, 44
        self.pro_button = Button(center_x + button_width + 16, 300 + (button_height - pro_h)//2,
                                 pro_w, pro_h, self._pro_label(), "toggle_pro", 22)

        # Достижения
        self.achievements_button = Button(center_x, 380, button_width, button_height, "Достижения", "achievements")

        # Архив — ПРАВЫЙ НИЖНИЙ УГОЛ
        self.archive_button = Button(SCREEN_WIDTH - 190, SCREEN_HEIGHT - 70, 160, 48, "Архив", "archive", 24)

        # Выход
        self.quit_button = Button(center_x, 460, button_width, button_height, "Выход", "quit")

        self.current_screen = "main"

    def _pro_label(self):
        return "ПРО" if self.pro_mode else "НУБ"

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == QUIT:
                return "quit"
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                if self.current_screen == "achievements":
                    self.current_screen = "main"
                else:
                    return "quit"
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if self.current_screen == "main":
                    for btn in (self.start_button, self.achievements_button, self.archive_button, self.quit_button, self.pro_button):
                        act = btn.check_click(mouse_pos)
                        if act == "start":
                            return "start"
                        elif act == "achievements":
                            self.current_screen = "achievements"
                        elif act == "archive":
                            return "archive"
                        elif act == "quit":
                            return "quit"
                        elif act == "toggle_pro":
                            self.pro_mode = not self.pro_mode
                            self.pro_button.text = self._pro_label()
                elif self.current_screen == "achievements":
                    self.current_screen = "main"
        if self.current_screen == "main":
            for btn in (self.start_button, self.achievements_button, self.archive_button, self.quit_button, self.pro_button):
                btn.check_hover(mouse_pos)
        return None

    def draw(self):
        self.screen.fill(MENU_BG)
        if self.current_screen == "main":
            self.draw_main_menu()
        elif self.current_screen == "achievements":
            self.draw_achievements()

    def draw_main_menu(self):
        title = self.title_font.render("Python Blaster", True, HIGHLIGHT_COLOR)
        subtitle = self.font.render("Code & Clear", True, TEXT_COLOR)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 120))
        self.screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 170))
        high_score = self.small_font.render(f"Рекорд: {self.game_data.data['high_score']}", True, TEXT_COLOR)
        self.screen.blit(high_score, (SCREEN_WIDTH // 2 - high_score.get_width() // 2, 210))

        self.start_button.draw(self.screen)
        self.pro_button.draw(self.screen)  # справа от старта
        self.achievements_button.draw(self.screen)
        self.quit_button.draw(self.screen)
        self.archive_button.draw(self.screen)  # низ справа

        instruction = self.small_font.render("ESC — выход", True, TEXT_COLOR)
        self.screen.blit(instruction, (SCREEN_WIDTH // 2 - instruction.get_width() // 2, 610))

    def draw_achievements(self):
        title = self.title_font.render("Достижения", True, HIGHLIGHT_COLOR)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
        stats = [
            f"Сыграно игр: {self.game_data.data['games_played']}",
            f"Рекорд: {self.game_data.data['high_score']}",
            f"Всего линий: {self.game_data.data['total_lines_cleared']}",
            f"Отвечено вопросов: {self.game_data.data['total_questions_answered']}",
            f"Правильных ответов: {self.game_data.data['total_correct_answers']}",
            f"Код-баттлов: {self.game_data.data['total_code_battles_completed']}"
        ]
        for i, stat in enumerate(stats):
            text = self.font.render(stat, True, TEXT_COLOR)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 120 + i * 40))
        achievements_title = self.font.render("Полученные достижения:", True, HIGHLIGHT_COLOR)
        self.screen.blit(achievements_title, (SCREEN_WIDTH // 2 - achievements_title.get_width() // 2, 350))
        achievements = self.game_data.data["achievements"]
        achievement_texts = [
            "🎮 Первая игра" if achievements["first_game"] else "❓ ???",
            "🏆 500 очков" if achievements["score_500"] else "❓ ???",
            "🏆 1000 очков" if achievements["score_1000"] else "❓ ???",
            "🏆 2000 очков" if achievements["score_2000"] else "❓ ???",
            "📊 10 линий" if achievements["clear_10_lines"] else "❓ ???",
            "📊 25 линий" if achievements["clear_25_lines"] else "❓ ???",
            "❓ 5 вопросов" if achievements["answer_5_questions"] else "❓ ???",
            "❓ 10 вопросов" if achievements["answer_10_questions"] else "❓ ???",
            "💻 5 код-баттлов" if achievements["complete_5_code_battles"] else "❓ ???",
            "💻 10 код-баттлов" if achievements["complete_10_code_battles"] else "❓ ???"
        ]
        small_font = pygame.font.SysFont('consolas', 22)
        for i, achievement in enumerate(achievement_texts):
            color = CORRECT_COLOR if "❓" not in achievement else (100, 100, 100)
            text = small_font.render(achievement, True, color)
            x_pos = SCREEN_WIDTH // 2 - 160 + (i % 2) * 320
            y_pos = 400 + (i // 2) * 28
            self.screen.blit(text, (x_pos, y_pos))

# -----------------------------
# Экран Архива — показывает каталог задач с решениями/объяснениями
# -----------------------------
class ArchiveScreen:
    def __init__(self, screen, catalog: CodeBattleCatalog):
        self.screen = screen
        self.catalog = catalog
        self.title_font = pygame.font.SysFont('consolas', 36, bold=True)
        self.font = pygame.font.SysFont('consolas', 20)
        self.small = pygame.font.SysFont('consolas', 16)
        self.items = list(self.catalog.items)
        self.page = 0
        self.per_page = 6
        self.selected = None
        self.btn_back = Button(60, 60, 160, 40, "← В меню", "back", 22)
        self.btn_prev = Button(60, SCREEN_HEIGHT - 70, 140, 40, "◀ Страница", "prev", 20)
        self.btn_next = Button(220, SCREEN_HEIGHT - 70, 140, 40, "Страница ▶", "next", 20)

    def refresh(self):
        self.items = list(self.catalog.items)
        self.page = 0
        self.selected = None

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == QUIT:
                return "quit"
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                return "back"
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                for btn in (self.btn_back, self.btn_prev, self.btn_next):
                    act = btn.check_click(mouse_pos)
                    if act == "back":
                        return "back"
                    elif act == "prev":
                        if self.page > 0:
                            self.page -= 1
                    elif act == "next":
                        if (self.page + 1) * self.per_page < len(self.items):
                            self.page += 1
                y0 = 130
                for i in range(self.per_page):
                    idx = self.page * self.per_page + i
                    if idx >= len(self.items):
                        break
                    row_rect = pygame.Rect(60, y0 + i * 80, 520, 70)
                    if row_rect.collidepoint(mouse_pos):
                        self.selected = idx
                        break
        self.btn_back.check_hover(mouse_pos)
        self.btn_prev.check_hover(mouse_pos)
        self.btn_next.check_hover(mouse_pos)
        return None

    def draw(self):
        self.screen.fill(MENU_BG)
        title = self.title_font.render("Архив задач (все решения)", True, HIGHLIGHT_COLOR)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 20))

        panel = pygame.Rect(40, 110, 560, SCREEN_HEIGHT - 180)
        pygame.draw.rect(self.screen, PANEL_BG, panel, border_radius=10)
        pygame.draw.rect(self.screen, GRID_HIGHLIGHT, panel, 2, border_radius=10)

        items = self.items
        y0 = 130
        for i in range(self.per_page):
            idx = self.page * self.per_page + i
            if idx >= len(items):
                break
            it = items[idx]
            row = pygame.Rect(60, y0 + i * 80, 520, 70)
            pygame.draw.rect(self.screen, (38, 48, 66), row, border_radius=8)
            if self.selected == idx:
                pygame.draw.rect(self.screen, HIGHLIGHT_COLOR, row, 2, border_radius=8)
            diff = it.get("difficulty", "—")
            rew = it.get("reward", 0)
            line1 = self.font.render(
                f"{it.get('name','Без названия')}  |  сложн.: {diff}  |  награда: {rew}",
                True, TEXT_COLOR
            )
            line2 = self.small.render(f"{it.get('description','')}", True, CODE_LINE_NUMBERS)
            self.screen.blit(line1, (row.x + 10, row.y + 6))
            self.screen.blit(line2, (row.x + 10, row.y + 40))

        detail = pygame.Rect(620, 110, SCREEN_WIDTH - 660, SCREEN_HEIGHT - 180)
        pygame.draw.rect(self.screen, PANEL_BG, detail, border_radius=10)
        pygame.draw.rect(self.screen, GRID_HIGHLIGHT, detail, 2, border_radius=10)

        hdr = self.font.render("Детали", True, TEXT_COLOR)
        self.screen.blit(hdr, (detail.x + 14, detail.y + 10))

        if self.selected is not None and self.selected < len(items):
            it = items[self.selected]
            y = detail.y + 40
            lines = [
                f"Задача: {it.get('name','')}",
                f"Описание: {it.get('description','')}",
                f"Время: {it.get('time_limit',0)} сек  |  Награда: {it.get('reward',0)}  |  Сложность: {it.get('difficulty','')}",
                "Объяснение:",
            ]
            for line in lines:
                txt = self.small.render(line, True, TEXT_COLOR)
                self.screen.blit(txt, (detail.x + 14, y)); y += 22

            # Объяснение
            exp_lines = (it.get("explanation","") or "").splitlines()
            for ln in exp_lines[:10]:
                txt = self.small.render(ln, True, CODE_LINE_NUMBERS)
                self.screen.blit(txt, (detail.x + 14, y)); y += 18

            # Код-решение
            y += 8
            code_hdr = self.small.render("Решение:", True, TEXT_COLOR)
            self.screen.blit(code_hdr, (detail.x + 14, y)); y += 20

            code_rect = pygame.Rect(detail.x + 10, y + 6, detail.width - 20, detail.height - (y - detail.y) - 16)
            pygame.draw.rect(self.screen, (20, 25, 35), code_rect, border_radius=8)
            pygame.draw.rect(self.screen, GRID_HIGHLIGHT, code_rect, 1, border_radius=8)
            code_font = pygame.font.SysFont('consolas', 16)
            code_lines = (it.get("solution","") or "").splitlines() or [""]
            max_lines = (code_rect.height - 10) // 18
            for i, line in enumerate(code_lines[:max_lines]):
                t = code_font.render(line, True, CODE_EDITOR_TEXT)
                self.screen.blit(t, (code_rect.x + 8, code_rect.y + 6 + i * 18))

        self.btn_back.draw(self.screen)
        self.btn_prev.draw(self.screen)
        self.btn_next.draw(self.screen)
        pygame.display.flip()

# -----------------------------
# Игра
# -----------------------------
class Game:
    def __init__(self, game_data, pro_mode=False, archive_log: "CodeBattleArchive" = None, catalog: "CodeBattleCatalog" = None):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Python Blaster: Code & Clear")
        self.clock = pygame.time.Clock()
        self.title_font = pygame.font.SysFont('consolas', 36, bold=True)
        self.font = pygame.font.SysFont('consolas', 24)
        self.small_font = pygame.font.SysFont('consolas', 18)

        self.board = GameBoard()
        self.quiz_engine = QuizEngine()
        self.catalog = catalog or CodeBattleCatalog()
        self.code_battle = CodeBattle(self.catalog)  # Внутри только шаблоны без решения
        self.particle_system = ParticleSystem()

        self.current_shapes: List[Shape] = [Shape(difficulty="easy") for _ in range(3)]
        self.game_over = False
        self.show_quiz = False
        self.show_code_battle = False
        self.current_question = None
        self.quiz_result = None
        self.bonus_active = None
        self.difficulty = "easy"
        self.game_data = game_data

        self.pro_mode = bool(pro_mode)
        self.archive_log = archive_log or CodeBattleArchive()

        self.questions_answered_this_game = 0
        self.correct_answers_this_game = 0
        self.lines_cleared_this_game = 0
        self.code_battles_completed_this_game = 0

        self.dragging = False
        self.dragged_shape: Optional[Shape] = None
        self.dragged_shape_index: Optional[int] = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0

        self.ghost_position: Optional[Tuple[int, int]] = None
        self.snap_position: Optional[Tuple[int, int]] = None

        self.code_battle_interval = 5
        self.last_event_lines = 0

        self.panel_rect = pygame.Rect(50, 150, 300, 400)

    def handle_events(self) -> str:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == QUIT:
                return "quit"
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                return "menu"

            if self.game_over:
                if event.type == KEYDOWN and (event.key == K_r or event.key == K_SPACE):
                    return "menu"
                continue

            if self.show_code_battle:
                if self.code_battle.handle_input(event):
                    continue
                if event.type == KEYDOWN and event.key == pygame.K_h:
                    self.code_battle.next_hint(); continue
                if event.type == KEYDOWN and self.code_battle.result:
                    # лог сыгранного баттла (не влияет на экран Архива задач)
                    r = self.code_battle.result
                    ch = self.code_battle.current_challenge or {}
                    self.archive_log.add(
                        challenge_name=ch.get("name", "Без названия"),
                        challenge_desc=ch.get("description", ""),
                        code=self.code_battle.player_code,
                        success=r.get("success", False),
                        message=r.get("message", ""),
                        reward=r.get("reward", 0),
                        time_spent_sec=int(ch.get("time_limit", 0) - self.code_battle.time_left if self.code_battle.time_left is not None else 0)
                    )
                    self.code_battles_completed_this_game += 1
                    self.show_code_battle = False
                    self.code_battle.result = None
                continue

            if self.show_quiz:
                if self.quiz_result:
                    if event.type == MOUSEBUTTONDOWN or (event.type == KEYDOWN and event.key != K_r):
                        self.quiz_result = None
                        self.show_quiz = False
                        self.current_question = None
                elif event.type == KEYDOWN and event.key in [K_1, K_2, K_3, K_4]:
                    answer_index = event.key - K_1
                    self.check_quiz_answer(answer_index)
                continue

            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = event.pos
                for i, shape in enumerate(self.current_shapes):
                    shape_x, shape_y = self.get_shape_panel_position(i, shape)
                    shape_rect = pygame.Rect(shape_x, shape_y,
                                             shape.width * PANEL_CELL_SIZE,
                                             shape.height * PANEL_CELL_SIZE)
                    if shape_rect.collidepoint(mouse_x, mouse_y):
                        self.dragging = True
                        self.dragged_shape = shape
                        self.dragged_shape_index = i
                        self.drag_offset_x = mouse_x - shape_rect.x
                        self.drag_offset_y = mouse_y - shape_rect.y
                        self.ghost_position = None
                        self.snap_position = None
                        break

            elif event.type == MOUSEBUTTONUP and event.button == 1:
                if self.dragging and self.dragged_shape:
                    mouse_x, mouse_y = event.pos
                    if self.panel_rect.collidepoint(mouse_x, mouse_y):
                        self.dragging = False
                        self.dragged_shape = None
                        self.dragged_shape_index = None
                        self.ghost_position = None
                        self.snap_position = None
                    else:
                        pos = self.snap_position if self.snap_position is not None else self.ghost_position
                        if pos is None:
                            grid_x = (mouse_x - GRID_OFFSET_X - self.drag_offset_x) // CELL_SIZE
                            grid_y = (mouse_y - GRID_OFFSET_Y - self.drag_offset_y) // CELL_SIZE
                        else:
                            grid_x, grid_y = pos
                        grid_x = max(0, min(GRID_SIZE - self.dragged_shape.width, grid_x))
                        grid_y = max(0, min(GRID_SIZE - self.dragged_shape.height, grid_y))
                        if self.board.place_shape(self.dragged_shape, grid_x, grid_y, self.particle_system):
                            if self.dragged_shape_index is not None:
                                if self.board.score > 1000:
                                    self.difficulty = "hard"
                                elif self.board.score > 500:
                                    self.difficulty = "normal"
                                self.current_shapes[self.dragged_shape_index] = Shape(difficulty=self.difficulty)

                            self.lines_cleared_this_game = self.board.lines_cleared

                            # События каждые 5 линий
                            if (self.board.lines_cleared >= self.last_event_lines + self.code_battle_interval and
                                    self.board.lines_cleared > 0):
                                self.last_event_lines = self.board.lines_cleared
                                if self.pro_mode:
                                    if random.random() < 0.5:
                                        self.show_code_battle = True
                                        self.code_battle.start_battle()
                                    else:
                                        self.show_quiz = True
                                        self.current_question = self.quiz_engine.get_random_question()
                                else:
                                    self.show_quiz = True
                                    self.current_question = self.quiz_engine.get_random_question()

                        self.dragging = False
                        self.dragged_shape = None
                        self.dragged_shape_index = None
                        self.ghost_position = None
                        self.snap_position = None

            elif event.type == MOUSEMOTION:
                if self.dragging and self.dragged_shape:
                    mouse_x, mouse_y = event.pos
                    grid_x = (mouse_x - GRID_OFFSET_X - self.drag_offset_x) // CELL_SIZE
                    grid_y = (mouse_y - GRID_OFFSET_Y - self.drag_offset_y) // CELL_SIZE
                    grid_x = max(0, min(GRID_SIZE - self.dragged_shape.width, grid_x))
                    grid_y = max(0, min(GRID_SIZE - self.dragged_shape.height, grid_y))
                    can_place = self.board.can_place_shape(self.dragged_shape, grid_x, grid_y)
                    if not can_place:
                        self.snap_position = self.find_nearby_placement(grid_x, grid_y)
                        self.ghost_position = self.snap_position
                    else:
                        self.ghost_position = (grid_x, grid_y)
                        self.snap_position = None

            elif event.type == KEYDOWN:
                if event.key == K_r:
                    self.current_shapes = [Shape(difficulty=self.difficulty) for _ in range(3)]

        return None

    def get_shape_panel_position(self, index: int, shape: Shape) -> Tuple[int, int]:
        panel_x = self.panel_rect.x
        panel_y = self.panel_rect.y
        panel_width = self.panel_rect.width
        panel_height = self.panel_rect.height
        slot_height = panel_height // 3
        y_offset = panel_y + index * slot_height + (slot_height - shape.height * PANEL_CELL_SIZE) // 2
        x_offset = panel_x + (panel_width - shape.width * PANEL_CELL_SIZE) // 2
        return x_offset, y_offset

    def find_nearby_placement(self, x: int, y: int, radius: int = 2) -> Optional[Tuple[int, int]]:
        if self.dragged_shape is None:
            return None
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                tx, ty = x + dx, y + dy
                if 0 <= tx <= GRID_SIZE - self.dragged_shape.width and 0 <= ty <= GRID_SIZE - self.dragged_shape.height:
                    if self.board.can_place_shape(self.dragged_shape, tx, ty):
                        return (tx, ty)
        return self.board.find_best_placement(self.dragged_shape)

    def check_quiz_answer(self, answer_index: int) -> None:
        if not self.current_question: return
        self.questions_answered_this_game += 1
        if answer_index == self.current_question["correct"]:
            self.quiz_result = {"correct": True, "message": "ПРАВИЛЬНО!", "color": CORRECT_COLOR}
            self.correct_answers_this_game += 1
            self.board.score += 50
        else:
            self.quiz_result = {
                "correct": False,
                "message": "НЕПРАВИЛЬНО!",
                "explanation": self.current_question["explanation"],
                "color": WRONG_COLOR
            }

    def reset_game(self) -> None:
        self.board.reset()
        self.current_shapes = [Shape(difficulty="easy") for _ in range(3)]
        self.game_over = False
        self.show_quiz = False
        self.show_code_battle = False
        self.quiz_result = None
        self.dragging = False
        self.dragged_shape = None
        self.dragged_shape_index = None
        self.ghost_position = None
        self.snap_position = None
        self.bonus_active = None
        self.difficulty = "easy"
        self.questions_answered_this_game = 0
        self.correct_answers_this_game = 0
        self.lines_cleared_this_game = 0
        self.code_battles_completed_this_game = 0
        self.last_event_lines = 0
        self.particle_system.particles.clear()

    def draw(self) -> None:
        self.screen.fill(BACKGROUND)
        self.particle_system.update()

        title = self.title_font.render("Python Blaster: Code & Clear", True, TEXT_COLOR)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 20))
        self.board.draw(self.screen)

        if self.dragging and self.dragged_shape and self.ghost_position is not None:
            ghost_x, ghost_y = self.ghost_position
            self.dragged_shape.draw(self.screen,
                                    GRID_OFFSET_X + ghost_x * CELL_SIZE,
                                    GRID_OFFSET_Y + ghost_y * CELL_SIZE,
                                    is_ghost=True)

        pygame.draw.rect(self.screen, PANEL_BG, self.panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, GRID_HIGHLIGHT, self.panel_rect, 2, border_radius=10)
        panel_title = self.font.render("Доступные фигуры:", True, TEXT_COLOR)
        self.screen.blit(panel_title, (self.panel_rect.x + 10, 120))
        for i, shape in enumerate(self.current_shapes):
            if self.dragging and i == self.dragged_shape_index:
                continue
            shape_x, shape_y = self.get_shape_panel_position(i, shape)
            shape.draw(self.screen, shape_x, shape_y, in_panel=True)

        if self.dragging and self.dragged_shape:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            draw_x = mouse_x - self.drag_offset_x
            draw_y = mouse_y - self.drag_offset_y
            valid_placement = False
            if self.ghost_position is not None:
                gx, gy = self.ghost_position
                valid_placement = self.board.can_place_shape(self.dragged_shape, gx, gy)
            self.dragged_shape.draw(self.screen, draw_x, draw_y, alpha=200,
                                    show_placement_hint=True, valid_placement=valid_placement)

        score_panel = pygame.Rect(SCREEN_WIDTH - 280, 120, 250, 160)
        pygame.draw.rect(self.screen, PANEL_BG, score_panel, border_radius=10)
        pygame.draw.rect(self.screen, GRID_HIGHLIGHT, score_panel, 2, border_radius=10)
        score_text = self.font.render(f"Счет: {self.board.score}", True, TEXT_COLOR)
        lines_text = self.font.render(f"Линии: {self.board.lines_cleared}", True, TEXT_COLOR)
        next_event = max(0, self.last_event_lines + 5 - self.board.lines_cleared)
        next_event_text = self.small_font.render(f"След. событие: {next_event}", True, TEXT_COLOR)
        difficulty_text = self.small_font.render(f"Сложность: {self.difficulty}", True, TEXT_COLOR)
        mode_text = self.small_font.render(f"ПРО: {'Да' if self.pro_mode else 'Нет'}", True, TEXT_COLOR)
        self.screen.blit(score_text, (SCREEN_WIDTH - 260, 140))
        self.screen.blit(lines_text, (SCREEN_WIDTH - 260, 170))
        self.screen.blit(next_event_text, (SCREEN_WIDTH - 260, 200))
        self.screen.blit(difficulty_text, (SCREEN_WIDTH - 260, 220))
        self.screen.blit(mode_text, (SCREEN_WIDTH - 260, 240))

        instructions_panel = pygame.Rect(SCREEN_WIDTH - 280, 300, 250, 180)
        pygame.draw.rect(self.screen, PANEL_BG, instructions_panel, border_radius=10)
        pygame.draw.rect(self.screen, GRID_HIGHLIGHT, instructions_panel, 2, border_radius=10)
        for i, line in enumerate([
            "Управление:",
            "Клик и перетаскивание",
            "R - замена фигур",
            "ESC - меню",
            "Фигуры магнитятся"
        ]):
            text = self.small_font.render(line, True, TEXT_COLOR)
            self.screen.blit(text, (SCREEN_WIDTH - 260, 320 + i * 25))

        self.particle_system.draw(self.screen)

        if self.show_code_battle:
            self.code_battle.update_timer()
            self.code_battle.draw(self.screen, self.particle_system)

        if self.show_quiz and self.current_question:
            if self.quiz_result:
                self.draw_quiz_result()
            else:
                self.draw_quiz()

        if self.game_over:
            self.draw_game_over()

        pygame.display.flip()

    def draw_quiz(self) -> None:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        quiz_rect = pygame.Rect(200, 150, 1000, 400)
        pygame.draw.rect(self.screen, PANEL_BG, quiz_rect, border_radius=15)
        pygame.draw.rect(self.screen, HIGHLIGHT_COLOR, quiz_rect, 3, border_radius=15)

        question_text = self.font.render("Вопрос по Python:", True, TEXT_COLOR)
        self.screen.blit(question_text, (SCREEN_WIDTH // 2 - question_text.get_width() // 2, 180))

        def wrap_text(text: str, max_width: int) -> List[str]:
            words = text.split(' ')
            lines: List[str] = []
            current_line: List[str] = []
            for word in words:
                test_line = ' '.join(current_line + [word])
                test_width = self.small_font.size(test_line)[0]
                if test_width <= max_width:
                    current_line.append(word)
                else:
                    lines.append(' '.join(current_line))
                    current_line = [word]
            if current_line: lines.append(' '.join(current_line))
            return lines

        q_lines = wrap_text(self.current_question["question"], 740)
        for i, line in enumerate(q_lines):
            text = self.small_font.render(line, True, TEXT_COLOR)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 220 + i * 25))

        y_offset = 220 + len(q_lines) * 25 + 20
        for i, option in enumerate(self.current_question["options"]):
            option_text = self.small_font.render(f"{i + 1}. {option}", True, TEXT_COLOR)
            self.screen.blit(option_text, (SCREEN_WIDTH // 2 - option_text.get_width() // 2, y_offset + i * 30))

        instruct_text = self.small_font.render("Нажмите 1-4 для выбора ответа", True, TEXT_COLOR)
        self.screen.blit(instruct_text, (SCREEN_WIDTH // 2 - instruct_text.get_width() // 2, y_offset + 150))

    def draw_quiz_result(self) -> None:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        result_rect = pygame.Rect(300, 200, 800, 300)
        pygame.draw.rect(self.screen, PANEL_BG, result_rect, border_radius=15)
        pygame.draw.rect(self.screen, self.quiz_result["color"], result_rect, 3, border_radius=15)
        result_text = self.title_font.render(self.quiz_result["message"], True, self.quiz_result["color"])
        self.screen.blit(result_text, (SCREEN_WIDTH // 2 - result_text.get_width() // 2, 250))
        if not self.quiz_result["correct"]:
            explanation_lines = self.wrap_text(self.current_question.get("explanation", ""), 550)
            for i, line in enumerate(explanation_lines):
                text = self.small_font.render(line, True, TEXT_COLOR)
                self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 320 + i * 25))
        instruct_text = self.small_font.render("Нажмите любую клавишу чтобы продолжить", True, TEXT_COLOR)
        self.screen.blit(instruct_text, (SCREEN_WIDTH // 2 - instruct_text.get_width() // 2, 450))

    def draw_game_over(self) -> None:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        self.screen.blit(overlay, (0, 0))
        game_over_panel = pygame.Rect(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 150, 400, 300)
        pygame.draw.rect(self.screen, PANEL_BG, game_over_panel, border_radius=15)
        pygame.draw.rect(self.screen, (231, 76, 60), game_over_panel, 3, border_radius=15)
        game_over_text = self.title_font.render("ИГРА ОКОНЧЕНА", True, (231, 76, 60))
        score_text = self.font.render(f"Финальный счет: {self.board.score}", True, TEXT_COLOR)
        lines_text = self.font.render(f"Очищено линий: {self.board.lines_cleared}", True, TEXT_COLOR)
        self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
        self.screen.blit(lines_text, (SCREEN_WIDTH // 2 - lines_text.get_width() // 2, SCREEN_HEIGHT // 2 - 10))
        center_x = SCREEN_WIDTH // 2; center_y = SCREEN_HEIGHT // 2
        self.particle_system.add_effect("game_over", center_x, center_y)
        restart_text = self.small_font.render("Нажмите R или SPACE для возврата в меню", True, TEXT_COLOR)
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 70))

    def wrap_text(self, text: str, max_width: int) -> List[str]:
        words = text.split(' ')
        lines: List[str] = []
        current_line: List[str] = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_width = self.small_font.size(test_line)[0]
            if test_width <= max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        return lines

    def update(self) -> None:
        can_place_any = any(self.board.find_best_placement(shape) is not None for shape in self.current_shapes)
        if not can_place_any and not self.game_over:
            self.game_over = True
            self.game_data.add_game_session(
                self.board.score,
                self.lines_cleared_this_game,
                self.questions_answered_this_game,
                self.correct_answers_this_game,
                self.code_battles_completed_this_game
            )

    def run(self) -> str:
        while True:
            result = self.handle_events()
            if result:
                return result
            self.update()
            self.draw()
            self.clock.tick(FPS)

# -----------------------------
# main()
# -----------------------------
def main():
    pygame.init()
    game_data = GameData()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Python Blaster: Code & Clear")
    menu = MainMenu(screen, game_data)
    catalog = CodeBattleCatalog()           # для Архива (все задачи)
    archive_screen = ArchiveScreen(screen, catalog)
    archive_log = CodeBattleArchive()       # лог сыгранных баттлов (не показываем в архиве)

    current_screen = "menu"

    while True:
        if current_screen == "menu":
            result = menu.handle_events()
            if result == "start":
                current_screen = "game"
            elif result == "archive":
                archive_screen.refresh()
                current_screen = "archive"
            elif result == "quit":
                break
            menu.draw()
            pygame.display.flip()

        elif current_screen == "archive":
            res = archive_screen.handle_events()
            if res == "back":
                current_screen = "menu"
            elif res == "quit":
                break
            archive_screen.draw()

        elif current_screen == "game":
            game = Game(game_data, pro_mode=menu.pro_mode, archive_log=archive_log, catalog=catalog)
            result = game.run()
            if result == "menu":
                current_screen = "menu"
            elif result == "quit":
                break

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
