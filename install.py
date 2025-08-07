#!/usr/bin/env python3
“””
Скрипт для установки зависимостей Telegram-бота
Используется когда нет доступа к терминалу
“””

import subprocess
import sys
import os

def install_dependencies():
“”“Установка библиотек через pip”””
print(“🚀 Начинаем установку библиотек для Telegram-бота…”)
print(”=” * 50)

```
try:
    # Проверяем наличие pip
    print("🔍 Проверяем pip...")
    subprocess.check_call([sys.executable, "-m", "pip", "--version"])
    print("✅ pip найден и работает")
    
    # Обновляем pip
    print("\n📦 Обновляем pip...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    print("✅ pip обновлен")
    
    # Устанавливаем python-telegram-bot
    print("\n🤖 Устанавливаем python-telegram-bot...")
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", 
        "python-telegram-bot==20.3",
        "--no-cache-dir"
    ])
    print("✅ python-telegram-bot установлен")
    
    # Проверяем установку
    print("\n🔍 Проверяем установку...")
    try:
        import telegram
        print(f"✅ Telegram библиотека найдена, версия: {telegram.__version__}")
    except ImportError:
        print("❌ Ошибка импорта telegram")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 ВСЕ БИБЛИОТЕКИ УСПЕШНО УСТАНОВЛЕНЫ!")
    print("🚀 Теперь можете запускать main.py")
    print("=" * 50)
    return True
    
except subprocess.CalledProcessError as e:
    print(f"❌ Ошибка установки: {e}")
    print("\n💡 Попробуйте:")
    print("1. Перезапустить скрипт")
    print("2. Использовать веб-версию Codespaces")
    return False
except Exception as e:
    print(f"❌ Неожиданная ошибка: {e}")
    return False
```

def check_files():
“”“Проверка наличия необходимых файлов”””
print(“📁 Проверяем файлы проекта…”)

```
required_files = ['main.py', 'requirements.txt']
missing_files = []

for file in required_files:
    if os.path.exists(file):
        print(f"✅ {file} найден")
    else:
        print(f"❌ {file} НЕ НАЙДЕН!")
        missing_files.append(file)

if missing_files:
    print(f"\n⚠️  Отсутствуют файлы: {', '.join(missing_files)}")
    print("Создайте их перед установкой библиотек!")
    return False

return True
```

def main():
“”“Основная функция”””
print(“🤖 УСТАНОВЩИК TELEGRAM-БОТА”)
print(“📱 Версия для мобильных устройств”)
print(”=” * 50)

```
# Проверяем файлы
if not check_files():
    return

print()

# Устанавливаем зависимости
if install_dependencies():
    print("\n🎯 СЛЕДУЮЩИЕ ШАГИ:")
    print("1. Убедитесь что токен установлен в main.py")
    print("2. Запустите: python main.py")
    print("3. Проверьте бота в Telegram")
else:
    print("\n🔧 ЕСЛИ ОШИБКИ ПРОДОЛЖАЮТСЯ:")
    print("1. Используйте веб-версию GitHub Codespaces")
    print("2. Или локальную установку Python")
```

if **name** == “**main**”:
main()
