# Руководство разработчика

Этот раздел содержит практические инструкции по расширению функционала бота-визитки.

## Добавление новой команды

Чтобы добавить новую команду (например, `/about`):

1. **Создайте хэндлер в роутерах**:
   Создайте или откройте существующий роутер в `app/bot/routers/` (например, `public.py`).
   ```python
   from aiogram import Router, F
   from aiogram.filters import Command
   from aiogram.types import Message
   
   router = Router(name="about_router")
   
   @router.message(Command("about"))
   async def cmd_about(message: Message):
       await message.answer("Информация о боте...")
   ```

2. **Зарегистрируйте роутер в `main.py` (если он новый)**:
   ```python
   from app.bot.routers.public import router as about_router
   dp.include_router(about_router)
   ```

## Работа с текстами (Text Catalog)

Бот не хранит длинные тексты напрямую в Python-коде. Для удобства редактирования все тексты вынесены в Markdown-файлы в папку `app/bot/texts/`.
Доступ к ним осуществляется через `app.bot.text_catalog`.

### Как добавить текст:
1. Откройте нужный файл в `app/bot/texts/` (например, `public.md`).
2. Добавьте новый заголовок второго уровня `## my_text_key` и напишите под ним текст:
   ```markdown
   ## about_message
   Это **жирный** текст про меня.
   Мой возраст: {age}
   ```
3. Вызовите его в коде:
   ```python
   from app.bot.text_catalog import text
   
   # Если есть форматирование, передайте аргументы как kwargs
   content = text("about_message", age=25)
   await message.answer(content)
   ```

> [!TIP]
> Утилита `text_catalog.py` также может собрать все `md` файлы в один `all.md` для удобного перевода или редактирования разом (см. ключи `--write-all` и `--unpack`).

## Машина состояний (FSM)

Для сложных диалогов, таких как создание нового кейса через админ-панель, используется FSM (Finite State Machine).
Состояния определяются в классе наследуемом от `StatesGroup`:

```python
from aiogram.fsm.state import State, StatesGroup

class CaseForm(StatesGroup):
    waiting_for_title = State()
    waiting_for_task = State()
    # ...
```

Для хранения состояний используется **Redis**. Настройки Redis (`REDIS_URL`) должны быть валидными в `.env`, иначе бот может использовать хранилище в памяти (MemoryStorage), которое сбросится при перезапуске.

## Тестирование

Для запуска тестов используется фреймворк `pytest`. Убедитесь, что у вас установлены dev-зависимости.

Запуск тестов в консоли:
```bash
pytest
```
Или быстрый запуск (тихий режим):
```bash
pytest -q
```

Файлы тестов лежат в папке `tests/`. При написании тестов используйте `pytest-asyncio` для асинхронных функций и моки (mocks) для имитации Aiogram и БД, где это необходимо.
