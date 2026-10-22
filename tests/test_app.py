"""Тесты сайта сортировок: алгоритмы, разбор ввода, JSON API и страницы.

Запуск из корня репозитория:  python -B -m pytest -q
Без готовых шаблонов:          python -B -m pytest -q -m "not html"
"""

import functools
import html
import random
import re
import time
import zlib
from pathlib import Path

import pytest

import app as app_module
from algorithms import ALGORITHMS
from app import MAX_ABS, MAX_ITEMS, parse_numbers

REPO_ROOT = Path(__file__).resolve().parent.parent

ALL_KEYS = list(ALGORITHMS)
INT_ONLY_KEYS = [k for k, a in ALGORITHMS.items() if a["int_only"]]
FLOAT_KEYS = [k for k, a in ALGORITHMS.items() if not a["int_only"]]
STABLE_COMPARISON_KEYS = [k for k, a in ALGORITHMS.items() if a["stable"] and not a["int_only"]]

REQUIRED_FIELDS = {"name", "full_name", "func", "file", "best", "average", "worst",
                   "memory", "stable", "int_only", "description"}
CYRILLIC = re.compile(r"[А-Яа-яЁё]")
NUMBER_RE = re.compile(r"-?\d+(?:\.\d+)?")

# Ввод для страниц: отрицательные числа, дубликат, дробное число
FORM_TEXT = "42 -7 3.5 1000 0 17 -7"
FORM_SORTED = [-7, -7, 0, 3.5, 17, 42, 1000]
INT_FORM_TEXT = "42, -7; 1000\n0 17 -7"
INT_FORM_SORTED = [-7, -7, 0, 17, 42, 1000]


def random_int_lists(seed, count=150, max_len=60, low=-100, high=100):
    rng = random.Random(seed)
    lists = []
    for _ in range(count):
        length = rng.randint(0, max_len)
        # Узкий диапазон — много дубликатов, широкий — почти без них
        span = rng.choice([3, 20, high - low])
        lo = rng.randint(low, high - span)
        lists.append([rng.randint(lo, lo + span) for _ in range(length)])
    return lists


def random_float_lists(seed, count=150, max_len=60):
    rng = random.Random(seed)
    lists = []
    for _ in range(count):
        length = rng.randint(0, max_len)
        pool = [rng.uniform(-1000, 1000) for _ in range(max(1, length // 3))]
        kind = rng.choice(["floats", "dups", "mixed"])
        if kind == "floats":
            data = [rng.uniform(-1000, 1000) for _ in range(length)]
        elif kind == "dups":
            data = [rng.choice(pool) for _ in range(length)]
        else:
            data = [rng.choice([rng.randint(-50, 50), round(rng.uniform(-50, 50), 2)])
                    for _ in range(length)]
        lists.append(data)
    return lists


def page_text(response):
    """Текст страницы без тегов и HTML-сущностей."""
    without_tags = re.sub(r"<[^>]*>", " ", response.get_data(as_text=True))
    return html.unescape(without_tags)


def has_number_run(text, values):
    """Есть ли в тексте подряд идущие числа values (между ними допускаются любые разделители)."""
    tokens = NUMBER_RE.findall(text)
    expected = [str(v) for v in values]
    n = len(expected)
    return any(tokens[i:i + n] == expected for i in range(len(tokens) - n + 1))


def only_call(rendered):
    assert len(rendered) == 1, f"ожидался один вызов render_template, было {len(rendered)}"
    return rendered[0]


# ---------------------------------------------------------------------------
# Реестр алгоритмов
# ---------------------------------------------------------------------------

def test_registry_has_all_eleven_algorithms():
    assert set(ALL_KEYS) == {"bubble", "selection", "insertion", "merge", "quick", "heap",
                             "shell", "counting", "radix", "comb", "cocktail"}
    assert set(INT_ONLY_KEYS) == {"counting", "radix"}


@pytest.mark.parametrize("key", ALL_KEYS)
def test_registry_entry_is_complete(key):
    algorithm = ALGORITHMS[key]
    assert REQUIRED_FIELDS <= set(algorithm)
    assert algorithm["func"].__name__ == f"{key}_sort"
    assert algorithm["file"] == f"{key}_sort.py"
    assert (REPO_ROOT / algorithm["file"]).is_file()
    assert isinstance(algorithm["stable"], bool)
    assert isinstance(algorithm["int_only"], bool)
    for field in ("best", "average", "worst", "memory"):
        assert algorithm[field].strip()
    # Весь текст сайта — на русском
    assert CYRILLIC.search(algorithm["name"])
    assert CYRILLIC.search(algorithm["full_name"])
    assert CYRILLIC.search(algorithm["description"])


# ---------------------------------------------------------------------------
# Функции сортировки
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("key", ALL_KEYS)
def test_sorts_random_int_lists(key):
    func = ALGORITHMS[key]["func"]
    for data in random_int_lists(seed=zlib.crc32(key.encode())):
        assert func(data) == sorted(data), data


@pytest.mark.parametrize("key", ALL_KEYS)
def test_sorts_wide_range_and_larger_int_lists(key):
    func = ALGORITHMS[key]["func"]
    rng = random.Random(12345)
    for length in (100, 300):
        data = [rng.randint(-5000, 5000) for _ in range(length)]
        assert func(data) == sorted(data)


@pytest.mark.parametrize("key", FLOAT_KEYS)
def test_sorts_random_float_lists(key):
    func = ALGORITHMS[key]["func"]
    for data in random_float_lists(seed=zlib.crc32(key.encode()) + 1):
        assert func(data) == sorted(data), data


@pytest.mark.parametrize("key", ALL_KEYS)
@pytest.mark.parametrize("data", [
    [],
    [7],
    [-3],
    [0],
    [2, 1],
    [1, 2],
    [5, 5, 5, 5],
    list(range(30)),
    list(range(30, 0, -1)),
    [0, -1, 1, -2, 2, -10, 10],
], ids=["empty", "single", "single-negative", "single-zero", "pair-desc", "pair-asc",
        "all-equal", "sorted", "reversed", "mixed-signs"])
def test_edge_cases(key, data):
    assert ALGORITHMS[key]["func"](data) == sorted(data)


@pytest.mark.parametrize("key", ALL_KEYS)
@pytest.mark.parametrize("data", [[], [1], [3, -1, 2, 2, 0, -5]], ids=["empty", "single", "many"])
def test_returns_new_list_and_does_not_mutate_input(key, data):
    original = list(data)
    result = ALGORITHMS[key]["func"](data)
    assert data == original
    assert result is not data
    # Изменение результата не должно затрагивать вход
    result.append(999)
    assert data == original


@pytest.mark.parametrize("key", FLOAT_KEYS)
def test_float_input_not_mutated(key):
    data = [3.5, -1.25, 2.0, 2.0, 0.0, -7.75]
    original = list(data)
    ALGORITHMS[key]["func"](data)
    assert data == original


@functools.total_ordering
class Tagged:
    """Сравнивается только по value; tag позволяет проверить порядок равных элементов."""

    def __init__(self, value, tag):
        self.value = value
        self.tag = tag

    def __eq__(self, other):
        return self.value == other.value

    def __lt__(self, other):
        return self.value < other.value

    def __repr__(self):
        return f"Tagged({self.value}, {self.tag})"


@pytest.mark.parametrize("key", STABLE_COMPARISON_KEYS)
def test_algorithms_marked_stable_are_stable(key):
    rng = random.Random(2024)
    for _ in range(30):
        data = [Tagged(rng.randint(0, 5), tag) for tag in range(rng.randint(0, 40))]
        result = ALGORITHMS[key]["func"](data)
        expected = sorted(data)  # sorted() устойчива
        assert [(x.value, x.tag) for x in result] == [(x.value, x.tag) for x in expected]


# ---------------------------------------------------------------------------
# parse_numbers
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("text", [
    "3 1 2",
    "3,1,2",
    "3;1;2",
    "3\n1\n2",
    "3\r\n1\r\n2",
    "3\t1\t2",
    "3, 1; 2",
    "  3 ,; 1\n\n ; 2 ,  ",
], ids=["spaces", "commas", "semicolons", "newlines", "crlf", "tabs", "mixed", "messy"])
def test_parse_separators(text):
    assert parse_numbers(text) == [3, 1, 2]


def test_parse_ints_stay_ints_and_floats_are_floats():
    numbers = parse_numbers("1 2.5 -3 -0.5 10 0.0")
    assert numbers == [1, 2.5, -3, -0.5, 10, 0.0]
    assert [type(x) for x in numbers] == [int, float, int, float, int, float]


def test_parse_negative_numbers():
    assert parse_numbers("-1, -20; -300\n-4.5") == [-1, -20, -300, -4.5]


@pytest.mark.parametrize("text", ["", "   ", "\n\n", " , ; \n ,"])
def test_parse_empty_input_is_error(text):
    with pytest.raises(ValueError, match="хотя бы одно число"):
        parse_numbers(text)


@pytest.mark.parametrize("text, bad", [
    ("1 abc 3", "abc"),
    ("1 2 три", "три"),
    ("1.5.2", "1.5.2"),
    ("5 --5", "--5"),
    ("7 1x", "1x"),
])
def test_parse_non_number_is_error(text, bad):
    with pytest.raises(ValueError, match="не число") as info:
        parse_numbers(text)
    assert bad in str(info.value)


def test_parse_accepts_exactly_max_items():
    numbers = parse_numbers(" ".join(str(i) for i in range(MAX_ITEMS)))
    assert numbers == list(range(MAX_ITEMS))


def test_parse_rejects_more_than_max_items():
    with pytest.raises(ValueError, match=str(MAX_ITEMS)):
        parse_numbers(" ".join("1" for _ in range(MAX_ITEMS + 1)))


@pytest.mark.parametrize("token", ["nan", "inf", "-inf", "Infinity", "1e400", "-1e999"])
def test_parse_rejects_nan_and_infinity(token):
    with pytest.raises(ValueError) as info:
        parse_numbers(f"1 {token} 2")
    assert f"«{token}»" in str(info.value)


@pytest.mark.parametrize("token", [str(MAX_ABS + 1), str(-MAX_ABS - 1), "1" * 5000, "1e16"])
def test_parse_rejects_too_large_numbers(token):
    with pytest.raises(ValueError, match="слишком большое число") as info:
        parse_numbers(f"1 {token} 2")
    # Длинное число не повторяется в сообщении целиком
    assert len(str(info.value)) < 200


def test_parse_accepts_numbers_up_to_max_abs():
    assert parse_numbers(f"{MAX_ABS} {-MAX_ABS}") == [MAX_ABS, -MAX_ABS]


# ---------------------------------------------------------------------------
# JSON API /api/sort
# ---------------------------------------------------------------------------

def post_api(client, payload):
    return client.post("/api/sort", json=payload)


@pytest.mark.parametrize("key", ALL_KEYS)
def test_api_sorts_ints_with_every_algorithm(client, key):
    numbers = [5, -2, 9, 0, -2, 3, 100, -50]
    response = post_api(client, {"algorithm": key, "numbers": numbers})
    assert response.status_code == 200
    data = response.get_json()
    assert data["algorithm"] == key
    assert data["result"] == sorted(numbers)
    assert isinstance(data["elapsed_ms"], (int, float))
    assert data["elapsed_ms"] >= 0
    assert "error" not in data


@pytest.mark.parametrize("key", FLOAT_KEYS)
def test_api_sorts_floats(client, key):
    numbers = [2.5, -1, 3.25, 0, -1.5, 2.5]
    response = post_api(client, {"algorithm": key, "numbers": numbers})
    assert response.status_code == 200
    assert response.get_json()["result"] == sorted(numbers)


@pytest.mark.parametrize("key", ALL_KEYS)
def test_api_empty_list(client, key):
    response = post_api(client, {"algorithm": key, "numbers": []})
    assert response.status_code == 200
    assert response.get_json()["result"] == []


def test_api_accepts_exactly_max_items(client):
    numbers = list(range(MAX_ITEMS, 0, -1))
    response = post_api(client, {"algorithm": "merge", "numbers": numbers})
    assert response.status_code == 200
    assert response.get_json()["result"] == sorted(numbers)


def assert_api_error(response):
    assert response.status_code == 400
    data = response.get_json()
    assert isinstance(data, dict)
    assert isinstance(data.get("error"), str) and data["error"]
    assert "result" not in data
    return data["error"]


@pytest.mark.parametrize("algorithm", ["unknown", "", "BUBBLE", "bubble_sort", 1, None])
def test_api_unknown_algorithm(client, algorithm):
    error = assert_api_error(post_api(client, {"algorithm": algorithm, "numbers": [3, 1]}))
    assert "Неизвестный алгоритм" in error


@pytest.mark.parametrize("numbers", [
    "3 1 2",
    "123",
    123,
    1.5,
    None,
    {"a": 1},
    [1, "2", 3],
    [1, None],
    [[1, 2]],
    [{"x": 1}],
], ids=["string", "digit-string", "int", "float", "null", "object",
        "list-with-string", "list-with-null", "nested-list", "list-with-object"])
def test_api_invalid_numbers(client, numbers):
    assert_api_error(post_api(client, {"algorithm": "merge", "numbers": numbers}))


def test_api_missing_numbers(client):
    assert_api_error(post_api(client, {"algorithm": "merge"}))


@pytest.mark.parametrize("numbers", [[True, 2], [1, False], [True]])
def test_api_bools_are_not_numbers(client, numbers):
    assert_api_error(post_api(client, {"algorithm": "merge", "numbers": numbers}))


def test_api_too_many_numbers(client):
    error = assert_api_error(post_api(client, {"algorithm": "merge",
                                               "numbers": [1] * (MAX_ITEMS + 1)}))
    assert str(MAX_ITEMS) in error


@pytest.mark.parametrize("key", INT_ONLY_KEYS)
def test_api_floats_with_int_only_algorithm(client, key):
    error = assert_api_error(post_api(client, {"algorithm": key, "numbers": [3, 1.5, 2]}))
    assert ALGORITHMS[key]["full_name"] in error
    assert "целыми" in error


def test_api_no_body(client):
    assert_api_error(client.post("/api/sort"))


def test_api_empty_json_object(client):
    assert_api_error(client.post("/api/sort", json={}))


@pytest.mark.parametrize("body", ["{not json", "", "{\"numbers\": [1, 2,]}", "null"])
def test_api_invalid_json(client, body):
    assert_api_error(client.post("/api/sort", data=body, content_type="application/json"))


def test_api_form_body_instead_of_json(client):
    assert_api_error(client.post("/api/sort", data={"algorithm": "merge", "numbers": "3 1 2"}))


def test_api_json_without_json_content_type(client):
    body = '{"algorithm": "merge", "numbers": [3, 1, 2]}'
    assert_api_error(client.post("/api/sort", data=body, content_type="text/plain"))


def test_api_get_not_allowed(client):
    assert client.get("/api/sort").status_code == 405


@pytest.mark.parametrize("body", ["[1, 2, 3]", "\"abc\"", "5", "true", "[]", "0"])
def test_api_non_object_json_body(client, body):
    error = assert_api_error(client.post("/api/sort", data=body, content_type="application/json"))
    assert "JSON-объектом" in error


@pytest.mark.parametrize("algorithm", [["merge"], {"name": "merge"}])
def test_api_unhashable_algorithm(client, algorithm):
    error = assert_api_error(post_api(client, {"algorithm": algorithm, "numbers": [3, 1]}))
    assert "Неизвестный алгоритм" in error


# 1e400 и -1e400 — не литералы NaN/Infinity, но json.loads превращает их в бесконечность
@pytest.mark.parametrize("literal", ["NaN", "Infinity", "-Infinity", "1e400", "-1e400"])
def test_api_rejects_nan_and_infinity(client, literal):
    body = f'{{"algorithm": "merge", "numbers": [3, {literal}, 1]}}'
    assert_api_error(client.post("/api/sort", data=body, content_type="application/json"))


@pytest.mark.parametrize("key", ["radix", "merge"])
@pytest.mark.parametrize("big", [MAX_ABS + 1, -MAX_ABS - 1, 10**4000], ids=["over", "under", "huge"])
def test_api_rejects_too_large_numbers(client, key, big):
    error = assert_api_error(post_api(client, {"algorithm": key, "numbers": [3, big, 1]}))
    assert "слишком большое число" in error
    assert len(error) < 200


def test_api_counting_with_wide_range_is_400_not_500(client):
    for numbers in ([0, 10**12], [-MAX_ABS, MAX_ABS], [89161234567, 89031234567]):
        error = assert_api_error(post_api(client, {"algorithm": "counting", "numbers": numbers}))
        assert ALGORITHMS["counting"]["full_name"] in error
    # Числа больше MAX_ABS отсеиваются ещё до сортировки — тоже 400, а не 500
    assert_api_error(post_api(client, {"algorithm": "counting", "numbers": [0, 10**20]}))


def test_api_counting_accepts_range_up_to_max_range(client):
    max_range = ALGORITHMS["counting"]["max_range"]
    numbers = [max_range, 5, 0, 5]
    response = post_api(client, {"algorithm": "counting", "numbers": numbers})
    assert response.status_code == 200
    assert response.get_json()["result"] == sorted(numbers)


def test_api_radix_handles_wide_range(client):
    numbers = [10**12, 0, -10**12, 7]
    response = post_api(client, {"algorithm": "radix", "numbers": numbers})
    assert response.status_code == 200
    assert response.get_json()["result"] == sorted(numbers)


def test_api_too_large_body_is_413_json(client):
    body = '{"algorithm": "merge", "numbers": [' + "1, " * 200_000 + "1]}"
    response = client.post("/api/sort", data=body, content_type="application/json")
    assert response.status_code == 413
    assert "Слишком большой запрос" in response.get_json()["error"]


def test_api_get_not_allowed_is_russian_json(client):
    response = client.get("/api/sort")
    assert response.status_code == 405
    assert "POST" in response.headers["Allow"]
    assert "Метод не поддерживается" in response.get_json()["error"]


def test_api_unexpected_error_is_500_json(client, monkeypatch):
    def broken_sort(items):
        raise RuntimeError("сломалось")

    monkeypatch.setitem(app_module.app.config, "PROPAGATE_EXCEPTIONS", False)
    monkeypatch.setitem(ALGORITHMS["merge"], "func", broken_sort)
    response = post_api(client, {"algorithm": "merge", "numbers": [3, 1]})
    assert response.status_code == 500
    assert "Внутренняя ошибка сервера" in response.get_json()["error"]


# ---------------------------------------------------------------------------
# Главная страница: логика (render_template подменён, шаблоны не нужны)
# ---------------------------------------------------------------------------

def test_index_get_context(client, rendered):
    response = client.get("/")
    assert response.status_code == 200
    template, context = only_call(rendered)
    assert template == "index.html"
    assert context["algorithms"] is ALGORITHMS
    assert context["selected"] in ALGORITHMS
    assert context["text"] == ""
    assert context["max_items"] == MAX_ITEMS
    for key in ("result", "elapsed_ms", "timings", "error"):
        assert key not in context


@pytest.mark.parametrize("key", ALL_KEYS)
def test_index_post_single_algorithm_context(client, rendered, key):
    response = client.post("/", data={"numbers": INT_FORM_TEXT, "algorithm": key})
    assert response.status_code == 200
    template, context = only_call(rendered)
    assert template == "index.html"
    assert "error" not in context
    assert context["result"] == INT_FORM_SORTED
    assert context["elapsed_ms"] >= 0
    assert context["selected"] == key
    assert context["text"] == INT_FORM_TEXT
    assert context["max_items"] == MAX_ITEMS
    assert "timings" not in context


@pytest.mark.parametrize("key", FLOAT_KEYS)
def test_index_post_single_algorithm_floats_context(client, rendered, key):
    client.post("/", data={"numbers": FORM_TEXT, "algorithm": key})
    _, context = only_call(rendered)
    assert "error" not in context
    assert context["result"] == FORM_SORTED


def check_timings(timings, expected_keys):
    assert sorted(t["key"] for t in timings) == sorted(expected_keys)
    for t in timings:
        assert t["name"] == ALGORITHMS[t["key"]]["name"]
        assert isinstance(t["ms"], (int, float)) and t["ms"] >= 0
    ms = [t["ms"] for t in timings]
    assert ms == sorted(ms), "timings должны идти по возрастанию времени"


def test_index_post_all_with_ints_runs_every_algorithm(client, rendered):
    response = client.post("/", data={"numbers": INT_FORM_TEXT, "algorithm": "all"})
    assert response.status_code == 200
    _, context = only_call(rendered)
    assert "error" not in context
    assert context["selected"] == "all"
    assert context["result"] == INT_FORM_SORTED
    check_timings(context["timings"], ALL_KEYS)
    assert context["skipped"] == []


def test_index_post_all_with_floats_skips_int_only(client, rendered):
    response = client.post("/", data={"numbers": FORM_TEXT, "algorithm": "all"})
    assert response.status_code == 200
    _, context = only_call(rendered)
    assert "error" not in context
    assert context["result"] == FORM_SORTED
    check_timings(context["timings"], FLOAT_KEYS)
    assert not {t["key"] for t in context["timings"]} & set(INT_ONLY_KEYS)
    assert [s["key"] for s in context["skipped"]] == INT_ONLY_KEYS
    for s in context["skipped"]:
        assert s["name"] == ALGORITHMS[s["key"]]["name"]
        assert "целыми" in s["reason"]


@pytest.mark.parametrize("text", ["0 1000000000000", "89161234567 89031234567", "5 3 10000000000"])
def test_index_post_all_with_wide_int_range_skips_counting(client, rendered, text):
    response = client.post("/", data={"numbers": text, "algorithm": "all"})
    assert response.status_code == 200
    _, context = only_call(rendered)
    assert "error" not in context
    numbers = parse_numbers(text)
    assert context["result"] == sorted(numbers)
    check_timings(context["timings"], [k for k in ALL_KEYS if k != "counting"])
    assert [s["key"] for s in context["skipped"]] == ["counting"]
    assert "разница между максимумом и минимумом" in context["skipped"][0]["reason"]


@pytest.mark.parametrize("text", ["0 1000000000000", "89161234567 89031234567"])
def test_index_post_counting_with_wide_range_is_error_and_fast(client, rendered, text):
    start = time.perf_counter()
    response = client.post("/", data={"numbers": text, "algorithm": "counting"})
    assert time.perf_counter() - start < 1
    assert response.status_code == 200
    _, context = only_call(rendered)
    assert ALGORITHMS["counting"]["full_name"] in context["error"]
    assert "result" not in context


@pytest.mark.parametrize("algorithm", ["counting", "radix", "merge", "all"])
@pytest.mark.parametrize("text", ["0 100000000000000000000", "1 " + "7" * 5000],
                         ids=["10**20", "5000-digits"])
def test_index_post_too_large_numbers_is_error(client, rendered, algorithm, text):
    response = client.post("/", data={"numbers": text, "algorithm": algorithm})
    assert response.status_code == 200
    _, context = only_call(rendered)
    assert "слишком большое число" in context["error"]
    assert "result" not in context


@pytest.mark.parametrize("algorithm", ["bubble", "quick", "merge", "all"])
@pytest.mark.parametrize("text", ["3 nan 1 2", "5 nan 4 3 2 1", "1 inf 2", "1 -inf 2"])
def test_index_post_nan_and_infinity_is_error(client, rendered, algorithm, text):
    response = client.post("/", data={"numbers": text, "algorithm": algorithm})
    assert response.status_code == 200
    _, context = only_call(rendered)
    assert "nan" in context["error"] or "inf" in context["error"]
    assert "result" not in context


@pytest.mark.parametrize("text, message", [
    ("1 два 3", "«два» — не число"),
    ("", "Введите хотя бы одно число"),
    ("  ,;  ", "Введите хотя бы одно число"),
    (" ".join(["1"] * (MAX_ITEMS + 1)), f"максимум {MAX_ITEMS}"),
], ids=["not-a-number", "empty", "only-separators", "too-many"])
@pytest.mark.parametrize("algorithm", ["merge", "all"])
def test_index_post_invalid_input_context(client, rendered, text, message, algorithm):
    response = client.post("/", data={"numbers": text, "algorithm": algorithm})
    assert response.status_code == 200
    _, context = only_call(rendered)
    assert message in context["error"]
    assert context["text"] == text
    for key in ("result", "elapsed_ms", "timings"):
        assert key not in context


@pytest.mark.parametrize("key", INT_ONLY_KEYS)
def test_index_post_int_only_with_floats_context(client, rendered, key):
    client.post("/", data={"numbers": FORM_TEXT, "algorithm": key})
    _, context = only_call(rendered)
    assert "целыми" in context["error"]
    assert ALGORITHMS[key]["full_name"] in context["error"]
    assert "result" not in context


@pytest.mark.parametrize("algorithm", ["unknown", "", "Bubble", "merge_sort"])
def test_index_post_unknown_algorithm_context(client, rendered, algorithm):
    response = client.post("/", data={"numbers": "3 1 2", "algorithm": algorithm})
    assert response.status_code == 200
    _, context = only_call(rendered)
    assert "Неизвестный алгоритм" in context["error"]
    assert "result" not in context


# ---------------------------------------------------------------------------
# Страница алгоритма: логика (render_template подменён)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("key", ALL_KEYS)
def test_algorithm_detail_context(client, rendered, key):
    response = client.get(f"/algorithms/{key}")
    assert response.status_code == 200
    template, context = only_call(rendered)
    assert template == "algorithm.html"
    assert context["key"] == key
    assert context["algorithm"] is ALGORITHMS[key]
    assert context["algorithms"] is ALGORITHMS
    expected_source = (REPO_ROOT / ALGORITHMS[key]["file"]).read_text(encoding="utf-8")
    assert context["source"] == expected_source


@pytest.mark.parametrize("key", ["unknown", "bubble_sort", "Bubble", "all", "..", "app"])
def test_algorithm_detail_unknown_key_404(client, rendered, key):
    assert client.get(f"/algorithms/{key}").status_code == 404
    template, context = only_call(rendered)
    assert template == "error.html"
    assert context["algorithms"] is ALGORITHMS
    assert context["code"] == 404
    assert context["title"] == "Страница не найдена"


def test_algorithm_detail_works_from_other_working_directory(client, rendered, monkeypatch,
                                                             tmp_path):
    monkeypatch.chdir(tmp_path)
    response = client.get("/algorithms/bubble")
    assert response.status_code == 200
    assert "def bubble_sort" in only_call(rendered)[1]["source"]


# ---------------------------------------------------------------------------
# Настоящие HTML-шаблоны (маркер html)
# ---------------------------------------------------------------------------

@pytest.mark.html
def test_html_index_get(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.mimetype == "text/html"
    raw = response.get_data(as_text=True)
    # Форма должна отправлять поля numbers и algorithm
    assert re.search(r"name=[\"']?numbers\b", raw)
    assert re.search(r"name=[\"']?algorithm\b", raw)
    text = page_text(response)
    for algorithm in ALGORITHMS.values():
        assert algorithm["name"] in text


@pytest.mark.html
@pytest.mark.parametrize("key", ["merge", "bubble", "quick"])
def test_html_index_post_single_shows_sorted_result(client, key):
    response = client.post("/", data={"numbers": FORM_TEXT, "algorithm": key})
    assert response.status_code == 200
    assert has_number_run(page_text(response), FORM_SORTED)


@pytest.mark.html
@pytest.mark.parametrize("key", INT_ONLY_KEYS)
def test_html_index_post_int_only_shows_sorted_result(client, key):
    response = client.post("/", data={"numbers": INT_FORM_TEXT, "algorithm": key})
    assert response.status_code == 200
    assert has_number_run(page_text(response), INT_FORM_SORTED)


def timings_rows(raw):
    """Ключи алгоритмов из строк таблицы времени (по порядку строк)."""
    m = re.search(r'<table class="timings">(.*?)</table>', raw, re.S)
    assert m, "на странице нет таблицы с временем работы"
    return re.findall(r'<tr>\s*<td class="num">\d+</td>\s*<td><a href="/algorithms/(\w+)"',
                      m.group(1))


def skipped_items(raw):
    """Ключи и текст пунктов списка пропущенных алгоритмов (None, если списка нет)."""
    m = re.search(r'<ul class="hint skipped">(.*?)</ul>', raw, re.S)
    if m is None:
        return None
    items = re.findall(r'<li><a href="/algorithms/(\w+)">(.*?)</li>', m.group(1), re.S)
    return [(key, html.unescape(re.sub(r"<[^>]*>", "", text))) for key, text in items]


@pytest.mark.html
@pytest.mark.parametrize("text, expected, sorted_values", [
    (FORM_TEXT, FLOAT_KEYS, FORM_SORTED),
    (INT_FORM_TEXT, ALL_KEYS, INT_FORM_SORTED),
], ids=["floats", "ints"])
def test_html_index_post_all_shows_result_and_timings(client, text, expected, sorted_values):
    response = client.post("/", data={"numbers": text, "algorithm": "all"})
    assert response.status_code == 200
    raw = response.get_data(as_text=True)
    assert has_number_run(page_text(response), sorted_values)
    rows = timings_rows(raw)
    assert len(rows) == len(expected) and sorted(rows) == sorted(expected)
    skipped = skipped_items(raw)
    if expected == FLOAT_KEYS:
        assert skipped is not None, "нет списка пропущенных алгоритмов"
        assert [key for key, _ in skipped] == INT_ONLY_KEYS
        for key, item in skipped:
            assert ALGORITHMS[key]["name"] in item
            assert "работает только с целыми числами" in item
    else:
        assert skipped is None


@pytest.mark.html
def test_html_index_post_all_wide_range_explains_why_counting_is_skipped(client):
    response = client.post("/", data={"numbers": "0 1000000000000", "algorithm": "all"})
    assert response.status_code == 200
    raw = response.get_data(as_text=True)
    assert "counting" not in timings_rows(raw)
    skipped = skipped_items(raw)
    assert [key for key, _ in skipped] == ["counting"]
    assert "разница между максимумом и минимумом" in skipped[0][1]
    assert "только с целыми" not in skipped[0][1]


@pytest.mark.html
@pytest.mark.parametrize("text, message", [
    ("1 два 3", "«два» — не число."),
    ("", "Введите хотя бы одно число."),
    (" ".join(["1"] * (MAX_ITEMS + 1)), f"Слишком много чисел: максимум {MAX_ITEMS}."),
], ids=["not-a-number", "empty", "too-many"])
def test_html_index_post_invalid_input_shows_error(client, text, message):
    response = client.post("/", data={"numbers": text, "algorithm": "merge"})
    assert response.status_code == 200
    assert message in page_text(response)


@pytest.mark.html
def test_html_index_error_is_exposed_to_assistive_tech(client):
    raw = client.post("/", data={"numbers": "1 2 abc", "algorithm": "merge"}).get_data(as_text=True)
    assert re.search(r"<title>Ошибка — ", raw)
    assert 'id="numbers-error"' in raw
    textarea = re.search(r'<textarea id="numbers"[^>]*>', raw).group(0)
    assert 'aria-describedby="numbers-error numbers-hint"' in textarea
    assert 'aria-invalid="true"' in textarea
    assert "autofocus" in textarea
    # Без ошибки — обычное состояние поля
    raw = client.get("/").get_data(as_text=True)
    textarea = re.search(r'<textarea id="numbers"[^>]*>', raw).group(0)
    assert 'aria-describedby="numbers-hint"' in textarea
    assert "aria-invalid" not in textarea


@pytest.mark.html
def test_html_index_post_nan_shows_error(client):
    response = client.post("/", data={"numbers": "3 nan 1 2", "algorithm": "bubble"})
    assert response.status_code == 200
    assert "«nan» — не число." in page_text(response)


@pytest.mark.html
def test_html_index_post_int_only_with_floats_shows_error(client):
    response = client.post("/", data={"numbers": FORM_TEXT, "algorithm": "counting"})
    assert response.status_code == 200
    assert "работает только с целыми числами" in page_text(response)


@pytest.mark.html
def test_html_index_post_unknown_algorithm_shows_error(client):
    response = client.post("/", data={"numbers": "3 1 2", "algorithm": "unknown"})
    assert response.status_code == 200
    assert "Неизвестный алгоритм." in page_text(response)


@pytest.mark.html
def test_html_index_keeps_entered_text(client):
    response = client.post("/", data={"numbers": "1 два 3", "algorithm": "merge"})
    assert "1 два 3" in page_text(response)


@pytest.mark.html
@pytest.mark.parametrize("key", ALL_KEYS)
def test_html_algorithm_detail(client, key):
    response = client.get(f"/algorithms/{key}")
    assert response.status_code == 200
    assert response.mimetype == "text/html"
    algorithm = ALGORITHMS[key]
    text = page_text(response)
    assert algorithm["name"] in text
    assert algorithm["description"] in text
    for field in ("best", "average", "worst", "memory"):
        assert algorithm[field] in text, field
    # Исходный код модуля (теги подсветки, если есть, уже вырезаны)
    assert f"def {key}_sort(items):" in text
    source = (REPO_ROOT / algorithm["file"]).read_text(encoding="utf-8")
    docstring = re.search(r'"""(.+?)"""', source).group(1)
    assert docstring in text
    assert re.search(rf"<h1>{algorithm['full_name']}</h1>", response.get_data(as_text=True))
    assert "Дробную часть отделяйте точкой" in text
    assert f"Не более {MAX_ITEMS} чисел" in text
    assert "d — число разрядов" in text


@pytest.mark.html
def test_html_unknown_page_is_russian_404(client):
    response = client.get("/algorithms/unknown")
    assert response.status_code == 404
    assert response.mimetype == "text/html"
    text = page_text(response)
    assert "Страница не найдена" in text
    assert "Ошибка 404" in text


@pytest.mark.html
def test_html_too_large_form_is_russian_413(client):
    response = client.post("/", data={"numbers": "1 " * 200_000, "algorithm": "merge"})
    assert response.status_code == 413
    assert response.mimetype == "text/html"
    assert "Слишком большой запрос" in page_text(response)
