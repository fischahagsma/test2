"""Сайт на Flask для демонстрации алгоритмов сортировки."""

import json
import math
import os
import re
import time

from flask import Flask, abort, jsonify, render_template, request
from werkzeug.exceptions import HTTPException

from algorithms import ALGORITHMS

# Алгоритмы O(n²) на больших списках работают слишком долго для веб-запроса
MAX_ITEMS = 2000
# Поразрядная сортировка делает проход на каждую цифру, поэтому числа из тысяч цифр
# заняли бы сервер на минуты. Ограничиваем величину чисел (и для формы, и для API)
MAX_ABS = 10**15
MAX_ABS_TEXT = "10¹⁵"

app = Flask(__name__)
# 2000 чисел заведомо помещаются в 256 КБ; тело больше — ответ 413 ещё до разбора
app.config["MAX_CONTENT_LENGTH"] = 256 * 1024


def shorten(text, limit=30):
    """Обрезает длинный фрагмент ввода, чтобы не повторять его в ошибке целиком."""
    return text if len(text) <= limit else text[:limit] + "…"


def validate_numbers(numbers, tokens=None):
    """Общая проверка для формы и API: количество, тип и величина чисел.

    tokens — исходные строки из формы, чтобы показать в ошибке то, что ввёл пользователь.
    """
    if len(numbers) > MAX_ITEMS:
        raise ValueError(f"Слишком много чисел: максимум {MAX_ITEMS}.")
    for i, x in enumerate(numbers):
        if (isinstance(x, bool) or not isinstance(x, (int, float))
                or isinstance(x, float) and math.isnan(x)):
            problem = "не число"
        elif abs(x) > MAX_ABS:  # сюда же попадают бесконечности
            problem = f"слишком большое число: допускаются числа по модулю не больше {MAX_ABS_TEXT}"
        else:
            continue
        shown = tokens[i] if tokens is not None else json.dumps(x, ensure_ascii=False)
        raise ValueError(f"«{shorten(shown)}» — {problem}.")
    return numbers


def parse_numbers(text):
    """Разбирает строку с числами через пробелы, запятые или точки с запятой."""
    tokens = [t for t in re.split(r"[\s,;]+", text.strip()) if t]
    if not tokens:
        raise ValueError("Введите хотя бы одно число.")
    if len(tokens) > MAX_ITEMS:
        raise ValueError(f"Слишком много чисел: максимум {MAX_ITEMS}.")
    numbers = []
    for token in tokens:
        try:
            numbers.append(int(token))
        except ValueError:
            # Сюда попадают и целые длиннее 4300 цифр: float() даёт для них inf,
            # и такое число отсеивает проверка величины в validate_numbers
            try:
                numbers.append(float(token))
            except ValueError:
                raise ValueError(f"«{shorten(token)}» — не число.") from None
    return validate_numbers(numbers, tokens)


def run_sort(key, numbers):
    """Запускает алгоритм и возвращает отсортированный список и время в миллисекундах."""
    algorithm = ALGORITHMS[key]
    if algorithm["int_only"] and any(isinstance(x, float) for x in numbers):
        raise ValueError(f"{algorithm['full_name']} работает только с целыми числами.")
    # Сортировка подсчётом заводит счётчик на каждое значение от минимума до максимума
    max_range = algorithm.get("max_range")
    if max_range and numbers and max(numbers) - min(numbers) > max_range:
        limit = f"{max_range:,}".replace(",", " ")
        raise ValueError(f"{algorithm['full_name']} не подходит для этих данных: разница "
                         f"между максимумом и минимумом больше {limit}.")
    start = time.perf_counter()
    result = algorithm["func"](numbers)
    elapsed_ms = (time.perf_counter() - start) * 1000
    return result, elapsed_ms


@app.route("/", methods=["GET", "POST"])
def index():
    context = {"algorithms": ALGORITHMS, "selected": "bubble", "text": "", "max_items": MAX_ITEMS}
    if request.method == "POST":
        context["text"] = request.form.get("numbers", "")
        context["selected"] = request.form.get("algorithm", "bubble")
        try:
            numbers = parse_numbers(context["text"])
            if context["selected"] == "all":
                # Сравниваем все алгоритмы, которые подходят для этих данных
                timings = []
                skipped = []
                for key, algorithm in ALGORITHMS.items():
                    try:
                        result, elapsed_ms = run_sort(key, numbers)
                    except ValueError as error:
                        skipped.append({"key": key, "name": algorithm["name"],
                                        "reason": str(error)})
                        continue
                    timings.append({"key": key, "name": algorithm["name"], "ms": elapsed_ms})
                context["result"] = result
                context["timings"] = sorted(timings, key=lambda t: t["ms"])
                context["skipped"] = skipped
            elif context["selected"] in ALGORITHMS:
                context["result"], context["elapsed_ms"] = run_sort(context["selected"], numbers)
            else:
                raise ValueError("Неизвестный алгоритм.")
        except ValueError as error:
            context["error"] = str(error)
    return render_template("index.html", **context)


@app.route("/algorithms/<key>")
def algorithm_detail(key):
    if key not in ALGORITHMS:
        abort(404)
    # Путь от папки приложения, а не от текущей папки процесса
    with open(os.path.join(app.root_path, ALGORITHMS[key]["file"]), encoding="utf-8") as f:
        source = f.read()
    return render_template("algorithm.html", key=key, algorithm=ALGORITHMS[key],
                           algorithms=ALGORITHMS, source=source, max_items=MAX_ITEMS)


@app.route("/api/sort", methods=["POST"])
def api_sort():
    """JSON API: {"algorithm": "merge", "numbers": [3, 1, 2]}."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="Тело запроса должно быть JSON-объектом."), 400
    key = data.get("algorithm", "bubble")
    numbers = data.get("numbers")
    if not isinstance(key, str) or key not in ALGORITHMS:
        return jsonify(error="Неизвестный алгоритм."), 400
    if not isinstance(numbers, list):
        return jsonify(error=f"numbers должен быть списком чисел (не более {MAX_ITEMS})."), 400
    try:
        validate_numbers(numbers)
        result, elapsed_ms = run_sort(key, numbers)
    except ValueError as error:
        return jsonify(error=str(error)), 400
    return jsonify(algorithm=key, result=result, elapsed_ms=elapsed_ms)


# Заголовок и текст страниц ошибок; для /api/ тот же текст отдаётся в JSON
ERROR_TEXTS = {
    404: ("Страница не найдена",
          "Такой страницы нет. Возможно, адрес набран с ошибкой или такого алгоритма на сайте нет."),
    405: ("Метод не поддерживается",
          "Этот адрес не принимает такой запрос. API: POST /api/sort с JSON."),
    413: ("Слишком большой запрос", f"Можно отправить не более {MAX_ITEMS} чисел."),
    500: ("Внутренняя ошибка сервера", "Что-то пошло не так. Попробуйте ещё раз."),
}


@app.errorhandler(HTTPException)
def http_error(error):
    title, message = ERROR_TEXTS.get(error.code, ("Ошибка", "Не удалось выполнить запрос."))
    headers = {}
    if getattr(error, "valid_methods", None):  # ответ 405 должен перечислять допустимые методы
        headers["Allow"] = ", ".join(error.valid_methods)
    if request.path.startswith("/api/"):
        return jsonify(error=f"{title}. {message}"), error.code, headers
    return render_template("error.html", algorithms=ALGORITHMS, code=error.code,
                           title=title, message=message), error.code, headers


if __name__ == "__main__":
    # Отладчик включается только явно: FLASK_DEBUG=1 python app.py
    app.run()
