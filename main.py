
##              ||||||    ||\    /||    /====\     /======\   ========    /======\   ========
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
from collections import deque, defaultdict

from pygame import K_DOWN
from pygame.locals import (
    QUIT, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION,
    KEYDOWN, K_r, K_1, K_2, K_3, K_4, K_SPACE, K_ESCAPE,
    K_RETURN, K_BACKSPACE, K_TAB, K_HOME, K_END, K_UP, K_RIGHT, K_LEFT
)

# ---------- Константы ----------
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 700
GRID_SIZE = 8
CELL_SIZE = 60
GRID_OFFSET_X = 600
GRID_OFFSET_Y = 100
PANEL_CELL_SIZE = 35
FPS = 60

# ---------- Палитра ----------
BACKGROUND = (15, 20, 30)
GRID_COLOR = (40, 50, 70)
GRID_HIGHLIGHT = (70, 90, 120)
CELL_COLORS = [
    (41, 128, 185), (39, 174, 96), (142, 68, 173),
    (230, 126, 34), (231, 76, 60), (26, 188, 156), (241, 196, 15),
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


# ---------- Частицы ----------
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


# ---------- Сохранение ----------
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
        self.data = self.default_data.copy()
        self.load_data()

    def load_data(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    self._update_dict_recursive(self.data, loaded)
            else:
                os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
                self.save_data()
        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")
            self.data = self.default_data.copy()
            self.save_data()

    def _update_dict_recursive(self, target, source):
        for k, v in target.items():
            if k in source:
                if isinstance(v, dict) and isinstance(source[k], dict):
                    self._update_dict_recursive(v, source[k])
                else:
                    target[k] = source[k]

    def save_data(self):
        try:
            self.data["last_played"] = datetime.now().isoformat()
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
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
        if updated:
            self.save_data()

    def add_game_session(self, score, lines_cleared, questions_answered, correct_answers, code_battles_completed=0):
        session = {
            "date": datetime.now().isoformat(),
            "score": score,
            "lines_cleared": lines_cleared,
            "questions_answered": questions_answered,
            "correct_answers": correct_answers,
            "code_battles_completed": code_battles_completed
        }
        if not any(s.get("date") == session["date"] for s in self.data["game_sessions"]):
            self.data["games_played"] += 1
            self.data["total_lines_cleared"] += lines_cleared
            self.data["total_questions_answered"] += questions_answered
            self.data["total_correct_answers"] += correct_answers
            self.data["total_code_battles_completed"] += code_battles_completed
            self.data["game_sessions"].append(session)
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


# ---------- Code Battle ----------
class CodeBattle:
    def __init__(self):
        self.challenges = [
            {
                "name": "Сумма двух чисел",
                "description": "Напишите функцию, которая возвращает сумму двух чисел",
                "template": "def add(a, b):\n    # Ваш код здесь\n    return",
                "test_cases": [
                    {"input": (1, 2), "expected": 3},
                    {"input": (5, 7), "expected": 12},
                    {"input": (-1, 1), "expected": 0},
                    {"input": (0, 0), "expected": 0}
                ],
                "difficulty": "easy",
                "time_limit": 120,
                "reward": 200,
                "hints": ["Просто сложите a и b", "Используйте оператор +", "Не забудьте вернуть результат"]
            },
            {
                "name": "Факториал",
                "description": "Напишите функцию для вычисления факториала числа",
                "template": "def factorial(n):\n    # Ваш код здесь\n    return",
                "test_cases": [
                    {"input": (0,), "expected": 1},
                    {"input": (1,), "expected": 1},
                    {"input": (5,), "expected": 120},
                    {"input": (7,), "expected": 5040}
                ],
                "difficulty": "medium",
                "time_limit": 180,
                "reward": 350,
                "hints": ["Факториал 0 равен 1", "Используйте рекурсию или цикл", "n * factorial(n-1)"]
            },
            {
                "name": "Палиндром",
                "description": "Проверьте, является ли строка палиндромом",
                "template": "def is_palindrome(s):\n    # Ваш код здесь\n    return",
                "test_cases": [
                    {"input": ("racecar",), "expected": True},
                    {"input": ("hello",), "expected": False},
                    {"input": ("a",), "expected": True},
                    {"input": ("",), "expected": True},
                    {"input": ("A man a plan a canal Panama",), "expected": True}
                ],
                "difficulty": "medium",
                "time_limit": 180,
                "reward": 300,
                "hints": ["Уберите пробелы, нижний регистр", "Сравните с s[::-1]", "Используйте replace/isalnum"]
            },
            {
                "name": "Фибоначчи",
                "description": "Верните n-ое число Фибоначчи",
                "template": "def fibonacci(n):\n    # Ваш код здесь\n    return",
                "test_cases": [
                    {"input": (0,), "expected": 0},
                    {"input": (1,), "expected": 1},
                    {"input": (2,), "expected": 1},
                    {"input": (6,), "expected": 8},
                    {"input": (10,), "expected": 55}
                ],
                "difficulty": "hard",
                "time_limit": 240,
                "reward": 500,
                "hints": ["F(0)=0, F(1)=1", "F(n)=F(n-1)+F(n-2)", "Итерация или мемоизация"]
            }
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
        self.player_code = self.current_challenge["template"]
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
                    cb = self.player_code[:self.cursor_position]
                    ca = self.player_code[self.cursor_position:]
                    self.player_code = cb + "    " + ca
                    self.cursor_position += 4
                return True
            elif event.key == K_DOWN and self.show_autocomplete:
                self.autocomplete_index = (self.autocomplete_index + 1) % len(self.autocomplete_options); return True
            elif event.key == K_UP and self.show_autocomplete:
                self.autocomplete_index = (self.autocomplete_index - 1) % len(self.autocomplete_options); return True
            elif event.key == K_RETURN and self.show_autocomplete:
                self.apply_autocomplete(); return True
            elif event.key == K_RETURN:
                cb = self.player_code[:self.cursor_position]
                ca = self.player_code[self.cursor_position:]
                self.player_code = cb + '\n' + ca
                self.cursor_position += 1
                return True
            elif event.key == K_BACKSPACE:
                if self.cursor_position > 0:
                    cb = self.player_code[:self.cursor_position - 1]
                    ca = self.player_code[self.cursor_position:]
                    self.player_code = cb + ca
                    self.cursor_position -= 1
                    self.check_autocomplete()
                return True
            elif event.key == K_LEFT:
                self.cursor_position = max(0, self.cursor_position - 1); self.show_autocomplete = False; return True
            elif event.key == K_RIGHT:
                self.cursor_position = min(len(self.player_code), self.cursor_position + 1); self.show_autocomplete=False;return True
            elif event.key == K_UP and not self.show_autocomplete:
                lines = self.player_code[:self.cursor_position].split('\n')
                if len(lines) > 1:
                    cur_len = len(lines[-1])
                    prev_len = len(lines[-2])
                    new_pos = self.cursor_position - len(lines[-1]) - 1 - max(0, cur_len - prev_len)
                    self.cursor_position = max(0, new_pos)
                return True
            elif event.key == K_DOWN and not self.show_autocomplete:
                lines = self.player_code[:self.cursor_position].split('\n')
                rem = self.player_code[self.cursor_position:].split('\n', 1)
                if len(rem) > 1:
                    cur_len = len(lines[-1])
                    next_len = len(rem[0])
                    new_pos = self.cursor_position + len(rem[0]) + 1 + max(0, cur_len - next_len)
                    self.cursor_position = min(len(self.player_code), new_pos)
                return True
            elif event.key == K_HOME:
                lines = self.player_code[:self.cursor_position].split('\n')
                self.cursor_position -= len(lines[-1]); return True
            elif event.key == K_END:
                rem = self.player_code[self.cursor_position:].split('\n', 1)
                if rem: self.cursor_position += len(rem[0]); return True
            elif event.unicode.isprintable():
                cb = self.player_code[:self.cursor_position]
                ca = self.player_code[self.cursor_position:]
                self.player_code = cb + event.unicode + ca
                self.cursor_position += 1
                self.check_autocomplete(); return True
        elif event.type == MOUSEBUTTONDOWN:
            if self.submit_button_rect.collidepoint(event.pos):
                self.submit_solution(); return True
            code_rect = pygame.Rect(120, 200, SCREEN_WIDTH - 240, 300)
            if code_rect.collidepoint(event.pos):
                click_x, click_y = event.pos
                line_num = min(len(self.player_code.split('\n')) - 1,
                               max(0, (click_y - 200) // self.line_height))
                lines = self.player_code.split('\n')
                line_text = lines[line_num] if line_num < len(lines) else ""
                char_pos = min(len(line_text), max(0, (click_x - 160) // 10))
                total_pos = sum(len(lines[i]) + 1 for i in range(line_num)) + char_pos
                self.cursor_position = min(total_pos, len(self.player_code))
                self.show_autocomplete = False; return True
        return False

    def check_autocomplete(self):
        if self.cursor_position == 0:
            self.show_autocomplete = False; return
        current = self.player_code[:self.cursor_position]
        last = ""
        for i in range(self.cursor_position - 1, -1, -1):
            if i < len(current) and (current[i].isalnum() or current[i] == '_'):
                last = current[i] + last
            else:
                break
        if len(last) >= 2:
            self.autocomplete_options = [kw for kw in self.keywords if kw.startswith(last)]
            self.show_autocomplete = len(self.autocomplete_options) > 0
            self.autocomplete_index = 0
        else:
            self.show_autocomplete = False

    def apply_autocomplete(self):
        if not self.show_autocomplete or not self.autocomplete_options: return
        selected = self.autocomplete_options[self.autocomplete_index]
        current = self.player_code[:self.cursor_position]
        word_start = self.cursor_position
        for i in range(self.cursor_position - 1, -1, -1):
            if i < len(current) and not (current[i].isalnum() or current[i] == '_'):
                word_start = i + 1; break
            if i == 0: word_start = 0; break
        cb = self.player_code[:word_start]
        ca = self.player_code[self.cursor_position:]
        self.player_code = cb + selected + ca
        self.cursor_position = word_start + len(selected)
        self.show_autocomplete = False

    def safe_execute(self, code, tests):
        safe_builtins = {'len': len, 'range': range, 'str': str, 'int': int, 'float': float,
                         'bool': bool, 'list': list, 'tuple': tuple, 'dict': dict, 'set': set}
        local_vars = {}
        try:
            exec(code, {"__builtins__": safe_builtins}, local_vars)
            func = None
            for v in local_vars.values():
                if callable(v): func = v; break
            if not func: return False, "Функция не найдена"
            for i, test in enumerate(tests):
                try:
                    res = func(*test["input"])
                    if res != test["expected"]:
                        return False, f"Тест {i + 1} не пройден: ожидалось {test['expected']}, получено {res}"
                except Exception as e:
                    return False, f"Ошибка в тесте {i + 1}: {str(e)}"
            return True, "Все тесты пройдены!"
        except Exception as e:
            return False, f"Ошибка выполнения: {str(e)}"

    def submit_solution(self):
        if not self.current_challenge or self.result: return
        ok, msg = self.safe_execute(self.player_code, self.current_challenge["test_cases"])
        self.result = {"success": ok, "message": msg, "reward": self.current_challenge["reward"] if ok else 0}
        return self.result

    def get_cursor_position(self):
        lines = self.player_code[:self.cursor_position].split('\n')
        return len(lines) - 1, len(lines[-1]) if lines else 0

    def tokenize_line(self, line):
        tokens = []; cur = ""; in_str = False; str_ch = None; in_comment = False
        for ch in line:
            if in_comment:
                cur += ch
            elif in_str:
                cur += ch
                if ch == str_ch:
                    tokens.append((cur, "string")); cur = ""; in_str = False; str_ch = None
            else:
                if ch in ['"', "'"]:
                    if cur: tokens.append((cur, "normal")); cur = ""
                    in_str = True; str_ch = ch; cur = ch
                elif ch == '#':
                    if cur: tokens.append((cur, "normal")); cur = ""
                    in_comment = True; cur = ch
                elif ch in ' \t\n()[]{}:,=+-*/%':
                    if cur:
                        tokens.append((cur, "keyword" if cur in self.keywords else "normal")); cur = ""
                    tokens.append((ch, "normal"))
                else:
                    cur += ch
        if cur:
            if in_comment: tokens.append((cur, "comment"))
            elif in_str: tokens.append((cur, "string"))
            else: tokens.append((cur, "keyword" if cur in self.keywords else "normal"))
        return tokens

    def get_token_color(self, token_type):
        colors = {"normal": CODE_EDITOR_TEXT, "keyword": (86, 156, 214), "string": (206, 145, 120), "comment": (106, 153, 85)}
        return colors.get(token_type, CODE_EDITOR_TEXT)

    def draw(self, surface, particle_system):
        if not self.current_challenge: return
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200)); surface.blit(overlay, (0, 0))
        battle_rect = pygame.Rect(100, 50, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 100)
        pygame.draw.rect(surface, CODE_EDITOR_BG, battle_rect, border_radius=15)
        pygame.draw.rect(surface, HIGHLIGHT_COLOR, battle_rect, 3, border_radius=15)

        title_font = pygame.font.SysFont('consolas', 32, bold=True)
        title = title_font.render("КОД-БАТТЛ!", True, HIGHLIGHT_COLOR)
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 70))

        challenge_font = pygame.font.SysFont('consolas', 24)
        name_text = challenge_font.render(f"Задача: {self.current_challenge['name']}", True, TEXT_COLOR)
        desc_text = self.code_font.render(self.current_challenge['description'], True, TEXT_COLOR)
        surface.blit(name_text, (120, 120)); surface.blit(desc_text, (120, 150))

        time_text = challenge_font.render(f"Время: {int(self.time_left)} сек", True, TEXT_COLOR)
        reward_text = challenge_font.render(f"Награда: {self.current_challenge['reward']} очков", True, CORRECT_COLOR)
        surface.blit(time_text, (SCREEN_WIDTH - 300, 120)); surface.blit(reward_text, (SCREEN_WIDTH - 300, 150))

        code_rect = pygame.Rect(120, 200, SCREEN_WIDTH - 240, 300)
        pygame.draw.rect(surface, (20, 25, 35), code_rect, border_radius=10)
        pygame.draw.rect(surface, GRID_HIGHLIGHT, code_rect, 2, border_radius=10)

        lines = self.player_code.split('\n'); visible = 12
        start = max(0, min(self.scroll_offset, len(lines) - visible)); end = min(len(lines), start + visible)
        for i in range(start, end):
            y = 210 + (i - start) * self.line_height
            line_num_text = self.code_font.render(str(i + 1), True, CODE_LINE_NUMBERS)
            surface.blit(line_num_text, (130, y))
            x_off = 160
            for token, ttype in self.tokenize_line(lines[i]):
                col = self.get_token_color(ttype)
                ts = self.code_font.render(token, True, col)
                surface.blit(ts, (x_off, y)); x_off += ts.get_width()

        if self.cursor_visible and not self.result:
            cur_line, cur_col = self.get_cursor_position()
            if start <= cur_line < end:
                cx = 160 + self.code_font.size(lines[cur_line][:cur_col])[0]
                cy = 210 + (cur_line - start) * self.line_height
                pygame.draw.line(surface, CODE_EDITOR_TEXT, (cx, cy), (cx, cy + self.line_height), 2)

        if self.show_autocomplete and self.autocomplete_options:
            ac_rect = pygame.Rect(160, 210 + self.line_height, 200, len(self.autocomplete_options) * self.line_height)
            pygame.draw.rect(surface, (40, 45, 60), ac_rect)
            pygame.draw.rect(surface, GRID_HIGHLIGHT, ac_rect, 1)
            for i, option in enumerate(self.autocomplete_options):
                col = HIGHLIGHT_COLOR if i == self.autocomplete_index else TEXT_COLOR
                t = self.code_font.render(option, True, col)
                surface.blit(t, (165, 215 + self.line_height + i * self.line_height))

        if "hints" in self.current_challenge:
            hint_rect = pygame.Rect(120, 520, SCREEN_WIDTH - 240, 60)
            pygame.draw.rect(surface, (30, 35, 45), hint_rect, border_radius=8)
            pygame.draw.rect(surface, GRID_HIGHLIGHT, hint_rect, 1, border_radius=8)
            hint = self.code_font.render(f"Подсказка: {self.current_challenge['hints'][self.current_hint]}", True, TEXT_COLOR)
            surface.blit(hint, (130, 540))
            hint_nav = self.code_font.render(f"({self.current_hint + 1}/{len(self.current_challenge['hints'])}) Нажмите H для следующей подсказки", True, CODE_LINE_NUMBERS)
            surface.blit(hint_nav, (130, 565))

        self.submit_button_rect = pygame.Rect(SCREEN_WIDTH - 320, 520, 200, 40)
        pygame.draw.rect(surface, BUTTON_COLOR, self.submit_button_rect, border_radius=8)
        pygame.draw.rect(surface, HIGHLIGHT_COLOR, self.submit_button_rect, 2, border_radius=8)
        submit_text = self.code_font.render("Отправить (Ctrl+Enter)", True, TEXT_COLOR)
        surface.blit(submit_text, (self.submit_button_rect.centerx - submit_text.get_width() // 2,
                                   self.submit_button_rect.centery - submit_text.get_height() // 2))

        if self.result:
            res_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 50, 400, 100)
            col = CORRECT_COLOR if self.result["success"] else WRONG_COLOR
            pygame.draw.rect(surface, PANEL_BG, res_rect, border_radius=10)
            pygame.draw.rect(surface, col, res_rect, 3, border_radius=10)
            result_font = pygame.font.SysFont('consolas', 24, bold=True)
            res_text = result_font.render("УСПЕХ!" if self.result["success"] else "НЕУДАЧА", True, col)
            msg_text = self.code_font.render(self.result["message"], True, TEXT_COLOR)
            surface.blit(res_text, (SCREEN_WIDTH // 2 - res_text.get_width() // 2, SCREEN_HEIGHT // 2 - 30))
            surface.blit(msg_text, (SCREEN_WIDTH // 2 - msg_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
            if self.result["success"]:
                for _ in range(10):
                    x = random.randint(SCREEN_WIDTH // 2 - 100, SCREEN_WIDTH // 2 + 100)
                    y = random.randint(SCREEN_HEIGHT // 2 - 50, SCREEN_HEIGHT // 2 + 50)
                    particle_system.add_effect("code_success", x, y)
        else:
            instruct_font = pygame.font.SysFont('consolas', 18)
            tips = ["Tab - отступ", "Ctrl+Enter - отправить", "H - подсказка", "Стрелки - курсор"]
            for i, line in enumerate(tips):
                t = instruct_font.render(line, True, TEXT_COLOR)
                surface.blit(t, (120, SCREEN_HEIGHT - 100 + i * 20))

    def next_hint(self):
        if self.current_challenge and "hints" in self.current_challenge:
            self.current_hint = (self.current_hint + 1) % len(self.current_challenge["hints"])


# ---------- Фигуры ----------
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
                if cell: self.blocks.append((x, y))
        self.surface = self._create_surface(CELL_SIZE)
        self.panel_surface = self._create_surface(PANEL_CELL_SIZE)

    def _create_surface(self, cell_size: int) -> pygame.Surface:
        surf = pygame.Surface((self.width * cell_size, self.height * cell_size), pygame.SRCALPHA)
        for bx, by in self.blocks:
            rect = pygame.Rect(bx * cell_size, by * cell_size, cell_size - 2, cell_size - 2)
            pygame.draw.rect(surf, self.color, rect)
            pygame.draw.rect(surf, HIGHLIGHT_COLOR, rect, 2)
            hl = pygame.Surface((cell_size // 3, cell_size // 3), pygame.SRCALPHA)
            hl.fill((255, 255, 255, 50)); surf.blit(hl, (bx * cell_size + 2, by * cell_size + 2))
        return surf

    def draw(self, surface: pygame.Surface, x: int, y: int,
             alpha: int = 255, show_placement_hint: bool = False,
             valid_placement: bool = True, is_ghost: bool = False, in_panel: bool = False) -> None:
        draw_surface = self.panel_surface if in_panel else self.surface
        cell_size = PANEL_CELL_SIZE if in_panel else CELL_SIZE
        if show_placement_hint and not in_panel:
            hint = pygame.Surface((self.width * cell_size, self.height * cell_size), pygame.SRCALPHA)
            color = VALID_PLACEMENT_COLOR if valid_placement else INVALID_PLACEMENT_COLOR
            for bx, by in self.blocks:
                rect = pygame.Rect(bx * cell_size, by * cell_size, cell_size - 2, cell_size - 2)
                pygame.draw.rect(hint, color, rect); pygame.draw.rect(hint, HIGHLIGHT_COLOR, rect, 2)
            if alpha < 255: hint.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(hint, (x, y)); return
        if is_ghost and not in_panel:
            ghost = self.surface.copy(); ghost.fill((255, 255, 255, GHOST_ALPHA), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(ghost, (x, y)); return
        if alpha < 255 and not in_panel:
            temp = self.surface.copy(); temp.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(temp, (x, y)); return
        surface.blit(draw_surface, (x, y))


# ---------- Доска ----------
class GameBoard:
    def __init__(self):
        self.reset()

    def reset(self) -> None:
        self.grid: List[List[int]] = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.colors: List[List[Optional[Tuple[int, int, int]]]] = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.score = 0
        self.lines_cleared = 0

    def can_place_shape(self, shape: Shape, x: int, y: int) -> bool:
        for bx, by in shape.blocks:
            gx, gy = x + bx, y + by
            if gx < 0 or gx >= GRID_SIZE or gy < 0 or gy >= GRID_SIZE or self.grid[gy][gx] != 0:
                return False
        return True

    def find_best_placement(self, shape: Shape) -> Optional[Tuple[int, int]]:
        best = (-1, -1); best_score = -1.0
        for y in range(GRID_SIZE - shape.height + 1):
            for x in range(GRID_SIZE - shape.width + 1):
                if self.can_place_shape(shape, x, y):
                    s = self.evaluate_placement(shape, x, y)
                    if s > best_score: best_score, best = s, (x, y)
        return None if best[0] == -1 else best

    def evaluate_placement(self, shape: Shape, x: int, y: int) -> float:
        score = 0.0
        for bx, by in shape.blocks:
            gx, gy = x + bx, y + by
            for dx, dy in ((0,-1),(1,0),(0,1),(-1,0)):
                nx, ny = gx + dx, gy + dy
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and self.grid[ny][nx] != 0:
                    score += 1.0
        score += (GRID_SIZE - y) * 0.5
        temp = [row[:] for row in self.grid]
        for bx, by in shape.blocks:
            temp[y + by][x + bx] = 1
        lines = sum(1 for row in temp if all(row))
        for c in range(GRID_SIZE):
            if all(temp[r][c] for r in range(GRID_SIZE)): lines += 1
        return score + lines * 10.0

    def place_shape(self, shape: Shape, x: int, y: int, particle_system=None) -> bool:
        if not self.can_place_shape(shape, x, y): return False
        for bx, by in shape.blocks:
            gx, gy = x + bx, y + by
            self.grid[gy][gx] = 1; self.colors[gy][gx] = shape.color
            if particle_system:
                cx = GRID_OFFSET_X + gx * CELL_SIZE + CELL_SIZE // 2
                cy = GRID_OFFSET_Y + gy * CELL_SIZE + CELL_SIZE // 2
                particle_system.add_effect("shape_place", cx, cy, shape.color)
        self.clear_lines(particle_system); return True

    def clear_lines(self, particle_system=None) -> int:
        lines_to_clear: List[Tuple[str, int]] = []
        for y in range(GRID_SIZE):
            if all(self.grid[y]): lines_to_clear.append(('h', y))
        for x in range(GRID_SIZE):
            if all(self.grid[y][x] for y in range(GRID_SIZE)): lines_to_clear.append(('v', x))

        cleared = 0
        for t, idx in lines_to_clear:
            if t == 'h':
                for x in range(GRID_SIZE):
                    if particle_system and self.colors[idx][x]:
                        cx = GRID_OFFSET_X + x * CELL_SIZE + CELL_SIZE // 2
                        cy = GRID_OFFSET_Y + idx * CELL_SIZE + CELL_SIZE // 2
                        particle_system.add_effect("line_clear", cx, cy, self.colors[idx][x])
                    self.grid[idx][x] = 0; self.colors[idx][x] = None
            else:
                for y in range(GRID_SIZE):
                    if particle_system and self.colors[y][idx]:
                        cx = GRID_OFFSET_X + idx * CELL_SIZE + CELL_SIZE // 2
                        cy = GRID_OFFSET_Y + y * CELL_SIZE + CELL_SIZE // 2
                        particle_system.add_effect("line_clear", cx, cy, self.colors[y][idx])
                    self.grid[y][idx] = 0; self.colors[y][idx] = None
            cleared += 1

        if cleared > 0:
            self.lines_cleared += cleared
            self.score += cleared * 100
            if cleared >= 2:
                self.score += (cleared - 1) * 50
                if particle_system:
                    cx = GRID_OFFSET_X + GRID_SIZE * CELL_SIZE // 2
                    cy = GRID_OFFSET_Y + GRID_SIZE * CELL_SIZE // 2
                    particle_system.add_effect("combo", cx, cy)
        return cleared

    def draw(self, surface: pygame.Surface) -> None:
        grid_bg = pygame.Rect(GRID_OFFSET_X - 10, GRID_OFFSET_Y - 10,
                              GRID_SIZE * CELL_SIZE + 20, GRID_SIZE * CELL_SIZE + 20)
        pygame.draw.rect(surface, PANEL_BG, grid_bg, border_radius=10)
        pygame.draw.rect(surface, GRID_HIGHLIGHT, grid_bg, 3, border_radius=10)
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                rect = pygame.Rect(GRID_OFFSET_X + x * CELL_SIZE, GRID_OFFSET_Y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(surface, GRID_COLOR, rect, 1)
                if self.grid[y][x]:
                    cell = pygame.Rect(rect.x + 1, rect.y + 1, CELL_SIZE - 2, CELL_SIZE - 2)
                    pygame.draw.rect(surface, self.colors[y][x], cell, border_radius=4)
                    pygame.draw.rect(surface, HIGHLIGHT_COLOR, cell, 2, border_radius=4)


# ---------- Smart Dealer: анализ + «проигрышные» выдачи ----------
def _neighbors4(x, y):
    for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
        nx, ny = x+dx, y+dy
        if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
            yield nx, ny

def get_empty_components(board):
    comp_id = {}; comp_size = defaultdict(int); cid = 0
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            if board.grid[y][x] == 0 and (x,y) not in comp_id:
                cid += 1; q = deque([(x,y)]); comp_id[(x,y)] = cid
                while q:
                    cx, cy = q.popleft(); comp_size[cid] += 1
                    for nx, ny in _neighbors4(cx, cy):
                        if board.grid[ny][nx] == 0 and (nx,ny) not in comp_id:
                            comp_id[(nx,ny)] = cid; q.append((nx,ny))
    return comp_id, comp_size

def precompute_line_counts(board):
    row_cnt = [sum(board.grid[y][x] for x in range(GRID_SIZE)) for y in range(GRID_SIZE)]
    col_cnt = [sum(board.grid[y][x] for y in range(GRID_SIZE)) for x in range(GRID_SIZE)]
    near_rows = {y for y in range(GRID_SIZE) if GRID_SIZE - row_cnt[y] <= 4 and row_cnt[y] < GRID_SIZE}
    near_cols = {x for x in range(GRID_SIZE) if GRID_SIZE - col_cnt[x] <= 4 and col_cnt[x] < GRID_SIZE}
    return row_cnt, col_cnt, near_rows, near_cols

def score_placement(board, shape, x, y, comp_id, comp_size, row_cnt, col_cnt, near_rows, near_cols):
    covered_by_row = defaultdict(int); covered_by_col = defaultdict(int)
    small_pockets = 0; near_complete = 0; adjacency = 0; singleton_penalty = 0
    placed = []
    for bx, by in shape.blocks:
        gx, gy = x + bx, y + by
        placed.append((gx, gy))
        covered_by_row[gy] += 1; covered_by_col[gx] += 1
        if (gx, gy) in comp_id and comp_size[comp_id[(gx, gy)]] <= 4: small_pockets += 1
        if gy in near_rows: near_complete += 1
        if gx in near_cols: near_complete += 1
        for nx, ny in _neighbors4(gx, gy):
            if board.grid[ny][nx] == 1: adjacency += 1

    cleared = 0
    for ry, cnt in covered_by_row.items():
        if row_cnt[ry] + cnt == GRID_SIZE: cleared += 1
    for cx, cnt in covered_by_col.items():
        if col_cnt[cx] + cnt == GRID_SIZE: cleared += 1

    empty_set = {(x, y) for y in range(GRID_SIZE) for x in range(GRID_SIZE) if board.grid[y][x] == 0}
    placed_set = set(placed)
    for gx, gy in placed:
        for nx, ny in _neighbors4(gx, gy):
            if (nx, ny) in empty_set and (nx, ny) not in placed_set:
                empt_nbrs = sum(((tx, ty) in empty_set and (tx, ty) not in placed_set) for tx, ty in _neighbors4(nx, ny))
                if empt_nbrs == 1: singleton_penalty += 1

    return 100 * cleared + 10 * near_complete + 6 * small_pockets + 2 * adjacency - 4 * singleton_penalty

def rank_shape_types_for_board(board, allowed_types):
    comp_id, comp_size = get_empty_components(board)
    row_cnt, col_cnt, near_rows, near_cols = precompute_line_counts(board)
    score_noise = min(getattr(board, "score", 0) / 2200.0, 0.30)

    ranked = []
    for t in allowed_types:
        shp = Shape(shape_type=t)
        best_score, placements = -10**9, 0
        for y in range(GRID_SIZE - shp.height + 1):
            for x in range(GRID_SIZE - shp.width + 1):
                if board.can_place_shape(shp, x, y):
                    placements += 1
                    s = score_placement(board, shp, x, y, comp_id, comp_size, row_cnt, col_cnt, near_rows, near_cols)
                    if s > best_score: best_score = s
        if placements > 0:
            if score_noise > 0:
                best_score += int(best_score * random.uniform(-score_noise, score_noise))
            ranked.append((t, best_score, placements))
    ranked.sort(key=lambda r: (r[1], r[2]), reverse=True)
    return ranked

def find_dead_types_for_board(board, allowed_types):
    """Типы фигур из пула, которые НИГДЕ не помещаются (dead-draw)."""
    dead = []
    for t in allowed_types:
        shp = Shape(shape_type=t)
        ok = False
        for y in range(GRID_SIZE - shp.height + 1):
            for x in range(GRID_SIZE - shp.width + 1):
                if board.can_place_shape(shp, x, y):
                    ok = True; break
            if ok: break
        if not ok: dead.append(t)
    return dead

def difficulty_progression(score):
    # пул
    if score < 400: pool = Shape.SIMPLE_SHAPES
    elif score < 1200: pool = Shape.SIMPLE_SHAPES + Shape.MEDIUM_SHAPES
    else: pool = list(range(len(Shape.SHAPES)))

    # вероятность dead-draw (чтобы можно было проиграть)
    if score < 600: p_dead = 0.00
    elif score < 1000: p_dead = 0.04
    elif score < 1200: p_dead = 0.08
    elif score < 1400: p_dead = 0.12
    elif score < 1600: p_dead = 0.18
    elif score < 2000: p_dead = 0.25
    else: p_dead = 0.33

    # базовые веса (helpful/neutral/spicy)
    if score < 200: p = (0.90, 0.10, 0.00); top_k = 3
    elif score < 400: p = (0.85, 0.13, 0.02); top_k = 3
    elif score < 600: p = (0.75, 0.18, 0.07); top_k = 3
    elif score < 800: p = (0.62, 0.23, 0.15); top_k = 3
    elif score < 1000: p = (0.50, 0.27, 0.23); top_k = 2
    elif score < 1200: p = (0.44, 0.30, 0.26); top_k = 2
    elif score < 1400: p = (0.38, 0.32, 0.30); top_k = 2
    elif score < 1600: p = (0.33, 0.33, 0.34); top_k = 1
    elif score < 1800: p = (0.28, 0.34, 0.38); top_k = 1
    elif score < 2000: p = (0.24, 0.34, 0.42); top_k = 1
    else: p = (0.20, 0.35, 0.45); top_k = 1

    return {"p_helpful": p[0], "p_neutral": p[1], "p_spicy": p[2], "top_k": top_k, "pool": pool, "p_dead": p_dead}

def smart_deal_shape(board, difficulty):
    cfg = difficulty_progression(board.score)
    ranked = rank_shape_types_for_board(board, cfg["pool"])
    dead_types = find_dead_types_for_board(board, cfg["pool"])

    # сначала шанс выдать «мертвую» фигуру — это и создаёт реальную возможность проиграть
    if dead_types and random.random() < cfg["p_dead"]:
        t = random.choice(dead_types)
        return Shape(shape_type=t, difficulty=difficulty)

    # иначе — как раньше: helpful / neutral / spicy
    if not ranked:
        return Shape(difficulty=difficulty)
    r = random.random()
    if r < cfg["p_helpful"]:
        k = min(cfg["top_k"], len(ranked))
        t = random.choice([t for (t, s, c) in ranked[:k]])
        return Shape(shape_type=t, difficulty=difficulty)
    r -= cfg["p_helpful"]
    if r < cfg["p_neutral"]:
        t, _, _ = random.choice(ranked)
        return Shape(shape_type=t, difficulty=difficulty)
    tail = ranked[-min(6, len(ranked)):]
    t, _, _ = random.choice(tail)
    return Shape(shape_type=t, difficulty=difficulty)


# ---------- Викторина ----------
class QuizEngine:
    def __init__(self):
        self.questions = []
        self.rng = random.Random()  # можно задать seed для воспроизводимости: random.Random(42)
        self.load_questions()

    def load_questions(self):
        """Загружаем вопросы и нормализуем их до 4 вариантов с валидным correct."""
        try:
            with open('data/questions.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                raw = data.get("questions", [])
        except Exception as e:
            print(f"Ошибка загрузки вопросов: {e}")
            raw = [
                {
                    "question": "Что выведет этот код: print('Hello' + 'World')?",
                    "options": ["HelloWorld", "Hello World", "Hello+World", "Ошибка"],
                    "correct": 0,
                    "explanation": "В Python оператор + для строк выполняет конкатенацию."
                }
            ]

        self.questions = []
        for q in raw:
            # Базовые поля
            question = str(q.get("question", "")).strip()
            options = list(q.get("options", []))
            explanation = str(q.get("explanation", "")).strip()

            # Если нет вариантов — делаем заглушки
            if not options:
                options = ["Вариант 1", "Вариант 2", "Вариант 3", "Вариант 4"]
                correct_idx = 0
            else:
                # Удалим дубликаты, сохраняя порядок
                seen = set()
                deduped = []
                for opt in options:
                    if opt not in seen:
                        seen.add(opt)
                        deduped.append(opt)
                options = deduped

                # Определим текст правильного ответа
                try:
                    original_correct_idx = int(q.get("correct", 0))
                except Exception:
                    original_correct_idx = 0
                original_correct_idx = max(0, min(original_correct_idx, len(options) - 1))
                correct_text = options[original_correct_idx] if options else "Вариант 1"

                # Приводим к ровно 4 вариантам (не теряя правильный)
                if len(options) < 4:
                    i = 1
                    while len(options) < 4:
                        filler = f"Вариант {i}"
                        if filler not in options:
                            options.append(filler)
                        i += 1
                elif len(options) > 4:
                    # Сохраним правильный + случайные 3 из остальных
                    others = [o for o in options if o != correct_text]
                    if len(others) < 3:
                        # если вдруг из-за дубликатов осталось мало — докинем заглушки
                        i = 1
                        while len(others) < 3:
                            filler = f"Вариант {i}"
                            if filler != correct_text and filler not in others:
                                others.append(filler)
                            i += 1
                    # Выбираем 3 случайных отвлекающих
                    picked = self.rng.sample(others, 3)
                    options = [correct_text] + picked

                # Пересчитаем корректный индекс относительно новых options (правильный всегда в списке)
                correct_idx = options.index(correct_text)

            self.questions.append({
                "question": question,
                "options": options,
                "correct": correct_idx,
                "explanation": explanation
            })

        print(f"Загружено и нормализовано вопросов: {len(self.questions)}")

    def get_random_question(self):
        """
        Возвращает НОВЫЙ объект вопроса:
        - варианты случайно перемешаны
        - индекс correct пересчитан под новую раскладку
        """
        if not self.questions:
            self.load_questions()

        base = self.rng.choice(self.questions)
        # Делаем копию и мешаем только копию
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

# ---------- UI ----------
class Button:
    def __init__(self, x, y, width, height, text, action=None, font_size=24):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.is_hovered = False
        self.font = pygame.font.SysFont('consolas', font_size, bold=True)

    def draw(self, surface):
        color = BUTTON_HOVER_COLOR if self.is_hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, HIGHLIGHT_COLOR, self.rect, 2, border_radius=8)
        # <<< ВЕРНУЛ ОТРИСОВКУ ТЕКСТА >>>
        text_surf = self.font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)

    def check_click(self, pos):
        if self.rect.collidepoint(pos) and self.action:
            return self.action
        return None


class MainMenu:
    def __init__(self, screen, game_data):
        self.screen = screen
        self.game_data = game_data
        self.title_font = pygame.font.SysFont('consolas', 48, bold=True)
        self.font = pygame.font.SysFont('consolas', 32)
        self.small_font = pygame.font.SysFont('consolas', 24)
        w, h = 300, 60; cx = SCREEN_WIDTH // 2 - w // 2
        self.start_button = Button(cx, 300, w, h, "Начать игру", "start")
        self.achievements_button = Button(cx, 380, w, h, "Достижения", "achievements")
        self.quit_button = Button(cx, 460, w, h, "Выход", "quit")
        self.current_screen = "main"

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == QUIT: return "quit"
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                if self.current_screen == "achievements": self.current_screen = "main"
                else: return "quit"
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if self.current_screen == "main":
                    r = self.start_button.check_click(mouse_pos)
                    if r == "start": return "start"
                    r = self.achievements_button.check_click(mouse_pos)
                    if r == "achievements": self.current_screen = "achievements"
                    r = self.quit_button.check_click(mouse_pos)
                    if r == "quit": return "quit"
                elif self.current_screen == "achievements":
                    self.current_screen = "main"
        if self.current_screen == "main":
            self.start_button.check_hover(mouse_pos)
            self.achievements_button.check_hover(mouse_pos)
            self.quit_button.check_hover(mouse_pos)
        return None

    def draw(self):
        self.screen.fill(MENU_BG)
        if self.current_screen == "main": self.draw_main_menu()
        elif self.current_screen == "achievements": self.draw_achievements()

    def draw_main_menu(self):
        title = self.title_font.render("Python Blaster", True, HIGHLIGHT_COLOR)
        subtitle = self.font.render("Code & Clear", True, TEXT_COLOR)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))
        self.screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 210))
        hs = self.small_font.render(f"Рекорд: {self.game_data.data['high_score']}", True, TEXT_COLOR)
        self.screen.blit(hs, (SCREEN_WIDTH // 2 - hs.get_width() // 2, 250))
        self.start_button.draw(self.screen); self.achievements_button.draw(self.screen); self.quit_button.draw(self.screen)
        note = self.small_font.render("Нажмите ESC для выхода", True, TEXT_COLOR)
        self.screen.blit(note, (SCREEN_WIDTH // 2 - note.get_width() // 2, 550))

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
        font = self.font
        for i, s in enumerate(stats):
            t = font.render(s, True, TEXT_COLOR)
            self.screen.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2, 120 + i * 40))
        at = font.render("Полученные достижения:", True, HIGHLIGHT_COLOR)
        self.screen.blit(at, (SCREEN_WIDTH // 2 - at.get_width() // 2, 350))
        ach = self.game_data.data["achievements"]
        items = [
            "🎮 Первая игра" if ach["first_game"] else "❓ ???",
            "🏆 500 очков" if ach["score_500"] else "❓ ???",
            "🏆 1000 очков" if ach["score_1000"] else "❓ ???",
            "🏆 2000 очков" if ach["score_2000"] else "❓ ???",
            "📊 10 линий" if ach["clear_10_lines"] else "❓ ???",
            "📊 25 линий" if ach["clear_25_lines"] else "❓ ???",
            "❓ 5 вопросов" if ach["answer_5_questions"] else "❓ ???",
            "❓ 10 вопросов" if ach["answer_10_questions"] else "❓ ???",
            "💻 5 код-баттлов" if ach["complete_5_code_battles"] else "❓ ???",
            "💻 10 код-баттлов" if ach["complete_10_code_battles"] else "❓ ???"
        ]
        small = self.small_font
        for i, it in enumerate(items):
            col = CORRECT_COLOR if "❓" not in it else (100, 100, 100)
            t = small.render(it, True, col)
            x = SCREEN_WIDTH // 2 - 150 + (i % 2) * 300
            y = 400 + (i // 2) * 30
            self.screen.blit(t, (x, y))
        back = small.render("Нажмите для возврата", True, TEXT_COLOR)
        self.screen.blit(back, (SCREEN_WIDTH // 2 - back.get_width() // 2, 550))


# ---------- Игра ----------
class Game:
    def __init__(self, game_data):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Python Blaster: Code & Clear")
        self.clock = pygame.time.Clock()
        self.title_font = pygame.font.SysFont('consolas', 36, bold=True)
        self.font = pygame.font.SysFont('consolas', 24)
        self.small_font = pygame.font.SysFont('consolas', 18)

        self.board = GameBoard()
        self.quiz_engine = QuizEngine()
        self.code_battle = CodeBattle()
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

        self.quiz_timer = 0
        self.quiz_interval = 5
        self.code_battle_interval = 5
        self.last_event_lines = 0

        self.panel_rect = pygame.Rect(50, 150, 300, 400)

    def deal_needed_shape(self) -> "Shape":
        return smart_deal_shape(self.board, self.difficulty)

    def handle_events(self) -> str:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == QUIT: return "quit"
            if event.type == KEYDOWN and event.key == K_ESCAPE: return "menu"

            if self.game_over:
                if event.type == KEYDOWN and (event.key == K_r or event.key == K_SPACE): return "menu"
                continue

            if self.show_code_battle:
                if self.code_battle.handle_input(event): continue
                if event.type == KEYDOWN and event.key == pygame.K_h:
                    self.code_battle.next_hint(); continue
                if event.type == KEYDOWN and self.code_battle.result:
                    self.show_code_battle = False; self.code_battle.result = None
                continue

            if self.show_quiz:
                if self.quiz_result:
                    if event.type == MOUSEBUTTONDOWN or (event.type == KEYDOWN and event.key != K_r):
                        self.quiz_result = None; self.show_quiz = False; self.current_question = None
                elif event.type == KEYDOWN and event.key in [K_1, K_2, K_3, K_4]:
                    self.check_quiz_answer(event.key - K_1)
                continue

            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for i, shape in enumerate(self.current_shapes):
                    sx, sy = self.get_shape_panel_position(i, shape)
                    srect = pygame.Rect(sx, sy, shape.width * PANEL_CELL_SIZE, shape.height * PANEL_CELL_SIZE)
                    if srect.collidepoint(mx, my):
                        self.dragging = True; self.dragged_shape = shape; self.dragged_shape_index = i
                        self.drag_offset_x = mx - srect.x; self.drag_offset_y = my - srect.y
                        self.ghost_position = None; self.snap_position = None
                        break

            elif event.type == MOUSEBUTTONUP and event.button == 1:
                if self.dragging and self.dragged_shape:
                    mx, my = event.pos
                    if self.panel_rect.collidepoint(mx, my):
                        pass
                    else:
                        pos = self.snap_position if self.snap_position is not None else self.ghost_position
                        if pos is None:
                            gx = (mx - GRID_OFFSET_X - self.drag_offset_x) // CELL_SIZE
                            gy = (my - GRID_OFFSET_Y - self.drag_offset_y) // CELL_SIZE
                        else:
                            gx, gy = pos
                        gx = max(0, min(GRID_SIZE - self.dragged_shape.width, gx))
                        gy = max(0, min(GRID_SIZE - self.dragged_shape.height, gy))

                        if self.board.place_shape(self.dragged_shape, gx, gy, self.particle_system):
                            if self.dragged_shape_index is not None:
                                if self.board.score > 1000: self.difficulty = "hard"
                                elif self.board.score > 500: self.difficulty = "normal"
                                # выдаём новую фигуру через дилера
                                self.current_shapes[self.dragged_shape_index] = self.deal_needed_shape()

                            self.lines_cleared_this_game = self.board.lines_cleared
                            if (self.board.lines_cleared >= self.last_event_lines + self.code_battle_interval and
                                self.board.lines_cleared > 0):
                                self.last_event_lines = self.board.lines_cleared
                                if random.random() < 0.5:
                                    self.show_code_battle = True; self.code_battle.start_battle()
                                else:
                                    self.show_quiz = True; self.current_question = self.quiz_engine.get_random_question()

                    self.dragging = False; self.dragged_shape = None; self.dragged_shape_index = None
                    self.ghost_position = None; self.snap_position = None

            elif event.type == MOUSEMOTION:
                if self.dragging and self.dragged_shape:
                    mx, my = event.pos
                    gx = (mx - GRID_OFFSET_X - self.drag_offset_x) // CELL_SIZE
                    gy = (my - GRID_OFFSET_Y - self.drag_offset_y) // CELL_SIZE
                    gx = max(0, min(GRID_SIZE - self.dragged_shape.width, gx))
                    gy = max(0, min(GRID_SIZE - self.dragged_shape.height, gy))
                    if not self.board.can_place_shape(self.dragged_shape, gx, gy):
                        self.snap_position = self.find_nearby_placement(gx, gy)
                        self.ghost_position = self.snap_position if self.snap_position is not None else None
                    else:
                        self.ghost_position = (gx, gy); self.snap_position = None

            elif event.type == KEYDOWN:
                if event.key == K_r:
                    # оставим как было — случайная замена (может помочь или навредить)
                    self.current_shapes = [Shape(difficulty=self.difficulty) for _ in range(3)]

        return None

    def get_shape_panel_position(self, index: int, shape: Shape) -> Tuple[int, int]:
        panel_x, panel_y, panel_w, panel_h = self.panel_rect.x, self.panel_rect.y, self.panel_rect.width, self.panel_rect.height
        slot_h = panel_h // 3
        y = panel_y + index * slot_h + (slot_h - shape.height * PANEL_CELL_SIZE) // 2
        x = panel_x + (panel_w - shape.width * PANEL_CELL_SIZE) // 2
        return x, y

    def find_nearby_placement(self, x: int, y: int, radius: int = 2) -> Optional[Tuple[int, int]]:
        if self.dragged_shape is None: return None
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                tx, ty = x + dx, y + dy
                if 0 <= tx <= GRID_SIZE - self.dragged_shape.width and 0 <= ty <= GRID_SIZE - self.dragged_shape.height:
                    if self.board.can_place_shape(self.dragged_shape, tx, ty): return (tx, ty)
        return self.board.find_best_placement(self.dragged_shape)

    def check_quiz_answer(self, answer_index: int) -> None:
        if not self.current_question: return
        self.questions_answered_this_game += 1
        if answer_index == self.current_question["correct"]:
            self.quiz_result = {"correct": True, "message": "ПРАВИЛЬНО!", "color": CORRECT_COLOR}
            self.correct_answers_this_game += 1; self.board.score += 50
        else:
            self.quiz_result = {"correct": False, "message": "НЕПРАВИЛЬНО!", "explanation": self.current_question["explanation"], "color": WRONG_COLOR}

    def reset_game(self) -> None:
        self.board.reset()
        self.current_shapes = [Shape(difficulty="easy") for _ in range(3)]
        self.game_over = False; self.show_quiz = False; self.show_code_battle = False
        self.quiz_result = None; self.dragging = False; self.dragged_shape = None; self.dragged_shape_index = None
        self.ghost_position = None; self.snap_position = None; self.quiz_timer = 0; self.bonus_active = None
        self.difficulty = "easy"
        self.questions_answered_this_game = 0; self.correct_answers_this_game = 0
        self.lines_cleared_this_game = 0; self.code_battles_completed_this_game = 0
        self.last_event_lines = 0; self.particle_system.particles.clear()

    def draw(self) -> None:
        self.screen.fill(BACKGROUND)
        self.particle_system.update()

        title = self.title_font.render("Python Blaster: Code & Clear", True, TEXT_COLOR)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 20))
        self.board.draw(self.screen)

        if self.dragging and self.dragged_shape and self.ghost_position is not None:
            gx, gy = self.ghost_position
            self.dragged_shape.draw(self.screen, GRID_OFFSET_X + gx * CELL_SIZE, GRID_OFFSET_Y + gy * CELL_SIZE, is_ghost=True)

        pygame.draw.rect(self.screen, PANEL_BG, self.panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, GRID_HIGHLIGHT, self.panel_rect, 2, border_radius=10)
        panel_title = self.font.render("Доступные фигуры:", True, TEXT_COLOR)
        self.screen.blit(panel_title, (self.panel_rect.x + 10, 120))

        for i, shape in enumerate(self.current_shapes):
            if self.dragging and i == self.dragged_shape_index: continue
            sx, sy = self.get_shape_panel_position(i, shape)
            shape.draw(self.screen, sx, sy, in_panel=True)

        if self.dragging and self.dragged_shape:
            mx, my = pygame.mouse.get_pos()
            dx = mx - self.drag_offset_x; dy = my - self.drag_offset_y
            valid = False
            if self.ghost_position is not None:
                gx, gy = self.ghost_position; valid = self.board.can_place_shape(self.dragged_shape, gx, gy)
            self.dragged_shape.draw(self.screen, dx, dy, alpha=200, show_placement_hint=True, valid_placement=valid)

        score_panel = pygame.Rect(SCREEN_WIDTH - 280, 120, 250, 120)
        pygame.draw.rect(self.screen, PANEL_BG, score_panel, border_radius=10)
        pygame.draw.rect(self.screen, GRID_HIGHLIGHT, score_panel, 2, border_radius=10)
        score_text = self.font.render(f"Счет: {self.board.score}", True, TEXT_COLOR)
        lines_text = self.font.render(f"Линии: {self.board.lines_cleared}", True, TEXT_COLOR)
        next_event = max(0, self.last_event_lines + self.code_battle_interval - self.board.lines_cleared)
        next_event_text = self.small_font.render(f"След. событие: {next_event}", True, TEXT_COLOR)
        diff_text = self.small_font.render(f"Сложность: {self.difficulty}", True, TEXT_COLOR)
        self.screen.blit(score_text, (SCREEN_WIDTH - 260, 140))
        self.screen.blit(lines_text, (SCREEN_WIDTH - 260, 170))
        self.screen.blit(next_event_text, (SCREEN_WIDTH - 260, 200))
        self.screen.blit(diff_text, (SCREEN_WIDTH - 260, 220))

        instr_panel = pygame.Rect(SCREEN_WIDTH - 280, 260, 250, 180)
        pygame.draw.rect(self.screen, PANEL_BG, instr_panel, border_radius=10)
        pygame.draw.rect(self.screen, GRID_HIGHLIGHT, instr_panel, 2, border_radius=10)
        instructions = ["Управление:", "Клик и перетаскивание", "ESC - в меню", ""]
        for i, line in enumerate(instructions):
            t = self.small_font.render(line, True, TEXT_COLOR)
            self.screen.blit(t, (SCREEN_WIDTH - 260, 280 + i * 25))

        self.particle_system.draw(self.screen)

        if self.show_code_battle:
            self.code_battle.update_timer()
            self.code_battle.draw(self.screen, self.particle_system)

        if self.show_quiz and self.current_question:
            if self.quiz_result: self.draw_quiz_result()
            else: self.draw_quiz()

        if self.game_over: self.draw_game_over()
        pygame.display.flip()

    def draw_quiz(self) -> None:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200)); self.screen.blit(overlay, (0, 0))
        rect = pygame.Rect(200, 150, 1000, 400)
        pygame.draw.rect(self.screen, PANEL_BG, rect, border_radius=15)
        pygame.draw.rect(self.screen, HIGHLIGHT_COLOR, rect, 3, border_radius=15)
        title = self.font.render("Вопрос по Python:", True, TEXT_COLOR)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 180))
        lines = self.wrap_text(self.current_question["question"], 740)
        for i, line in enumerate(lines):
            t = self.small_font.render(line, True, TEXT_COLOR)
            self.screen.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2, 220 + i * 25))
        y = 220 + len(lines) * 25 + 20
        for i, opt in enumerate(self.current_question["options"]):
            t = self.small_font.render(f"{i + 1}. {opt}", True, TEXT_COLOR)
            self.screen.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2, y + i * 30))
        tip = self.small_font.render("Нажмите 1-4 для выбора ответа", True, TEXT_COLOR)
        self.screen.blit(tip, (SCREEN_WIDTH // 2 - tip.get_width() // 2, y + 150))

    def draw_quiz_result(self) -> None:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200)); self.screen.blit(overlay, (0, 0))
        rect = pygame.Rect(300, 200, 800, 300)
        pygame.draw.rect(self.screen, PANEL_BG, rect, border_radius=15)
        pygame.draw.rect(self.screen, self.quiz_result["color"], rect, 3, border_radius=15)
        txt = self.title_font.render(self.quiz_result["message"], True, self.quiz_result["color"])
        self.screen.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2, 250))
        if not self.quiz_result["correct"]:
            expl = self.wrap_text(self.quiz_result["explanation"], 550)
            for i, line in enumerate(expl):
                t = self.small_font.render(line, True, TEXT_COLOR)
                self.screen.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2, 320 + i * 25))
        tip = self.small_font.render("Нажмите любую клавишу чтобы продолжить", True, TEXT_COLOR)
        self.screen.blit(tip, (SCREEN_WIDTH // 2 - tip.get_width() // 2, 450))

    def draw_game_over(self) -> None:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220)); self.screen.blit(overlay, (0, 0))
        panel = pygame.Rect(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 150, 400, 300)
        pygame.draw.rect(self.screen, PANEL_BG, panel, border_radius=15)
        pygame.draw.rect(self.screen, (231, 76, 60), panel, 3, border_radius=15)
        title = self.title_font.render("ИГРА ОКОНЧЕНА", True, (231, 76, 60))
        sc = self.font.render(f"Финальный счет: {self.board.score}", True, TEXT_COLOR)
        ln = self.font.render(f"Очищено линий: {self.board.lines_cleared}", True, TEXT_COLOR)
        hs = self.font.render(f"Рекорд: {self.game_data.data['high_score']}", True, TEXT_COLOR)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
        self.screen.blit(sc, (SCREEN_WIDTH // 2 - sc.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
        self.screen.blit(ln, (SCREEN_WIDTH // 2 - ln.get_width() // 2, SCREEN_HEIGHT // 2 - 10))
        self.screen.blit(hs, (SCREEN_WIDTH // 2 - hs.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        self.particle_system.add_effect("game_over", cx, cy)
        tip = self.small_font.render("Нажмите R или SPACE для возврата в меню", True, TEXT_COLOR)
        self.screen.blit(tip, (SCREEN_WIDTH // 2 - tip.get_width() // 2, SCREEN_HEIGHT // 2 + 70))

    def wrap_text(self, text: str, max_width: int) -> List[str]:
        words = text.split(' '); lines: List[str] = []; cur: List[str] = []
        for w in words:
            t = ' '.join(cur + [w]); wdt = self.small_font.size(t)[0]
            if wdt <= max_width: cur.append(w)
            else: lines.append(' '.join(cur)); cur = [w]
        if cur: lines.append(' '.join(cur))
        return lines

    def update(self) -> None:
        can_place_any = any(self.board.find_best_placement(s) is not None for s in self.current_shapes)
        if not can_place_any and not self.game_over:
            self.game_over = True
            self.game_data.add_game_session(
                self.board.score, self.lines_cleared_this_game,
                self.questions_answered_this_game, self.correct_answers_this_game,
                self.code_battles_completed_this_game
            )

    def run(self) -> str:
        while True:
            result = self.handle_events()
            if result: return result
            self.update(); self.draw(); self.clock.tick(FPS)


# ---------- Main ----------
def main():
    pygame.init()
    game_data = GameData()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Python Blaster: Code & Clear")
    menu = MainMenu(screen, game_data)
    current = "menu"
    while True:
        if current == "menu":
            r = menu.handle_events()
            if r == "start": current = "game"
            elif r == "quit": break
            menu.draw(); pygame.display.flip()
        elif current == "game":
            game = Game(game_data)
            r = game.run()
            if r == "menu": current = "menu"
            elif r == "quit": break
    pygame.quit(); sys.exit()


if __name__ == "__main__":
    main()
