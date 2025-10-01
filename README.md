# Python Blaster: Code & Clear

Аркадная игра-головоломка на **Pygame**: размещай фигуры на сетке, собирай линии, зарабатывай очки и периодически проходи мини‑викторины/код‑баттлы. 
Проект запускается из `main.py` (вход: `main()`), данные и вопросы лежат в папке `data/`.

## Требования
- Python 3.10+
- pip

## Установка
```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows (PowerShell)
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

## Подготовка данных
Минимальная структура:
```
project/
├─ main.py
├─ data/
│  ├─ questions.json
│  └─ game_data.json   # создаётся автоматически
```

## Запуск
```bash
python main.py
```

## Тесты и стиль
```bash
pytest -q
ruff check .
ruff format .
```

## CI
В `.github/workflows/ci.yml` включены базовые тесты на GitHub Actions.

## Лицензия
MIT — см. `LICENSE`.
