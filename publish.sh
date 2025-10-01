#!/usr/bin/env bash
set -e

# Пользователь/репозиторий GitHub
GITHUB_USER="Tima0707"
REPO_NAME="PythonBlaster"
EMAIL="Tima0707@users.noreply.github.com"
USE_SSH="n"   # y = SSH, n = HTTPS

# 0) Настройка git (если не задано)
git config --global user.name "$GITHUB_USER" || true
git config --global user.email "$EMAIL" || true

# 1) Гарантируем наличие служебных файлов/папок
mkdir -p .github/workflows data
[ -f requirements.txt ] || printf "pygame>=2.5\npytest>=8\nruff>=0.6\n" > requirements.txt

# 2) Инициализация git
[ -d .git ] || git init
git add .
git commit -m "Initial commit: bootstrap" || true
git branch -M main

# 3) Подключаем удалённый репозиторий
git remote remove origin 2>/dev/null || true
if [ "$USE_SSH" = "y" ]; then
  if [ ! -f ~/.ssh/id_ed25519 ]; then
    ssh-keygen -t ed25519 -C "$EMAIL" -N "" -f ~/.ssh/id_ed25519
    echo "Добавь этот ключ в GitHub → Settings → SSH and GPG keys:"
    cat ~/.ssh/id_ed25519.pub
    read -p "Нажми Enter после добавления ключа..."
  fi
  git remote add origin git@github.com:$GITHUB_USER/$REPO_NAME.git
else
  git remote add origin https://github.com/$GITHUB_USER/$REPO_NAME.git
  echo "Если спросит пароль — используй Personal Access Token вместо пароля."
fi

# 4) Если удалённая ветка уже существует — подтянем (не критично, просто аккуратнее)
git fetch origin main || true
git pull --rebase origin main || true

# 5) Публикация
git push -u origin main

echo "✅ Готово: https://github.com/$GITHUB_USER/$REPO_NAME"
