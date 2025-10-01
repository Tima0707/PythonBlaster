import pygame
import sys
import random
import json
import os
import time
import math
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime

from pygame import K_DOWN
from pygame.locals import (
    QUIT, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION,
    KEYDOWN, K_r, K_1, K_2, K_3, K_4, K_SPACE, K_ESCAPE,
    K_RETURN, K_BACKSPACE, K_TAB, K_HOME, K_END, K_UP, K_RIGHT, K_LEFT
)

# Константы - увеличенные размеры
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 700
GRID_SIZE = 8
CELL_SIZE = 60
GRID_OFFSET_X = 600
GRID_OFFSET_Y = 100
PANEL_CELL_SIZE = 35
FPS = 60

# Цвета — спокойная синяя палитра с лёгкими неоновыми акцентами
BACKGROUND_TOP = (10, 18, 32)
BACKGROUND_BOTTOM = (8, 24, 46)
MENU_BACKGROUND_TOP = (12, 24, 40)
MENU_BACKGROUND_BOTTOM = (9, 20, 34)
NEON_ACCENT = (70, 160, 240)
NEON_SECONDARY = (58, 132, 210)
GRID_COLOR = (40, 72, 110)
GRID_HIGHLIGHT = (90, 170, 240)
GRID_BACKGROUND = (18, 30, 52)
CELL_COLORS = [
    (42, 92, 150),
    (48, 110, 170),
    (34, 86, 140),
    (52, 102, 160),
    (60, 120, 178),
    (46, 96, 150),
    (54, 108, 168),
]
TEXT_COLOR = (222, 230, 242)
HIGHLIGHT_COLOR = NEON_ACCENT
VALID_PLACEMENT_COLOR = NEON_ACCENT
INVALID_PLACEMENT_COLOR = (130, 70, 200)
GHOST_ALPHA = 135
PANEL_BG = (20, 32, 54)
BUTTON_COLOR = (32, 80, 140)
BUTTON_HOVER_COLOR = (44, 110, 170)
CORRECT_COLOR = NEON_ACCENT
WRONG_COLOR = (140, 90, 200)
MENU_BG = MENU_BACKGROUND_BOTTOM
CODE_EDITOR_BG = (16, 28, 48)
CODE_EDITOR_TEXT = (220, 228, 240)
CODE_LINE_NUMBERS = (110, 134, 168)


def lighten_color(color: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
    """Осветляет цвет на заданный коэффициент."""
    factor = max(0.0, min(1.0, factor))
    return tuple(int(c + (255 - c) * factor) for c in color)


def darken_color(color: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
    """Затемняет цвет на заданный коэффициент."""
    factor = max(0.0, min(1.0, factor))
    return tuple(int(c * (1 - factor)) for c in color)


_gradient_cache: Dict[Tuple[int, int, Tuple[int, int, int], Tuple[int, int, int]], pygame.Surface] = {}


def get_vertical_gradient(size: Tuple[int, int], top_color: Tuple[int, int, int],
                          bottom_color: Tuple[int, int, int]) -> pygame.Surface:
    """Возвращает вертикальный градиент с кэшированием."""
    key = (size[0], size[1], top_color, bottom_color)
    cached = _gradient_cache.get(key)
    if cached and cached.get_size() == size:
        return cached

    width, height = size
    gradient = pygame.Surface((width, height), pygame.SRCALPHA)
    if height <= 1:
        gradient.fill((*top_color, 255))
    else:
        for y in range(height):
            ratio = y / (height - 1)
            color = tuple(
                int(top_color[i] + (bottom_color[i] - top_color[i]) * ratio)
                for i in range(3)
            )
            pygame.draw.line(gradient, (*color, 255), (0, y), (width, y))

    _gradient_cache[key] = gradient
    return gradient


def draw_glow(surface: pygame.Surface, rect: pygame.Rect, color: Tuple[int, int, int],
              spread: int = 10, max_alpha: int = 55, border_radius: int = 12) -> None:
    """Рисует мягкое свечение вокруг прямоугольника."""
    if spread <= 0 or max_alpha <= 0:
        return

    glow_surface = pygame.Surface((rect.width + spread * 2, rect.height + spread * 2), pygame.SRCALPHA)
    for i in range(spread, 0, -1):
        alpha = int(max_alpha * (i / spread) ** 2)
        if alpha <= 0:
            continue
        inflate = int(i * 1.5)
        glow_rect = pygame.Rect(spread - i, spread - i,
                                rect.width + inflate, rect.height + inflate)
        pygame.draw.rect(
            glow_surface,
            (*color, alpha),
            glow_rect,
            border_radius=max(0, border_radius + max(0, i // 3))
        )
    surface.blit(glow_surface, (rect.x - spread, rect.y - spread), special_flags=pygame.BLEND_ADD)


def draw_neon_panel(surface: pygame.Surface, rect: pygame.Rect, border_radius: int = 12,
                    top_color: Optional[Tuple[int, int, int]] = None,
                    bottom_color: Optional[Tuple[int, int, int]] = None,
                    glow_color: Tuple[int, int, int] = NEON_ACCENT) -> None:
    """Рисует панель с градиентом и неоновым свечением."""
    draw_glow(surface, rect, glow_color, spread=12, max_alpha=50, border_radius=border_radius + 6)
    panel_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
    top = top_color or lighten_color(PANEL_BG, 0.2)
    bottom = bottom_color or darken_color(PANEL_BG, 0.1)
    panel_surface.blit(get_vertical_gradient(rect.size, top, bottom), (0, 0))

    pygame.draw.rect(panel_surface, (*glow_color, 110), panel_surface.get_rect(),
                     2, border_radius=border_radius)
    inner_rect = panel_surface.get_rect().inflate(-10, -10)
    if inner_rect.width > 0 and inner_rect.height > 0:
        pygame.draw.rect(panel_surface, (*glow_color, 28), inner_rect,
                         border_radius=max(0, border_radius - 5))

    surface.blit(panel_surface, rect.topleft)


def draw_dynamic_background(surface: pygame.Surface, top_color: Tuple[int, int, int],
                            bottom_color: Tuple[int, int, int],
                            accent_color: Tuple[int, int, int]) -> None:
    """Рисует динамический фон с мягким градиентом и деликатными световыми линиями."""
    width, height = surface.get_size()
    surface.blit(get_vertical_gradient((width, height), top_color, bottom_color), (0, 0))

    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    phase = pygame.time.get_ticks() / 1000.0
    spacing = 200
    shift = (phase * 25) % spacing

    for x in range(-height, width + spacing, spacing):
        start = (x + shift, 0)
        end = (x + height + shift, height)
        alpha = int(18 + 16 * math.sin((x / spacing) + phase))
        pygame.draw.line(overlay, (*accent_color, alpha), start, end, 1)

    pulse = 0.45 + 0.35 * math.sin(phase)
    glow_centers = [
        (width * 0.25, height * 0.3),
        (width * 0.75, height * 0.7)
    ]
    for cx, cy in glow_centers:
        radius = int(120 + 25 * pulse)
        glow_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        for r in range(radius, 0, -14):
            alpha = int(28 * (r / radius) ** 2)
            pygame.draw.circle(glow_surface, (*accent_color, alpha), (radius, radius), r)
        surface.blit(glow_surface, (int(cx - radius), int(cy - radius)), special_flags=pygame.BLEND_ADD)

    surface.blit(overlay, (0, 0), special_flags=pygame.BLEND_ADD)


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
            "line_clear": {"count": 50, "colors": [(0, 210, 255), (0, 170, 255), (80, 200, 255)]},
            "shape_place": {"count": 25, "colors": [(0, 190, 255), (0, 150, 255), (40, 120, 255)]},
            "combo": {"count": 80, "colors": [(0, 200, 255), (80, 180, 255), (160, 220, 255)]},
            "code_success": {"count": 100, "colors": [(0, 230, 255), (60, 210, 255), (140, 230, 255)]},
            "game_over": {"count": 150, "colors": [(0, 120, 255), (0, 80, 200), (0, 40, 140)]}
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


class GameData:
    """Класс для управления данными игры с улучшенной системой хранения"""

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
        """Загружает данные из файла с улучшенной обработкой ошибок"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    self._update_dict_recursive(self.data, loaded_data)
            else:
                os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
                self.save_data()
        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")
            self.data = self.default_data.copy()
            self.save_data()

    def _update_dict_recursive(self, target, source):
        """Рекурсивно обновляет словарь, сохраняя структуру целевого"""
        for key, value in target.items():
            if key in source:
                if isinstance(value, dict) and isinstance(source[key], dict):
                    self._update_dict_recursive(value, source[key])
                else:
                    target[key] = source[key]

    def save_data(self):
        """Сохраняет данные в файл с временной меткой"""
        try:
            self.data["last_played"] = datetime.now().isoformat()
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения данных: {e}")

    def update_high_score(self, score):
        """Обновляет рекорд"""
        if score > self.data["high_score"]:
            self.data["high_score"] = score
            self.save_data()
            return True
        return False

    def update_achievements(self, game_stats):
        """Обновляет достижения на основе статистики игры"""
        updated = False

        if game_stats["score"] >= 500 and not self.data["achievements"]["score_500"]:
            self.data["achievements"]["score_500"] = True
            updated = True
        if game_stats["score"] >= 1000 and not self.data["achievements"]["score_1000"]:
            self.data["achievements"]["score_1000"] = True
            updated = True
        if game_stats["score"] >= 2000 and not self.data["achievements"]["score_2000"]:
            self.data["achievements"]["score_2000"] = True
            updated = True

        if game_stats["lines_cleared"] >= 10 and not self.data["achievements"]["clear_10_lines"]:
            self.data["achievements"]["clear_10_lines"] = True
            updated = True
        if game_stats["lines_cleared"] >= 25 and not self.data["achievements"]["clear_25_lines"]:
            self.data["achievements"]["clear_25_lines"] = True
            updated = True

        if self.data["total_questions_answered"] >= 5 and not self.data["achievements"]["answer_5_questions"]:
            self.data["achievements"]["answer_5_questions"] = True
            updated = True
        if self.data["total_questions_answered"] >= 10 and not self.data["achievements"]["answer_10_questions"]:
            self.data["achievements"]["answer_10_questions"] = True
            updated = True

        if self.data["total_code_battles_completed"] >= 5 and not self.data["achievements"]["complete_5_code_battles"]:
            self.data["achievements"]["complete_5_code_battles"] = True
            updated = True
        if self.data["total_code_battles_completed"] >= 10 and not self.data["achievements"][
            "complete_10_code_battles"]:
            self.data["achievements"]["complete_10_code_battles"] = True
            updated = True

        if not self.data["achievements"]["first_game"]:
            self.data["achievements"]["first_game"] = True
            updated = True

        if updated:
            self.save_data()

        return updated

    def add_game_session(self, score, lines_cleared, questions_answered, correct_answers, code_battles_completed=0):
        """Добавляет статистику игровой сессии с записью даты"""
        session_data = {
            "date": datetime.now().isoformat(),
            "score": score,
            "lines_cleared": lines_cleared,
            "questions_answered": questions_answered,
            "correct_answers": correct_answers,
            "code_battles_completed": code_battles_completed
        }

        if not any(s.get("date") == session_data["date"] for s in self.data["game_sessions"]):
            self.data["games_played"] += 1
            self.data["total_lines_cleared"] += lines_cleared
            self.data["total_questions_answered"] += questions_answered
            self.data["total_correct_answers"] += correct_answers
            self.data["total_code_battles_completed"] += code_battles_completed
            self.data["game_sessions"].append(session_data)

            if len(self.data["game_sessions"]) > 50:
                self.data["game_sessions"] = self.data["game_sessions"][-50:]

            self.update_high_score(score)

            game_stats = {
                "score": score,
                "lines_cleared": lines_cleared,
                "questions_answered": questions_answered,
                "correct_answers": correct_answers
            }

            self.update_achievements(game_stats)
            self.save_data()


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
                "hints": [
                    "Просто сложите a и b",
                    "Используйте оператор +",
                    "Не забудьте вернуть результат"
                ]
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
                "hints": [
                    "Факториал 0 равен 1",
                    "Используйте рекурсию или цикл",
                    "Для рекурсии: factorial(n) = n * factorial(n-1)"
                ]
            },
            {
                "name": "Палиндром",
                "description": "Напишите функцию, которая проверяет, является ли строка палиндромом",
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
                "hints": [
                    "Уберите пробелы и приведите к нижнему регистру",
                    "Сравните строку с её перевернутой версией",
                    "Можно использовать срезы: s[::-1]"
                ]
            },
            {
                "name": "Числа Фибоначчи",
                "description": "Напишите функцию, которая возвращает n-ное число Фибоначчи",
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
                "hints": [
                    "F(0) = 0, F(1) = 1",
                    "F(n) = F(n-1) + F(n-2)",
                    "Используйте цикл или рекурсию с мемоизацией"
                ]
            }
        ]
        self.current_challenge = None
        self.player_code = ""
        self.start_time = 0
        self.time_left = 0
        self.result = None
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_position = 0  # Позиция курсора в тексте
        self.code_font = pygame.font.SysFont('consolas', 20)
        self.line_height = 25
        self.scroll_offset = 0
        self.show_autocomplete = False
        self.autocomplete_options = []
        self.autocomplete_index = 0
        self.current_hint = 0

        # Ключевые слова Python для автодополнения
        self.keywords = ["def", "return", "if", "else", "elif", "for", "while",
                         "in", "range", "len", "str", "int", "float", "list",
                         "dict", "True", "False", "None", "and", "or", "not"]

        # Кнопка отправки
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

            # Мигающий курсор
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
            # Ctrl+Enter для отправки
            if event.key == K_RETURN and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                self.submit_solution()
                return True

            # Tab для отступа или автодополнения
            elif event.key == K_TAB:
                if self.show_autocomplete and self.autocomplete_options:
                    # Применяем автодополнение
                    self.apply_autocomplete()
                else:
                    # Вставляем 4 пробела вместо табуляции
                    code_before = self.player_code[:self.cursor_position]
                    code_after = self.player_code[self.cursor_position:]
                    self.player_code = code_before + "    " + code_after
                    self.cursor_position += 4
                return True

            # Стрелки для навигации по автодополнению
            elif event.key == K_DOWN and self.show_autocomplete:
                self.autocomplete_index = (self.autocomplete_index + 1) % len(self.autocomplete_options)
                return True
            elif event.key == K_UP and self.show_autocomplete:
                self.autocomplete_index = (self.autocomplete_index - 1) % len(self.autocomplete_options)
                return True

            # Enter для выбора автодополнения
            elif event.key == K_RETURN and self.show_autocomplete:
                self.apply_autocomplete()
                return True

            # Обычный Enter (без автодополнения)
            elif event.key == K_RETURN:
                code_before = self.player_code[:self.cursor_position]
                code_after = self.player_code[self.cursor_position:]
                self.player_code = code_before + '\n' + code_after
                self.cursor_position += 1
                return True

            # Backspace
            elif event.key == K_BACKSPACE:
                if self.cursor_position > 0:
                    code_before = self.player_code[:self.cursor_position - 1]
                    code_after = self.player_code[self.cursor_position:]
                    self.player_code = code_before + code_after
                    self.cursor_position -= 1
                    # Проверяем автодополнение после удаления символа
                    self.check_autocomplete()
                return True

            # Стрелки для перемещения курсора
            elif event.key == K_LEFT:
                self.cursor_position = max(0, self.cursor_position - 1)
                self.show_autocomplete = False  # Скрываем автодополнение при перемещении курсора
                return True
            elif event.key == K_RIGHT:
                self.cursor_position = min(len(self.player_code), self.cursor_position + 1)
                self.show_autocomplete = False  # Скрываем автодополнение при перемещении курсора
                return True
            elif event.key == K_UP and not self.show_autocomplete:
                # Перемещение на строку вверх (упрощенная версия)
                lines = self.player_code[:self.cursor_position].split('\n')
                if len(lines) > 1:
                    current_line_len = len(lines[-1])
                    prev_line_len = len(lines[-2])
                    new_pos = self.cursor_position - len(lines[-1]) - 1 - max(0, len(lines[-1]) - prev_line_len)
                    self.cursor_position = max(0, new_pos)
                return True
            elif event.key == K_DOWN and not self.show_autocomplete:
                # Перемещение на строку вниз (упрощенная версия)
                lines = self.player_code[:self.cursor_position].split('\n')
                remaining = self.player_code[self.cursor_position:].split('\n', 1)
                if len(remaining) > 1:
                    current_line_len = len(lines[-1])
                    next_line_len = len(remaining[0])
                    new_pos = self.cursor_position + len(remaining[0]) + 1 + max(0, current_line_len - next_line_len)
                    self.cursor_position = min(len(self.player_code), new_pos)
                return True

            # Home и End
            elif event.key == K_HOME:
                # Перемещение в начало строки
                lines = self.player_code[:self.cursor_position].split('\n')
                self.cursor_position -= len(lines[-1])
                return True
            elif event.key == K_END:
                # Перемещение в конец строки
                lines = self.player_code[:self.cursor_position].split('\n')
                remaining = self.player_code[self.cursor_position:].split('\n', 1)
                if remaining:
                    self.cursor_position += len(remaining[0])
                return True

            # Пробел и другие символы
            elif event.unicode.isprintable():
                code_before = self.player_code[:self.cursor_position]
                code_after = self.player_code[self.cursor_position:]
                self.player_code = code_before + event.unicode + code_after
                self.cursor_position += 1

                # Проверяем автодополнение
                self.check_autocomplete()
                return True

        elif event.type == MOUSEBUTTONDOWN:
            # Обработка клика по кнопке отправки
            if self.submit_button_rect.collidepoint(event.pos):
                self.submit_solution()
                return True

            # Обработка клика по коду для установки курсора
            code_rect = pygame.Rect(120, 200, SCREEN_WIDTH - 240, 300)
            if code_rect.collidepoint(event.pos):
                # Упрощенная установка курсора по клику
                click_x, click_y = event.pos
                line_height = self.line_height
                line_num = min(len(self.player_code.split('\n')) - 1,
                               max(0, (click_y - 200) // line_height))
                lines = self.player_code.split('\n')

                # Находим приблизительную позицию в строке
                line_text = lines[line_num] if line_num < len(lines) else ""
                char_pos = min(len(line_text), max(0, (click_x - 160) // 10))

                # Вычисляем общую позицию курсора
                total_pos = sum(len(lines[i]) + 1 for i in range(line_num)) + char_pos
                self.cursor_position = min(total_pos, len(self.player_code))
                self.show_autocomplete = False  # Скрываем автодополнение при клике
                return True

        return False
    def check_autocomplete(self):
        """Проверяет, нужно ли показать автодополнение"""
        if self.cursor_position == 0:
            self.show_autocomplete = False
            return

        current_text = self.player_code[:self.cursor_position]
        last_word = ""

        # Ищем последнее слово с проверкой границ
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
        """Применяет выбранное автодополнение"""
        if not self.show_autocomplete or not self.autocomplete_options:
            return

        selected = self.autocomplete_options[self.autocomplete_index]

        # Находим начало текущего слова
        current_text = self.player_code[:self.cursor_position]
        word_start = self.cursor_position
        for i in range(self.cursor_position - 1, -1, -1):
            if i < len(current_text) and not (current_text[i].isalnum() or current_text[i] == '_'):
                word_start = i + 1
                break
            if i == 0:
                word_start = 0
                break

        # Заменяем слово
        code_before = self.player_code[:word_start]
        code_after = self.player_code[self.cursor_position:]
        self.player_code = code_before + selected + code_after
        self.cursor_position = word_start + len(selected)
        self.show_autocomplete = False

    def next_hint(self):
        """Показывает следующую подсказку"""
        if self.current_challenge and "hints" in self.current_challenge:
            self.current_hint = (self.current_hint + 1) % len(self.current_challenge["hints"])

    def safe_execute(self, code, test_cases):
        """Безопасное выполнение кода игрока"""
        safe_builtins = {
            'len': len, 'range': range, 'str': str, 'int': int, 'float': float,
            'bool': bool, 'list': list, 'tuple': tuple, 'dict': dict, 'set': set
        }

        local_vars = {}
        try:
            exec(code, {"__builtins__": safe_builtins}, local_vars)

            function = None
            for var in local_vars.values():
                if callable(var):
                    function = var
                    break

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

    def draw(self, surface, particle_system):
        if not self.current_challenge:
            return

        # Фон
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))

        # Основное окно
        battle_rect = pygame.Rect(100, 50, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 100)
        draw_neon_panel(
            surface,
            battle_rect,
            border_radius=28,
            top_color=lighten_color(CODE_EDITOR_BG, 0.4),
            bottom_color=darken_color(CODE_EDITOR_BG, 0.05),
            glow_color=NEON_SECONDARY
        )

        # Заголовок
        title_font = pygame.font.SysFont('consolas', 32, bold=True)
        title = title_font.render("КОД-БАТТЛ!", True, HIGHLIGHT_COLOR)
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 70))

        # Название задачи и описание
        challenge_font = pygame.font.SysFont('consolas', 24)
        name_text = challenge_font.render(f"Задача: {self.current_challenge['name']}", True, TEXT_COLOR)
        desc_text = self.code_font.render(self.current_challenge['description'], True, TEXT_COLOR)

        surface.blit(name_text, (battle_rect.x + 30, battle_rect.y + 70))
        surface.blit(desc_text, (battle_rect.x + 30, battle_rect.y + 100))

        # Таймер и награда
        time_text = challenge_font.render(f"Время: {int(self.time_left)} сек", True, TEXT_COLOR)
        reward_text = challenge_font.render(f"Награда: {self.current_challenge['reward']} очков", True, CORRECT_COLOR)

        surface.blit(time_text, (battle_rect.right - 260, battle_rect.y + 70))
        surface.blit(reward_text, (battle_rect.right - 260, battle_rect.y + 100))

        # Редактор кода
        code_rect = pygame.Rect(120, 200, SCREEN_WIDTH - 240, 300)
        code_surface = pygame.Surface(code_rect.size, pygame.SRCALPHA)
        code_surface.blit(
            get_vertical_gradient(code_rect.size,
                                   lighten_color(CODE_EDITOR_BG, 0.3),
                                   darken_color(CODE_EDITOR_BG, 0.1)),
            (0, 0)
        )
        pygame.draw.rect(code_surface, (*NEON_ACCENT, 140), code_surface.get_rect(), 2, border_radius=16)
        inner_code_rect = code_surface.get_rect().inflate(-10, -10)
        if inner_code_rect.width > 0 and inner_code_rect.height > 0:
            pygame.draw.rect(code_surface, (*NEON_SECONDARY, 40), inner_code_rect, border_radius=12)
        draw_glow(surface, code_rect, NEON_SECONDARY, spread=12, max_alpha=70, border_radius=20)
        surface.blit(code_surface, code_rect.topleft)

        # Отображение кода с подсветкой синтаксиса
        lines = self.player_code.split('\n')
        visible_lines = 12  # Максимальное количество видимых строк

        # Определяем диапазон строк для отображения с учетом прокрутки
        start_line = max(0, min(self.scroll_offset, len(lines) - visible_lines))
        end_line = min(len(lines), start_line + visible_lines)

        for i in range(start_line, end_line):
            line_num = i + 1
            y_pos = 210 + (i - start_line) * self.line_height

            # Номера строк
            line_num_text = self.code_font.render(str(line_num), True, CODE_LINE_NUMBERS)
            surface.blit(line_num_text, (130, y_pos))

            # Подсветка синтаксиса
            line_text = lines[i]
            tokens = self.tokenize_line(line_text)
            x_offset = 160

            for token, token_type in tokens:
                color = self.get_token_color(token_type)
                token_surface = self.code_font.render(token, True, color)
                surface.blit(token_surface, (x_offset, y_pos))
                x_offset += token_surface.get_width()

        # Курсор
        if self.cursor_visible and not self.result:
            cursor_line, cursor_col = self.get_cursor_position()
            if start_line <= cursor_line < end_line:
                cursor_x = 160 + self.code_font.size(lines[cursor_line][:cursor_col])[0]
                cursor_y = 210 + (cursor_line - start_line) * self.line_height
                pygame.draw.line(surface, CODE_EDITOR_TEXT,
                                 (cursor_x, cursor_y),
                                 (cursor_x, cursor_y + self.line_height), 2)

        # Автодополнение
        if self.show_autocomplete and self.autocomplete_options:
            autocomplete_rect = pygame.Rect(160, 210 + self.line_height, 240,
                                            len(self.autocomplete_options) * self.line_height)
            auto_surface = pygame.Surface(autocomplete_rect.size, pygame.SRCALPHA)
            auto_surface.blit(
                get_vertical_gradient(autocomplete_rect.size,
                                       lighten_color(CODE_EDITOR_BG, 0.25),
                                       darken_color(CODE_EDITOR_BG, 0.1)),
                (0, 0)
            )
            pygame.draw.rect(auto_surface, (*NEON_ACCENT, 160), auto_surface.get_rect(), 2, border_radius=10)
            surface.blit(auto_surface, autocomplete_rect.topleft)

            for i, option in enumerate(self.autocomplete_options):
                color = HIGHLIGHT_COLOR if i == self.autocomplete_index else TEXT_COLOR
                option_text = self.code_font.render(option, True, color)
                surface.blit(option_text, (
                    autocomplete_rect.x + 12,
                    autocomplete_rect.y + 6 + i * self.line_height
                ))

        # Подсказки
        if "hints" in self.current_challenge:
            hint_rect = pygame.Rect(120, 520, SCREEN_WIDTH - 240, 60)
            hint_surface = pygame.Surface(hint_rect.size, pygame.SRCALPHA)
            hint_surface.blit(
                get_vertical_gradient(hint_rect.size,
                                       lighten_color(CODE_EDITOR_BG, 0.25),
                                       darken_color(CODE_EDITOR_BG, 0.05)),
                (0, 0)
            )
            pygame.draw.rect(hint_surface, (*NEON_SECONDARY, 140), hint_surface.get_rect(), 2, border_radius=12)
            surface.blit(hint_surface, hint_rect.topleft)

            hint_text = self.code_font.render(
                f"Подсказка: {self.current_challenge['hints'][self.current_hint]}",
                True, TEXT_COLOR
            )
            surface.blit(hint_text, (hint_rect.x + 12, hint_rect.y + 12))

            hint_nav = self.code_font.render(
                f"({self.current_hint + 1}/{len(self.current_challenge['hints'])}) Нажмите H для следующей подсказки",
                True, CODE_LINE_NUMBERS
            )
            surface.blit(hint_nav, (hint_rect.x + 12, hint_rect.y + 32))

        # Кнопка отправки
        self.submit_button_rect = pygame.Rect(SCREEN_WIDTH - 320, 520, 220, 46)
        draw_neon_panel(
            surface,
            self.submit_button_rect,
            border_radius=14,
            top_color=lighten_color(BUTTON_COLOR, 0.3),
            bottom_color=darken_color(BUTTON_COLOR, 0.2)
        )

        submit_text = self.code_font.render("Отправить (Ctrl+Enter)", True, TEXT_COLOR)
        surface.blit(submit_text, (self.submit_button_rect.centerx - submit_text.get_width() // 2,
                                   self.submit_button_rect.centery - submit_text.get_height() // 2))

        # Результат
        if self.result:
            result_rect = pygame.Rect(SCREEN_WIDTH // 2 - 220, SCREEN_HEIGHT // 2 - 60, 440, 120)
            color = CORRECT_COLOR if self.result["success"] else WRONG_COLOR
            draw_neon_panel(
                surface,
                result_rect,
                border_radius=18,
                top_color=lighten_color(PANEL_BG, 0.3),
                bottom_color=darken_color(PANEL_BG, 0.1),
                glow_color=color
            )

            result_font = pygame.font.SysFont('consolas', 24, bold=True)
            result_text = result_font.render(
                "УСПЕХ!" if self.result["success"] else "НЕУДАЧА",
                True, color
            )
            message_text = self.code_font.render(self.result["message"], True, TEXT_COLOR)

            surface.blit(result_text, (SCREEN_WIDTH // 2 - result_text.get_width() // 2,
                                       SCREEN_HEIGHT // 2 - 30))
            surface.blit(message_text, (SCREEN_WIDTH // 2 - message_text.get_width() // 2,
                                        SCREEN_HEIGHT // 2 + 10))

            if self.result["success"]:
                for _ in range(10):
                    x = random.randint(SCREEN_WIDTH // 2 - 100, SCREEN_WIDTH // 2 + 100)
                    y = random.randint(SCREEN_HEIGHT // 2 - 50, SCREEN_HEIGHT // 2 + 50)
                    particle_system.add_effect("code_success", x, y)

        # Инструкция
        instruct_font = pygame.font.SysFont('consolas', 18)
        if not self.result:
            instructions = [
                "Tab - отступ (4 пробела)",
                "Ctrl+Enter - отправить решение",
                "H - следующая подсказка",
                "Стрелки - перемещение курсора"
            ]

            for i, instruction in enumerate(instructions):
                text = instruct_font.render(instruction, True, TEXT_COLOR)
                surface.blit(text, (battle_rect.x + 30, battle_rect.bottom - 120 + i * 20))
        else:
            instruct_text = instruct_font.render("Нажмите любую клавишу чтобы продолжить", True, TEXT_COLOR)
            surface.blit(instruct_text, (battle_rect.centerx - instruct_text.get_width() // 2,
                                         battle_rect.bottom - 80))

    def get_cursor_position(self):
        """Возвращает позицию курсора (строка, столбец)"""
        lines = self.player_code[:self.cursor_position].split('\n')
        line = len(lines) - 1
        col = len(lines[-1]) if lines else 0
        return line, col

    def tokenize_line(self, line):
        """Разбивает строку на токены для подсветки синтаксиса"""
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
        """Возвращает цвет для типа токена"""
        colors = {
            "normal": CODE_EDITOR_TEXT,
            "keyword": (86, 156, 214),  # Синий
            "string": (206, 145, 120),  # Оранжевый
            "comment": (106, 153, 85),  # Зеленый
        }
        return colors.get(token_type, CODE_EDITOR_TEXT)

class Shape:
    """
    Представление фигуры. SHAPES вынесены в атрибут класса для доступа извне.
    Каждая фигура кэширует собственную поверхность для быстрой отрисовки.
    """
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
        border_radius = max(2, min(10, cell_size // 2))
        for bx, by in self.blocks:
            block_surface = pygame.Surface((cell_size - 2, cell_size - 2), pygame.SRCALPHA)
            top_color = lighten_color(self.color, 0.35)
            bottom_color = darken_color(self.color, 0.25)
            block_surface.blit(
                get_vertical_gradient((cell_size - 2, cell_size - 2), top_color, bottom_color),
                (0, 0)
            )
            pygame.draw.rect(
                block_surface,
                (*HIGHLIGHT_COLOR, 130),
                block_surface.get_rect(),
                2,
                border_radius=border_radius
            )

            highlight = pygame.Surface((cell_size - 6, cell_size // 3), pygame.SRCALPHA)
            highlight.fill((*TEXT_COLOR, 25))
            block_surface.blit(highlight, (3, 3))

            surf.blit(block_surface, (bx * cell_size + 1, by * cell_size + 1))
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
            surface.blit(hint, (x, y))
            return

        if is_ghost and not in_panel:
            ghost = self.surface.copy()
            ghost.fill((255, 255, 255, GHOST_ALPHA), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(ghost, (x, y))
            return

        if alpha < 255 and not in_panel:
            temp = self.surface.copy()
            temp.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(temp, (x, y))
            return

        surface.blit(draw_surface, (x, y))


class GameBoard:
    def __init__(self):
        self.reset()

    def reset(self) -> None:
        self.grid: List[List[int]] = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.colors: List[List[Optional[Tuple[int, int, int]]]] = [[None for _ in range(GRID_SIZE)] for _ in
                                                                   range(GRID_SIZE)]
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
            if all(row):
                lines += 1
        for col in range(GRID_SIZE):
            if all(temp_grid[r][col] for r in range(GRID_SIZE)):
                lines += 1

        score += lines * 10.0
        return score

    def place_shape(self, shape: Shape, x: int, y: int, particle_system=None) -> bool:
        if not self.can_place_shape(shape, x, y):
            return False

        for block_x, block_y in shape.blocks:
            grid_x, grid_y = x + block_x, y + block_y
            self.grid[grid_y][grid_x] = 1
            self.colors[grid_y][grid_x] = shape.color

            # Эффект частиц при размещении фигуры
            if particle_system:
                center_x = GRID_OFFSET_X + grid_x * CELL_SIZE + CELL_SIZE // 2
                center_y = GRID_OFFSET_Y + grid_y * CELL_SIZE + CELL_SIZE // 2
                particle_system.add_effect("shape_place", center_x, center_y, shape.color)

        self.clear_lines(particle_system)
        return True

    def clear_lines(self, particle_system=None) -> int:
        lines_to_clear: List[Tuple[str, int]] = []

        # Горизонтали
        for y in range(GRID_SIZE):
            if all(self.grid[y]):
                lines_to_clear.append(('horizontal', y))

        # Вертикали
        for x in range(GRID_SIZE):
            if all(self.grid[y][x] for y in range(GRID_SIZE)):
                lines_to_clear.append(('vertical', x))

        cleared = 0
        for line_type, index in lines_to_clear:
            if line_type == 'horizontal':
                for x in range(GRID_SIZE):
                    # Эффект частиц при очистке линии
                    if particle_system and self.colors[index][x]:
                        center_x = GRID_OFFSET_X + x * CELL_SIZE + CELL_SIZE // 2
                        center_y = GRID_OFFSET_Y + index * CELL_SIZE + CELL_SIZE // 2
                        particle_system.add_effect("line_clear", center_x, center_y, self.colors[index][x])

                    self.grid[index][x] = 0
                    self.colors[index][x] = None
            elif line_type == 'vertical':
                for y in range(GRID_SIZE):
                    # Эффект частиц при очистке линии
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
                # Эффект комбо
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
        grid_bg = pygame.Rect(
            GRID_OFFSET_X - 16,
            GRID_OFFSET_Y - 16,
            GRID_SIZE * CELL_SIZE + 32,
            GRID_SIZE * CELL_SIZE + 32
        )
        draw_neon_panel(
            surface,
            grid_bg,
            border_radius=18,
            top_color=lighten_color(GRID_BACKGROUND, 0.2),
            bottom_color=darken_color(GRID_BACKGROUND, 0.1),
            glow_color=NEON_SECONDARY
        )

        inner_rect = pygame.Rect(
            GRID_OFFSET_X,
            GRID_OFFSET_Y,
            GRID_SIZE * CELL_SIZE,
            GRID_SIZE * CELL_SIZE
        )
        inner_surface = pygame.Surface(inner_rect.size, pygame.SRCALPHA)
        inner_surface.fill((*GRID_BACKGROUND, 190))

        grid_surface = pygame.Surface(inner_rect.size, pygame.SRCALPHA)

        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(grid_surface, (*GRID_COLOR, 110), rect, 1)

                if self.grid[y][x] != 0:
                    cell_rect = pygame.Rect(
                        x * CELL_SIZE + 1,
                        y * CELL_SIZE + 1,
                        CELL_SIZE - 2,
                        CELL_SIZE - 2
                    )
                    pygame.draw.rect(grid_surface, self.colors[y][x], cell_rect, border_radius=6)
                    pygame.draw.rect(grid_surface, (*HIGHLIGHT_COLOR, 160), cell_rect, 2, border_radius=6)

        pygame.draw.rect(grid_surface, (*NEON_ACCENT, 70), grid_surface.get_rect(), 2)

        inner_surface.blit(grid_surface, (0, 0))
        surface.blit(inner_surface, inner_rect.topleft)


class QuizEngine:
    def __init__(self):
        self.questions = []
        self.load_questions()

    def load_questions(self):
        try:
            with open('data/questions.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.questions = data.get("questions", [])
                print(f"Загружено {len(self.questions)} вопросов")
        except Exception as e:
            print(f"Ошибка загрузки вопросов: {e}")
            self.questions = [
                {
                    "question": "Что выведет этот код: print('Hello' + 'World')?",
                    "options": ["HelloWorld", "Hello World", "Hello+World", "Ошибка"],
                    "correct": 0,
                    "explanation": "В Python оператор + для строк выполняет конкатенацию (объединение) строк."
                }
            ]

    def get_random_question(self):
        if not self.questions:
            self.load_questions()
        return random.choice(self.questions) if self.questions else None


class Button:
    def __init__(self, x, y, width, height, text, action=None, font_size=24):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.is_hovered = False
        self.font = pygame.font.SysFont('consolas', font_size)

    def draw(self, surface):
        base_color = BUTTON_HOVER_COLOR if self.is_hovered else BUTTON_COLOR
        top_color = lighten_color(base_color, 0.3)
        bottom_color = darken_color(base_color, 0.2)

        button_surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        button_surface.blit(
            get_vertical_gradient(self.rect.size, top_color, bottom_color),
            (0, 0)
        )
        pygame.draw.rect(button_surface, (*NEON_ACCENT, 150),
                         button_surface.get_rect(), 2, border_radius=14)
        inner_rect = button_surface.get_rect().inflate(-8, -8)
        if inner_rect.width > 0 and inner_rect.height > 0:
            pygame.draw.rect(button_surface, (*NEON_ACCENT, 40), inner_rect, border_radius=10)

        draw_glow(surface, self.rect, NEON_ACCENT, spread=18, max_alpha=80, border_radius=18)
        surface.blit(button_surface, self.rect.topleft)

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

        button_width, button_height = 300, 60
        center_x = SCREEN_WIDTH // 2 - button_width // 2
        self.start_button = Button(center_x, 300, button_width, button_height, "Начать игру", "start")
        self.achievements_button = Button(center_x, 380, button_width, button_height, "Достижения", "achievements")
        self.quit_button = Button(center_x, 460, button_width, button_height, "Выход", "quit")

        self.current_screen = "main"

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
                    result = self.start_button.check_click(mouse_pos)
                    if result == "start":
                        return "start"

                    result = self.achievements_button.check_click(mouse_pos)
                    if result == "achievements":
                        self.current_screen = "achievements"

                    result = self.quit_button.check_click(mouse_pos)
                    if result == "quit":
                        return "quit"
                elif self.current_screen == "achievements":
                    self.current_screen = "main"

        if self.current_screen == "main":
            self.start_button.check_hover(mouse_pos)
            self.achievements_button.check_hover(mouse_pos)
            self.quit_button.check_hover(mouse_pos)

        return None

    def draw(self):
        draw_dynamic_background(self.screen, MENU_BACKGROUND_TOP, MENU_BACKGROUND_BOTTOM, NEON_ACCENT)

        if self.current_screen == "main":
            self.draw_main_menu()
        elif self.current_screen == "achievements":
            self.draw_achievements()

    def draw_main_menu(self):
        card_rect = pygame.Rect(SCREEN_WIDTH // 2 - 260, 140, 520, 360)
        draw_neon_panel(
            self.screen,
            card_rect,
            border_radius=24,
            top_color=lighten_color(PANEL_BG, 0.35),
            bottom_color=darken_color(PANEL_BG, 0.1)
        )

        title = self.title_font.render("Python Blaster", True, TEXT_COLOR)
        subtitle = self.font.render("Code & Clear", True, NEON_ACCENT)

        self.screen.blit(title, (card_rect.centerx - title.get_width() // 2, 170))
        self.screen.blit(subtitle, (card_rect.centerx - subtitle.get_width() // 2, 215))

        high_score = self.small_font.render(f"Рекорд: {self.game_data.data['high_score']}", True, TEXT_COLOR)
        self.screen.blit(high_score, (card_rect.centerx - high_score.get_width() // 2, 250))

        self.start_button.draw(self.screen)
        self.achievements_button.draw(self.screen)
        self.quit_button.draw(self.screen)

        instruction = self.small_font.render("Нажмите ESC для выхода", True, CODE_LINE_NUMBERS)
        self.screen.blit(instruction, (card_rect.centerx - instruction.get_width() // 2, 480))

    def draw_achievements(self):
        title_rect = pygame.Rect(SCREEN_WIDTH // 2 - 260, 60, 520, 80)
        draw_neon_panel(
            self.screen,
            title_rect,
            border_radius=22,
            top_color=lighten_color(PANEL_BG, 0.3),
            bottom_color=darken_color(PANEL_BG, 0.1)
        )

        title = self.title_font.render("Достижения", True, TEXT_COLOR)
        self.screen.blit(title, (title_rect.centerx - title.get_width() // 2,
                                 title_rect.centery - title.get_height() // 2))

        stats_rect = pygame.Rect(SCREEN_WIDTH // 2 - 500, 160, 1000, 160)
        draw_neon_panel(
            self.screen,
            stats_rect,
            border_radius=20,
            top_color=lighten_color(PANEL_BG, 0.25),
            bottom_color=darken_color(PANEL_BG, 0.1)
        )

        stats = [
            f"Сыграно игр: {self.game_data.data['games_played']}",
            f"Рекорд: {self.game_data.data['high_score']}",
            f"Всего линий: {self.game_data.data['total_lines_cleared']}",
            f"Отвечено вопросов: {self.game_data.data['total_questions_answered']}",
            f"Правильных ответов: {self.game_data.data['total_correct_answers']}",
            f"Код-баттлов: {self.game_data.data['total_code_battles_completed']}"
        ]

        for i, stat in enumerate(stats):
            text = self.small_font.render(stat, True, TEXT_COLOR)
            row = i // 3
            col = i % 3
            x = stats_rect.x + 40 + col * (stats_rect.width // 3)
            y = stats_rect.y + 20 + row * 40
            self.screen.blit(text, (x, y))

        achievements_panel = pygame.Rect(SCREEN_WIDTH // 2 - 500, 340, 1000, 260)
        draw_neon_panel(
            self.screen,
            achievements_panel,
            border_radius=20,
            top_color=lighten_color(PANEL_BG, 0.25),
            bottom_color=darken_color(PANEL_BG, 0.1),
            glow_color=NEON_SECONDARY
        )

        achievements_title = self.font.render("Полученные достижения:", True, NEON_ACCENT)
        self.screen.blit(achievements_title,
                         (achievements_panel.centerx - achievements_title.get_width() // 2,
                          achievements_panel.y + 15))

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

        for i, achievement in enumerate(achievement_texts):
            color = CORRECT_COLOR if "❓" not in achievement else CODE_LINE_NUMBERS
            text = self.small_font.render(achievement, True, color)
            col = i % 2
            row = i // 2
            x = achievements_panel.x + 40 + col * (achievements_panel.width // 2)
            y = achievements_panel.y + 60 + row * 32
            self.screen.blit(text, (x, y))

        instruction = self.small_font.render("Нажмите для возврата", True, CODE_LINE_NUMBERS)
        self.screen.blit(instruction, (achievements_panel.centerx - instruction.get_width() // 2,
                                       achievements_panel.bottom - 40))


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

        # Статистика для достижений
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
        self.code_battle_interval = 5  # Теперь оба события каждые 5 линий
        self.last_event_lines = 0  # Отслеживаем последнее событие

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
                # Обрабатываем ввод в код-баттл
                if self.code_battle.handle_input(event):
                    continue

                # H для следующей подсказки
                if event.type == KEYDOWN and event.key == pygame.K_h:
                    self.code_battle.next_hint()
                    continue

                if event.type == KEYDOWN and self.code_battle.result:
                    # Любая клавиша после результата
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
                # Проверяем клик по фигурам в панели
                for i, shape in enumerate(self.current_shapes):
                    # Вычисляем позицию фигуры в панели
                    shape_x, shape_y = self.get_shape_panel_position(i, shape)
                    shape_rect = pygame.Rect(
                        shape_x,
                        shape_y,
                        shape.width * PANEL_CELL_SIZE,
                        shape.height * PANEL_CELL_SIZE
                    )
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
                        pos = None
                        if self.snap_position is not None:
                            pos = self.snap_position
                        elif self.ghost_position is not None:
                            pos = self.ghost_position

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

                            # Обновляем статистику линий для этой игры
                            self.lines_cleared_this_game = self.board.lines_cleared

                            # Проверяем триггер для событий (каждые 5 линий)
                            if (self.board.lines_cleared >= self.last_event_lines + self.code_battle_interval and
                                    self.board.lines_cleared > 0):

                                self.last_event_lines = self.board.lines_cleared

                                # Случайный выбор: 50% код-баттл, 50% тест
                                if random.random() < 0.5:
                                    self.show_code_battle = True
                                    self.code_battle.start_battle()
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
                        if self.snap_position is not None:
                            self.ghost_position = self.snap_position
                        else:
                            self.ghost_position = None
                            self.snap_position = None
                    else:
                        self.ghost_position = (grid_x, grid_y)
                        self.snap_position = None

            elif event.type == KEYDOWN:
                if event.key == K_r:
                    self.current_shapes = [Shape(difficulty=self.difficulty) for _ in range(3)]

        return None

    def get_shape_panel_position(self, index: int, shape: Shape) -> Tuple[int, int]:
        """Вычисляет позицию фигуры в панели для центрированного расположения"""
        panel_x = self.panel_rect.x
        panel_y = self.panel_rect.y + 60
        panel_width = self.panel_rect.width
        panel_height = self.panel_rect.height - 80

        # Располагаем фигуры вертикально с равными отступами
        slot_height = panel_height // 3
        y_offset = panel_y + index * slot_height + (slot_height - shape.height * PANEL_CELL_SIZE) // 2

        # Центрируем по горизонтали
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
        if not self.current_question:
            return

        self.questions_answered_this_game += 1

        if answer_index == self.current_question["correct"]:
            self.quiz_result = {
                "correct": True,
                "message": "ПРАВИЛЬНО!",
                "color": CORRECT_COLOR
            }
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
        self.quiz_timer = 0
        self.bonus_active = None
        self.difficulty = "easy"
        self.questions_answered_this_game = 0
        self.correct_answers_this_game = 0
        self.lines_cleared_this_game = 0
        self.code_battles_completed_this_game = 0
        self.last_event_lines = 0
        self.particle_system.particles.clear()

    def draw(self) -> None:
        draw_dynamic_background(self.screen, BACKGROUND_TOP, BACKGROUND_BOTTOM, NEON_ACCENT)

        # Сначала обновляем частицы
        self.particle_system.update()

        title_rect = pygame.Rect(SCREEN_WIDTH // 2 - 260, 18, 520, 64)
        draw_neon_panel(
            self.screen,
            title_rect,
            border_radius=24,
            top_color=lighten_color(PANEL_BG, 0.35),
            bottom_color=darken_color(PANEL_BG, 0.15)
        )
        title = self.title_font.render("Python Blaster: Code & Clear", True, TEXT_COLOR)
        self.screen.blit(title, (title_rect.centerx - title.get_width() // 2,
                                 title_rect.centery - title.get_height() // 2))

        self.board.draw(self.screen)

        if self.dragging and self.dragged_shape and self.ghost_position is not None:
            ghost_x, ghost_y = self.ghost_position
            self.dragged_shape.draw(
                self.screen,
                GRID_OFFSET_X + ghost_x * CELL_SIZE,
                GRID_OFFSET_Y + ghost_y * CELL_SIZE,
                is_ghost=True
            )

        # Рисуем панель фигур
        draw_neon_panel(
            self.screen,
            self.panel_rect,
            border_radius=16,
            top_color=lighten_color(PANEL_BG, 0.25),
            bottom_color=darken_color(PANEL_BG, 0.1),
            glow_color=NEON_SECONDARY
        )

        panel_title = self.font.render("Доступные фигуры:", True, NEON_ACCENT)
        self.screen.blit(panel_title, (self.panel_rect.x + 20, self.panel_rect.y + 20))

        # Рисуем фигуры в панели с центрированием
        for i, shape in enumerate(self.current_shapes):
            if self.dragging and i == self.dragged_shape_index:
                continue  # не рисуем ту, что тащат

            shape_x, shape_y = self.get_shape_panel_position(i, shape)
            shape.draw(self.screen, shape_x, shape_y, in_panel=True)

        # Рисуем перетаскиваемую фигуру рядом с мышью
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

        # Уменьшенная панель счета
        score_panel = pygame.Rect(SCREEN_WIDTH - 280, 120, 250, 120)
        draw_neon_panel(
            self.screen,
            score_panel,
            border_radius=14,
            top_color=lighten_color(PANEL_BG, 0.3),
            bottom_color=darken_color(PANEL_BG, 0.05)
        )

        score_text = self.font.render(f"Счет: {self.board.score}", True, NEON_ACCENT)
        lines_text = self.font.render(f"Линии: {self.board.lines_cleared}", True, TEXT_COLOR)
        next_event = max(0, self.last_event_lines + self.code_battle_interval - self.board.lines_cleared)
        next_event_text = self.small_font.render(f"След. событие: {next_event}", True, CODE_LINE_NUMBERS)
        difficulty_text = self.small_font.render(f"Сложность: {self.difficulty}", True, CODE_LINE_NUMBERS)

        self.screen.blit(score_text, (score_panel.x + 20, score_panel.y + 20))
        self.screen.blit(lines_text, (score_panel.x + 20, score_panel.y + 52))
        self.screen.blit(next_event_text, (score_panel.x + 20, score_panel.y + 82))
        self.screen.blit(difficulty_text, (score_panel.x + 20, score_panel.y + 108))

        # Уменьшенная панель инструкций
        instructions_panel = pygame.Rect(SCREEN_WIDTH - 280, 260, 250, 180)
        draw_neon_panel(
            self.screen,
            instructions_panel,
            border_radius=14,
            top_color=lighten_color(PANEL_BG, 0.2),
            bottom_color=darken_color(PANEL_BG, 0.1),
            glow_color=NEON_SECONDARY
        )

        instructions = [
            "Управление:",
            "Клик и перетаскивание",
            "R - замена фигур",
            "ESC - в меню",
            "",
            "Фигура 'примагнитится'"
        ]
        for i, line in enumerate(instructions):
            color = NEON_ACCENT if i == 0 else TEXT_COLOR
            if not line:
                color = CODE_LINE_NUMBERS
            text = self.small_font.render(line, True, color)
            self.screen.blit(text, (instructions_panel.x + 20, instructions_panel.y + 20 + i * 25))

        # ТЕПЕРЬ ЧАСТИЦЫ РИСУЮТСЯ ПОСЛЕ ВСЕГО ОСТАЛЬНОГО
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
        draw_neon_panel(
            self.screen,
            quiz_rect,
            border_radius=24,
            top_color=lighten_color(PANEL_BG, 0.3),
            bottom_color=darken_color(PANEL_BG, 0.1)
        )

        question_text = self.font.render("Вопрос по Python:", True, NEON_ACCENT)
        self.screen.blit(question_text, (SCREEN_WIDTH // 2 - question_text.get_width() // 2, 180))

        question_lines = self.wrap_text(self.current_question["question"], 740)
        for i, line in enumerate(question_lines):
            text = self.small_font.render(line, True, TEXT_COLOR)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 220 + i * 25))

        y_offset = 220 + len(question_lines) * 25 + 20
        for i, option in enumerate(self.current_question["options"]):
            option_text = self.small_font.render(f"{i + 1}. {option}", True, TEXT_COLOR)
            self.screen.blit(option_text, (SCREEN_WIDTH // 2 - option_text.get_width() // 2, y_offset + i * 30))

        instruct_text = self.small_font.render("Нажмите 1-4 для выбора ответа", True, CODE_LINE_NUMBERS)
        self.screen.blit(instruct_text, (SCREEN_WIDTH // 2 - instruct_text.get_width() // 2, y_offset + 150))

    def draw_quiz_result(self) -> None:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        result_rect = pygame.Rect(300, 200, 800, 300)
        draw_neon_panel(
            self.screen,
            result_rect,
            border_radius=24,
            top_color=lighten_color(PANEL_BG, 0.3),
            bottom_color=darken_color(PANEL_BG, 0.1),
            glow_color=self.quiz_result["color"]
        )

        result_text = self.title_font.render(self.quiz_result["message"], True, self.quiz_result["color"])
        self.screen.blit(result_text, (SCREEN_WIDTH // 2 - result_text.get_width() // 2, 250))

        if not self.quiz_result["correct"]:
            explanation_lines = self.wrap_text(self.quiz_result["explanation"], 550)
            for i, line in enumerate(explanation_lines):
                text = self.small_font.render(line, True, TEXT_COLOR)
                self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 320 + i * 25))

        instruct_text = self.small_font.render("Нажмите любую клавишу чтобы продолжить", True, CODE_LINE_NUMBERS)
        self.screen.blit(instruct_text, (SCREEN_WIDTH // 2 - instruct_text.get_width() // 2, 450))

    def draw_game_over(self) -> None:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        self.screen.blit(overlay, (0, 0))

        game_over_panel = pygame.Rect(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 150, 400, 300)
        draw_neon_panel(
            self.screen,
            game_over_panel,
            border_radius=22,
            top_color=lighten_color(PANEL_BG, 0.3),
            bottom_color=darken_color(PANEL_BG, 0.1),
            glow_color=NEON_ACCENT
        )

        game_over_text = self.title_font.render("ИГРА ОКОНЧЕНА", True, NEON_ACCENT)
        score_text = self.font.render(f"Финальный счет: {self.board.score}", True, TEXT_COLOR)
        lines_text = self.font.render(f"Очищено линий: {self.board.lines_cleared}", True, TEXT_COLOR)
        high_score_text = self.font.render(f"Рекорд: {self.game_data.data['high_score']}", True, TEXT_COLOR)

        self.screen.blit(game_over_text,
                         (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
        self.screen.blit(lines_text, (SCREEN_WIDTH // 2 - lines_text.get_width() // 2, SCREEN_HEIGHT // 2 - 10))
        self.screen.blit(high_score_text,
                         (SCREEN_WIDTH // 2 - high_score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))

        # Добавляем эффект частиц при завершении игры
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        self.particle_system.add_effect("game_over", center_x, center_y)

        restart_text = self.small_font.render("Нажмите R или SPACE для возврата в меню", True, CODE_LINE_NUMBERS)
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
        can_place_any = False
        for shape in self.current_shapes:
            if self.board.find_best_placement(shape) is not None:
                can_place_any = True
                break

        if not can_place_any and not self.game_over:
            self.game_over = True
            # Сохраняем статистику текущей игры
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


def main():
    pygame.init()

    game_data = GameData()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Python Blaster: Code & Clear")

    menu = MainMenu(screen, game_data)

    current_screen = "menu"

    while True:
        if current_screen == "menu":
            result = menu.handle_events()
            if result == "start":
                current_screen = "game"
            elif result == "quit":
                break
            menu.draw()
            pygame.display.flip()

        elif current_screen == "game":
            game = Game(game_data)
            result = game.run()
            if result == "menu":
                current_screen = "menu"
            elif result == "quit":
                break

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()