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

# ---------- ВНЕШНИЕ СЕТЕВЫЕ ЗАВИСИМОСТИ ----------
try:
    import requests
except Exception:
    requests = None

# ---------- SUPABASE  ----------
SUPABASE_URL = "https://uecbggbbaivumtvjbgki.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVlY2JnZ2JiYWl2dW10dmpiZ2tpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk0Mzc0NjgsImV4cCI6MjA3NTAxMzQ2OH0.F2qccp-u9b5DaKIGhzES_yq4aQ1aMfqizcfaEIHHc6I"

# ---------- КОНСТАНТЫ UI/ГЕЙМПЛЕЯ ----------
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 700
GRID_SIZE = 8
CELL_SIZE = 60
GRID_OFFSET_X = 600
GRID_OFFSET_Y = 100
PANEL_CELL_SIZE = 35
FPS = 60

BACKGROUND = (15, 20, 30)
GRID_COLOR = (40, 50, 70)
GRID_HIGHLIGHT = (70, 90, 120)
CELL_COLORS = [
    (41, 128, 185), (39, 174, 96), (142, 68, 173),
    (230, 126, 34), (231, 76, 60), (26, 188, 156), (241, 196, 15)
]
TEXT_COLOR = (236, 240, 241)
HIGHLIGHT_COLOR = (52, 152, 219)
VALID_PLACEMENT_COLOR = (46, 204, 113)
INVALID_PLACEMENT_COLOR = (231, 76, 60)
GHOST_ALPHA = 150
PANEL_BG = (30, 40, 55)
MENU_BG = (20, 30, 48)
CODE_EDITOR_BG = (25, 35, 45)
CODE_EDITOR_TEXT = (220, 220, 220)
CODE_LINE_NUMBERS = (100, 100, 120)

# --- НЦВЕТА КНОПОК ---
BTN_GREEN     = (46, 204, 113); BTN_GREEN_H = (39, 174, 96)
BTN_YELLOW    = (241, 196, 15); BTN_YELLOW_H = (243, 215, 60)
BTN_BLUE      = (52, 152, 219); BTN_BLUE_H = (93, 173, 226)
BTN_GREY      = (127, 140, 141); BTN_GREY_H = (149, 165, 166)
BTN_TOGGLE    = BTN_BLUE;       BTN_TOGGLE_H = BTN_BLUE_H
CORRECT_COLOR = (46, 204, 113)
WRONG_COLOR = (231, 76, 60)

# ---------- ФАЙЛЫ ----------
DATA_DIR = "data"
QUESTIONS_PATH = os.path.join(DATA_DIR, "questions.json")
BATTLES_CATALOG_PATH = os.path.join(DATA_DIR, "code_battles_catalog.json")
BATTLES_LOG_PATH = os.path.join(DATA_DIR, "code_battles.json")
GAME_DATA_PATH = os.path.join(DATA_DIR, "game_data.json")


def ensure_data_files():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(QUESTIONS_PATH):
        with open(QUESTIONS_PATH, "w", encoding="utf-8") as f:
            json.dump({
                "questions": [
                    {
                        "question": "Что выведет print(len('Python'))?",
                        "options": ["6", "5", "7", "Ошибка"],
                        "correct": 0,
                        "explanation": "Длина строки 'Python' равна 6."
                    }
                ]
            }, f, ensure_ascii=False, indent=2)
    if not os.path.exists(BATTLES_CATALOG_PATH):
        with open(BATTLES_CATALOG_PATH, "w", encoding="utf-8") as f:
            json.dump({
                "items": [
                    {
                        "name": "Сумма двух чисел",
                        "description": "Верните сумму a и b",
                        "template": "def add(a, b):\n    # Напишите ваш код здесь\n    pass",
                        "test_cases": [
                            {"input": [1, 2], "expected": 3},
                            {"input": [5, 7], "expected": 12},
                            {"input": [-1, 1], "expected": 0},
                            {"input": [0, 0], "expected": 0}
                        ],
                        "difficulty": "easy",
                        "time_limit": 120,
                        "reward": 200,
                        "hints": ["Используйте оператор +", "Не забудьте вернуть результат"],
                        "solution": "def add(a, b):\n    return a + b",
                        "explanation": "Складываем аргументы и возвращаем сумму."
                    }
                ]
            }, f, ensure_ascii=False, indent=2)
    if not os.path.exists(BATTLES_LOG_PATH):
        with open(BATTLES_LOG_PATH, "w", encoding="utf-8") as f:
            json.dump({"items": []}, f, ensure_ascii=False, indent=2)
    if not os.path.exists(GAME_DATA_PATH):
        with open(GAME_DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({
                "high_score": 0,
                "achievements": {
                    "first_game": False,
                    "score_500": False, "score_1000": False, "score_2000": False,
                    "clear_10_lines": False, "clear_25_lines": False,
                    "answer_5_questions": False, "answer_10_questions": False,
                    "complete_5_code_battles": False, "complete_10_code_battles": False
                },
                "games_played": 0,
                "total_lines_cleared": 0,
                "total_questions_answered": 0,
                "total_correct_answers": 0,
                "total_code_battles_completed": 0,
                "last_played": None,
                "game_sessions": []
            }, f, ensure_ascii=False, indent=2)


# ---------- ОНЛАЙН-ЛИДЕРБОРД ----------
class OnlineLeaderboard:
    def __init__(self, url: str, anon_key: str):
        self.url = url.rstrip("/")
        self.key = anon_key

    @property
    def available(self) -> bool:
        return bool(requests and self.url.startswith("http") and self.key)

    @property
    def _headers(self):
        return {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }

    def fetch_top_mode(self, mode: str, limit: int = 10, timeout=6):
        """
        Возвращает топ по режиму без дат и лишних полей.
        """
        if not self.available:
            return False, "Online disabled"
        params = {
            "select": "name,score,mode",
            "order": "score.desc,name.asc",
            "limit": str(limit),
            "mode": f"eq.{mode}"
        }
        try:
            r = requests.get(f"{self.url}/rest/v1/scores", headers=self._headers, params=params, timeout=timeout)
            r.raise_for_status()
            return True, r.json()
        except Exception as e:
            return False, str(e)

    def fetch_user_mode(self, name: str, mode: str, timeout=6):
        """
        Возвращает запись игрока (name,mode) если существует.
        """
        if not self.available:
            return False, "Online disabled"
        params = {"select": "name,score,mode", "name": f"eq.{name}", "mode": f"eq.{mode}", "limit": "1"}
        try:
            r = requests.get(f"{self.url}/rest/v1/scores", headers=self._headers, params=params, timeout=timeout)
            r.raise_for_status()
            data = r.json()
            return True, (data[0] if data else None)
        except Exception as e:
            return False, str(e)

    def insert_score(self, name: str, score: int, mode: str, timeout=6):
        if not self.available:
            return False, "Online disabled"
        payload = {"name": name[:12], "score": int(score), "mode": mode}
        try:
            r = requests.post(f"{self.url}/rest/v1/scores", headers=self._headers, json=payload, timeout=timeout)
            r.raise_for_status()
            return True, r.json()
        except Exception as e:
            return False, str(e)

    def update_if_better(self, name: str, score: int, mode: str, timeout=6):
        """
        Если новой результат лучше по score — обновляем, иначе оставляем старый.
        Нет дат и дополнительных полей.
        """
        if not self.available:
            return False, "Online disabled"
        ok, existing = self.fetch_user_mode(name, mode, timeout=timeout)
        if not ok:
            return False, existing

        if existing is None:
            return self.insert_score(name, score, mode, timeout=timeout)

        old_score = int(existing.get("score", 0))
        if score > old_score:
            try:
                r = requests.patch(
                    f"{self.url}/rest/v1/scores",
                    headers=self._headers,
                    params={"name": f"eq.{name}", "mode": f"eq.{mode}"},
                    json={"score": int(score)},
                    timeout=timeout
                )
                r.raise_for_status()
                return True, r.json()
            except Exception as e:
                return False, str(e)
        else:
            return True, "kept_old_better"


# ---------- ВСПОМОГАТЕЛЬНЫЕ КЛАССЫ/СИСТЕМЫ ----------
class Particle:
    def __init__(self, x, y, color, velocity=None, life=60, size=20, particle_type="circle"):
        self.x = x; self.y = y; self.color = color
        self.velocity = velocity or [random.uniform(-5, 5), random.uniform(-5, 5)]
        self.life = life; self.max_life = life
        self.size = size; self.type = particle_type
        self.gravity = 0.15; self.decay = 0.95

    def update(self):
        self.x += self.velocity[0]; self.y += self.velocity[1]
        self.velocity[1] += self.gravity
        self.velocity[0] *= self.decay; self.velocity[1] *= self.decay
        self.life -= 1; self.size = max(1, self.size * 0.98)
        return self.life > 0

    def draw(self, surface):
        alpha = int(255 * (self.life / self.max_life))
        if self.type == "circle":
            color = (*self.color, alpha)
            s = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
            pygame.draw.circle(s, color, (self.size, self.size), self.size)
            surface.blit(s, (int(self.x - self.size), int(self.y - self.size)))


class ParticleSystem:
    def __init__(self):
        self.particles = []
        self.effects = {
            "line_clear": {"count": 50, "colors": [(255,255,200),(255,200,100),(255,150,50)]},
            "shape_place": {"count": 25, "colors": [(100,200,255),(50,150,255),(0,100,200)]},
            "combo": {"count": 80, "colors": [(255,50,50),(255,100,100),(255,150,150)]},
            "code_success": {"count": 100, "colors": [(50,255,100),(100,255,150),(150,255,200)]},
            "game_over": {"count": 150, "colors": [(255,50,50),(255,100,100),(200,50,50)]}
        }
    def add_effect(self, effect_type, x, y, color=None):
        if effect_type in self.effects:
            eff = self.effects[effect_type]
            colors = [color] if color else eff["colors"]
            for _ in range(eff["count"]):
                particle_color = random.choice(colors)
                size = random.uniform(3, 8); life = random.randint(60, 120)
                vel = [random.uniform(-6,6), random.uniform(-6,6)]
                self.particles.append(Particle(x,y,particle_color,vel,life,size,"circle"))
    def update(self):
        self.particles = [p for p in self.particles if p.update()]
    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)


class GameData:
    def __init__(self):
        self.data_file = GAME_DATA_PATH
        self.default_data = {
            "high_score": 0,
            "achievements": {
                "first_game": False,
                "score_500": False, "score_1000": False, "score_2000": False,
                "clear_10_lines": False, "clear_25_lines": False,
                "answer_5_questions": False, "answer_10_questions": False,
                "complete_5_code_battles": False, "complete_10_code_battles": False
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
                with open(self.data_file, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                self._deep_update(self.data, loaded)
            else:
                os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
                self.save_data()
        except Exception as e:
            print(f"[GameData] load error: {e}")
            self.data = self.default_data.copy(); self.save_data()

    def _deep_update(self, target, src):
        for k, v in target.items():
            if k in src:
                if isinstance(v, dict) and isinstance(src[k], dict):
                    self._deep_update(v, src[k])
                else:
                    target[k] = src[k]

    def save_data(self):
        try:
            self.data["last_played"] = datetime.now().isoformat()
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[GameData] save error: {e}")

    def update_high_score(self, score: int):
        if score > self.data["high_score"]:
            self.data["high_score"] = score
            self.save_data()
            return True
        return False

    def add_game_session(self, score, lines_cleared, questions_answered, correct_answers, code_battles_completed=0):
        self.data["games_played"] += 1
        self.data["total_lines_cleared"] += lines_cleared
        self.data["total_questions_answered"] += questions_answered
        self.data["total_correct_answers"] += correct_answers
        self.data["total_code_battles_completed"] += code_battles_completed
        self.data["game_sessions"].append({
            "date": datetime.now().isoformat(),
            "score": score,
            "lines_cleared": lines_cleared,
            "questions_answered": questions_answered,
            "correct_answers": correct_answers,
            "code_battles_completed": code_battles_completed
        })
        self.data["game_sessions"] = self.data["game_sessions"][-50:]
        self.update_high_score(score)
        self.save_data()

    def update_achievements(self):
        a = self.data["achievements"]
        if not a["first_game"]: a["first_game"] = True
        if self.data["high_score"] >= 500: a["score_500"] = True
        if self.data["high_score"] >= 1000: a["score_1000"] = True
        if self.data["high_score"] >= 2000: a["score_2000"] = True
        if self.data["total_lines_cleared"] >= 10: a["clear_10_lines"] = True
        if self.data["total_lines_cleared"] >= 25: a["clear_25_lines"] = True
        if self.data["total_questions_answered"] >= 5: a["answer_5_questions"] = True
        if self.data["total_questions_answered"] >= 10: a["answer_10_questions"] = True
        if self.data["total_code_battles_completed"] >= 5: a["complete_5_code_battles"] = True
        if self.data["total_code_battles_completed"] >= 10: a["complete_10_code_battles"] = True
        self.save_data()


class QuizEngine:
    def __init__(self):
        self.questions = []
        self.load_questions()

    def load_questions(self):
        try:
            with open(QUESTIONS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.questions = data.get("questions", [])
        except Exception as e:
            print(f"[Quiz] load error: {e}")
            self.questions = []

    def get_random_question(self):
        if not self.questions:
            self.load_questions()
        if not self.questions:
            return None
        q = random.choice(self.questions)
        options = q["options"][:]
        correct_idx = q["correct"]
        correct_val = options[correct_idx]
        random.shuffle(options)
        new_correct = options.index(correct_val)
        return {
            "question": q["question"],
            "options": options,
            "correct": new_correct,
            "explanation": q.get("explanation", "")
        }


class CodeBattleCatalog:
    def __init__(self):
        self.items = []
        self.load()
    def load(self):
        try:
            with open(BATTLES_CATALOG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.items = data.get("items", [])
        except Exception as e:
            print(f"[Catalog] load error: {e}")
            self.items = []
    def random_challenge(self):
        return random.choice(self.items) if self.items else None


class CodeBattleLog:
    def add_item(self, challenge, code: str, success: bool, message: str, reward: int, time_spent: float):
        try:
            with open(BATTLES_LOG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {"items": []}
        data["items"].append({
            "date": datetime.now().isoformat(),
            "challenge_name": challenge.get("name",""),
            "challenge_desc": challenge.get("description",""),
            "code": code,
            "success": bool(success),
            "message": message,
            "reward": int(reward),
            "time_spent_sec": int(time_spent)
        })
        data["items"] = data["items"][-200:]
        try:
            with open(BATTLES_LOG_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[BattleLog] save error: {e}")


class Button:
    def __init__(self, x, y, width, height, text, action=None, font_size=24,
                 color=(52,152,219), color_hover=(93,173,226), icon: Optional[str]=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.is_hovered = False
        self.color = color
        self.color_h = color_hover
        self.icon = icon  # 'trophy' | 'table' | None
        try:
            self.font = pygame.font.SysFont('consolas', font_size)
        except:
            self.font = pygame.font.SysFont(None, font_size)

    def draw(self, surface):
        color = self.color_h if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, GRID_HIGHLIGHT, self.rect, 2, border_radius=10)

        
        if self.icon == "trophy":
            self._draw_trophy(surface, self.rect.centerx - 16, self.rect.centery - 18)
        elif self.icon == "table":
            self._draw_table(surface, self.rect.centerx - 16, self.rect.centery - 16)

        
        if self.text:
            text_surf = self.font.render(self.text, True, TEXT_COLOR)
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)

    def _draw_trophy(self, surface, x, y):
        cup = (255, 215, 0); dark = (180, 140, 0)
        pygame.draw.rect(surface, cup,  (x+6,  y+4,  20, 16), border_radius=4)   
        pygame.draw.rect(surface, dark, (x+12, y+20, 8, 10),  border_radius=2)   
        pygame.draw.rect(surface, cup,  (x+4,  y+30, 24, 6),  border_radius=2)   
        pygame.draw.circle(surface, cup, (x+6,  y+12), 6, 3)
        pygame.draw.circle(surface, cup, (x+26, y+12), 6, 3)

    def _draw_table(self, surface, x, y):
        
        frame = (235, 245, 255)
        pygame.draw.rect(surface, frame, (x, y, 32, 32), border_radius=6, width=3)
        
        for gy in (y+10, y+20):
            pygame.draw.line(surface, frame, (x+4, gy), (x+28, gy), 2)
        
        for gx in (x+12, x+20):
            pygame.draw.line(surface, frame, (gx, y+4), (gx, y+28), 2)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)

    def check_click(self, pos):
        if self.rect.collidepoint(pos) and self.action:
            return self.action
        return None


# ---------- ФИГУРЫ/ДОСКА ----------
class Shape:
    SIMPLE_SHAPES = [0,1,2,4,5,6,10,11,12,13,16,17,18,19,20,21,22,23]
    MEDIUM_SHAPES = [3,7,8,14,15,24,25]
    COMPLEX_SHAPES = [9,26,27]
    SHAPES = [
        [[1,1]], [[1,1,1]], [[1,1,1,1]], [[1,1,1,1,1]],
        [[1],[1]], [[1],[1],[1]], [[1],[1],[1],[1]], [[1],[1],[1],[1],[1]],
        [[1,1],[1,1]], [[1,1,1],[1,1,1],[1,1,1]],
        [[1,0],[1,0],[1,1]], [[0,1],[0,1],[1,1]],
        [[1,1],[1,0],[1,0]], [[1,1],[0,1],[0,1]],
        [[1,1,1],[1,0,0]], [[1,1,1],[0,0,1]],
        [[1,1,1],[0,1,0]], [[0,1,0],[1,1,1]],
        [[1,0],[1,1],[1,0]], [[0,1],[1,1],[0,1]],
        [[1,1,0],[0,1,1]], [[0,1,1],[1,1,0]],
        [[1,0],[1,1],[0,1]], [[0,1],[1,1],[1,0]],
        [[1,1],[1,0]], [[1,1],[0,1]],
        [[1,1,1],[1,0,0],[1,0,0]], [[1,1,1],[0,0,1],[0,0,1]],
    ]
    def __init__(self, shape_type: Optional[int]=None, difficulty: str="easy"):
        self.blocks: List[Tuple[int,int]] = []
        self.color = random.choice(CELL_COLORS)
        if shape_type is None:
            if difficulty == "easy":
                shape_type = random.choice(self.SIMPLE_SHAPES)
            elif difficulty == "hard":
                weights = [2]*len(self.SIMPLE_SHAPES) + [5]*len(self.MEDIUM_SHAPES) + [9]*len(self.COMPLEX_SHAPES)
                all_s = self.SIMPLE_SHAPES + self.MEDIUM_SHAPES + self.COMPLEX_SHAPES
                shape_type = random.choices(all_s, weights=weights, k=1)[0]
            else:
                weights = [4]*len(self.SIMPLE_SHAPES) + [5]*len(self.MEDIUM_SHAPES) + [6]*len(self.COMPLEX_SHAPES)
                all_s = self.SIMPLE_SHAPES + self.MEDIUM_SHAPES + self.COMPLEX_SHAPES
                shape_type = random.choices(all_s, weights=weights, k=1)[0]
        pattern = self.SHAPES[shape_type]
        self.height = len(pattern); self.width = len(pattern[0]) if self.height>0 else 0
        for y, row in enumerate(pattern):
            for x, c in enumerate(row):
                if c: self.blocks.append((x,y))
        self.surface = self._create_surface(CELL_SIZE)
        self.panel_surface = self._create_surface(PANEL_CELL_SIZE)
    def _create_surface(self, cell):
        surf = pygame.Surface((self.width*cell, self.height*cell), pygame.SRCALPHA)
        for bx, by in self.blocks:
            rect = pygame.Rect(bx*cell, by*cell, cell-2, cell-2)
            pygame.draw.rect(surf, self.color, rect)
            pygame.draw.rect(surf, HIGHLIGHT_COLOR, rect, 2)
        return surf
    def draw(self, surface, x, y, alpha=255, show_placement_hint=False, valid_placement=True, is_ghost=False, in_panel=False):
        draw_surface = self.panel_surface if in_panel else self.surface
        if show_placement_hint and not in_panel:
            hint = pygame.Surface(draw_surface.get_size(), pygame.SRCALPHA)
            color = VALID_PLACEMENT_COLOR if valid_placement else INVALID_PLACEMENT_COLOR
            hint.fill((0,0,0,0))
            cell = PANEL_CELL_SIZE if in_panel else CELL_SIZE
            for bx, by in self.blocks:
                rr = pygame.Rect(bx*cell, by*cell, cell-2, cell-2)
                pygame.draw.rect(hint, color, rr)
                pygame.draw.rect(hint, HIGHLIGHT_COLOR, rr, 2)
            if alpha < 255:
                hint.fill((255,255,255,alpha), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(hint, (x,y)); return
        if is_ghost and not in_panel:
            ghost = self.surface.copy()
            ghost.fill((255,255,255,150), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(ghost, (x,y)); return
        if alpha < 255 and not in_panel:
            temp = self.surface.copy()
            temp.fill((255,255,255,alpha), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(temp, (x,y)); return
        surface.blit(draw_surface, (x,y))


class GameBoard:
    def __init__(self): self.reset()
    def reset(self):
        self.grid = [[0]*GRID_SIZE for _ in range(GRID_SIZE)]
        self.colors = [[None]*GRID_SIZE for _ in range(GRID_SIZE)]
        self.score = 0; self.lines_cleared = 0
    def can_place_shape(self, shape: Shape, x: int, y: int) -> bool:
        for bx, by in shape.blocks:
            gx, gy = x+bx, y+by
            if gx<0 or gx>=GRID_SIZE or gy<0 or gy>=GRID_SIZE or self.grid[gy][gx]!=0:
                return False
        return True
    def evaluate_placement(self, shape: Shape, x: int, y: int) -> float:
        score = 0.0
        for bx, by in shape.blocks:
            gx, gy = x+bx, y+by
            for dx, dy in [(0,-1),(1,0),(0,1),(-1,0)]:
                nx, ny = gx+dx, gy+dy
                if 0<=nx<GRID_SIZE and 0<=ny<GRID_SIZE and self.grid[ny][nx]!=0:
                    score += 1
        score += (GRID_SIZE - y) * 0.4
        temp = [row[:] for row in self.grid]
        for bx, by in shape.blocks:
            temp[y+by][x+bx] = 1
        lines = 0
        for row in temp:  # горизонтали
            if all(row): lines += 1
        for col in range(GRID_SIZE):  # вертикали
            if all(temp[r][col] for r in range(GRID_SIZE)): lines += 1
        score += lines * 10.0
        # штраф "карманов"
        holes = 0
        for gy in range(GRID_SIZE):
            for gx in range(GRID_SIZE):
                if temp[gy][gx]==0:
                    walls = 0
                    for dx, dy in [(0,-1),(1,0),(0,1),(-1,0)]:
                        nx, ny = gx+dx, gy+dy
                        if not (0<=nx<GRID_SIZE and 0<=ny<GRID_SIZE) or temp[ny][nx]==1:
                            walls += 1
                    if walls >= 3: holes += 1
        score -= holes * 0.8
        return score
    def find_best_placement(self, shape: Shape):
        best = (-1e9, -1, -1)
        for y in range(GRID_SIZE - shape.height + 1):
            for x in range(GRID_SIZE - shape.width + 1):
                if self.can_place_shape(shape, x, y):
                    s = self.evaluate_placement(shape, x, y)
                    if s > best[0]: best = (s, x, y)
        return None if best[1] == -1 else (best[1], best[2])
    def place_shape(self, shape: Shape, x: int, y: int, ps=None):
        if not self.can_place_shape(shape, x, y): return False
        for bx, by in shape.blocks:
            gx, gy = x+bx, y+by
            self.grid[gy][gx]=1; self.colors[gy][gx]=shape.color
            if ps:
                cx = GRID_OFFSET_X + gx*CELL_SIZE + CELL_SIZE//2
                cy = GRID_OFFSET_Y + gy*CELL_SIZE + CELL_SIZE//2
                ps.add_effect("shape_place", cx, cy, shape.color)
        self.clear_lines(ps); return True
    def clear_lines(self, ps=None):
        to_clear = []
        for y in range(GRID_SIZE):
            if all(self.grid[y]): to_clear.append(("h", y))
        for x in range(GRID_SIZE):
            if all(self.grid[y][x] for y in range(GRID_SIZE)): to_clear.append(("v", x))
        cleared = 0
        for t, idx in to_clear:
            if t == "h":
                for x in range(GRID_SIZE):
                    if ps and self.colors[idx][x]:
                        cx = GRID_OFFSET_X + x*CELL_SIZE + CELL_SIZE//2
                        cy = GRID_OFFSET_Y + idx*CELL_SIZE + CELL_SIZE//2
                        ps.add_effect("line_clear", cx, cy, self.colors[idx][x])
                    self.grid[idx][x]=0; self.colors[idx][x]=None
            else:
                for y in range(GRID_SIZE):
                    if ps and self.colors[y][idx]:
                        cx = GRID_OFFSET_X + idx*CELL_SIZE + CELL_SIZE//2
                        cy = GRID_OFFSET_Y + y*CELL_SIZE + CELL_SIZE//2
                        ps.add_effect("line_clear", cx, cy, self.colors[y][idx])
                    self.grid[y][idx]=0; self.colors[y][idx]=None
            cleared += 1
        if cleared:
            self.lines_cleared += cleared
            self.score += cleared*100
            if cleared >= 2:
                self.score += (cleared-1)*50
                if ps:
                    cx = GRID_OFFSET_X + GRID_SIZE*CELL_SIZE//2
                    cy = GRID_OFFSET_Y + GRID_SIZE*CELL_SIZE//2
                    ps.add_effect("combo", cx, cy)


# ---------- CODE-BATTLE ----------
class CodeBattle:
    def __init__(self, catalog: 'CodeBattleCatalog'):
        self.catalog = catalog
        self.current_challenge = None
        self.player_code = ""
        self.start_time = 0.0
        self.time_left = 0.0
        self.result = None
        self.cursor_visible = True; self.cursor_timer = 0
        self.cursor_position = 0; self.line_height = 25; self.scroll_offset = 0
        self.show_autocomplete = False; self.autocomplete_options = []; self.autocomplete_index = 0
        self.current_hint = 0
        self.keywords = ["def","return","if","else","elif","for","while","in","range","len","str","int","float","list","dict","True","False","None","and","or","not"]
        try:
            self.code_font = pygame.font.SysFont('consolas', 20)
        except:
            self.code_font = pygame.font.SysFont(None, 20)
        self.submit_button_rect = pygame.Rect(0,0,200,40)
        self.log = CodeBattleLog()

    def start_battle(self):
        self.current_challenge = self.catalog.random_challenge()
        if not self.current_challenge: return None
        self.player_code = self.current_challenge.get("template","")
        self.cursor_position = len(self.player_code)
        self.start_time = time.time(); self.time_left = float(self.current_challenge.get("time_limit",120))
        self.result = None; self.scroll_offset = 0; self.current_hint = 0
        return self.current_challenge

    def update_timer(self):
        if self.current_challenge and not self.result:
            elapsed = time.time() - self.start_time
            self.time_left = max(0, self.current_challenge["time_limit"] - elapsed)
            self.cursor_timer += 1
            if self.cursor_timer >= 30:
                self.cursor_visible = not self.cursor_visible; self.cursor_timer = 0
            if self.time_left <= 0:
                self.submit_solution()

    def handle_input(self, event):
        if not self.current_challenge or self.result: return False
        if event.type == pygame.KEYDOWN:
            mods = pygame.key.get_mods()
            if event.key == pygame.K_RETURN and (mods & pygame.KMOD_CTRL):
                self.submit_solution(); return True
            elif event.key == pygame.K_TAB:
                if self.show_autocomplete and self.autocomplete_options:
                    self.apply_autocomplete()
                else:
                    self._insert("    ")
                return True
            elif event.key == pygame.K_DOWN and self.show_autocomplete:
                self.autocomplete_index = (self.autocomplete_index+1)%len(self.autocomplete_options); return True
            elif event.key == pygame.K_UP and self.show_autocomplete:
                self.autocomplete_index = (self.autocomplete_index-1)%len(self.autocomplete_options); return True
            elif event.key == pygame.K_RETURN and self.show_autocomplete:
                self.apply_autocomplete(); return True
            elif event.key == pygame.K_RETURN:
                self._insert("\n"); return True
            elif event.key == pygame.K_BACKSPACE:
                if self.cursor_position>0:
                    self.player_code = self.player_code[:self.cursor_position-1] + self.player_code[self.cursor_position:]
                    self.cursor_position -= 1; self.check_autocomplete()
                return True
            elif event.key == pygame.K_LEFT:
                self.cursor_position = max(0, self.cursor_position-1); self.show_autocomplete=False; return True
            elif event.key == pygame.K_RIGHT:
                self.cursor_position = min(len(self.player_code), self.cursor_position+1); self.show_autocomplete=False; return True
            elif event.key == pygame.K_HOME:
                lines = self.player_code[:self.cursor_position].split('\n')
                self.cursor_position -= len(lines[-1]); return True
            elif event.key == pygame.K_END:
                lines = self.player_code[self.cursor_position:].split('\n',1)
                if lines: self.cursor_position += len(lines[0]); return True
            elif event.unicode and event.unicode.isprintable():
                self._insert(event.unicode); self.check_autocomplete(); return True
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.submit_button_rect.collidepoint(event.pos):
                self.submit_solution(); return True
        return False

    def _insert(self, s: str):
        self.player_code = self.player_code[:self.cursor_position] + s + self.player_code[self.cursor_position:]
        self.cursor_position += len(s)

    def check_autocomplete(self):
        if self.cursor_position == 0: self.show_autocomplete = False; return
        cur = self.player_code[:self.cursor_position]; last_word = ""
        for i in range(self.cursor_position-1, -1, -1):
            if cur[i].isalnum() or cur[i]=='_':
                last_word = cur[i] + last_word
            else:
                break
        if len(last_word)>=2:
            self.autocomplete_options = [kw for kw in self.keywords if kw.startswith(last_word)]
            self.show_autocomplete = len(self.autocomplete_options)>0; self.autocomplete_index=0
        else:
            self.show_autocomplete = False

    def apply_autocomplete(self):
        if not self.show_autocomplete or not self.autocomplete_options: return
        selected = self.autocomplete_options[self.autocomplete_index]
        cur = self.player_code[:self.cursor_position]; start = self.cursor_position
        for i in range(self.cursor_position-1, -1, -1):
            if not (cur[i].isalnum() or cur[i]=='_'):
                start = i+1; break
            if i==0: start = 0; break
        self.player_code = self.player_code[:start] + selected + self.player_code[self.cursor_position:]
        self.cursor_position = start + len(selected); self.show_autocomplete=False

    def safe_execute(self, code, tests):
        safe_builtins = {
            'len': len, 'range': range, 'str': str, 'int': int, 'float': float,
            'bool': bool, 'list': list, 'tuple': tuple, 'dict': dict, 'set': set,
            'sum': sum, 'min': min, 'max': max
        }
        local_vars = {}
        try:
            exec(code, {"__builtins__": safe_builtins}, local_vars)
            func = None
            for v in local_vars.values():
                if callable(v): func = v; break
            if not func: return False, "Функция не найдена"
            for i, tc in enumerate(tests, 1):
                res = func(*tc.get("input", []))
                if res != tc.get("expected", None):
                    return False, f"Тест {i} не пройден: ожидалось {tc['expected']}, получено {res}"
            return True, "Все тесты пройдены!"
        except Exception as e:
            return False, f"Ошибка выполнения: {e}"

    def submit_solution(self):
        if not self.current_challenge or self.result: return
        ok, msg = self.safe_execute(self.player_code, self.current_challenge.get("test_cases", []))
        self.result = {"success": ok, "message": msg, "reward": self.current_challenge.get("reward",0) if ok else 0}
        self.log.add_item(self.current_challenge, self.player_code, ok, msg, self.result["reward"], time.time()-self.start_time)

    def draw(self, surface, ps):
        if not self.current_challenge: return
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); overlay.fill((0,0,0,200))
        surface.blit(overlay, (0,0))
        battle_rect = pygame.Rect(100, 50, SCREEN_WIDTH-200, SCREEN_HEIGHT-100)
        pygame.draw.rect(surface, CODE_EDITOR_BG, battle_rect, border_radius=15)
        pygame.draw.rect(surface, HIGHLIGHT_COLOR, battle_rect, 3, border_radius=15)
        try:
            title_font = pygame.font.SysFont('consolas', 32, bold=True)
            font_24 = pygame.font.SysFont('consolas', 24)
            font_18 = pygame.font.SysFont('consolas', 18)
        except:
            title_font = pygame.font.SysFont(None, 32)
            font_24 = pygame.font.SysFont(None, 24)
            font_18 = pygame.font.SysFont(None, 18)
        title = title_font.render("КОД-БАТТЛ!", True, HIGHLIGHT_COLOR)
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 70))
        name_text = font_24.render(f"Задача: {self.current_challenge['name']}", True, TEXT_COLOR)
        desc_text = font_18.render(self.current_challenge['description'], True, TEXT_COLOR)
        surface.blit(name_text, (120, 120)); surface.blit(desc_text, (120, 150))
        time_text = font_24.render(f"Время: {int(self.time_left)} сек", True, TEXT_COLOR)
        reward_text = font_24.render(f"Награда: {self.current_challenge['reward']} очков", True, CORRECT_COLOR)
        surface.blit(time_text, (SCREEN_WIDTH-300, 120)); surface.blit(reward_text, (SCREEN_WIDTH-300, 150))
        code_rect = pygame.Rect(120, 200, SCREEN_WIDTH-240, 300)
        pygame.draw.rect(surface, (20,25,35), code_rect, border_radius=10)
        pygame.draw.rect(surface, GRID_HIGHLIGHT, code_rect, 2, border_radius=10)
        lines = self.player_code.split('\n'); visible = 12
        start = max(0, min(self.scroll_offset, len(lines)-visible)); end = min(len(lines), start+visible)
        for i in range(start, end):
            y = 210 + (i-start)*self.line_height
            ln_text = self.code_font.render(str(i+1), True, CODE_LINE_NUMBERS)
            surface.blit(ln_text, (130, y))
            txt = self.code_font.render(lines[i], True, CODE_EDITOR_TEXT)
            surface.blit(txt, (160, y))
        if self.cursor_visible and not self.result:
            cur_line = self.player_code[:self.cursor_position].count('\n')
            if start <= cur_line < end:
                ls = self.player_code.rfind('\n', 0, self.cursor_position)
                ls = 0 if ls==-1 else ls+1
                col = self.cursor_position - ls
                cursor_x = 160 + self.code_font.size(lines[cur_line][:col])[0]
                cursor_y = 210 + (cur_line-start)*self.line_height
                pygame.draw.line(surface, CODE_EDITOR_TEXT, (cursor_x, cursor_y), (cursor_x, cursor_y+self.line_height), 2)
        if self.show_autocomplete and self.autocomplete_options:
            ac_rect = pygame.Rect(160, 210+self.line_height, 200, len(self.autocomplete_options)*self.line_height)
            pygame.draw.rect(surface, (40,45,60), ac_rect); pygame.draw.rect(surface, GRID_HIGHLIGHT, ac_rect, 1)
            for i, opt in enumerate(self.autocomplete_options):
                color = HIGHLIGHT_COLOR if i==self.autocomplete_index else TEXT_COLOR
                surface.blit(self.code_font.render(opt, True, color), (165, 215+self.line_height + i*self.line_height))
        hints = self.current_challenge.get("hints", [])
        if hints:
            hint_rect = pygame.Rect(120, 520, SCREEN_WIDTH-240, 60)
            pygame.draw.rect(surface, (30,35,45), hint_rect, border_radius=8)
            pygame.draw.rect(surface, GRID_HIGHLIGHT, hint_rect, 1, border_radius=8)
            ht = self.code_font.render(f"Подсказка: {hints[self.current_hint % len(hints)]}", True, TEXT_COLOR)
            surface.blit(ht, (130, 540))
        self.submit_button_rect = pygame.Rect(SCREEN_WIDTH-320, 520, 200, 40)
        pygame.draw.rect(surface, BTN_BLUE, self.submit_button_rect, border_radius=8)
        pygame.draw.rect(surface, HIGHLIGHT_COLOR, self.submit_button_rect, 2, border_radius=8)
        st = self.code_font.render("Отправить (Ctrl+Enter)", True, TEXT_COLOR)
        surface.blit(st, (self.submit_button_rect.centerx - st.get_width()//2, self.submit_button_rect.centery - st.get_height()//2))
        if self.result:
            res_rect = pygame.Rect(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 50, 400, 100)
            color = CORRECT_COLOR if self.result["success"] else WRONG_COLOR
            pygame.draw.rect(surface, PANEL_BG, res_rect, border_radius=10)
            pygame.draw.rect(surface, color, res_rect, 3, border_radius=10)
            try: rf = pygame.font.SysFont('consolas', 24, bold=True)
            except: rf = pygame.font.SysFont(None, 24)
            res_text = rf.render("УСПЕХ!" if self.result["success"] else "НЕУДАЧА", True, color)
            msg_text = self.code_font.render(self.result["message"], True, TEXT_COLOR)
            surface.blit(res_text, (SCREEN_WIDTH//2 - res_text.get_width()//2, SCREEN_HEIGHT//2 - 30))
            surface.blit(msg_text, (SCREEN_WIDTH//2 - msg_text.get_width()//2, SCREEN_HEIGHT//2 + 10))
            if self.result["success"]:
                for _ in range(6):
                    x = random.randint(SCREEN_WIDTH//2 - 100, SCREEN_WIDTH//2 + 100)
                    y = random.randint(SCREEN_HEIGHT//2 - 50, SCREEN_HEIGHT//2 + 50)
                    ps.add_effect("code_success", x, y)


# ---------- АРХИВ ----------
class ArchiveScreen:
    def __init__(self, screen, catalog: CodeBattleCatalog):
        self.screen = screen; self.catalog = catalog; self.index = 0
        try:
            self.title_font = pygame.font.SysFont('consolas', 36, bold=True)
            self.font = pygame.font.SysFont('consolas', 24)
            self.small = pygame.font.SysFont('consolas', 18)
        except:
            self.title_font = pygame.font.SysFont(None, 36)
            self.font = pygame.font.SysFont(None, 24)
            self.small = pygame.font.SysFont(None, 18)
    def handle(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return "menu"
                elif event.key == pygame.K_RIGHT: self.index = (self.index+1) % max(1, len(self.catalog.items))
                elif event.key == pygame.K_LEFT: self.index = (self.index-1) % max(1, len(self.catalog.items))
        return None
    def draw(self):
        self.screen.fill(MENU_BG)
        title = self.title_font.render("АРХИВ (все задачи каталога)", True, HIGHLIGHT_COLOR)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 30))
        if not self.catalog.items:
            txt = self.font.render("Каталог пуст. Добавьте задачи в data/code_battles_catalog.json", True, TEXT_COLOR)
            self.screen.blit(txt, (SCREEN_WIDTH//2 - txt.get_width()//2, SCREEN_HEIGHT//2))
            pygame.display.flip(); return
        item = self.catalog.items[self.index]
        panel = pygame.Rect(100, 100, SCREEN_WIDTH-200, SCREEN_HEIGHT-160)
        pygame.draw.rect(self.screen, PANEL_BG, panel, border_radius=12)
        pygame.draw.rect(self.screen, GRID_HIGHLIGHT, panel, 2, border_radius=12)
        lines = [
            f"{self.index+1}/{len(self.catalog.items)}  •  {item.get('name','')}",
            f"Сложность: {item.get('difficulty','n/a')}   •   Награда: {item.get('reward',0)}   •   Лимит: {item.get('time_limit',0)}с",
            "",
            f"Описание: {item.get('description','')}",
            "",
            "Решение:",
        ]
        y = 120
        for L in lines:
            t = self.font.render(L, True, TEXT_COLOR); self.screen.blit(t, (120, y)); y += 30
        solution = item.get("solution", "")
        for line in solution.split("\n"):
            t = self.small.render(line, True, (200,220,255)); self.screen.blit(t, (140, y)); y += 22
        y += 10
        self.screen.blit(self.font.render("Объяснение:", True, TEXT_COLOR), (120, y)); y += 30
        for line in wrap_text(item.get("explanation",""), self.small, SCREEN_WIDTH-240):
            self.screen.blit(self.small.render(line, True, TEXT_COLOR), (140, y)); y += 22
        hint = self.small.render("← / → листать, ESC — в меню", True, TEXT_COLOR)
        self.screen.blit(hint, (SCREEN_WIDTH//2 - hint.get_width()//2, SCREEN_HEIGHT-50))
        pygame.display.flip()


# ---------- МЕНЮ ----------
class MainMenu:
    def __init__(self, screen, game_data, leaderboard=None):
        self.last_fetch_ts = 0.0
        self.top_cache = {"nub": [], "pro": []}
        self.screen = screen
        self.game_data = game_data
        self.leaderboard = leaderboard
        try:
            self.title_font = pygame.font.SysFont('consolas', 48, bold=True)
            self.font = pygame.font.SysFont('consolas', 32)
            self.small_font = pygame.font.SysFont('consolas', 24)
        except:
            self.title_font = pygame.font.SysFont(None, 48)
            self.font = pygame.font.SysFont(None, 32)
            self.small_font = pygame.font.SysFont(None, 24)

        # Базовая геометрия
        start_w, start_h = 360, 66
        start_x = SCREEN_WIDTH // 2 - start_w // 2
        start_y = 300

        # Центр 
        self.start_button = Button(start_x, start_y, start_w, start_h,
                                   "Начать игру", "start",
                                   color=BTN_GREEN, color_hover=BTN_GREEN_H)

        # Маленькие иконки
        icon_size = 60
        gap = 14
        self.leaderboard_button = Button(self.start_button.rect.x - icon_size - gap,
                                         self.start_button.rect.y + (start_h - icon_size)//2,
                                         icon_size, icon_size, "",
                                         "leaderboard", color=BTN_BLUE, color_hover=BTN_BLUE_H, icon="table")

        self.achievements_button = Button(self.start_button.rect.right + gap,
                                          self.start_button.rect.y + (start_h - icon_size)//2,
                                          icon_size, icon_size, "",
                                          "achievements", color=BTN_YELLOW, color_hover=BTN_YELLOW_H, icon="trophy")

        # Тумблер НУБ/ПРО 
        toggle_w, toggle_h = 140, 44
        self.mode_button = Button(SCREEN_WIDTH//2 - toggle_w//2,
                                  self.start_button.rect.bottom + 14,
                                  toggle_w, toggle_h, "НУБ", "toggle_mode",
                                  font_size=24, color=BTN_TOGGLE, color_hover=BTN_TOGGLE_H)

        # Архив 
        self.archive_button = Button(SCREEN_WIDTH - 180, SCREEN_HEIGHT - 70, 150, 50,
                                     "Архив", "archive", color=BTN_GREY, color_hover=BTN_GREY_H)

        self.current_screen = "main"
        self.pro_mode = False  # False = НУБ; True = ПРО

    def handle_events(self):
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if self.current_screen in ("achievements", "leaderboard"):
                    self.current_screen = "main"
                else:
                    return "quit"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.current_screen == "main":
                    for btn in [self.start_button, self.mode_button,
                                self.achievements_button, self.leaderboard_button, self.archive_button]:
                        res = btn.check_click(mouse)
                        if res == "start":
                            return "start"
                        if res == "toggle_mode":
                            self.pro_mode = not self.pro_mode
                            self.mode_button.text = "ПРО" if self.pro_mode else "НУБ"
                        if res == "achievements":
                            self.current_screen = "achievements"
                        if res == "leaderboard":
                            self.current_screen = "leaderboard"
                        if res == "archive":
                            return "archive"
                else:
                    # кликом выходим из экранов в главное меню
                    self.current_screen = "main"

        if self.current_screen == "main":
            for btn in [self.start_button, self.mode_button,
                        self.achievements_button, self.leaderboard_button, self.archive_button]:
                btn.check_hover(mouse)
        return None

    def draw(self):
        self.screen.fill(MENU_BG)
        if self.current_screen == "main":
            self._draw_main()
        elif self.current_screen == "achievements":
            self._draw_achievements()
        elif self.current_screen == "leaderboard":
            self._draw_leaderboard()
        pygame.display.flip()

    def _draw_main(self):
        title = self.title_font.render("Python Blaster", True, HIGHLIGHT_COLOR)
        subtitle = self.font.render("Code & Clear", True, TEXT_COLOR)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))
        self.screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 210))

        hs = self.small_font.render(f"Рекорд: {self.game_data.data['high_score']}", True, TEXT_COLOR)
        self.screen.blit(hs, (SCREEN_WIDTH // 2 - hs.get_width() // 2, 250))

        # Кнопки по макету
        self.leaderboard_button.draw(self.screen)   
        self.start_button.draw(self.screen)         
        self.achievements_button.draw(self.screen)  
        self.mode_button.draw(self.screen)          
        self.archive_button.draw(self.screen)       


    def _draw_achievements(self):
        title = self.title_font.render("Достижения", True, HIGHLIGHT_COLOR)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 60))
        stats = [
            f"Сыграно игр: {self.game_data.data['games_played']}",
            f"Рекорд: {self.game_data.data['high_score']}",
            f"Всего линий: {self.game_data.data['total_lines_cleared']}",
            f"Отвечено вопросов: {self.game_data.data['total_questions_answered']}",
            f"Правильных ответов: {self.game_data.data['total_correct_answers']}",
            f"Код-баттлов: {self.game_data.data['total_code_battles_completed']}"
        ]
        y = 130
        for s in stats:
            t = self.font.render(s, True, TEXT_COLOR)
            self.screen.blit(t, (SCREEN_WIDTH//2 - t.get_width()//2, y)); y += 40
        a = self.game_data.data["achievements"]
        pairs = [
            ("🎮 Первая игра", a["first_game"]),
            ("🏆 500 очков", a["score_500"]),
            ("🏆 1000 очков", a["score_1000"]),
            ("🏆 2000 очков", a["score_2000"]),
            ("📊 10 линий", a["clear_10_lines"]),
            ("📊 25 линий", a["clear_25_lines"]),
            ("❓ 5 вопросов", a["answer_5_questions"]),
            ("❓ 10 вопросов", a["answer_10_questions"]),
            ("💻 5 код-баттлов", a["complete_5_code_battles"]),
            ("💻 10 код-баттлов", a["complete_10_code_battles"]),
        ]
        y = 400
        for i, (name, ok) in enumerate(pairs):
            color = CORRECT_COLOR if ok else (120,120,120)
            t = self.small_font.render(name, True, color)
            x = SCREEN_WIDTH//2 - 150 + (i%2)*300; yy = y + (i//2)*28
            self.screen.blit(t, (x, yy))
        back = self.small_font.render("Клик/ESC — назад", True, TEXT_COLOR)
        self.screen.blit(back, (SCREEN_WIDTH//2 - back.get_width()//2, 620))

    def _draw_leaderboard(self):
        title = self.title_font.render("Таблица лидеров (НУБ / ПРО)", True, HIGHLIGHT_COLOR)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 60))

        now = time.time()
        if self.leaderboard and now - self.last_fetch_ts > 5:
            for mode in ("nub", "pro"):
                ok, data = self.leaderboard.fetch_top_mode(mode, limit=10)
                self.top_cache[mode] = data if ok else []
            self.last_fetch_ts = now

        # две панели
        panel_w = (SCREEN_WIDTH - 300)//2
        left_panel = pygame.Rect(120, 130, panel_w, SCREEN_HEIGHT-250)
        right_panel = pygame.Rect(160+panel_w, 130, panel_w, SCREEN_HEIGHT-250)

        for rect, name in [(left_panel, "НУБ"), (right_panel, "ПРО")]:
            pygame.draw.rect(self.screen, PANEL_BG, rect, border_radius=12)
            pygame.draw.rect(self.screen, GRID_HIGHLIGHT, rect, 2, border_radius=12)
            cap = self.small_font.render(name, True, TEXT_COLOR)
            self.screen.blit(cap, (rect.centerx - cap.get_width()//2, rect.y + 12))
            header = self.small_font.render("№   Имя             Очки", True, TEXT_COLOR)
            self.screen.blit(header, (rect.x + 16, rect.y + 40))
            y = rect.y + 70
            rows = self.top_cache["nub" if name=="НУБ" else "pro"] or []
            if not rows:
                msg = self.small_font.render("Нет данных / оффлайн", True, WRONG_COLOR)
                self.screen.blit(msg, (rect.x + 16, y))
            else:
                for i, row in enumerate(rows, 1):
                    line = f"{i:>2}.  {row.get('name','')[:14]:<14}  {int(row.get('score',0)):<6}"
                    t = self.small_font.render(line, True, TEXT_COLOR)
                    self.screen.blit(t, (rect.x + 16, y)); y += 28

        back = self.small_font.render("Клик/ESC — назад", True, TEXT_COLOR)
        self.screen.blit(back, (SCREEN_WIDTH//2 - back.get_width()//2, 620))


# ---------- ИГРА ----------
class Game:
    def __init__(self, game_data: GameData, pro_mode: bool, leaderboard: OnlineLeaderboard):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Python Blaster: Code & Clear")
        self.clock = pygame.time.Clock()
        try:
            self.title_font = pygame.font.SysFont('consolas', 36, bold=True)
            self.font = pygame.font.SysFont('consolas', 24)
            self.small_font = pygame.font.SysFont('consolas', 18)
        except:
            self.title_font = pygame.font.SysFont(None, 36)
            self.font = pygame.font.SysFont(None, 24)
            self.small_font = pygame.font.SysFont(None, 18)

        self.board = GameBoard()
        self.quiz_engine = QuizEngine()
        self.catalog = CodeBattleCatalog()
        self.code_battle = CodeBattle(self.catalog)
        self.particle_system = ParticleSystem()

        self.current_shapes: List[Shape] = [Shape(difficulty="easy") for _ in range(3)]
        self.game_over = False
        self.show_quiz = False
        self.show_code_battle = False
        self.current_question = None
        self.quiz_result = None

        self.game_data = game_data
        self.questions_answered_this_game = 0
        self.correct_answers_this_game = 0
        self.lines_cleared_this_game = 0
        self.code_battles_completed_this_game = 0

        self.dragging = False; self.dragged_shape = None; self.dragged_shape_index = None
        self.drag_offset_x = 0; self.drag_offset_y = 0
        self.ghost_position = None; self.snap_position = None

        self.quiz_interval = 5; self.code_battle_interval = 5; self.last_event_lines = 0

        self.panel_rect = pygame.Rect(50, 150, 300, 400)
        self.difficulty = "easy"
        self.pro_mode = pro_mode
        self.leaderboard = leaderboard

        # Ввод имени для онлайна
        self.name_input = ""; self.ask_name = False; self.submitted_score = False

    def handle_events(self) -> str:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "quit"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: return "menu"

            if self.game_over:
                if self.ask_name:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            if self.name_input.strip():
                                mode = "pro" if self.pro_mode else "nub"
                                ok, _ = self.leaderboard.update_if_better(
                                    name=self.name_input.strip(),
                                    score=self.board.score,
                                    mode=mode
                                )
                                self.submitted_score = ok; self.ask_name = False
                        elif event.key == pygame.K_BACKSPACE:
                            self.name_input = self.name_input[:-1]
                        else:
                            if event.unicode and (event.unicode.isalnum() or event.unicode in "_- "):
                                if len(self.name_input) < 12:
                                    self.name_input += event.unicode
                    continue
                else:
                    if event.type == pygame.KEYDOWN and (event.key == pygame.K_r or event.key == pygame.K_SPACE):
                        return "menu"
                continue

            if self.show_code_battle:
                if self.code_battle.handle_input(event): continue
                if event.type == pygame.KEYDOWN and event.key == pygame.K_h:
                    self.code_battle.current_hint += 1; continue
                if event.type == pygame.KEYDOWN and self.code_battle.result:
                    if self.code_battle.result["success"]:
                        self.board.score += self.code_battle.result["reward"]
                        self.code_battles_completed_this_game += 1
                    self.show_code_battle = False; self.code_battle.result = None
                continue

            if self.show_quiz:
                if self.quiz_result:
                    if event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.KEYDOWN and event.key != pygame.K_r):
                        self.quiz_result = None; self.show_quiz = False; self.current_question = None
                elif event.type == pygame.KEYDOWN and event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                    self.check_quiz_answer(event.key - pygame.K_1)
                continue

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for i, shape in enumerate(self.current_shapes):
                    sx, sy = self.get_shape_panel_position(i, shape)
                    rect = pygame.Rect(sx, sy, shape.width*PANEL_CELL_SIZE, shape.height*PANEL_CELL_SIZE)
                    if rect.collidepoint(mx, my):
                        self.dragging = True; self.dragged_shape = shape; self.dragged_shape_index = i
                        self.drag_offset_x = mx - rect.x; self.drag_offset_y = my - rect.y
                        self.ghost_position = None; self.snap_position = None; break

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.dragging and self.dragged_shape:
                    mx, my = event.pos
                    if not self.panel_rect.collidepoint(mx, my):
                        pos = self.snap_position if self.snap_position is not None else self.ghost_position
                        if pos is None:
                            gx = (mx - GRID_OFFSET_X - self.drag_offset_x)//CELL_SIZE
                            gy = (my - GRID_OFFSET_Y - self.drag_offset_y)//CELL_SIZE
                        else:
                            gx, gy = pos
                        gx = max(0, min(GRID_SIZE - self.dragged_shape.width, gx))
                        gy = max(0, min(GRID_SIZE - self.dragged_shape.height, gy))
                        if self.board.place_shape(self.dragged_shape, gx, gy, self.particle_system):
                            if self.board.score > 1200: self.difficulty = "hard"
                            elif self.board.score > 500: self.difficulty = "normal"
                            if self.dragged_shape_index is not None:
                                self.current_shapes[self.dragged_shape_index] = Shape(difficulty=self.difficulty)
                            self.lines_cleared_this_game = self.board.lines_cleared
                            if (self.board.lines_cleared >= self.last_event_lines + self.code_battle_interval and
                                self.board.lines_cleared > 0):
                                self.last_event_lines = self.board.lines_cleared
                                if self.pro_mode:
                                    if random.random() < 0.5:
                                        self.show_code_battle = True; self.code_battle.start_battle()
                                    else:
                                        self.show_quiz = True; self.current_question = self.quiz_engine.get_random_question()
                                else:
                                    self.show_quiz = True; self.current_question = self.quiz_engine.get_random_question()
                    self.dragging = False; self.dragged_shape = None; self.dragged_shape_index = None
                    self.ghost_position = None; self.snap_position = None

            elif event.type == pygame.MOUSEMOTION:
                if self.dragging and self.dragged_shape:
                    mx, my = event.pos
                    gx = (mx - GRID_OFFSET_X - self.drag_offset_x)//CELL_SIZE
                    gy = (my - GRID_OFFSET_Y - self.drag_offset_y)//CELL_SIZE
                    gx = max(0, min(GRID_SIZE - self.dragged_shape.width, gx))
                    gy = max(0, min(GRID_SIZE - self.dragged_shape.height, gy))
                    if not self.board.can_place_shape(self.dragged_shape, gx, gy):
                        self.snap_position = self.find_nearby_placement(gx, gy); self.ghost_position = self.snap_position
                    else:
                        self.ghost_position = (gx, gy); self.snap_position = None

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.current_shapes = [Shape(difficulty=self.difficulty) for _ in range(3)]

        return None

    def get_shape_panel_position(self, index: int, shape: Shape) -> Tuple[int, int]:
        slot_h = self.panel_rect.height // 3
        y_off = self.panel_rect.y + index*slot_h + (slot_h - shape.height*PANEL_CELL_SIZE)//2
        x_off = self.panel_rect.x + (self.panel_rect.width - shape.width*PANEL_CELL_SIZE)//2
        return x_off, y_off

    def find_nearby_placement(self, x: int, y: int, r: int=2):
        if self.dragged_shape is None: return None
        for dy in range(-r, r+1):
            for dx in range(-r, r+1):
                tx, ty = x+dx, y+dy
                if 0<=tx<=GRID_SIZE-self.dragged_shape.width and 0<=ty<=GRID_SIZE-self.dragged_shape.height:
                    if self.board.can_place_shape(self.dragged_shape, tx, ty):
                        return (tx, ty)
        return self.board.find_best_placement(self.dragged_shape)

    def check_quiz_answer(self, idx: int):
        if not self.current_question: return
        self.questions_answered_this_game += 1
        if idx == self.current_question["correct"]:
            self.quiz_result = {"correct": True, "message": "ПРАВИЛЬНО!", "color": CORRECT_COLOR}
            self.correct_answers_this_game += 1; self.board.score += 50
        else:
            self.quiz_result = {"correct": False, "message": "НЕПРАВИЛЬНО!", "color": WRONG_COLOR,
                                "explanation": self.current_question.get("explanation","")}

    def reset_game(self):
        self.board.reset()
        self.current_shapes = [Shape(difficulty="easy") for _ in range(3)]
        self.game_over = False; self.show_quiz = False; self.show_code_battle = False
        self.quiz_result = None; self.dragging = False; self.dragged_shape = None
        self.dragged_shape_index = None; self.ghost_position = None; self.snap_position = None
        self.difficulty = "easy"; self.questions_answered_this_game = 0; self.correct_answers_this_game = 0
        self.lines_cleared_this_game = 0; self.code_battles_completed_this_game = 0
        self.last_event_lines = 0; self.particle_system.particles.clear()
        self.name_input = ""; self.ask_name = False; self.submitted_score = False

    def draw(self):
        self.screen.fill(BACKGROUND)
        self.particle_system.update()

        title = self.title_font.render("Python Blaster: Code & Clear", True, TEXT_COLOR)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 20))
        self.draw_board(); self.draw_panel(); self.draw_score()

        self.particle_system.draw(self.screen)
        if self.show_code_battle:
            self.code_battle.update_timer(); self.code_battle.draw(self.screen, self.particle_system)
        if self.show_quiz and self.current_question:
            if self.quiz_result: self.draw_quiz_result()
            else: self.draw_quiz()
        if self.game_over: self.draw_game_over()

        pygame.display.flip()

    def draw_board(self):
        grid_bg = pygame.Rect(GRID_OFFSET_X-10, GRID_OFFSET_Y-10, GRID_SIZE*CELL_SIZE+20, GRID_SIZE*CELL_SIZE+20)
        pygame.draw.rect(self.screen, PANEL_BG, grid_bg, border_radius=10)
        pygame.draw.rect(self.screen, GRID_HIGHLIGHT, grid_bg, 3, border_radius=10)
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                rect = pygame.Rect(GRID_OFFSET_X + x*CELL_SIZE, GRID_OFFSET_Y + y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, GRID_COLOR, rect, 1)
                if self.board.grid[y][x]:
                    cell_rect = pygame.Rect(rect.x+1, rect.y+1, CELL_SIZE-2, CELL_SIZE-2)
                    pygame.draw.rect(self.screen, self.board.colors[y][x], cell_rect, border_radius=4)
                    pygame.draw.rect(self.screen, HIGHLIGHT_COLOR, cell_rect, 2, border_radius=4)
        if self.dragging and self.dragged_shape and self.ghost_position is not None:
            gx, gy = self.ghost_position
            self.dragged_shape.draw(self.screen, GRID_OFFSET_X + gx*CELL_SIZE, GRID_OFFSET_Y + gy*CELL_SIZE, is_ghost=True)

    def draw_panel(self):
        pygame.draw.rect(self.screen, PANEL_BG, self.panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, GRID_HIGHLIGHT, self.panel_rect, 2, border_radius=10)
        t = self.font.render("Доступные фигуры:", True, TEXT_COLOR)
        self.screen.blit(t, (self.panel_rect.x + 10, 120))
        for i, shape in enumerate(self.current_shapes):
            if self.dragging and i == self.dragged_shape_index: continue
            sx, sy = self.get_shape_panel_position(i, shape)
            shape.draw(self.screen, sx, sy, in_panel=True)
        if self.dragging and self.dragged_shape:
            mx, my = pygame.mouse.get_pos()
            dx, dy = mx - self.drag_offset_x, my - self.drag_offset_y
            valid = False
            if self.ghost_position is not None:
                gx, gy = self.ghost_position
                valid = self.board.can_place_shape(self.dragged_shape, gx, gy)
            self.dragged_shape.draw(self.screen, dx, dy, alpha=200, show_placement_hint=True, valid_placement=valid)

    def draw_score(self):
        score_panel = pygame.Rect(SCREEN_WIDTH - 280, 120, 250, 120)
        pygame.draw.rect(self.screen, PANEL_BG, score_panel, border_radius=10)
        pygame.draw.rect(self.screen, GRID_HIGHLIGHT, score_panel, 2, border_radius=10)
        score_text = self.font.render(f"Счёт: {self.board.score}", True, TEXT_COLOR)
        lines_text = self.font.render(f"Линии: {self.board.lines_cleared}", True, TEXT_COLOR)
        next_event = max(0, self.last_event_lines + 5 - self.board.lines_cleared)
        next_event_text = self.small_font.render(f"След. событие: {next_event}", True, TEXT_COLOR)
        difficulty_text = self.small_font.render(f"Сложность: {self.difficulty}", True, TEXT_COLOR)
        mode_text = self.small_font.render(f"Режим: {'ПРО' if self.pro_mode else 'НУБ'}", True, TEXT_COLOR)
        self.screen.blit(score_text, (SCREEN_WIDTH - 260, 140))
        self.screen.blit(lines_text, (SCREEN_WIDTH - 260, 170))
        self.screen.blit(next_event_text, (SCREEN_WIDTH - 260, 200))
        self.screen.blit(difficulty_text, (SCREEN_WIDTH - 260, 220))
        self.screen.blit(mode_text, (SCREEN_WIDTH - 260, 240))

        instructions_panel = pygame.Rect(SCREEN_WIDTH - 280, 260, 250, 180)
        pygame.draw.rect(self.screen, PANEL_BG, instructions_panel, border_radius=10)
        pygame.draw.rect(self.screen, GRID_HIGHLIGHT, instructions_panel, 2, border_radius=10)
        for i, line in enumerate(["Управление:", "Клик и перетаскивание","ESC — меню"]):
            self.screen.blit(self.small_font.render(line, True, TEXT_COLOR), (SCREEN_WIDTH - 260, 280 + i*25))

    def draw_quiz(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); overlay.fill((0,0,0,200))
        self.screen.blit(overlay, (0,0))
        quiz_rect = pygame.Rect(200, 150, 1000, 400)
        pygame.draw.rect(self.screen, PANEL_BG, quiz_rect, border_radius=15)
        pygame.draw.rect(self.screen, HIGHLIGHT_COLOR, quiz_rect, 3, border_radius=15)
        question_text = self.font.render("Вопрос по Python:", True, TEXT_COLOR)
        self.screen.blit(question_text, (SCREEN_WIDTH//2 - question_text.get_width()//2, 180))
        lines = wrap_text(self.current_question["question"], self.small_font, 740)
        for i, line in enumerate(lines):
            t = self.small_font.render(line, True, TEXT_COLOR)
            self.screen.blit(t, (SCREEN_WIDTH//2 - t.get_width()//2, 220 + i*25))
        y = 220 + len(lines)*25 + 20
        for i, opt in enumerate(self.current_question["options"]):
            t = self.small_font.render(f"{i+1}. {opt}", True, TEXT_COLOR)
            self.screen.blit(t, (SCREEN_WIDTH//2 - t.get_width()//2, y + i*30))
        hint = self.small_font.render("Нажмите 1–4 для ответа", True, TEXT_COLOR)
        self.screen.blit(hint, (SCREEN_WIDTH//2 - hint.get_width()//2, y + 150))

    def draw_quiz_result(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); overlay.fill((0,0,0,200))
        self.screen.blit(overlay, (0,0))
        result_rect = pygame.Rect(300, 200, 800, 300)
        pygame.draw.rect(self.screen, PANEL_BG, result_rect, border_radius=15)
        pygame.draw.rect(self.screen, self.quiz_result["color"], result_rect, 3, border_radius=15)
        res = self.title_font.render(self.quiz_result["message"], True, self.quiz_result["color"])
        self.screen.blit(res, (SCREEN_WIDTH//2 - res.get_width()//2, 250))
        if not self.quiz_result["correct"]:
            for i, line in enumerate(wrap_text(self.quiz_result.get("explanation",""), self.small_font, 550)):
                t = self.small_font.render(line, True, TEXT_COLOR)
                self.screen.blit(t, (SCREEN_WIDTH//2 - t.get_width()//2, 320 + i*25))
        instruct = self.small_font.render("Нажмите любую клавишу", True, TEXT_COLOR)
        self.screen.blit(instruct, (SCREEN_WIDTH//2 - instruct.get_width()//2, 450))

    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); overlay.fill((0,0,0,220))
        self.screen.blit(overlay, (0,0))
        panel = pygame.Rect(SCREEN_WIDTH//2 - 220, SCREEN_HEIGHT//2 - 170, 440, 320)
        pygame.draw.rect(self.screen, PANEL_BG, panel, border_radius=15)
        pygame.draw.rect(self.screen, WRONG_COLOR, panel, 3, border_radius=15)
        go = self.title_font.render("ИГРА ОКОНЧЕНА", True, WRONG_COLOR)
        score = self.font.render(f"Счёт: {self.board.score}", True, TEXT_COLOR)
        lines = self.font.render(f"Линии: {self.board.lines_cleared}", True, TEXT_COLOR)
        self.screen.blit(go, (SCREEN_WIDTH//2 - go.get_width()//2, SCREEN_HEIGHT//2 - 120))
        self.screen.blit(score, (SCREEN_WIDTH//2 - score.get_width()//2, SCREEN_HEIGHT//2 - 70))
        self.screen.blit(lines, (SCREEN_WIDTH//2 - lines.get_width()//2, SCREEN_HEIGHT//2 - 40))
        if self.ask_name:
            prompt = self.small_font.render("Введите имя (до 12) и Enter — отправить рекорд:", True, TEXT_COLOR)
            self.screen.blit(prompt, (SCREEN_WIDTH//2 - prompt.get_width()//2, SCREEN_HEIGHT//2 + 10))
            box = pygame.Rect(SCREEN_WIDTH//2 - 180, SCREEN_HEIGHT//2 + 40, 360, 36)
            pygame.draw.rect(self.screen, (30,40,55), box, border_radius=8)
            pygame.draw.rect(self.screen, GRID_HIGHLIGHT, box, 2, border_radius=8)
            t = self.font.render(self.name_input or "", True, TEXT_COLOR)
            self.screen.blit(t, (box.x + 10, box.y + 6))
            caret_x = box.x + 10 + t.get_width() + 2
            pygame.draw.line(self.screen, TEXT_COLOR, (caret_x, box.y + 6), (caret_x, box.y + 30), 2)
        else:
            if self.submitted_score:
                ok_text = self.small_font.render("Рекорд отправлен (онлайн)!", True, CORRECT_COLOR)
                self.screen.blit(ok_text, (SCREEN_WIDTH//2 - ok_text.get_width()//2, SCREEN_HEIGHT//2 + 10))
            else:
                skip = self.small_font.render("Рекорд не отправлен.", True, WRONG_COLOR)
                self.screen.blit(skip, (SCREEN_WIDTH//2 - skip.get_width()//2, SCREEN_HEIGHT//2 + 10))
        tip = self.small_font.render("R или SPACE — в меню", True, TEXT_COLOR)
        self.screen.blit(tip, (SCREEN_WIDTH//2 - tip.get_width()//2, SCREEN_HEIGHT//2 + 70))
        self.particle_system.add_effect("game_over", SCREEN_WIDTH//2, SCREEN_HEIGHT//2)

    def update(self):
        can_place = any(self.board.find_best_placement(s) is not None for s in self.current_shapes)
        if not can_place and not self.game_over:
            self.game_over = True
            self.game_data.add_game_session(
                self.board.score,
                self.lines_cleared_this_game,
                self.questions_answered_this_game,
                self.correct_answers_this_game,
                self.code_battles_completed_this_game
            )
            self.game_data.update_achievements()
            self.ask_name = True

    def run(self) -> str:
        while True:
            res = self.handle_events()
            if res: return res
            self.update(); self.draw(); self.clock.tick(FPS)


# ---------- УТИЛЫ ----------
def wrap_text(text: str, font: pygame.font.Font, max_width: int) -> List[str]:
    words = text.split(' '); lines=[]; cur=[]
    for w in words:
        test = ' '.join(cur+[w])
        if font.size(test)[0] <= max_width: cur.append(w)
        else:
            if cur: lines.append(' '.join(cur))
            cur=[w]
    if cur: lines.append(' '.join(cur))
    return lines


# ---------- MAIN ----------
def main():
    ensure_data_files()
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Python Blaster: Code & Clear")

    game_data = GameData()
    leaderboard = OnlineLeaderboard(SUPABASE_URL, SUPABASE_ANON_KEY)
    menu = MainMenu(screen, game_data, leaderboard)
    catalog = CodeBattleCatalog()

    cur = "menu"
    while True:
        if cur == "menu":
            r = menu.handle_events()
            if r == "start":
                cur = "game"
            elif r == "archive":
                arch = ArchiveScreen(screen, catalog)
                while True:
                    rr = arch.handle()
                    if rr == "quit":
                        pygame.quit(); sys.exit()
                    if rr == "menu":
                        break
                    arch.draw()
                cur = "menu"
            elif r == "quit":
                break
            menu.draw()

        elif cur == "game":
            result = Game(game_data, pro_mode=menu.pro_mode, leaderboard=leaderboard).run()
            if result == "menu": cur = "menu"
            elif result == "quit": break

        pygame.time.delay(10)

    pygame.quit(); sys.exit()


if __name__ == "__main__":
    main()



