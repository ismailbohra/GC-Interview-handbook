# Python GC-Interview Preparation Handbook

This handbook organizes the raw question list into topic-wise sections and adds interview-ready answers below each question. The answers start simple, then go deeper into internals, tradeoffs, and practical engineering use.

## Python Basics

### Question: What are iterators in Python?

Answer:

An iterator is an object that returns one item at a time and keeps track of its current position. In Python, an iterator implements the iterator protocol through `__iter__()` and `__next__()`.

Internally, a `for` loop calls `iter()` to get an iterator and then repeatedly calls `next()` until `StopIteration` is raised. That is why files, lists, generators, and many custom objects can all be used in loops.

In real systems, iterators are useful when you want sequential access over large or streaming data without loading everything into memory. Best practice is to rely on Python's built-in iteration model rather than writing custom iterator classes unless you need explicit state management. A common pitfall is forgetting that iterators are consumable and may not be reusable after one pass.

```python
# Basic usage: iter() and next()
numbers = [10, 20, 30]
iterator = iter(numbers)

print(next(iterator))  # 10
print(next(iterator))  # 20
```

A custom iterator class implementing the full protocol:

```python
class PaginatedAPI:
    """Custom iterator that fetches pages from an API one at a time."""

    def __init__(self, url, page_size=10):
        self.url = url
        self.page_size = page_size
        self._page = 0
        self._exhausted = False

    def __iter__(self):
        return self

    def __next__(self):
        if self._exhausted:
            raise StopIteration
        self._page += 1
        data = self._fetch(self._page)
        if not data:
            self._exhausted = True
            raise StopIteration
        return data

    def _fetch(self, page):
        # In real code this would call requests.get(...)
        return [{"id": i} for i in range((page - 1) * self.page_size, page * self.page_size)]


# Using the custom iterator
for page in PaginatedAPI("/users", page_size=5):
    print(page)  # each iteration lazily fetches one page
    break  # stop after first page for demo
```

Key takeaway: understanding the iterator protocol lets you build memory-efficient abstractions over databases, files, network streams, or any sequential data source.

### Question: What are generators in Python?

Answer:

A generator is a concise way to create an iterator by using `yield`. Instead of computing all results up front, it produces values lazily as they are requested.

Internally, Python stores the generator's execution frame and local variables, pauses at each `yield`, and resumes from the same point on the next `next()` call. That makes generators much more memory efficient than building large intermediate lists.

Generators are a strong fit for streaming files, paginated APIs, event pipelines, and data processing jobs. Best practice is to keep generator logic predictable and side-effect light. A common pitfall is trying to iterate over the same generator twice and forgetting it has already been exhausted.

```python
# Basic generator with yield
def fibonacci(limit):
    first, second = 0, 1
    for _ in range(limit):
        yield first
        first, second = second, first + second
```

Generator expression (inline form):

```python
squares = (x * x for x in range(1_000_000))  # no list created in memory
print(next(squares))  # 0
print(next(squares))  # 1
```

### Question: What are decorators in Python?

Answer:

A decorator is a callable that wraps another function or class to add behavior without modifying the original implementation directly. It is Python's standard way to apply reusable cross-cutting logic.

Internally, decorators usually rely on closures. A wrapper function receives the original function, adds logic before or after it, and returns a new callable. 
Real-world uses include logging, authentication, retries, caching, rate limiting, and instrumentation. Best practice is to keep decorators explicit and lightweight. A common pitfall is adding too much hidden behavior, which makes debugging and reasoning harder.

```python
# Basic decorator

def logged(func):
    def wrapper(*args, **kwargs):
        print(f"calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@logged
def total(numbers):
    return sum(numbers)
```

Class-based decorator (useful for stateful decoration):

```python
class CountCalls:
    """Tracks how many times a function has been called."""

    def __init__(self, func):
        self.func = func
        self.count = 0
        wraps(func)(self)  # preserve metadata

    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"{self.func.__name__} called {self.count} times")
        return self.func(*args, **kwargs)

@CountCalls
def say_hello(name):
    return f"Hello, {name}"

say_hello("Asha")  # say_hello called 1 times
say_hello("Ravi")  # say_hello called 2 times
print(say_hello.count)  # 2
```

### Question: How do list comprehensions work in Python?

Answer:

List comprehensions are a compact way to build a list from another iterable. They are typically used for transformation, filtering, or both.

Internally, Python evaluates the source iterable, applies the expression for each item, optionally filters with an `if` condition, and stores the results in a new list. They are usually faster and clearer than manually appending in a loop when the logic is simple.

Use list comprehensions when the operation is short and readable, such as mapping values or filtering API data. The main pitfall is turning them into dense one-liners with nested logic, which hurts readability.

```python
# Basic filter + transform
numbers = [1, 2, 3, 4, 5, 6]
even_squares = [value * value for value in numbers if value % 2 == 0]
# [4, 16, 36]
```

Conditional expression inside a comprehension (if-else in the expression, not filter):

```python
labels = ["even" if n % 2 == 0 else "odd" for n in range(5)]
# ['even', 'odd', 'even', 'odd', 'even']
```

Key takeaway: comprehensions should stay readable. If the logic needs more than one condition or a nested loop, consider a regular loop or a helper function instead.

### Question: How do dictionary comprehensions work in Python?

Answer:

Dictionary comprehensions work like list comprehensions, but they build key-value pairs instead of a sequence. They are useful when you want to transform data into a lookup structure.

Internally, Python evaluates each item, computes a key and a value, and inserts them into a new dictionary. Because dictionaries are hash-based, they are ideal for indexing and fast retrieval by key.

In real code, they are useful for ID-to-object maps, configuration transformation, and response normalization. Best practice is to keep the key and value expressions simple. A common pitfall is silently overwriting keys if the comprehension generates duplicates.

```python
# Basic ID-to-name mapping
users = [
    {"id": 1, "name": "Asha"},
    {"id": 2, "name": "Ravi"},
]
user_map = {user["id"]: user["name"] for user in users}
# {1: 'Asha', 2: 'Ravi'}
```

Inverting a dictionary:

```python
status_codes = {200: "OK", 404: "Not Found", 500: "Server Error"}
code_lookup = {desc: code for code, desc in status_codes.items()}
# {'OK': 200, 'Not Found': 404, 'Server Error': 500}
```

Key takeaway: dict comprehensions are great for one-to-one mappings.

### Question: When should you use a list in Python?

Answer:

Use a list when order matters, duplicates are allowed, and you need fast indexed access or efficient appends at the end.

Lists are the default general-purpose sequence in Python. The main pitfall is using them for frequent front insertions or front pops, because those operations require shifting the remaining elements.

```python
# Basic usage
tasks = ["parse", "validate"]
tasks.append("store")
print(tasks[0])  # 'parse'
```

Common list operations every backend developer should know:

```python
# Slicing
numbers = [10, 20, 30, 40, 50]
print(numbers[1:4])   # [20, 30, 40]
print(numbers[::-1])  # [50, 40, 30, 20, 10] — reverse

# Sorting with key function
users = [{"name": "Ravi", "age": 30}, {"name": "Asha", "age": 25}]
users.sort(key=lambda u: u["age"])

# Unpacking
first, *rest = [1, 2, 3, 4]
print(first)  # 1
print(rest)   # [2, 3, 4]

# List as stack (append + pop from end is O(1))
stack = []
stack.append("frame-1")
stack.append("frame-2")
stack.pop()  # 'frame-2' — LIFO
```

Performance pitfall — avoid front insertion on large lists:

```python
import timeit
from collections import deque

# list.insert(0, x) is O(n)
timeit.timeit(lambda: [].insert(0, 1), number=100_000)  # slow

# deque.appendleft(x) is O(1)
timeit.timeit(lambda: deque().appendleft(1), number=100_000)  # fast
```

### Question: When should you use a tuple in Python?

Answer:

Use a tuple when the collection is fixed and should not change. Tuples are a good fit for coordinates, fixed records, or values that should be hashable and safe to use as dictionary keys.

Their immutability also communicates intent clearly. In interviews, it is useful to mention that tuples are typically lighter than lists for fixed data.

```python
# Basic tuple unpacking
point = (10, 20)
x, y = point
```

Tuples as dictionary keys (hashable because immutable):

```python
# Using tuples as composite keys for caching or grid lookups
distance_cache = {}
distance_cache[("CityA", "CityB")] = 450
distance_cache[("CityB", "CityC")] = 320
print(distance_cache[("CityA", "CityB")])  # 450
```

`namedtuple` for lightweight immutable records:

```python
from collections import namedtuple

User = namedtuple("User", ["id", "name", "role"])
user = User(id=1, name="Asha", role="admin")

print(user.name)   # 'Asha'
print(user[2])     # 'admin' — still supports indexing
print(user._asdict())  # {'id': 1, 'name': 'Asha', 'role': 'admin'}
```

Tuples for returning multiple values from a function:

```python
def divide(a, b):
    return a // b, a % b  # returns a tuple

quotient, remainder = divide(17, 5)
print(quotient, remainder)  # 3 2
```

### Question: When should you use a set in Python?

Answer:

Use a set when uniqueness and fast membership testing are the main concerns. Sets are ideal for deduplication, intersection, difference operations, and access-control checks.

Internally, sets are hash-based, so membership checks are typically average-case $O(1)$. The pitfall is forgetting that sets are unordered collections of unique elements.

```python
# Basic membership check
seen_users = {101, 102, 103}
print(102 in seen_users)  # True — O(1) average
```

Set operations for real-world use cases:

```python
# Deduplication
raw_ids = [1, 2, 2, 3, 1, 4]
unique_ids = list(set(raw_ids))  # [1, 2, 3, 4] (order not guaranteed)

# Intersection — find common users between two systems
system_a_users = {"asha", "ravi", "priya"}
system_b_users = {"ravi", "ankit", "priya"}
common = system_a_users & system_b_users  # {'ravi', 'priya'}

# Difference — find users only in system A
only_a = system_a_users - system_b_users  # {'asha'}

# Symmetric difference — users in exactly one system
exclusive = system_a_users ^ system_b_users  # {'asha', 'ankit'}
```

`frozenset` for immutable sets (usable as dict keys or set members):

```python
permissions = frozenset(["read", "write"])
role_map = {permissions: "editor"}  # frozenset is hashable
```

### Question: When should you use a dictionary in Python?

Answer:

Use a dictionary when you need key-value storage and fast access by key. Dictionaries are the backbone of configuration objects, caches, object indexing, and JSON-like structures.

They are also hash-based, which is why lookups are typically very fast. Best practice is to choose clear, stable keys and avoid using a dictionary where a simpler structure would communicate the intent better.

```python
# Basic key-value lookup
user_by_id = {101: "Asha", 102: "Ravi"}
print(user_by_id[101])  # 'Asha'
```

Safe access patterns:

```python
# .get() to avoid KeyError
user = user_by_id.get(999, "Unknown")  # 'Unknown'

# setdefault — insert default if key missing, return existing if present
counters = {}
counters.setdefault("login", 0)
counters["login"] += 1
```

`defaultdict` and `Counter` for common patterns:

```python
from collections import defaultdict, Counter

# Grouping items
orders = [("Asha", "Laptop"), ("Ravi", "Phone"), ("Asha", "Mouse")]
by_customer = defaultdict(list)
for name, product in orders:
    by_customer[name].append(product)
# {'Asha': ['Laptop', 'Mouse'], 'Ravi': ['Phone']}

# Counting occurrences
words = ["error", "info", "error", "warn", "error", "info"]
word_counts = Counter(words)
print(word_counts.most_common(2))  # [('error', 3), ('info', 2)]
```

Merging dictionaries (Python 3.9+):

```python
defaults = {"timeout": 30, "retries": 3}
overrides = {"timeout": 10, "debug": True}
config = defaults | overrides  # {'timeout': 10, 'retries': 3, 'debug': True}
```

### Question: When should you use deque in Python?

Answer:

Use `collections.deque` when you need efficient insertion and removal from both ends, especially for queue or sliding-window workloads.

It is the right choice for breadth-first search, job buffering, and consumer-producer style logic. A common pitfall is using a list instead and paying unnecessary front-pop costs.

```python
from collections import deque

# Basic FIFO queue
queue = deque(["job-1", "job-2"])
queue.append("job-3")
print(queue.popleft())  # 'job-1'
```

Bounded deque (automatically discards oldest when full):

```python
from collections import deque

# Keep only the last 5 log entries
recent_logs = deque(maxlen=5)
for i in range(10):
    recent_logs.append(f"log-{i}")
print(list(recent_logs))  # ['log-5', 'log-6', 'log-7', 'log-8', 'log-9']
```

Sliding window pattern (common in interviews and streaming):

```python
from collections import deque

def max_sliding_window(nums, k):
    """Find max in each sliding window of size k using a monotonic deque."""
    result = []
    window = deque()  # stores indices of useful elements
    for i, num in enumerate(nums):
        # Remove indices outside the current window
        while window and window[0] <= i - k:
            window.popleft()
        # Remove smaller elements from the back
        while window and nums[window[-1]] <= num:
            window.pop()
        window.append(i)
        if i >= k - 1:
            result.append(nums[window[0]])
    return result

print(max_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3))
# [3, 3, 5, 5, 6, 7]
```

BFS with deque (the standard interview pattern):

```python
from collections import deque

def bfs(graph, start):
    visited = set()
    queue = deque([start])
    visited.add(start)
    while queue:
        node = queue.popleft()
        print(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

bfs({"A": ["B", "C"], "B": ["D"], "C": [], "D": []}, "A")
```

### Question: Which is better for faster retrieval in Python: a set or a dictionary?

Answer:

For membership checks, both `set` and `dict` are typically average-case $O(1)$ because both are backed by hash tables. If you only need to know whether a value exists, a set is the cleaner structure. If you need associated data, a dictionary is the correct choice.

Internally, both hash the key and look it up in a table. A set stores only keys, while a dictionary stores key-value pairs, so a dictionary usually has a slightly larger memory footprint.

In practice, sets are useful for deduplication and access-control checks, while dictionaries are used for caching, indexing entities, and configuration storage. A common pitfall is using a dictionary with meaningless placeholder values when a set would communicate intent more clearly.

```python
# Set: membership check
allowed_roles = {"admin", "editor"}
print("admin" in allowed_roles)  # True — O(1)

# Dict: key-to-value lookup
role_permissions = {"admin": ["read", "write"], "viewer": ["read"]}
print(role_permissions["admin"])  # ['read', 'write'] — O(1)
```

Memory comparison:

```python
import sys

# Set stores only keys
s = {1, 2, 3, 4, 5}
print(sys.getsizeof(s))  # ~216 bytes

# Dict stores keys + values, so larger footprint
d = {1: None, 2: None, 3: None, 4: None, 5: None}
print(sys.getsizeof(d))  # ~232 bytes
```

Real-world decision guide:

```python
# Use SET when you only care about "is this item present?"
blocked_ips = {"10.0.0.1", "192.168.1.100"}
def is_blocked(ip):
    return ip in blocked_ips

# Use DICT when you need the value associated with the key
rate_limits = {"free": 100, "pro": 1000, "enterprise": 10000}
def get_limit(plan):
    return rate_limits.get(plan, 50)  # default 50 for unknown plans

# Anti-pattern: dict with meaningless values when a set would do
bad = {"admin": True, "editor": True}  # just use a set instead
good = {"admin", "editor"}
```

### Question: What are context managers in Python?

Answer:

A context manager defines setup and cleanup behavior around a block of code and is used with the `with` statement. It usually implements `__enter__()` and `__exit__()`, or is created with `contextlib.contextmanager`.

The idea is to make resource handling explicit. Files, sockets, locks, and database sessions all have an acquire-release lifecycle, and a context manager models that lifecycle directly in code.

Class-based context manager (using the protocol directly):

```python
class DatabaseConnection:
    """Custom context manager implementing __enter__ and __exit__."""

    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.connection = None

    def __enter__(self):
        print(f"Connecting to {self.connection_string}")
        self.connection = {"status": "open"}  # simulate connection
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Closing connection")
        self.connection["status"] = "closed"
        # Return False (or None) to propagate exceptions
        # Return True to suppress exceptions (rarely wanted)
        return False


with DatabaseConnection("postgres://localhost/db") as conn:
    print(conn["status"])  # 'open'
# After the block: connection is guaranteed closed
```

Function-based context manager using `contextlib` (more concise):

```python
from contextlib import contextmanager

@contextmanager
def db_session(session_factory):
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
```

Nested context managers and `contextlib.suppress`:

```python
from contextlib import suppress
import os

# Suppress specific exceptions cleanly
with suppress(FileNotFoundError):
    os.remove("temp_file.txt")  # no error if file doesn't exist

# Multiple context managers in one statement
with open("input.txt") as src, open("output.txt", "w") as dst:
    dst.write(src.read())
```

Key takeaway: use class-based context managers when you need state or reusable objects, and `@contextmanager` for simpler acquire/release patterns.

### Question: Why are context managers important?

Answer:

Context managers matter because they guarantee cleanup, even when an exception occurs. Garbage collection is not a safe substitute for timely release of files, network connections, locks, or transactions.

In production systems, they help prevent leaked file descriptors, unreleased locks, hanging transactions, and inconsistent resource handling. Best practice is to use a context manager whenever resource acquisition and release must be paired. A common pitfall is suppressing exceptions accidentally in `__exit__()` when that was not intended.

```python
# Context manager guarantees cleanup even on exception
with open("app.log", "r", encoding="utf-8") as handle:
    first_line = handle.readline()
# handle is closed here, even if readline() raised an exception
```

What happens WITHOUT a context manager (resource leak):

```python
import os

# BAD: if process() raises, the file descriptor leaks
f = open("data.txt", "w")
f.write("important data")
# process()  <-- if this crashes, f.close() never runs
f.close()

# GOOD: context manager guarantees close
with open("data.txt", "w") as f:
    f.write("important data")
    # even if an exception happens here, __exit__ still runs
```

Real-world pattern — timing block:

```python
import time
from contextlib import contextmanager

@contextmanager
def timer(label):
    start = time.perf_counter()
    yield
    elapsed = time.perf_counter() - start
    print(f"{label}: {elapsed:.4f}s")

with timer("database query"):
    # simulate work
    total = sum(range(1_000_000))
# Output: database query: 0.0312s
```

Real-world pattern — temporary directory:

```python
import tempfile
import os

with tempfile.TemporaryDirectory() as tmpdir:
    path = os.path.join(tmpdir, "report.csv")
    with open(path, "w") as f:
        f.write("id,name\n1,Asha")
    # tmpdir and all files inside are auto-deleted after this block
```

### Question: What is duck typing in Python?

Answer:

Duck typing means Python focuses on behavior rather than declared types. If an object supports the methods or operations your code expects, it can be used, regardless of its inheritance hierarchy.

Internally, Python resolves attribute access at runtime. If the required method exists, the call works; if not, you get an exception such as `AttributeError` or `TypeError`.

This is useful for flexible APIs, file-like objects, dependency injection, and tests that use fakes or mocks. Best practice is to document expected behavior clearly and use protocols or type hints in larger codebases. A common pitfall is being so flexible that interface mismatches are only discovered at runtime.

```python
# Duck typing in action: any object with .read() works
def read_first_line(source):
    return source.read().splitlines()[0]

class FakeFile:
    def read(self):
        return "hello\nworld"

print(read_first_line(FakeFile()))  # 'hello'
```

Using `typing.Protocol` to formalize duck typing (Python 3.8+):

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Readable(Protocol):
    def read(self) -> str: ...

class S3File:
    def read(self) -> str:
        return "data from S3"

class DatabaseBlob:
    def read(self) -> str:
        return "data from DB"

def process(source: Readable) -> str:
    """Works with any object that has a .read() method."""
    return source.read().upper()

# Both work despite having no common base class
print(process(S3File()))         # 'DATA FROM S3'
print(process(DatabaseBlob()))   # 'DATA FROM DB'

# Runtime check
print(isinstance(S3File(), Readable))  # True
```

Key takeaway: `Protocol` bridges duck typing with static type checking. You get the flexibility of duck typing with IDE support and mypy validation.

### Question: How do you create an isolated Python environment?

Answer:

The standard approach is to create a virtual environment with `python -m venv .venv`, activate it, and install packages into that environment instead of the system interpreter.

Internally, the environment points to its own Python executable and its own `site-packages` directory. That prevents dependency clashes across projects.

In real teams, isolated environments make local development, CI, and deployment more predictable. Best practice is to keep the environment directory out of version control and document the setup steps clearly.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Question: How do you share Python dependencies with other developers?

Answer:

You share dependencies by committing a manifest such as `requirements.txt`, `pyproject.toml`, or a lock file, depending on the packaging tool your team uses.

For reproducibility, I prefer making the dependency file the source of truth and documenting the install command in the README. For deployable services, pinning versions matters because unpinned dependencies make builds drift over time.

The common pitfall is assuming everyone has the same globally installed packages or committing a local environment folder instead of the dependency manifest.

```bash
pip freeze > requirements.txt
pip install -r requirements.txt
```

### Question: How would you implement Fibonacci using a generator?

Answer:

The implementation is straightforward: keep track of the previous two numbers and `yield` one value at a time.

```python
def fibonacci(limit):
    first, second = 0, 1
    for _ in range(limit):
        yield first
        first, second = second, first + second

for number in fibonacci(7):
    print(number)
```

This solution runs in $O(n)$ time and uses constant extra memory because it stores only the current state, not the full sequence.

### Question: Why is a generator a good fit for Fibonacci?

Answer:

Fibonacci is naturally incremental, so a generator maps well to the problem. You usually do not need the entire sequence up front; you want values one by one.

That means lazy evaluation, lower memory usage, and clearer intent. In interviews, I usually mention that a list is better only if you need random access or repeated traversal. Otherwise, a generator is cleaner and more scalable.

```python
from itertools import islice

first_five = list(islice(fibonacci(1_000_000), 5))
print(first_five)
```

## Advanced Python

### Question: What is Method Resolution Order in Python?

Answer:

Method Resolution Order, or MRO, is the order Python follows when searching for methods and attributes in a class hierarchy. It becomes especially important in multiple inheritance.

Python uses the C3 linearization algorithm, which preserves local precedence order and produces a deterministic lookup order. That is why `super()` can work consistently even in more complex hierarchies.

```python
# Diamond inheritance: which greet() gets called?
class A:
    def greet(self):
        return "A"

class B(A):
    pass

class C(A):
    def greet(self):
        return "C"

class D(B, C):
    pass

print(D.mro())
# [D, B, C, A, object]
print(D().greet())  # 'C' — C comes before A in MRO
```

Cooperative multiple inheritance with `super()` chaining:

```python
class Base:
    def __init__(self):
        print("Base.__init__")

class Mixin1(Base):
    def __init__(self):
        print("Mixin1.__init__")
        super().__init__()  # delegates to next in MRO

class Mixin2(Base):
    def __init__(self):
        print("Mixin2.__init__")
        super().__init__()

class Service(Mixin1, Mixin2):
    def __init__(self):
        print("Service.__init__")
        super().__init__()

Service()
# Output (follows MRO: Service -> Mixin1 -> Mixin2 -> Base):
# Service.__init__
# Mixin1.__init__
# Mixin2.__init__
# Base.__init__
```

Inspecting MRO programmatically:

```python
# Useful for debugging complex hierarchies
for cls in Service.__mro__:
    print(f"{cls.__name__}: {[m for m in cls.__dict__ if not m.startswith('_')]}")
```

### Question: Why does Method Resolution Order matter in multiple inheritance?

Answer:

Without MRO, Python would have no consistent rule for deciding which parent implementation to call. MRO prevents ambiguity and makes cooperative multiple inheritance possible.

In real systems, that matters when combining mixins for logging, permissions, serialization, or framework behavior. Best practice is to use `super()` consistently. A common pitfall is calling parent classes directly, which can break the resolution chain and duplicate or skip initialization.

```python
class LoggerMixin:
    def save(self):
        print("log before save")
        return super().save()

class Repository:
    def save(self):
        print("saved")

class AuditRepository(LoggerMixin, Repository):
    pass

AuditRepository().save()
```

### Question: How do you handle multiple exceptions in Python?

Answer:

You can catch multiple related exceptions in a single `except` block by passing them as a tuple. That is useful when the recovery behavior is the same.

The key engineering principle is to catch only what you can actually handle. Broad `except Exception` blocks should usually be reserved for process boundaries such as worker loops or request boundaries where you need to log and convert failures.

```python
# Catching multiple related exceptions with shared recovery
try:
    value = int(payload["count"])
except (KeyError, TypeError, ValueError) as error:
    raise ValueError("invalid count field") from error
```

Exception chaining with `from` (preserves the original traceback):

```python
def fetch_user(user_id):
    try:
        return db.query(f"SELECT * FROM users WHERE id = {user_id}")
    except ConnectionError as e:
        raise ServiceUnavailableError("database unreachable") from e
        # The original ConnectionError is preserved in __cause__
```

Exception groups (Python 3.11+) for handling multiple concurrent failures:

```python
# When multiple tasks fail simultaneously (e.g., asyncio.gather)
try:
    raise ExceptionGroup("batch failures", [
        ValueError("bad input in row 1"),
        TypeError("wrong type in row 5"),
    ])
except* ValueError as eg:
    print(f"Value errors: {eg.exceptions}")
except* TypeError as eg:
    print(f"Type errors: {eg.exceptions}")
```

Structured error handling in a real API handler:

```python
from fastapi import HTTPException

def process_order(data: dict):
    try:
        amount = float(data["amount"])
        if amount <= 0:
            raise ValueError("amount must be positive")
    except KeyError:
        raise HTTPException(status_code=400, detail="missing 'amount' field")
    except (TypeError, ValueError) as e:
        raise HTTPException(status_code=422, detail=str(e))
```

### Question: How do you create custom exceptions in Python?

Answer:

You create a custom exception by subclassing `Exception` and giving it a domain-specific name. That makes failure states explicit and easier to handle at higher layers.

Custom exceptions are especially valuable in service code because they separate business failures from generic runtime errors. For example, `InvalidOrderError` communicates much more than a raw `ValueError`.

```python
# Basic custom exception
class InvalidOrderError(Exception):
    pass
```

Custom exception with structured attributes (production pattern):

```python
class DomainError(Exception):
    """Base exception for all business logic errors."""
    def __init__(self, message, code=None, details=None):
        super().__init__(message)
        self.code = code
        self.details = details or {}

class OrderNotFoundError(DomainError):
    pass

class InsufficientStockError(DomainError):
    pass

class PaymentDeclinedError(DomainError):
    pass


# Usage in service layer
def place_order(order_id, quantity):
    stock = get_stock(order_id)
    if stock < quantity:
        raise InsufficientStockError(
            f"Only {stock} items available",
            code="INSUFFICIENT_STOCK",
            details={"available": stock, "requested": quantity},
        )


# Catching at API boundary and converting to HTTP response
from fastapi import HTTPException

try:
    place_order("SKU-100", 50)
except DomainError as e:
    raise HTTPException(
        status_code=422,
        detail={"message": str(e), "code": e.code, **e.details},
    )
```

Key takeaway: a well-designed exception hierarchy lets you catch broad categories (`DomainError`) or specific failures (`InsufficientStockError`), and carry structured data for logging and error responses.

### Question: How do you use finally correctly in Python?

Answer:

Use `finally` for cleanup that must run whether the code succeeds, fails, or returns early. Examples include closing files, releasing locks, or cleaning temporary resources.

Internally, Python executes the `finally` block during stack unwinding. Best practice is to keep it focused on cleanup and avoid putting complex business logic there. A common pitfall is returning from `finally`, which can hide the original exception.

```python
# Basic finally for guaranteed cleanup
handle = open("data.txt", "r", encoding="utf-8")
try:
    print(handle.readline())
finally:
    handle.close()  # runs even if readline() raises
```

try/except/else/finally — the full flow:

```python
def safe_divide(a, b):
    try:
        result = a / b
    except ZeroDivisionError:
        print("Cannot divide by zero")
        return None
    else:
        # Only runs if NO exception occurred
        print(f"Division successful: {result}")
        return result
    finally:
        # ALWAYS runs — even after return statements above
        print("Cleanup complete")

safe_divide(10, 2)
# Division successful: 5.0
# Cleanup complete

safe_divide(10, 0)
# Cannot divide by zero
# Cleanup complete
```

Dangerous pitfall — returning from `finally` swallows exceptions:

```python
def dangerous():
    try:
        raise ValueError("something broke")
    finally:
        return 42  # This SWALLOWS the ValueError silently!

print(dangerous())  # 42 — no error raised, the bug is hidden
```

Real-world pattern — lock release:

```python
import threading

lock = threading.Lock()

def critical_section():
    lock.acquire()
    try:
        # Do work that might fail
        process_shared_resource()
    finally:
        lock.release()  # Lock is ALWAYS released
    # Better: use `with lock:` context manager instead
```

### Question: How does garbage collection work in Python?

Answer:

CPython primarily manages memory through reference counting. When an object's reference count reaches zero, it can usually be reclaimed immediately. On top of that, Python has a cyclic garbage collector for cases where objects reference each other in a cycle.

Internally, container objects are tracked across generations. Younger objects are checked more often because most objects die young. The `gc` module lets you inspect and tune this behavior, but application code usually should not manipulate GC settings without profiling evidence.

The important practical point is that garbage collection handles memory, not timely release of external resources like sockets or database connections. That is why context managers still matter.

```python
import gc
import sys

# Reference counting in action
a = [1, 2, 3]
print(sys.getrefcount(a))  # 2 (variable 'a' + getrefcount argument)

b = a  # another reference
print(sys.getrefcount(a))  # 3

del b  # reference count drops
print(sys.getrefcount(a))  # 2
```

Cyclic references — why the cyclic GC exists:

```python
import gc

class Node:
    def __init__(self, name):
        self.name = name
        self.ref = None

# Create a cycle: a -> b -> a
a = Node("A")
b = Node("B")
a.ref = b
b.ref = a  # circular reference

# Delete the variables, but the cycle keeps objects alive
del a, b

# Reference counting alone can't free them
# The cyclic garbage collector detects and collects them
collected = gc.collect()
print(f"Cyclic GC collected {collected} objects")
```

Generational garbage collection:

```python
import gc

# Python uses 3 generations: young, middle, old
# Most objects die young, so Gen 0 is checked most often
print(gc.get_threshold())   # (700, 10, 10) by default
print(gc.get_count())       # (current gen0, gen1, gen2 counts)
```

Weak references — reference without preventing garbage collection:

```python
import weakref

class ExpensiveObject:
    def __init__(self, name):
        self.name = name

obj = ExpensiveObject("cache-entry")
weak = weakref.ref(obj)

print(weak())        # <ExpensiveObject object> — still alive
del obj
print(weak())        # None — garbage collected, weak ref doesn't prevent it
```

Key takeaway: GC handles memory, but not external resources. Always use context managers for files, sockets, and connections regardless of GC behavior.

## OOP Concepts

### Question: What is encapsulation in object-oriented programming?

Answer:

Encapsulation means bundling data and behavior together and controlling how internal state is accessed or modified. The goal is to protect invariants and make the object responsible for its own correctness.

In Python, encapsulation is supported more by conventions and API design than by strict access modifiers. In practice, private behavior is usually indicated with an underscore prefix, and well-designed methods expose safe operations instead of raw state mutation.

```python
# Basic encapsulation: underscore convention
class BankAccount:
    def __init__(self):
        self._balance = 0

    def deposit(self, amount):
        self._balance += amount
```

Using `@property` for controlled access (getter/setter pattern):

```python
class BankAccount:
    def __init__(self, initial_balance=0):
        self._balance = initial_balance
        self._transactions = []

    @property
    def balance(self):
        """Read-only access to balance."""
        return self._balance

    @balance.setter
    def balance(self, value):
        raise AttributeError("Use deposit() or withdraw() to change balance")

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit must be positive")
        self._balance += amount
        self._transactions.append(("deposit", amount))

    def withdraw(self, amount):
        if amount > self._balance:
            raise ValueError("Insufficient funds")
        self._balance -= amount
        self._transactions.append(("withdraw", amount))

    @property
    def transaction_history(self):
        """Return a copy so internal list can't be mutated externally."""
        return list(self._transactions)


account = BankAccount(100)
account.deposit(50)
account.withdraw(30)
print(account.balance)              # 120
print(account.transaction_history)   # [('deposit', 50), ('withdraw', 30)]
# account.balance = 999             # AttributeError!
```

Name mangling with double underscore (rarely needed but good to know):

```python
class Secret:
    def __init__(self):
        self.__key = "hidden"  # name-mangled to _Secret__key

s = Secret()
# print(s.__key)         # AttributeError
print(s._Secret__key)    # 'hidden' — still accessible, just discouraged
```

Key takeaway: Python uses conventions, not compiler enforcement. `@property` is the Pythonic way to add validation while keeping the API clean.

### Question: What is abstraction in object-oriented programming?

Answer:

Abstraction means exposing what an object does while hiding unnecessary implementation details. It lets callers depend on a clean interface instead of on low-level mechanics.

In backend systems, abstraction is useful for repositories, payment gateways, storage providers, and service contracts. Best practice is to hide complexity without hiding behavior. A common pitfall is creating abstractions so generic that they stop being meaningful.

```python
from abc import ABC, abstractmethod

# Abstract base class defining the contract
class Storage(ABC):
    @abstractmethod
    def save(self, key: str, data: bytes) -> None:
        pass

    @abstractmethod
    def load(self, key: str) -> bytes:
        pass
```

Concrete implementations hiding internal complexity:

```python
import json
import os

class LocalFileStorage(Storage):
    def __init__(self, base_dir: str):
        self.base_dir = base_dir

    def save(self, key: str, data: bytes) -> None:
        path = os.path.join(self.base_dir, key)
        with open(path, "wb") as f:
            f.write(data)

    def load(self, key: str) -> bytes:
        path = os.path.join(self.base_dir, key)
        with open(path, "rb") as f:
            return f.read()


class S3Storage(Storage):
    def __init__(self, bucket: str, client):
        self.bucket = bucket
        self.client = client

    def save(self, key: str, data: bytes) -> None:
        self.client.put_object(Bucket=self.bucket, Key=key, Body=data)

    def load(self, key: str) -> bytes:
        response = self.client.get_object(Bucket=self.bucket, Key=key)
        return response["Body"].read()


# Caller code is decoupled from storage details
def backup_report(storage: Storage, report_data: bytes):
    storage.save("report_2024.pdf", report_data)

# Switch implementations without changing business logic
backup_report(LocalFileStorage("/tmp/backups"), b"PDF data")
# backup_report(S3Storage("my-bucket", s3_client), b"PDF data")
```

Key takeaway: abstraction lets you define WHAT an interface does while hiding HOW each implementation does it. Callers program against the abstract contract.

### Question: What is inheritance in object-oriented programming?

Answer:

Inheritance allows a class to reuse or extend behavior from a base class. It models an "is-a" relationship.

It is useful when the subtype truly preserves the contract of the parent type. In Python, inheritance also interacts with MRO and `super()`, so cooperative design matters. A common pitfall is building deep inheritance trees for convenience when composition would be safer.

```python
# Basic inheritance
class Vehicle:
    def __init__(self, brand):
        self.brand = brand

    def move(self):
        return f"{self.brand} is moving"

class Car(Vehicle):
    pass

print(Car("Toyota").move())  # 'Toyota is moving'
```

Method overriding with `super()` to extend (not replace) parent behavior:

```python
class Vehicle:
    def __init__(self, brand, year):
        self.brand = brand
        self.year = year

    def describe(self):
        return f"{self.year} {self.brand}"

class ElectricCar(Vehicle):
    def __init__(self, brand, year, battery_kwh):
        super().__init__(brand, year)  # reuse parent init
        self.battery_kwh = battery_kwh

    def describe(self):
        base = super().describe()  # extend parent method
        return f"{base} (Electric, {self.battery_kwh} kWh)"

car = ElectricCar("Tesla", 2024, 75)
print(car.describe())  # '2024 Tesla (Electric, 75 kWh)'
```

Inheritance gone wrong — when subtype violates the parent contract:

```python
# Anti-pattern: Square inheriting from Rectangle breaks expectations
class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

class Square(Rectangle):
    def __init__(self, side):
        super().__init__(side, side)
    # If someone sets square.width = 5, height stays unchanged
    # This violates the Liskov Substitution Principle
```

Key takeaway: inherit only when the subtype truly IS-A parent type and preserves all behavioral guarantees.

### Question: What is polymorphism in object-oriented programming?

Answer:

Polymorphism means different objects can respond to the same interface in different ways. That lets you write code against behavior rather than concrete implementations.

This is powerful in business applications because you can swap strategies, payment methods, storage backends, or serializers without changing the calling code.

```python
# Polymorphism: different classes, same interface
class PaymentMethod:
    def pay(self, amount):
        raise NotImplementedError

class CardPayment(PaymentMethod):
    def pay(self, amount):
        return f"Paid {amount} by card"

class UpiPayment(PaymentMethod):
    def pay(self, amount):
        return f"Paid {amount} by UPI"

class CryptoPayment(PaymentMethod):
    def pay(self, amount):
        return f"Paid {amount} by crypto"
```

Polymorphism in action — caller doesn't need to know the concrete type:

```python
def checkout(payment: PaymentMethod, total: float):
    """Works with any payment method without type checking."""
    result = payment.pay(total)
    print(result)
    return result

# All three work identically from the caller's perspective
checkout(CardPayment(), 99.99)
checkout(UpiPayment(), 99.99)
checkout(CryptoPayment(), 99.99)
```

Polymorphism with a registry pattern (extensible without modifying existing code):

```python
class NotificationSender:
    def send(self, message: str, recipient: str) -> None:
        raise NotImplementedError

class EmailSender(NotificationSender):
    def send(self, message, recipient):
        print(f"Email to {recipient}: {message}")

class SmsSender(NotificationSender):
    def send(self, message, recipient):
        print(f"SMS to {recipient}: {message}")

class SlackSender(NotificationSender):
    def send(self, message, recipient):
        print(f"Slack to {recipient}: {message}")

# Registry: add new senders without changing dispatch logic
SENDERS = {
    "email": EmailSender(),
    "sms": SmsSender(),
    "slack": SlackSender(),
}

def notify(channel: str, message: str, recipient: str):
    sender = SENDERS.get(channel)
    if not sender:
        raise ValueError(f"Unknown channel: {channel}")
    sender.send(message, recipient)  # polymorphic dispatch

notify("email", "Order shipped", "asha@example.com")
notify("slack", "Deploy complete", "#ops")
```

### Question: When should you prefer composition over inheritance?

Answer:

Prefer composition when the relationship is really "has-a" rather than "is-a", or when behavior should be assembled from smaller parts. Composition usually reduces coupling and makes change safer.

For example, composing a service from a repository, validator, and logger is usually cleaner than inheriting from a large base service class. Best practice is to use inheritance only when the subtype relationship is stable and behaviorally correct. A common pitfall is deep inheritance hierarchies that become fragile over time.

```python
# Basic composition: service composed of smaller parts
class OrderService:
    def __init__(self, repository, notifier):
        self.repository = repository
        self.notifier = notifier
```

Full working example showing composition vs inheritance:

```python
# Components (small, focused, reusable)
class OrderRepository:
    def save(self, order):
        print(f"Saved order {order['id']} to database")
        return order

    def find(self, order_id):
        return {"id": order_id, "status": "pending"}

class InventoryChecker:
    def check(self, product_id, quantity):
        available = 100  # simulate inventory lookup
        return available >= quantity

class EmailNotifier:
    def send(self, to, subject, body):
        print(f"Email to {to}: {subject}")

class EventLogger:
    def log(self, event_type, data):
        print(f"Event: {event_type} | {data}")


# Composed service: assembles behavior from parts
class OrderService:
    def __init__(self, repo, inventory, notifier, logger):
        self.repo = repo
        self.inventory = inventory
        self.notifier = notifier
        self.logger = logger

    def place_order(self, customer_email, product_id, quantity):
        if not self.inventory.check(product_id, quantity):
            raise ValueError("Insufficient stock")

        order = self.repo.save({"id": 1, "product": product_id, "qty": quantity})
        self.notifier.send(customer_email, "Order Confirmed", f"Order #{order['id']}")
        self.logger.log("order_placed", {"order_id": order["id"]})
        return order


# Easy to test: inject mocks for any component
service = OrderService(
    repo=OrderRepository(),
    inventory=InventoryChecker(),
    notifier=EmailNotifier(),
    logger=EventLogger(),
)
service.place_order("asha@example.com", "SKU-100", 2)
```

Key takeaway: composition gives you flexibility to swap, mock, or recombine parts. Inheritance locks you into a rigid tree structure that becomes brittle as requirements change.

## Concurrency (Threads / Processes / Asyncio)

### Question: What is the difference between a thread and a process?

Answer:

A process has its own memory space and operating system resources. A thread runs inside a process and shares that process memory with other threads.

That means threads are lighter and cheaper to create, but shared state becomes a correctness risk. Processes are heavier, but they give better isolation and are a stronger choice for CPU-bound parallel work in CPython.

```python
import threading
import multiprocessing

# Basic creation
thread = threading.Thread(target=print, args=("io-task",))
process = multiprocessing.Process(target=print, args=("cpu-task",))
```

Shared state in threads (same memory — needs synchronization):

```python
import threading

counter = 0
lock = threading.Lock()

def increment(n):
    global counter
    for _ in range(n):
        with lock:  # Without this lock, counter becomes incorrect
            counter += 1

threads = [threading.Thread(target=increment, args=(100_000,)) for _ in range(4)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print(counter)  # 400000 (correct because of lock)
```

Processes have isolated memory (no shared state by default):

```python
import multiprocessing

def worker(shared_value, lock):
    for _ in range(100_000):
        with lock:
            shared_value.value += 1

if __name__ == "__main__":
    # Explicit shared memory required for inter-process communication
    shared = multiprocessing.Value("i", 0)
    lock = multiprocessing.Lock()

    processes = [multiprocessing.Process(target=worker, args=(shared, lock)) for _ in range(4)]
    for p in processes:
        p.start()
    for p in processes:
        p.join()
    print(shared.value)  # 400000
```

Key takeaway: threads share memory (fast but dangerous), processes are isolated (safe but heavier). Choose based on whether you need shared state or true CPU parallelism.

### Question: What is the difference between asyncio and threading?

Answer:

`asyncio` is cooperative concurrency built around an event loop. Tasks yield control explicitly at `await` points. Threading is preemptive concurrency managed by the operating system scheduler.

`asyncio` shines when you have many waiting I/O operations and an async-friendly stack. Threading is often more practical when the libraries you depend on are blocking and synchronous. The common pitfall is calling blocking code inside the event loop and stalling every task.

```python
# asyncio: cooperative concurrency with explicit await points
import asyncio
import httpx

async def fetch_user(client, user_id):
    response = await client.get(f"https://api.example.com/users/{user_id}")
    return response.json()

async def main():
    async with httpx.AsyncClient() as client:
        # All three run concurrently, not sequentially
        tasks = [fetch_user(client, uid) for uid in [1, 2, 3]]
        results = await asyncio.gather(*tasks)
    return results
```

Threading: preemptive concurrency with blocking libraries:

```python
import requests
from concurrent.futures import ThreadPoolExecutor

def fetch_user_sync(user_id):
    response = requests.get(f"https://api.example.com/users/{user_id}", timeout=5)
    return response.json()

# Threads handle the blocking I/O
with ThreadPoolExecutor(max_workers=5) as pool:
    futures = [pool.submit(fetch_user_sync, uid) for uid in [1, 2, 3]]
    results = [f.result() for f in futures]
```

Mixing async with blocking code (run blocking code in a thread from async):

```python
import asyncio

async def async_main():
    loop = asyncio.get_event_loop()
    # Run blocking function in a thread pool without blocking the event loop
    result = await loop.run_in_executor(None, fetch_user_sync, 1)
    return result
```

Key takeaway: use asyncio when your entire stack is async-aware. Use threading when you have blocking libraries. Never call blocking code directly inside an async function.

### Question: Are API calls considered I/O-bound tasks?

Answer:

Yes. Network calls are classic I/O-bound work because the process spends most of its time waiting on the network, not using CPU.

That is why threads or async tasks can improve throughput for API-heavy workflows. The important follow-up is that concurrency alone is not enough; you also need timeouts, retries, rate limiting, and partial failure handling.

```python
import requests

response = requests.get("https://example.com/health", timeout=5)
print(response.status_code)
```

Why concurrency helps — sequential vs concurrent API calls:

```python
import time
import requests
from concurrent.futures import ThreadPoolExecutor

urls = [f"https://httpbin.org/delay/1" for _ in range(5)]

# Sequential: ~5 seconds total (each waits for the previous)
def sequential():
    return [requests.get(url, timeout=5).status_code for url in urls]

# Concurrent: ~1 second total (all wait in parallel)
def concurrent():
    with ThreadPoolExecutor(max_workers=5) as pool:
        futures = [pool.submit(requests.get, url, timeout=5) for url in urls]
        return [f.result().status_code for f in futures]

start = time.time()
sequential()
print(f"Sequential: {time.time() - start:.1f}s")  # ~5s

start = time.time()
concurrent()
print(f"Concurrent: {time.time() - start:.1f}s")  # ~1s
```

Key takeaway: the CPU is idle during network waits, so threads/async let you overlap those waits. But always add timeouts, retries, and error handling per request.

### Question: How should you run API calls concurrently?

Answer:

If your application is synchronous, a thread pool is usually the pragmatic choice. If your application is already async, use `asyncio` with an async client such as `httpx` or `aiohttp`.

Best practice is to bound concurrency, set explicit timeouts, and handle errors per request rather than letting one failure collapse the whole batch.

```python
import asyncio
import httpx

async def fetch(url, client):
    response = await client.get(url, timeout=5.0)
    response.raise_for_status()
    return response.json()

async def fetch_all(urls):
    async with httpx.AsyncClient() as client:
        return await asyncio.gather(*(fetch(url, client) for url in urls))
```

With bounded concurrency using `asyncio.Semaphore` (production pattern):

```python
import asyncio
import httpx

async def fetch_with_limit(url, client, semaphore):
    async with semaphore:  # limit concurrent requests
        response = await client.get(url, timeout=10.0)
        response.raise_for_status()
        return response.json()

async def fetch_all_bounded(urls, max_concurrent=5):
    semaphore = asyncio.Semaphore(max_concurrent)
    async with httpx.AsyncClient() as client:
        tasks = [fetch_with_limit(url, client, semaphore) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    # Separate successes from failures
    successes = [r for r in results if not isinstance(r, Exception)]
    failures = [r for r in results if isinstance(r, Exception)]
    print(f"Succeeded: {len(successes)}, Failed: {len(failures)}")
    return successes
```

Synchronous approach with `ThreadPoolExecutor` and retry logic:

```python
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_with_retry(url, max_retries=3):
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            if attempt == max_retries:
                raise
            print(f"Retry {attempt}/{max_retries} for {url}: {e}")

def fetch_all_sync(urls, workers=10):
    results = {}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        future_to_url = {pool.submit(fetch_with_retry, url): url for url in urls}
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                results[url] = future.result()
            except Exception as e:
                results[url] = {"error": str(e)}
    return results
```

Key takeaway: always bound concurrency, set timeouts, handle partial failures, and choose async vs threads based on your stack.

### Question: What is the Global Interpreter Lock in Python?

Answer:

The Global Interpreter Lock, or GIL, is a mutex in CPython that allows only one thread at a time to execute Python bytecode inside a process.

It exists mainly to simplify memory management for CPython's reference-counted object model. The GIL does not mean threads are useless, but it does mean CPU-bound Python bytecode does not run in true parallel on multiple cores inside one process.

```python
# GIL means only one thread executes Python bytecode at a time
# But I/O releases the GIL, so threads still help for I/O

import threading
import time

def cpu_bound(n):
    """Pure CPU work — GIL prevents true parallelism in threads."""
    total = 0
    for i in range(n):
        total += i * i
    return total

# Single thread
start = time.time()
cpu_bound(10_000_000)
print(f"Single thread: {time.time() - start:.2f}s")

# Two threads — NOT faster due to GIL contention
start = time.time()
t1 = threading.Thread(target=cpu_bound, args=(5_000_000,))
t2 = threading.Thread(target=cpu_bound, args=(5_000_000,))
t1.start(); t2.start()
t1.join(); t2.join()
print(f"Two threads: {time.time() - start:.2f}s")  # same or slower!
```

Key takeaway: for CPU-bound work, threads do NOT help in CPython. The GIL serializes Python bytecode execution. Use `multiprocessing` or C extensions for true CPU parallelism.

### Question: How does the GIL affect threads and processes?

Answer:

For CPU-bound work, the GIL limits the benefit of threads in CPython, so multiprocessing is usually the better fit. For I/O-bound work, threads still help because the interpreter releases the GIL during many blocking system calls.

Best practice is simple: use threads for I/O-heavy workloads, processes for CPU-heavy workloads, and measure real bottlenecks instead of blaming every performance issue on the GIL.

```python
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import time

def cpu_work(n):
    return sum(i * i for i in range(n))

def io_work(url):
    import requests
    return requests.get(url, timeout=5).status_code

# CPU-bound: ProcessPoolExecutor bypasses GIL (separate interpreters)
with ProcessPoolExecutor(max_workers=4) as pool:
    results = list(pool.map(cpu_work, [5_000_000] * 4))
    # Actually runs in parallel on multiple cores

# I/O-bound: ThreadPoolExecutor is sufficient (GIL released during I/O)
with ThreadPoolExecutor(max_workers=10) as pool:
    urls = ["https://httpbin.org/get"] * 10
    results = list(pool.map(io_work, urls))
    # Threads overlap I/O waits effectively
```

Decision matrix:

```python
# Choose based on workload type:
#
# | Workload   | Tool                  | Why                          |
# |------------|-----------------------|------------------------------|
# | I/O-bound  | ThreadPoolExecutor    | GIL released during I/O      |
# | I/O-bound  | asyncio               | Even lighter, no thread cost |
# | CPU-bound  | ProcessPoolExecutor   | Bypasses GIL completely      |
# | CPU-bound  | C extension / NumPy   | GIL released in C code       |
# | Mixed      | Processes + async I/O | Isolate CPU from I/O         |
```

## Testing

### Question: What is the default testing module in Python?

Answer:

The standard library testing framework is `unittest`. It provides test cases, assertions, setup and teardown hooks, and test discovery out of the box.

It follows an xUnit style and is fully capable for many projects, especially when external dependencies are limited or a legacy codebase already uses it.

```python
import unittest

class TestMath(unittest.TestCase):
    def test_add(self):
        self.assertEqual(1 + 1, 2)
```

Full `unittest` example with setUp, tearDown, and multiple assertion types:

```python
import unittest

class TestUserService(unittest.TestCase):
    def setUp(self):
        """Runs before each test method."""
        self.users = {1: {"name": "Asha", "role": "admin"}}

    def tearDown(self):
        """Runs after each test method."""
        self.users.clear()

    def test_user_exists(self):
        self.assertIn(1, self.users)

    def test_user_name(self):
        self.assertEqual(self.users[1]["name"], "Asha")

    def test_user_not_found(self):
        with self.assertRaises(KeyError):
            _ = self.users[999]

    def test_role_is_string(self):
        self.assertIsInstance(self.users[1]["role"], str)

    @unittest.skip("Feature not yet implemented")
    def test_future_feature(self):
        pass


if __name__ == "__main__":
    unittest.main()
```

### Question: How does unittest compare with pytest?

Answer:

`unittest` is class-based and more explicit. `pytest` is usually more ergonomic because it supports function-based tests, better assertion introspection, parameterization, and a strong plugin ecosystem.

In practice, I usually prefer `pytest` for modern application code because it reduces boilerplate and scales well. The pitfall is focusing on framework preference instead of test quality; good test design matters more than the tool.

```python
# unittest: class-based, explicit assertions
self.assertEqual(total([1, 2]), 3)
self.assertRaises(ValueError, parse, "bad")
self.assertTrue(is_valid(data))

# pytest: function-based, plain assert with introspection
assert total([1, 2]) == 3
assert is_valid(data)
with pytest.raises(ValueError, match="invalid"):
    parse("bad")
```

Parameterized tests (pytest excels here):

```python
import pytest

@pytest.mark.parametrize("input_val, expected", [
    ([1, 2, 3], 6),
    ([], 0),
    ([10], 10),
    ([-1, 1], 0),
])
def test_total(input_val, expected):
    assert sum(input_val) == expected
```

Custom markers and test organization:

```python
import pytest

@pytest.mark.slow
def test_heavy_computation():
    result = expensive_operation()
    assert result > 0

@pytest.mark.integration
def test_database_connection():
    conn = connect_to_db()
    assert conn.is_alive()

# Run only fast tests: pytest -m "not slow"
# Run integration tests: pytest -m integration
```

### Question: What are fixtures in pytest?

Answer:

Fixtures are reusable setup components that provide dependencies to tests, such as users, clients, temp directories, or database sessions.

Pytest resolves fixtures by name and manages their lifecycle by scope, which makes test setup more composable than repeating setup logic in every test.

```python
import pytest

@pytest.fixture
def sample_user():
    return {"id": 1, "name": "Asha", "role": "admin"}

def test_user_role(sample_user):
    assert sample_user["role"] == "admin"
```

Fixture scopes and composition:

```python
import pytest

@pytest.fixture(scope="session")
def db_connection():
    """Created once for the entire test session."""
    conn = create_connection("test_db")
    yield conn
    conn.close()  # cleanup after all tests finish

@pytest.fixture(scope="function")
def db_session(db_connection):
    """Created fresh for each test function, uses the shared connection."""
    session = db_connection.create_session()
    yield session
    session.rollback()  # rollback after each test for isolation

@pytest.fixture
def sample_order(db_session):
    """Fixture composing with db_session."""
    order = {"id": 1, "product": "Laptop", "amount": 999.99}
    db_session.add(order)
    return order

def test_order_amount(sample_order):
    assert sample_order["amount"] == 999.99
```

Shared fixtures in `conftest.py` (auto-discovered by pytest):

```python
# conftest.py (place in tests/ directory)
import pytest

@pytest.fixture
def api_client():
    """Available to ALL tests without explicit import."""
    from fastapi.testclient import TestClient
    from app.main import app
    return TestClient(app)

@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test-token-123"}
```

### Question: Why are fixtures useful in pytest?

Answer:

Fixtures reduce duplication, make dependencies explicit, and keep test setup consistent. They are especially useful when multiple tests need the same environment, objects, or mocks.

Best practice is to keep fixtures small and composable. A common pitfall is building overly complex fixture graphs that hide where test state is actually coming from.

```python
def test_name(sample_user):
    assert sample_user["name"] == "Asha"

def test_id(sample_user):
    assert sample_user["id"] == 1
```

### Question: What is mocking in tests?

Answer:

Mocking means replacing a real dependency with a controllable test double. In Python, the standard tool is usually `unittest.mock`.

You typically mock things outside the unit under test, such as HTTP clients, email senders, cloud SDKs, or time functions. That keeps tests deterministic and focused.

```python
from unittest.mock import patch, MagicMock

with patch("service.send_email") as mock_send:
    mock_send.return_value = True
```

Full mock example — testing a service without real dependencies:

```python
from unittest.mock import patch, MagicMock, call

class OrderService:
    def __init__(self, repo, notifier):
        self.repo = repo
        self.notifier = notifier

    def place_order(self, data):
        order = self.repo.save(data)
        self.notifier.send(order["id"], "Order placed")
        return order


def test_place_order():
    # Create mock dependencies
    mock_repo = MagicMock()
    mock_repo.save.return_value = {"id": 42, "status": "created"}

    mock_notifier = MagicMock()

    service = OrderService(repo=mock_repo, notifier=mock_notifier)
    result = service.place_order({"product": "Laptop"})

    # Verify behavior
    assert result["id"] == 42
    mock_repo.save.assert_called_once_with({"product": "Laptop"})
    mock_notifier.send.assert_called_once_with(42, "Order placed")
```

Mocking with `side_effect` for sequences and errors:

```python
from unittest.mock import MagicMock

mock_api = MagicMock()

# Return different values on successive calls
mock_api.fetch.side_effect = [{"id": 1}, {"id": 2}, {"id": 3}]
print(mock_api.fetch())  # {'id': 1}
print(mock_api.fetch())  # {'id': 2}

# Simulate an exception on the first call, success on retry
mock_api.fetch.side_effect = [ConnectionError("timeout"), {"id": 1}]
try:
    mock_api.fetch()
except ConnectionError:
    result = mock_api.fetch()  # succeeds on retry
    assert result["id"] == 1
```

Patching at the correct location:

```python
# WRONG: patching where the function is defined
with patch("email_module.send_email"):
    ...

# RIGHT: patching where the function is imported/used
with patch("order_service.send_email"):
    ...
# Always patch where the name is looked up, not where it's defined
```

### Question: Why do we use mocks in tests?

Answer:

We use mocks to isolate units of behavior, avoid slow or flaky external dependencies, and simulate edge cases that are hard to trigger with real systems.

Best practice is to mock at system boundaries, not every internal helper. The common pitfall is over-mocking, which creates tests that pass even though the real integration is broken.

```python
@patch("payments.gateway.charge")
def test_charge_failure(mock_charge):
    mock_charge.side_effect = TimeoutError()
    # Now test that your code handles the timeout correctly
```

Real-world example — testing an API endpoint with mocked database:

```python
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

def test_get_user_not_found(api_client):
    with patch("app.services.user_service.get_user") as mock_get:
        mock_get.return_value = None

        response = api_client.get("/users/999")

        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"
        mock_get.assert_called_once_with(999)


def test_get_user_success(api_client):
    with patch("app.services.user_service.get_user") as mock_get:
        mock_get.return_value = {"id": 1, "name": "Asha"}

        response = api_client.get("/users/1")

        assert response.status_code == 200
        assert response.json()["name"] == "Asha"
```

Key takeaway: mock at system boundaries (HTTP clients, databases, email), not every internal helper. Over-mocking creates tests that pass even when real integration is broken.

## Logging / Debugging

### Question: How do you debug code in practice?

Answer:

I usually start by reproducing the issue reliably, narrowing the failing path, inspecting logs and inputs, and then validating assumptions with a debugger, focused logging, or a small isolated test.

At a senior level, debugging is less about printing random values and more about building a theory, testing it quickly, and tracing the failure to the real boundary where bad state first appears.

```python
# Quick debugging with breakpoint()
def process(order):
    breakpoint()  # drops into pdb debugger
    return order["total"] * 0.18
```

Structured debugging approach:

```python
import logging
import traceback

logger = logging.getLogger(__name__)

def debug_failing_function(data):
    # Step 1: Log inputs to reproduce the issue
    logger.debug(f"Input data: {data}")

    try:
        result = transform(data)
    except Exception as e:
        # Step 2: Capture full traceback
        logger.error(f"Failed to transform: {e}")
        logger.error(traceback.format_exc())

        # Step 3: Inspect the problematic state
        logger.error(f"Data type: {type(data)}, keys: {data.keys() if hasattr(data, 'keys') else 'N/A'}")
        raise

    return result
```

Using `pdb` commands effectively:

```python
# Inside pdb/breakpoint():
# l (list)       — show surrounding code
# n (next)       — execute next line
# s (step)       — step into function call
# c (continue)   — continue until next breakpoint
# p variable     — print variable value
# pp expression  — pretty-print expression
# w (where)      — show call stack
# b 42           — set breakpoint at line 42
# !expr          — evaluate Python expression

# Conditional breakpoint:
import pdb
for i, item in enumerate(items):
    if item["status"] == "failed":
        pdb.set_trace()  # only break on failed items
```

Writing a minimal reproducer test:

```python
def test_reproduce_bug_123():
    """Minimal test to reproduce reported issue."""
    # Exact input that triggered the bug
    bad_input = {"amount": "not-a-number", "currency": None}

    # This should raise ValueError, not crash with TypeError
    with pytest.raises(ValueError, match="invalid amount"):
        process_payment(bad_input)
```

Key takeaway: senior debugging is systematic — reproduce, isolate, inspect state at the failure boundary, fix, and add a regression test.

### Question: When should you use logging instead of print statements?

Answer:

Use logging whenever the output needs severity levels, timestamps, routing, structure, searchability, or production visibility. `print()` is acceptable for a quick local check, but it does not scale operationally.

The Python `logging` module routes records through loggers, handlers, and formatters, which lets you send the same event to console, files, or centralized systems. A common pitfall is logging secrets or writing noisy logs that no one can use during an incident.

```python
import logging

# Basic configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("order processed", extra={"order_id": 101})
```

Proper logging setup with handlers and formatters:

```python
import logging
import sys

def setup_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    ))

    # File handler for errors only
    file_handler = logging.FileHandler("errors.log")
    file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(funcName)s:%(lineno)d | %(message)s"
    ))

    logger.addHandler(console)
    logger.addHandler(file_handler)
    return logger


logger = setup_logger("myapp")
logger.info("Server started on port 8000")
logger.warning("Slow query detected", extra={"latency_ms": 850})
logger.error("Failed to connect to payment gateway")
```

Log levels and when to use each:

```python
logger.debug("Query params: %s", params)      # Development only
logger.info("Order %s created", order_id)       # Normal operations
logger.warning("Rate limit approaching: %d/100", count)  # Needs attention
logger.error("Payment failed: %s", str(e))      # Error but service continues
logger.critical("Database connection lost")      # Service may be down
```

Key takeaway: never use `print()` in production code. Configure handlers for different destinations (console, file, cloud), and use structured data for searchability.

### Question: How would you design logging for a real backend application?

Answer:

I would standardize structured logs, usually JSON in production, include request correlation IDs, and ensure the service logs meaningful lifecycle events, downstream failures, and latency.

In a web service, middleware is a good place to attach request metadata and write one summary log per request. Business code should log domain-significant events, not every line of execution. Best practice is to make logs actionable: what failed, where it failed, and which identifiers help trace the issue further.

```python
import logging

logger = logging.getLogger("api")
logger.info(
    "request_complete",
    extra={"request_id": "req-123", "path": "/users", "latency_ms": 42},
)
```

Structured JSON logging for production (machine-readable):

```python
import logging
import json
import uuid
from datetime import datetime, timezone

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }
        # Include any extra fields
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id
        if hasattr(record, "latency_ms"):
            log_entry["latency_ms"] = record.latency_ms
        return json.dumps(log_entry)

# Setup
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger = logging.getLogger("api")
logger.addHandler(handler)
logger.setLevel(logging.INFO)

logger.info("request handled", extra={"request_id": "req-abc", "latency_ms": 42})
# Output: {"timestamp": "2024-...", "level": "INFO", "message": "request handled", "request_id": "req-abc", "latency_ms": 42}
```

Request correlation middleware (FastAPI example):

```python
import uuid
import logging
from contextvars import ContextVar
from fastapi import FastAPI, Request

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")

class CorrelationFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_var.get()
        return True

logger = logging.getLogger("api")
logger.addFilter(CorrelationFilter())

app = FastAPI()

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    rid = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request_id_var.set(rid)
    logger.info(f"Started {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Completed {response.status_code}", extra={"latency_ms": 42})
    response.headers["X-Request-ID"] = rid
    return response
```

Key takeaway: production logging should be structured (JSON), include correlation IDs, and log meaningful lifecycle events — not every line of code.

## Databases (SQL / NoSQL)

### Question: What are ACID properties?

Answer:

ACID stands for Atomicity, Consistency, Isolation, and Durability. Atomicity means a transaction either fully succeeds or fully fails. Consistency means the database moves from one valid state to another. Isolation means concurrent transactions should not interfere in a way that breaks correctness. Durability means committed data survives crashes.

Internally, databases enforce these guarantees using locks, multiversion concurrency control, write-ahead logs, and transaction managers. In real systems, ACID matters for payments, inventory, and financial records where correctness is non-negotiable.

Best practice is to keep transactions as short as possible and choose an isolation level intentionally. The pitfall is assuming stronger isolation is always better; it can increase contention and reduce throughput.

```sql
-- Basic transaction ensuring atomicity
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;
```

Isolation levels in practice:

```sql
-- Set isolation level per transaction
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
BEGIN;
SELECT balance FROM accounts WHERE id = 1;  -- sees only committed data
COMMIT;

-- Isolation levels from weakest to strongest:
-- READ UNCOMMITTED  -> allows dirty reads (rarely used)
-- READ COMMITTED    -> default in PostgreSQL, prevents dirty reads
-- REPEATABLE READ   -> prevents non-repeatable reads
-- SERIALIZABLE      -> strongest, prevents phantom reads
```

ACID in Python with SQLAlchemy:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

engine = create_engine("postgresql://localhost/bank")

def transfer(from_id, to_id, amount):
    with Session(engine) as session:
        try:
            sender = session.get(Account, from_id)
            receiver = session.get(Account, to_id)

            if sender.balance < amount:
                raise ValueError("Insufficient funds")

            sender.balance -= amount
            receiver.balance += amount
            session.commit()   # Atomic: both updates or neither
        except Exception:
            session.rollback()  # Undo on any failure
            raise
```

Key takeaway: understand each ACID property independently, and know which isolation level your database uses by default and what anomalies each level prevents.

### Question: What is a dirty read?

Answer:

A dirty read happens when one transaction reads data written by another transaction that has not yet committed. If the writer later rolls back, the reader has observed data that should never have existed from the business point of view.

Dirty reads are a direct isolation problem. They matter in financial and operational systems because they can produce incorrect downstream decisions. In interviews, this is a good place to mention isolation levels and the tradeoff between correctness and concurrency.

```sql
-- Session A
BEGIN;
UPDATE orders SET status = 'paid' WHERE id = 10;

-- Session B reads 'paid' before Session A commits.
-- If Session A rolls back, Session B observed a dirty read.
```

### Question: What is indexing in databases?

Answer:

An index is a data structure that helps the database find rows faster without scanning the entire table. Most relational databases use B-tree indexes by default, though hash, bitmap, and specialized indexes also exist depending on the engine.

Indexes are most valuable on large tables, foreign keys, unique constraints, frequently filtered columns, and join keys. Best practice is to add indexes based on real query patterns rather than intuition.

```sql
-- Basic single-column index
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
```

Composite index (multi-column — order matters):

```sql
-- Useful for queries that filter on both columns
CREATE INDEX idx_orders_status_date ON orders(status, created_at);

-- This index helps:
SELECT * FROM orders WHERE status = 'paid' AND created_at > '2024-01-01';

-- This index does NOT help (skips the first column):
SELECT * FROM orders WHERE created_at > '2024-01-01';
-- Rule: composite index follows leftmost prefix rule
```

Covering index (includes extra columns to avoid table lookup):

```sql
-- Index covers the query completely — no need to read the table
CREATE INDEX idx_orders_covering ON orders(customer_id) INCLUDE (status, total);

-- This query is served entirely from the index:
SELECT status, total FROM orders WHERE customer_id = 42;
```

Partial index (index only a subset of rows):

```sql
-- Index only active users — smaller, faster
CREATE INDEX idx_active_users ON users(email) WHERE status = 'active';
```

Unique index for data integrity:

```sql
CREATE UNIQUE INDEX idx_users_email ON users(email);
-- Prevents duplicate emails at the database level
```

Key takeaway: indexing is not just `CREATE INDEX`. Know composite indexes (column order matters), covering indexes (avoid table lookups), partial indexes (filter indexed rows), and unique indexes (enforce constraints).

### Question: How does indexing work internally?

Answer:

Internally, the index stores indexed values in a structure optimized for lookup, range scans, and sometimes ordering. The optimizer decides whether using the index is cheaper than scanning the entire table.

In practice, an index is a performance tradeoff: it speeds reads that match the index but adds maintenance work on writes. That is why execution plans matter more than just knowing index syntax.

```sql
EXPLAIN SELECT *
FROM orders
WHERE customer_id = 42;
```

### Question: What are the disadvantages of indexing?

Answer:

Indexes improve reads, but they are not free. They consume storage, slow down inserts and updates, and increase maintenance overhead because the database must keep the index in sync with the underlying table.

Too many indexes can also confuse the optimizer or add complexity without real benefit. Another common pitfall is indexing low-selectivity columns that do not meaningfully narrow the result set.

```sql
-- Every INSERT now updates the table plus all related indexes.
INSERT INTO orders (id, customer_id, status) VALUES (101, 42, 'created');
```

### Question: What is the difference between GROUP BY, HAVING, and ORDER BY?

Answer:

`GROUP BY` groups rows so aggregate functions like `COUNT`, `SUM`, `AVG`, `MIN`, and `MAX` can operate on each group. `HAVING` filters groups after aggregation. `ORDER BY` sorts the final result set.

This is a common interview topic because it shows whether someone understands logical query flow rather than just syntax. The practical rule is: `WHERE` filters rows before grouping, `HAVING` filters after grouping, and `ORDER BY` only affects presentation order.

```sql
SELECT customer_id, COUNT(*) AS total_orders
FROM orders
WHERE status = 'paid'
GROUP BY customer_id
HAVING COUNT(*) > 5
ORDER BY total_orders DESC;
```

### Question: When should you use CTEs?

Answer:

Use a Common Table Expression when a query becomes easier to read as named steps, especially for layered filtering, ranking, recursion, or complex reporting logic.

CTEs are valuable when you want to explain the query clearly to another engineer. The main pitfall is assuming they are always a performance optimization; in many databases they are primarily a readability tool, and execution behavior depends on the engine.

```sql
WITH recent_orders AS (
    SELECT *
    FROM orders
    WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
)
SELECT COUNT(*)
FROM recent_orders;
```

### Question: When should you use JOINs?

Answer:

Use a JOIN when the data you need lives in multiple related tables. This is fundamental to normalized relational design.

In practice, joins power reporting, entity lookups, authorization checks, and dashboard queries. Best practice is to join on indexed keys and verify execution plans on important queries. A common pitfall is joining large tables carelessly and discovering performance problems only in production.

```sql
SELECT o.id, c.name
FROM orders o
JOIN customers c ON c.id = o.customer_id;
```

### Question: When should you use aggregate functions?

Answer:

Aggregate functions are used when you need summaries instead of raw rows, such as counts, totals, averages, minimums, or maximums.

They are central to analytics, dashboards, billing summaries, fraud detection, and operational reporting. In interviews, I usually mention that aggregate queries are often combined with `GROUP BY` and sometimes with `HAVING` for post-aggregation filtering.

```sql
SELECT AVG(amount) AS average_order_value
FROM orders;
```

This is a typical interview example:

```sql
WITH customer_totals AS (
    SELECT customer_id, SUM(amount) AS total_amount
    FROM orders
    GROUP BY customer_id
)
SELECT customer_id, total_amount
FROM customer_totals
WHERE total_amount > 1000
ORDER BY total_amount DESC;
```

### Question: What are database keys?

Answer:

Keys define identity and relationships in relational databases. A primary key uniquely identifies a row. A foreign key links rows across tables. A unique key enforces uniqueness for non-primary attributes.

They matter because they encode correctness directly in the schema. Best practice is to design keys deliberately and support them with appropriate indexes where needed.

```sql
CREATE TABLE orders (
    id BIGINT PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    order_number TEXT UNIQUE,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);
```

### Question: What are database views?

Answer:

A view is a saved query that presents data as a virtual table. It is useful when you want to simplify repeated access patterns, hide complexity, or expose a stable interface over underlying tables.

Views are especially useful for reporting, data access control, and compatibility layers during schema evolution. The pitfall is treating a view as if it were free; complex views can still be expensive depending on the query engine.

```sql
CREATE VIEW active_customers AS
SELECT id, name
FROM customers
WHERE status = 'active';
```

### Question: What is an ORM?

Answer:

An ORM, or Object-Relational Mapper, maps relational data into objects and translates object operations into SQL. It reduces repetitive CRUD boilerplate and makes application code more domain-oriented.

The tradeoff is abstraction versus visibility. ORMs improve productivity, but engineers still need to understand the SQL being generated or performance issues will be hard to diagnose.

```python
# Basic model definition
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
```

ORM with relationships (one-to-many):

```python
from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)

    # One user has many orders
    orders = relationship("Order", back_populates="user", lazy="selectin")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    amount = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Many orders belong to one user
    user = relationship("User", back_populates="orders")
```

N+1 query problem and how to fix it:

```python
# BAD: N+1 queries — 1 query for users + N queries for their orders
users = session.query(User).all()
for user in users:
    print(user.orders)  # Each access fires a separate SELECT!

# GOOD: Eager loading with joinedload — 1 query total
from sqlalchemy.orm import joinedload

users = session.query(User).options(joinedload(User.orders)).all()
for user in users:
    print(user.orders)  # Already loaded, no extra queries

# GOOD: selectin loading — 2 queries total (1 for users, 1 for orders)
from sqlalchemy.orm import selectinload

users = session.query(User).options(selectinload(User.orders)).all()
```

Key takeaway: knowing ORM basics is not enough. Understand relationships, lazy vs eager loading, and the N+1 problem. Check generated SQL with `echo=True` on the engine.

### Question: What is SQLAlchemy?

Answer:

SQLAlchemy is the most widely used Python database toolkit and ORM. It supports both ORM-style interaction and a lower-level SQL expression API.

That makes it useful across a wide range of applications, from small CRUD services to more complex systems that mix ORM logic with explicit SQL. Best practice is to choose the right level of abstraction for the query rather than forcing everything through the ORM layer.

```python
# Basic query
from sqlalchemy import select
result = session.execute(select(User).where(User.name == "Asha"))
user = result.scalar_one()
```

SQLAlchemy query patterns every backend developer should know:

```python
from sqlalchemy import select, func, and_, or_, desc

# Filtering with multiple conditions
stmt = select(User).where(
    and_(
        User.role == "admin",
        User.is_active == True,
    )
)

# Aggregation
stmt = select(func.count(Order.id), func.sum(Order.amount)).where(
    Order.user_id == 42
)
count, total = session.execute(stmt).one()

# Pagination
page, page_size = 2, 20
stmt = (
    select(User)
    .order_by(desc(User.created_at))
    .offset((page - 1) * page_size)
    .limit(page_size)
)
users = session.execute(stmt).scalars().all()

# Subquery
active_user_ids = select(User.id).where(User.is_active == True).subquery()
stmt = select(Order).where(Order.user_id.in_(active_user_ids))
```

Session lifecycle and transaction management:

```python
from sqlalchemy.orm import Session

# Pattern 1: Context manager (recommended)
with Session(engine) as session:
    user = session.get(User, 42)
    user.name = "Updated"
    session.commit()
# Session automatically closed after the block

# Pattern 2: FastAPI dependency injection
from fastapi import Depends

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    return db.get(User, user_id)
```

### Question: When should you use an ORM?

Answer:

Use an ORM when it improves developer velocity, keeps common persistence code readable, and aligns well with the application's domain model.

For performance-critical reports, advanced analytics, or complex joins, raw SQL is often the better tool. The pitfall is treating the ORM as magic and ignoring N+1 queries, poor eager-loading strategy, or inefficient generated SQL.

```python
# Basic session.get()
def get_user(session, user_id):
    return session.get(User, user_id)
```

When to use ORM vs raw SQL — decision matrix:

```python
# USE ORM for:
# - CRUD operations (simple, readable, type-safe)
def create_user(session, name, email):
    user = User(name=name, email=email)
    session.add(user)
    session.commit()
    return user

def update_user(session, user_id, **updates):
    user = session.get(User, user_id)
    for key, value in updates.items():
        setattr(user, key, value)
    session.commit()
    return user


# USE RAW SQL for:
# - Complex reports, analytics, bulk operations
from sqlalchemy import text

def monthly_revenue(session):
    result = session.execute(text("""
        SELECT DATE_TRUNC('month', created_at) AS month,
               SUM(amount) AS revenue,
               COUNT(*) AS order_count
        FROM orders
        WHERE status = 'paid'
        GROUP BY 1
        ORDER BY 1 DESC
        LIMIT 12
    """))
    return result.fetchall()


# Bulk update (ORM would load each row individually)
def deactivate_old_users(session):
    session.execute(text("""
        UPDATE users SET is_active = false
        WHERE last_login < NOW() - INTERVAL '1 year'
    """))
    session.commit()
```

Key takeaway: ORMs are tools, not religions. Use them for domain logic and CRUD. Drop to SQL for performance-critical queries, analytics, and bulk operations.

### Question: What is the difference between relational and non-relational databases?

Answer:

Relational databases store structured data in tables with schemas, relationships, and SQL-based querying. Non-relational databases, or NoSQL databases, trade some relational guarantees for flexibility, horizontal scale, or specialized access patterns.

Relational databases are strong when data integrity, joins, and transactions are central. NoSQL databases are strong when workloads need very high scale, flexible schemas, or key-value or document access patterns.

Best practice is to choose based on access pattern, consistency needs, and operational constraints. Many real systems are hybrid and use both models for different parts of the problem.

```sql
-- Relational row
SELECT id, email FROM users WHERE id = 101;
```

```json
// Document-style record
{
    "id": 101,
    "email": "asha@example.com",
    "preferences": {"theme": "dark"}
}
```

### Question: What are BASE properties?

Answer:

BASE stands for Basically Available, Soft state, and Eventual consistency. It describes a design approach often used in distributed NoSQL systems where availability and partition tolerance are prioritized over immediate consistency.

This does not mean the system is incorrect; it means the system accepts that replicas may converge over time rather than staying strongly consistent at every instant. That tradeoff can be entirely appropriate for user sessions, feeds, or catalog data, but not for every workload.

```text
write -> primary node accepts request
read  -> replica may briefly return old value
later -> replicas converge to the latest state
```

### Question: What is DynamoDB?

Answer:

DynamoDB is AWS's fully managed NoSQL database service. It is designed for low-latency key-value and document workloads at large scale.

Internally, data access is driven by partition keys and optional sort keys. Secondary indexes provide additional query paths, but table design still starts from access patterns rather than from relational normalization.

```python
table.put_item(Item={"pk": "USER#101", "sk": "PROFILE", "name": "Asha"})
```

### Question: When is DynamoDB a good choice?

Answer:

DynamoDB is a strong choice for session stores, user profiles, event metadata, shopping carts, and other workloads that need predictable low latency with minimal operational overhead.

Best practice is to design the table around the access pattern first. The common pitfall is trying to use DynamoDB like a generic relational database and discovering too late that the query model does not fit.

```python
table.get_item(Key={"pk": "USER#101", "sk": "PROFILE"})
```

## System Design / Principles

### Question: What is the Single Responsibility Principle?

Answer:

The Single Responsibility Principle says a module or class should have one clear reason to change. It should own one cohesive responsibility rather than mixing unrelated concerns.

In practice, this improves readability, testing, and change safety. A common pitfall is turning SRP into excessive fragmentation; the goal is cohesion, not tiny classes for their own sake.

```python
# BAD: One class doing too many things
class OrderProcessor:
    def validate(self, order):
        ...
    def save_to_db(self, order):
        ...
    def send_email(self, order):
        ...
    def generate_invoice_pdf(self, order):
        ...

# GOOD: Each class has one responsibility
class OrderValidator:
    def validate(self, order):
        if order["amount"] <= 0:
            raise ValueError("Invalid amount")

class OrderRepository:
    def save(self, order):
        print(f"Saved order {order['id']}")

class InvoiceGenerator:
    def generate(self, order):
        return f"Invoice for order {order['id']}"

class OrderNotifier:
    def notify(self, order):
        print(f"Email sent for order {order['id']}")


# Orchestrator composes them
class OrderService:
    def __init__(self, validator, repo, invoicer, notifier):
        self.validator = validator
        self.repo = repo
        self.invoicer = invoicer
        self.notifier = notifier

    def process(self, order):
        self.validator.validate(order)
        self.repo.save(order)
        self.invoicer.generate(order)
        self.notifier.notify(order)
```

Key takeaway: SRP doesn't mean "one method per class". It means each class has one cohesive reason to change. The validator changes when rules change, the notifier changes when email logic changes, etc.

### Question: What is the Open/Closed Principle?

Answer:

The Open/Closed Principle says software entities should be open for extension but closed for modification. In other words, stable code should gain new behavior without constant rewrites.

This usually leads to better extensibility through interfaces, composition, and strategy objects. The pitfall is overengineering abstractions before there is a real extension point.

```python
# Strategy pattern — swap algorithms without changing the caller
from abc import ABC, abstractmethod

class DiscountStrategy(ABC):
    @abstractmethod
    def apply(self, amount: float) -> float:
        pass

class NoDiscount(DiscountStrategy):
    def apply(self, amount):
        return amount

class FestivalDiscount(DiscountStrategy):
    def apply(self, amount):
        return amount * 0.9

class LoyaltyDiscount(DiscountStrategy):
    def __init__(self, years):
        self.years = years

    def apply(self, amount):
        discount = min(self.years * 0.02, 0.15)  # max 15% off
        return amount * (1 - discount)


# Caller doesn't know which strategy it's using
class Checkout:
    def __init__(self, discount: DiscountStrategy):
        self.discount = discount

    def total(self, amount):
        return self.discount.apply(amount)


# Swap strategies at runtime
print(Checkout(NoDiscount()).total(100))          # 100.0
print(Checkout(FestivalDiscount()).total(100))     # 90.0
print(Checkout(LoyaltyDiscount(5)).total(100))     # 90.0
```

Key takeaway: Open/Closed means adding new behavior (like a new discount type) only requires creating a new class — no modification to existing code.

### Question: What is the Liskov Substitution Principle?

Answer:

Liskov Substitution means a subtype should be usable anywhere its base type is expected without breaking correctness. Child classes must preserve the contract of the parent abstraction.

This is why inheritance must be behaviorally valid, not just structurally convenient. The pitfall is subclassing for reuse while subtly changing assumptions such as allowed inputs, side effects, or error behavior.

```python
class Bird:
    def move(self):
        return "moving"

class Sparrow(Bird):
    pass
```

### Question: What is the Interface Segregation Principle?

Answer:

Interface Segregation says clients should not depend on methods they do not need. Smaller, focused interfaces are easier to implement, test, and evolve.

In backend systems, this often shows up as focused repository or service interfaces instead of giant all-purpose abstractions. The pitfall is defining broad interfaces that force callers and implementers to know too much.

```python
class Reader:
    def read(self):
        raise NotImplementedError

class Writer:
    def write(self, value):
        raise NotImplementedError
```

### Question: What is the Dependency Inversion Principle?

Answer:

Dependency Inversion says higher-level modules should depend on abstractions, not concrete low-level implementations. This reduces coupling and improves testability.

In practice, business logic should depend on contracts such as repositories or gateways, while infrastructure details implement those contracts. The pitfall is adding abstractions without a clear boundary or benefit.

```python
class UserRepository:
    def get(self, user_id):
        raise NotImplementedError

class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository
```

### Question: What does DRY mean in software design?

Answer:

DRY means Do Not Repeat Yourself. The goal is to avoid duplicated knowledge so behavior has a single source of truth.

This reduces inconsistency and makes change safer, but DRY should be applied with judgment. A common pitfall is forcing unrelated cases into one abstraction too early and creating a harder design.

```python
def normalize_email(value):
    return value.strip().lower()
```

### Question: What does KISS mean in software design?

Answer:

KISS means Keep It Simple, Stupid. It is a reminder to prefer the simplest solution that solves the problem well.

Simple does not mean naive; it means easier to understand, debug, and operate. A common pitfall is choosing an elaborate design for problems that do not need it.

```python
def is_even(number):
    return number % 2 == 0
```

### Question: What does YAGNI mean in software design?

Answer:

YAGNI means You Aren't Gonna Need It. It warns against building speculative features before there is a real requirement.

This principle is valuable because premature flexibility creates real complexity today for hypothetical benefit later. The common pitfall is confusing foresight with premature abstraction.

```python
# Good now
def export_csv(rows):
    ...

# Do not add export_pdf/export_xml until the requirement exists.
```

### Question: What are design patterns?

Answer:

Design patterns are reusable solutions to recurring design problems. They are not copy-paste templates; they are vocabulary for discussing structure and tradeoffs.

They matter because they let teams talk about common design shapes precisely. Best practice is to use a pattern only when it genuinely simplifies the code. The pitfall is writing pattern-first code instead of solving the actual problem.

```python
class NotificationFactory:
    _registry = {}

    @classmethod
    def register(cls, kind, notifier_cls):
        cls._registry[kind] = notifier_cls

    @classmethod
    def create(cls, kind):
        notifier_cls = cls._registry.get(kind)
        if not notifier_cls:
            raise ValueError(f"Unknown notification type: {kind}")
        return notifier_cls()


class EmailNotifier:
    def send(self, msg):
        print(f"Email: {msg}")

class SmsNotifier:
    def send(self, msg):
        print(f"SMS: {msg}")


# Register implementations
NotificationFactory.register("email", EmailNotifier)
NotificationFactory.register("sms", SmsNotifier)

# Create without knowing the concrete class
notifier = NotificationFactory.create("email")
notifier.send("Hello!")  # Email: Hello!
```

Key takeaway: patterns are tools for managing complexity, not goals to pursue. Apply them when the codebase actually needs the structure they provide.

### Question: Which design patterns are most useful in backend systems?

Answer:

The most common useful patterns are Factory for controlled object creation, Strategy for interchangeable behavior, Repository for persistence boundaries, and Adapter for integrating external systems behind internal contracts.

These patterns help manage complexity without locking the code into a rigid framework. The common pitfall is introducing them before the code actually needs the indirection.

```python
# Repository pattern: clean data access boundary
from abc import ABC, abstractmethod
from typing import Optional

class UserRepository(ABC):
    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[dict]:
        pass

    @abstractmethod
    def save(self, user: dict) -> dict:
        pass

    @abstractmethod
    def delete(self, user_id: int) -> None:
        pass


class PostgresUserRepository(UserRepository):
    def __init__(self, session):
        self.session = session

    def find_by_id(self, user_id):
        return self.session.get(User, user_id)

    def save(self, user):
        self.session.add(user)
        self.session.commit()
        return user

    def delete(self, user_id):
        user = self.find_by_id(user_id)
        if user:
            self.session.delete(user)
            self.session.commit()


class InMemoryUserRepository(UserRepository):
    """For tests — no database needed."""
    def __init__(self):
        self._store = {}

    def find_by_id(self, user_id):
        return self._store.get(user_id)

    def save(self, user):
        self._store[user["id"]] = user
        return user

    def delete(self, user_id):
        self._store.pop(user_id, None)


# Strategy pattern: interchangeable algorithms
class CompressionStrategy:
    def compress(self, data: bytes) -> bytes:
        raise NotImplementedError

class GzipCompression(CompressionStrategy):
    def compress(self, data):
        import gzip
        return gzip.compress(data)

class NoCompression(CompressionStrategy):
    def compress(self, data):
        return data
```

### Question: How do WebSockets work?

Answer:

WebSockets provide a persistent, full-duplex connection between client and server. Unlike standard HTTP request-response interactions, either side can send messages after the connection is established.

The connection starts as an HTTP handshake with an `Upgrade` request. If both sides agree, the protocol switches to WebSocket and stays open. After that, messages are exchanged in frames over the same TCP connection.

WebSockets are useful for chat applications, live notifications, collaborative editing, dashboards, and streaming updates. Best practice is to plan for connection lifecycle management, heartbeats, authentication, and horizontal scaling.

```python
from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("connected")
```

Connection manager for real-world WebSocket (chat/notifications):

```python
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set

class ConnectionManager:
    """Manages active WebSocket connections with room support."""

    def __init__(self):
        self._connections: Dict[str, Set[WebSocket]] = {}  # room -> connections

    async def connect(self, websocket: WebSocket, room: str):
        await websocket.accept()
        self._connections.setdefault(room, set()).add(websocket)

    def disconnect(self, websocket: WebSocket, room: str):
        self._connections.get(room, set()).discard(websocket)

    async def broadcast(self, room: str, message: str):
        for connection in self._connections.get(room, set()):
            await connection.send_text(message)


manager = ConnectionManager()

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await manager.connect(websocket, room_id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(room_id, f"Message: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
        await manager.broadcast(room_id, "A user left the chat")
```

Key takeaway: production WebSockets need lifecycle management, room/group support, heartbeats, and authentication during the handshake.

### Question: How are WebSockets different from normal HTTP requests?

Answer:

Normal HTTP is request-response: the client asks, the server responds, and the interaction usually ends. WebSockets are persistent and full-duplex, so either side can send messages at any time after the connection is established.

That makes WebSockets better for real-time communication, but they also add operational complexity around state, scaling, and connection management. A common pitfall is using WebSockets when polling or server-sent events would be simpler.

```http
GET /users/101 HTTP/1.1
Host: api.example.com

GET /ws HTTP/1.1
Upgrade: websocket
Connection: Upgrade
```

### Question: What is the TCP three-way handshake?

Answer:

The TCP three-way handshake establishes a reliable connection between a client and a server. First, the client sends `SYN`. Second, the server replies with `SYN-ACK`. Third, the client responds with `ACK`.

This process synchronizes sequence numbers and confirms that both sides are ready to send and receive data. It is the foundation for reliable ordered delivery in TCP.

In interviews, I usually connect this to higher-level protocols. HTTP, WebSocket traffic, and database connections often run on top of TCP, so understanding the handshake helps explain latency, connection setup cost, and why connection reuse matters.

```text
Client -> SYN -> Server
Client <- SYN-ACK <- Server
Client -> ACK -> Server
```

## Data Structures & Algorithms

### Question: Which Python data structure gives O(1) time for popping the first element?

Answer:

The right answer is `collections.deque`, not `list`. A list is efficient for appending and popping from the end, but removing from the front is $O(n)$ because all remaining elements shift left.

A deque is implemented as a double-ended queue optimized for insertion and removal at both ends. That makes `popleft()` effectively $O(1)$.

This matters in queue workloads such as breadth-first search, job buffering, and sliding window algorithms. Best practice is to pick the structure that matches the access pattern instead of defaulting to list.

```python
from collections import deque

queue = deque([1, 2, 3])
first = queue.popleft()
```

### Question: How does a heap work?

Answer:

A heap is a specialized tree-based structure commonly implemented as an array. In a min-heap, the smallest element is always at the root, which is index `0` in Python's `heapq`.

Internally, the heap property guarantees that each parent is less than or equal to its children in a min-heap. This partial ordering is what makes heaps efficient for repeated access to the smallest item.

Heaps are useful for priority queues, schedulers, top-k queries, and graph algorithms. Best practice is to use a heap when you need priority access, not when you need the entire dataset globally sorted.

```python
import heapq

heap = [3, 1, 5]
heapq.heapify(heap)
print(heap[0])  # 1 — smallest element
```

Top-K pattern (one of the most common heap interview problems):

```python
import heapq

def top_k_largest(nums, k):
    """Find k largest elements using a min-heap of size k."""
    # Keep a min-heap of size k
    # The root is always the smallest of the k largest
    return heapq.nlargest(k, nums)

def top_k_frequent(words, k):
    """Find k most frequent words."""
    from collections import Counter
    counts = Counter(words)
    return heapq.nlargest(k, counts.keys(), key=counts.get)

print(top_k_largest([3, 1, 5, 12, 2, 11], 3))  # [12, 11, 5]
print(top_k_frequent(["apple", "banana", "apple", "cherry", "banana", "apple"], 2))
# ['apple', 'banana']
```

Priority queue with custom ordering:

```python
import heapq

class Task:
    def __init__(self, priority, name):
        self.priority = priority
        self.name = name

    def __lt__(self, other):
        return self.priority < other.priority  # lower number = higher priority

    def __repr__(self):
        return f"Task({self.priority}, {self.name})"

task_queue = []
heapq.heappush(task_queue, Task(3, "low-priority"))
heapq.heappush(task_queue, Task(1, "critical"))
heapq.heappush(task_queue, Task(2, "normal"))

while task_queue:
    task = heapq.heappop(task_queue)
    print(f"Processing: {task}")
# Processing: Task(1, critical)
# Processing: Task(2, normal)
# Processing: Task(3, low-priority)
```

Merge K sorted lists (classic heap problem):

```python
import heapq

def merge_sorted_lists(lists):
    """Merge k sorted lists into one sorted list using a heap."""
    result = []
    # Push (value, list_index, element_index) for each list's first element
    heap = [(lst[0], i, 0) for i, lst in enumerate(lists) if lst]
    heapq.heapify(heap)

    while heap:
        val, list_idx, elem_idx = heapq.heappop(heap)
        result.append(val)
        if elem_idx + 1 < len(lists[list_idx]):
            next_val = lists[list_idx][elem_idx + 1]
            heapq.heappush(heap, (next_val, list_idx, elem_idx + 1))
    return result

print(merge_sorted_lists([[1, 4, 7], [2, 5, 8], [3, 6, 9]]))
# [1, 2, 3, 4, 5, 6, 7, 8, 9]
```

### Question: What does heapify do?

Answer:

`heapify` takes a regular list and rearranges it into a valid heap. In Python's `heapq`, this happens in linear time.

This is more efficient than pushing each item individually when you already have the full collection. It is a common follow-up point in interviews because it tests whether someone knows the difference between building and maintaining a heap.

```python
import heapq

values = [9, 4, 7, 1]
heapq.heapify(values)
```

### Question: How does pop work on a heap?

Answer:

When you pop from a min-heap, the root value is removed first because it is the smallest. Then the last element is moved to the root and the heap is adjusted downward until the heap property is restored.

That gives `heappop` a time complexity of $O(log n)$. The pitfall is assuming a heap is the same as a sorted list. It is only partially ordered.

```python
import heapq

values = [5, 2, 8, 1, 3]
heapq.heapify(values)
smallest = heapq.heappop(values)
```

### Question: How does binary search work?

Answer:

Binary search finds a target in a sorted collection by repeatedly cutting the search space in half. That gives it $O(log n)$ time complexity.

Internally, you compare the target with the middle element. If the target is smaller, search the left half. If larger, search the right half. Continue until the value is found or the search range becomes empty.

The classic pitfall is an off-by-one error in the loop condition or midpoint update.

```python
def binary_search(values, target):
    left, right = 0, len(values) - 1
    while left <= right:
        mid = (left + right) // 2
        if values[mid] == target:
            return mid
        if values[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
```

### Question: When should you use binary search?

Answer:

Use binary search when the data is sorted and random access to the middle element is cheap, such as with arrays or Python lists.

It is especially useful for exact lookup, lower-bound and upper-bound problems, and search-on-answer patterns in algorithm interviews. Best practice is to define the search invariant clearly before writing code.

```python
from bisect import bisect_left

values = [1, 3, 5, 7]
position = bisect_left(values, 5)
```

### Question: What should you know about linked lists for interviews?

Answer:

For linked lists, you should know insertion and deletion behavior, why random access is slow, and common patterns such as reversing a list, detecting a cycle, or using slow and fast pointers.

Interviewers often use linked lists to test pointer manipulation and invariants. Best practice is to explain state changes clearly rather than just reciting code.

```python
class Node:
    def __init__(self, value, next_node=None):
        self.value = value
        self.next = next_node
```

Linked list operations:

```python
class LinkedList:
    def __init__(self):
        self.head = None

    def append(self, value):
        new_node = Node(value)
        if not self.head:
            self.head = new_node
            return
        current = self.head
        while current.next:
            current = current.next
        current.next = new_node

    def prepend(self, value):
        self.head = Node(value, self.head)

    def delete(self, value):
        if not self.head:
            return
        if self.head.value == value:
            self.head = self.head.next
            return
        current = self.head
        while current.next:
            if current.next.value == value:
                current.next = current.next.next
                return
            current = current.next

    def to_list(self):
        result = []
        current = self.head
        while current:
            result.append(current.value)
            current = current.next
        return result


ll = LinkedList()
ll.append(1)
ll.append(2)
ll.append(3)
ll.prepend(0)
print(ll.to_list())  # [0, 1, 2, 3]
ll.delete(2)
print(ll.to_list())  # [0, 1, 3]
```

Cycle detection (Floyd's tortoise and hare):

```python
def has_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            return True
    return False

# Create a cycle for testing
a, b, c = Node(1), Node(2), Node(3)
a.next = b
b.next = c
c.next = b  # cycle: c -> b -> c -> ...
print(has_cycle(a))  # True
```

Find middle of linked list (fast/slow pointer):

```python
def find_middle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow.value
```

### Question: What should you know about stacks for interviews?

Answer:

For stacks, you should know the LIFO model and common use cases such as expression parsing, bracket matching, recursion simulation, and depth-first traversal.

In interviews, the key is recognizing when the most recent unfinished work should be processed first. A stack is often the right mental model for that class of problem.

```python
# Basic stack operations
stack = []
stack.append("(")
stack.pop()
```

Bracket matching (classic stack problem):

```python
def is_valid_brackets(s):
    stack = []
    matching = {")": "(", "]": "[", "}": "{"}

    for char in s:
        if char in "([{":
            stack.append(char)
        elif char in ")]}":
            if not stack or stack[-1] != matching[char]:
                return False
            stack.pop()

    return len(stack) == 0

print(is_valid_brackets("({[]})"))   # True
print(is_valid_brackets("([)]"))     # False
print(is_valid_brackets("{{"))       # False
```

Evaluate postfix expression using a stack:

```python
def eval_postfix(tokens):
    """Evaluate a postfix (RPN) expression."""
    stack = []
    ops = {
        "+": lambda a, b: a + b,
        "-": lambda a, b: a - b,
        "*": lambda a, b: a * b,
        "/": lambda a, b: int(a / b),
    }

    for token in tokens:
        if token in ops:
            b, a = stack.pop(), stack.pop()
            stack.append(ops[token](a, b))
        else:
            stack.append(int(token))

    return stack[0]

print(eval_postfix(["2", "3", "+", "4", "*"]))  # 20 = (2+3)*4
```

DFS using an explicit stack (instead of recursion):

```python
def dfs_iterative(graph, start):
    visited = set()
    stack = [start]
    result = []
    while stack:
        node = stack.pop()
        if node not in visited:
            visited.add(node)
            result.append(node)
            # Add neighbors in reverse for consistent ordering
            for neighbor in reversed(graph[node]):
                if neighbor not in visited:
                    stack.append(neighbor)
    return result
```

### Question: What should you know about queues for interviews?

Answer:

For queues, you should know the FIFO model and how it supports scheduling, buffering, and breadth-first search.

In Python, `collections.deque` is usually the right implementation. A common pitfall is using a list and repeatedly popping from the front.

```python
from collections import deque

# Basic FIFO queue
queue = deque([1, 2])
queue.append(3)
queue.popleft()  # 1
```

BFS level-order traversal (queues are essential for BFS):

```python
from collections import deque

def bfs_shortest_path(graph, start, target):
    """Find shortest path in unweighted graph using BFS."""
    queue = deque([(start, [start])])  # (node, path)
    visited = {start}

    while queue:
        node, path = queue.popleft()
        if node == target:
            return path  # shortest path found

        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))

    return None  # no path exists


graph = {
    "A": ["B", "C"],
    "B": ["A", "D", "E"],
    "C": ["A", "F"],
    "D": ["B"],
    "E": ["B", "F"],
    "F": ["C", "E"],
}
print(bfs_shortest_path(graph, "A", "F"))  # ['A', 'C', 'F']
```

Task scheduler with priority (using heapq as priority queue):

```python
import heapq

task_queue = []
heapq.heappush(task_queue, (2, "send_email"))   # priority 2
heapq.heappush(task_queue, (1, "process_payment"))  # priority 1 (highest)
heapq.heappush(task_queue, (3, "generate_report"))  # priority 3

while task_queue:
    priority, task = heapq.heappop(task_queue)
    print(f"Running: {task} (priority {priority})")
# Runs in priority order: process_payment, send_email, generate_report
```

### Question: What should you know about trees for interviews?

Answer:

For trees, you should understand traversals, recursion, height and balance, binary search tree properties, and when tree structure gives better query performance than a flat scan.

Interview questions often focus on traversal patterns, recursion, path problems, and subtree properties. Best practice is to state the traversal order and base cases clearly.

```python
class TreeNode:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right
```

Tree traversals (the three patterns every interviewer expects you to know):

```python
# Build a sample tree:
#       1
#      / \
#     2   3
#    / \
#   4   5

root = TreeNode(1, TreeNode(2, TreeNode(4), TreeNode(5)), TreeNode(3))


def inorder(node):
    """Left -> Root -> Right (gives sorted order for BST)."""
    if not node:
        return []
    return inorder(node.left) + [node.value] + inorder(node.right)

def preorder(node):
    """Root -> Left -> Right (useful for serialization/copying)."""
    if not node:
        return []
    return [node.value] + preorder(node.left) + preorder(node.right)

def postorder(node):
    """Left -> Right -> Root (useful for deletion/cleanup)."""
    if not node:
        return []
    return postorder(node.left) + postorder(node.right) + [node.value]


print(inorder(root))    # [4, 2, 5, 1, 3]
print(preorder(root))   # [1, 2, 4, 5, 3]
print(postorder(root))  # [4, 5, 2, 3, 1]
```

Level-order traversal (BFS on a tree):

```python
from collections import deque

def level_order(root):
    if not root:
        return []
    result = []
    queue = deque([root])
    while queue:
        level = []
        for _ in range(len(queue)):
            node = queue.popleft()
            level.append(node.value)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        result.append(level)
    return result

print(level_order(root))  # [[1], [2, 3], [4, 5]]
```

Common tree interview problems:

```python
def max_depth(node):
    """Height of the tree."""
    if not node:
        return 0
    return 1 + max(max_depth(node.left), max_depth(node.right))

def is_balanced(node):
    """Check if tree is height-balanced."""
    def check(node):
        if not node:
            return 0
        left = check(node.left)
        right = check(node.right)
        if left == -1 or right == -1 or abs(left - right) > 1:
            return -1
        return 1 + max(left, right)
    return check(node) != -1

print(max_depth(root))    # 3
print(is_balanced(root))  # True
```

### Question: What should you know about graphs for interviews?

Answer:

For graphs, you should understand adjacency list representations, BFS, DFS, cycle detection, topological sort, shortest path basics, and connected components.

Graphs model dependencies, networks, routes, and arbitrary relationships. Interviewers often care more about choosing the right traversal than about memorizing graph vocabulary.

```python
# Adjacency list representation
graph = {
    "A": ["B", "C"],
    "B": ["D"],
    "C": [],
    "D": [],
}
```

BFS (breadth-first search):

```python
from collections import deque

def bfs(graph, start):
    visited = set()
    queue = deque([start])
    visited.add(start)
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return order

print(bfs(graph, "A"))  # ['A', 'B', 'C', 'D']
```

DFS (depth-first search) — recursive and iterative:

```python
def dfs_recursive(graph, node, visited=None):
    if visited is None:
        visited = set()
    visited.add(node)
    print(node)
    for neighbor in graph[node]:
        if neighbor not in visited:
            dfs_recursive(graph, neighbor, visited)

def dfs_iterative(graph, start):
    visited = set()
    stack = [start]
    order = []
    while stack:
        node = stack.pop()
        if node not in visited:
            visited.add(node)
            order.append(node)
            for neighbor in reversed(graph[node]):
                stack.append(neighbor)
    return order
```

Cycle detection in a directed graph:

```python
def has_cycle(graph):
    """Detect cycle using DFS with coloring (white/gray/black)."""
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {node: WHITE for node in graph}

    def dfs(node):
        color[node] = GRAY  # currently visiting
        for neighbor in graph[node]:
            if color[neighbor] == GRAY:  # back edge = cycle
                return True
            if color[neighbor] == WHITE and dfs(neighbor):
                return True
        color[node] = BLACK  # fully processed
        return False

    return any(dfs(node) for node in graph if color[node] == WHITE)


# Test
cyclic_graph = {"A": ["B"], "B": ["C"], "C": ["A"]}  # A->B->C->A
print(has_cycle(cyclic_graph))  # True

acyclic_graph = {"A": ["B"], "B": ["C"], "C": []}
print(has_cycle(acyclic_graph))  # False
```

Topological sort (dependency ordering):

```python
from collections import deque

def topological_sort(graph):
    """Kahn's algorithm using in-degree."""
    in_degree = {node: 0 for node in graph}
    for node in graph:
        for neighbor in graph[node]:
            in_degree[neighbor] += 1

    queue = deque([node for node in in_degree if in_degree[node] == 0])
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(order) != len(graph):
        raise ValueError("Graph has a cycle")
    return order


# Task dependencies
tasks = {
    "install": ["build"],
    "build": ["test"],
    "test": ["deploy"],
    "deploy": [],
}
print(topological_sort(tasks))  # ['install', 'build', 'test', 'deploy']
```

### Question: How do you reverse a linked list?

Answer:

The standard iterative solution uses three pointers: `previous`, `current`, and `next_node`. You walk the list once and reverse each node's pointer as you go. This runs in $O(n)$ time and $O(1)$ extra space.

Internally, the important idea is that you must save the next node before changing the current node's `next` pointer, otherwise you lose the rest of the list.

This question is common because it tests pointer manipulation and careful reasoning about state changes. Best practice is to explain the invariant clearly during the interview.

```python
class Node:
    def __init__(self, value, next_node=None):
        self.value = value
        self.next = next_node

def reverse_list(head):
    previous = None
    current = head
    while current:
        next_node = current.next
        current.next = previous
        previous = current
        current = next_node
    return previous

```

## FastAPI / Backend Development

### Question: What is a router in FastAPI?

Answer:

A router in FastAPI is a way to group related endpoints and mount them into the main application. It helps organize code by feature, such as users, orders, or authentication.

Routers matter because they keep larger services modular. Best practice is to keep handlers in routers thin and push business logic into services or domain modules.

```python
from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])
```

Full router with CRUD endpoints and dependency injection:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/users", tags=["users"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def list_users(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return db.query(User).offset(skip).limit(limit).all()


@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", status_code=201)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    user = User(**payload.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
```

Mounting router in the main app:

```python
from fastapi import FastAPI

app = FastAPI(title="User Service")
app.include_router(router)
app.include_router(order_router)  # add more routers as the app grows
```

### Question: How do you declare routes in FastAPI?

Answer:

Routes are declared with decorators such as `@app.get()` or `@router.post()`. The decorator defines the path and method, and the function body implements the handler.

FastAPI builds on Starlette's ASGI model, so route definitions are lightweight and explicit. Best practice is to use routers with prefixes and tags to keep related endpoints grouped.

```python
@router.get("/{user_id}")
def get_user(user_id: int):
    return {"id": user_id}
```

### Question: How do request models work in FastAPI?

Answer:

FastAPI uses Pydantic models for request validation and serialization. You define a model with typed fields, and FastAPI validates incoming request data against that model automatically.

This is valuable because validation rules live close to the API contract and can be reused across handlers. A common pitfall is putting business rules inside the model when they really belong in the service layer.

```python
from pydantic import BaseModel, EmailStr, Field, field_validator

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(..., ge=18, le=120)

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("Name cannot be blank")
        return v.strip()
```

Response model (control what gets returned to the client):

```python
from pydantic import BaseModel
from datetime import datetime

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}  # allows ORM objects


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user  # FastAPI filters fields to match UserResponse
```

Nested models and optional fields:

```python
from pydantic import BaseModel
from typing import Optional

class Address(BaseModel):
    street: str
    city: str
    zip_code: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[Address] = None


@router.patch("/{user_id}")
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    update_data = payload.model_dump(exclude_unset=True)  # only fields that were sent
    for key, value in update_data.items():
        setattr(user, key, value)
    db.commit()
    return user
```

Key takeaway: Pydantic models are your API contract. Use them for request validation, response filtering, and documentation — never trust raw client input.

### Question: How does FastAPI generate Swagger and OpenAPI documentation?

Answer:

FastAPI inspects route definitions, type hints, and Pydantic models to generate an OpenAPI schema automatically. Swagger UI is then rendered from that schema.

That means your interactive docs stay synchronized with the actual code as long as the route signatures and models are maintained correctly.

```python
from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI(
    title="User Service",
    description="API for managing users",
    version="1.0.0",
)
router = APIRouter(prefix="/users", tags=["users"])


class UserCreate(BaseModel):
    name: str
    email: str

    model_config = {
        "json_schema_extra": {
            "examples": [{"name": "Asha", "email": "asha@example.com"}]
        }
    }

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

class ErrorResponse(BaseModel):
    detail: str


@router.post(
    "/",
    response_model=UserResponse,
    status_code=201,
    summary="Create a new user",
    responses={
        201: {"description": "User created successfully"},
        422: {"model": ErrorResponse, "description": "Validation error"},
    },
)
def create_user(payload: UserCreate):
    """Create a user with the given name and email.

    - **name**: User's display name
    - **email**: Must be a valid email address
    """
    return {"id": 1, "name": payload.name, "email": payload.email}


@router.get("/", response_model=List[UserResponse], summary="List all users")
def list_users(skip: int = 0, limit: int = 20):
    """Retrieve users with pagination."""
    return []


app.include_router(router)
# Swagger UI at /docs, ReDoc at /redoc, OpenAPI JSON at /openapi.json
```

Key takeaway: FastAPI's auto-docs are only as good as your models and annotations. Use `response_model`, `summary`, docstrings, and `json_schema_extra` to make the docs actually useful.

### Question: What is the difference between Django and FastAPI?

Answer:

Django is a batteries-included web framework with ORM, admin panel, auth system, templating, and strong conventions. FastAPI is a modern, lightweight API framework focused on performance, type hints, async support, and developer experience for APIs.

Internally, Django is historically centered around the WSGI model, though modern versions support async in selected areas. FastAPI is designed around ASGI and is a more natural fit for async APIs and service-oriented backends.

```python
# Django
urlpatterns = [path("users/", views.users)]

# FastAPI
@app.get("/users")
def users():
    return []
```

### Question: When would you choose Django over FastAPI, or FastAPI over Django?

Answer:

I would choose Django when I want a full-stack framework with mature built-ins such as admin, auth, and ORM. I would choose FastAPI for API-first services, microservices, high-concurrency I/O workloads, and teams that want automatic request validation and API documentation.

Best practice is to choose based on product shape and team needs, not on benchmark screenshots. The pitfall is forcing FastAPI into a use case where Django's built-in ecosystem would reduce delivery time, or using Django when the service is really just a thin high-throughput API.

```bash
# Django
python manage.py runserver

# FastAPI
uvicorn main:app --reload
```

## REST APIs / Authentication

### Question: Should REST endpoint names use verbs or nouns?

Answer:

REST endpoint names should generally use nouns, because the resource is represented by the URL and the action is represented by the HTTP method. For example, `/users` with `GET` means fetch users, and `/users` with `POST` means create a user.

Best practice is to model resources clearly and let HTTP methods express the action. A common pitfall is creating action-heavy paths such as `/createUser` or `/deleteOrder` for APIs that are supposed to be resource-oriented.

```http
GET /users
POST /users
GET /users/101
DELETE /users/101
```

### Question: What does REST architecture mean in practice?

Answer:

REST emphasizes stateless communication, resource-oriented design, standard HTTP semantics, representations of resources, and a uniform interface.

In practice, that means predictable URLs, correct status codes, sensible use of idempotent methods, and clear boundaries between resources. The pitfall is calling any HTTP API "REST" even when it ignores those design principles.

```http
GET /orders/101 HTTP/1.1

HTTP/1.1 200 OK
Content-Type: application/json
```

### Question: What is GET in REST APIs?

Answer:

`GET` is used to retrieve data and should not modify server state. It is typically safe and cacheable.

That makes it the right choice for reads, searches, and fetch operations. A common pitfall is putting side effects behind a `GET` route and breaking client assumptions.

```bash
curl -X GET https://api.example.com/users/101
```

### Question: What is POST in REST APIs?

Answer:

`POST` is usually used to create a subordinate resource or trigger non-idempotent processing. Repeating the same `POST` may produce different outcomes unless the API explicitly adds idempotency controls.

It is common for create operations, workflow triggers, and actions that do not fit cleanly into replacement semantics.

```bash
curl -X POST https://api.example.com/users \
    -H "Content-Type: application/json" \
    -d '{"name": "Asha"}'
```

### Question: What is PUT in REST APIs?

Answer:

`PUT` is generally used to replace a resource representation and is expected to be idempotent. Sending the same `PUT` request multiple times should result in the same final state.

It is a good fit when the client knows the full desired representation of the resource.

```bash
curl -X PUT https://api.example.com/users/101 \
    -H "Content-Type: application/json" \
    -d '{"name": "Asha", "email": "asha@example.com"}'
```

### Question: What is PATCH in REST APIs?

Answer:

`PATCH` is used for partial updates. Instead of replacing the whole resource, it changes only the fields described by the request.

This is useful when sending the full representation would be unnecessary or expensive. The pitfall is using `PATCH` without defining clear partial update semantics.

```bash
curl -X PATCH https://api.example.com/users/101 \
    -H "Content-Type: application/json" \
    -d '{"name": "Asha Bohra"}'
```

### Question: What is DELETE in REST APIs?

Answer:

`DELETE` removes a resource and is usually treated as idempotent. Calling it multiple times should not keep changing the state beyond the resource being gone.

In practice, the implementation may do a hard delete or a soft delete. The important part is that the API contract is clear.

```bash
curl -X DELETE https://api.example.com/users/101
```

### Question: What is JWT?

Answer:

JWT stands for JSON Web Token. It is a compact token format used to carry claims such as subject, issuer, audience, expiry, and permissions.

Internally, a JWT has three parts: header, payload, and signature. The signature protects integrity, not confidentiality. That means the token can be decoded, so sensitive information should not be placed in the payload.

JWTs are useful when you want portable, signed identity claims across services. Best practice is to keep them short-lived and minimally privileged.

```python
import jwt

# Encoding a JWT
token = jwt.encode({"sub": "101", "role": "admin"}, "secret", algorithm="HS256")
```

Decoding and full validation:

```python
import jwt
from datetime import datetime, timedelta, timezone

SECRET_KEY = "your-secret-key"  # In production, use env variable
ALGORITHM = "HS256"


def create_access_token(user_id: int, role: str, expires_minutes: int = 30):
    payload = {
        "sub": str(user_id),
        "role": role,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=expires_minutes),
        "iss": "myapp",
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            issuer="myapp",
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError as e:
        raise ValueError(f"Invalid token: {e}")


# Usage
token = create_access_token(user_id=42, role="admin")
print(decode_access_token(token))
# {'sub': '42', 'role': 'admin', 'iat': ..., 'exp': ..., 'iss': 'myapp'}
```

FastAPI dependency for JWT authentication:

```python
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    try:
        payload = decode_access_token(credentials.credentials)
        return {"user_id": int(payload["sub"]), "role": payload["role"]}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/me")
def get_profile(user=Depends(get_current_user)):
    return {"user_id": user["user_id"], "role": user["role"]}


# Role-based access control
def require_admin(user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

@router.delete("/{user_id}")
def delete_user(user_id: int, admin=Depends(require_admin)):
    ...
```

Key takeaway: JWT is not just `encode/decode`. Production usage requires proper expiry, issuer validation, role-based guards, and secure key management.

### Question: What are alternatives to JWT?

Answer:

Alternatives include opaque session tokens stored server-side, signed cookies, API keys for simpler integrations, OAuth access tokens from an identity provider, and mTLS for service-to-service trust.

The right choice depends on whether you need stateless claims, revocation control, browser sessions, delegated authorization, or mutual service trust. A common pitfall is using JWT by default when a simpler session model would be safer.

```http
Cookie: session_id=abc123
X-API-Key: my-api-key
Authorization: Bearer <opaque-access-token>
```

### Question: How do you validate a JWT in the backend?

Answer:

Validation has multiple steps. First, parse the token safely. Second, verify the signature using the correct secret or public key. Third, validate registered claims such as `exp`, `nbf`, `iss`, and `aud`. Fourth, map the subject and permissions into your authorization model.

Internally, the server uses the algorithm in the header together with the configured key material to confirm the token was issued by a trusted authority and has not been tampered with. For OAuth or OpenID Connect providers, this often involves verifying a token signed with a rotating public key from the provider's JWKS endpoint.

In real systems, validation is usually done in middleware or a dependency layer so route handlers receive an already-authenticated principal. Best practice is to reject unexpected algorithms, validate audience and issuer, and distinguish authentication from authorization.

The main pitfall is checking only that the token parses or only that the signature is valid while ignoring expiry, audience, or revocation.

```python
import jwt

def validate_token(token, public_key):
    return jwt.decode(
        token,
        public_key,
        algorithms=["RS256"],
        audience="api-service",
        issuer="https://issuer.example.com",
    )
```

Complete JWT validation middleware for FastAPI:

```python
import jwt
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware


class JWTMiddleware(BaseHTTPMiddleware):
    """Validates JWT on every request except whitelisted paths."""

    SKIP_PATHS = {"/health", "/docs", "/openapi.json"}

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing token")

        token = auth_header.split(" ", 1)[1]

        try:
            payload = jwt.decode(
                token,
                PUBLIC_KEY,
                algorithms=["RS256"],
                audience="api-service",
                issuer="https://issuer.example.com",
            )
            # Attach user info to request state for downstream handlers
            request.state.user = {
                "id": payload["sub"],
                "role": payload.get("role"),
            }
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

        return await call_next(request)


app.add_middleware(JWTMiddleware)
```

Key takeaway: validation means checking signature, expiry, issuer, and audience — not just parsing. Reject unexpected algorithms to prevent algorithm confusion attacks.

### Question: What is OAuth?

Answer:

OAuth is an authorization framework that lets a user or system grant limited access to protected resources without sharing the original credentials with the client.

Internally, OAuth defines flows where a client obtains an access token from an authorization server and then uses that token to call a resource server. The specific flow depends on the client type. For example, Authorization Code with PKCE is standard for user-facing applications.

Best practice is to separate authentication from authorization in your explanation: OAuth is about delegated authorization, while OpenID Connect adds an identity layer on top.

```http
GET /authorize?response_type=code&client_id=app-123&redirect_uri=https://client.example.com/callback
```

### Question: What problem does OAuth solve?

Answer:

OAuth solves the problem of delegated access. It allows one application to act on behalf of a user or system within a limited scope, without exposing the original credentials to that application.

That is why it is used for social login, third-party API access, enterprise identity integration, and service delegation. A common pitfall is using the term loosely for any token-based auth scheme, even when no delegated authorization model exists.

```bash
curl -X POST https://auth.example.com/token \
    -d "grant_type=authorization_code" \
    -d "code=auth-code"
```

## Docker / DevOps

### Question: What is Docker?

Answer:

Docker is a platform for packaging applications and their dependencies into portable containers.

Internally, containers share the host kernel but use isolation features such as namespaces and cgroups. That makes them lighter than full virtual machines while still providing process isolation and reproducible packaging.

Docker is useful for local development, CI pipelines, microservices, and reproducible deployments. Best practice is to build small images, pin base images, and separate build-time and runtime concerns.

```dockerfile
# Basic Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

Multi-stage build (production pattern — smaller final image):

```dockerfile
# Stage 1: Build (includes build tools)
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --target=/install -r requirements.txt

# Stage 2: Runtime (only runtime dependencies)
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /install /usr/local/lib/python3.12/site-packages
COPY . .

# Run as non-root user (security best practice)
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

`.dockerignore` (reduce build context):

```text
.git
.venv
__pycache__
*.pyc
.env
tests/
```

Key takeaway: multi-stage builds separate build dependencies from runtime, resulting in smaller, more secure images. Always run as non-root in production.

### Question: What does containerization solve?

Answer:

Containerization solves consistency and portability problems. It helps ensure the same application artifact runs the same way across developer laptops, CI systems, and production environments.

It also improves deployment packaging and isolation, but it does not replace good configuration, security, or observability practices.

```bash
docker build -t users-service .
docker run -p 8000:8000 users-service
```

### Question: What is the difference between Docker and Docker Compose?

Answer:

Docker is the underlying container platform. Docker Compose is a tool for defining and running multiple related containers as a single application stack.

In practice, Docker is what you use to build images and run individual containers. Compose is what you use when your application needs an app container, a database, a cache, and perhaps a message broker working together for local development or simple deployments.

Best practice is to use Compose for local multi-service workflows and keep the configuration readable. The pitfall is treating Compose as a production orchestration platform for systems that actually need stronger scheduling, scaling, and fault management.

```yaml
services:
    api:
        build: .
    db:
        image: postgres:16
```

Production-ready Docker Compose with health checks, networking, and env vars:

```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/myapp
      - REDIS_URL=redis://cache:6379/0
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_started
    restart: unless-stopped

  db:
    image: postgres:16
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: myapp
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 5s
      timeout: 5s
      retries: 5

  cache:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  pgdata:
```

Key takeaway: use `depends_on` with `condition: service_healthy` so your app doesn't start before the database is actually ready. Don't use Compose for production orchestration — use Kubernetes or ECS.

### Question: What are Docker volumes?

Answer:

Volumes are persistent storage mechanisms for containers. They let data outlive the lifecycle of a container, which is important for databases, uploads, and shared state during development.

Internally, a volume is managed by Docker and mounted into the container filesystem. This is different from the writable container layer, which is ephemeral.

Best practice is to keep application containers stateless where possible and use volumes intentionally. A common pitfall is mounting data carelessly and then running into permission or synchronization issues.

```yaml
services:
    db:
        image: postgres:16
        volumes:
            - pgdata:/var/lib/postgresql/data

volumes:
    pgdata:
```

### Question: What Docker commands are most important to know?

Answer:

The most important Docker commands are `docker build`, `docker run`, `docker ps`, `docker logs`, `docker exec`, `docker images`, `docker stop`, and `docker rm`. For Compose, the essential ones are `docker compose up`, `docker compose down`, and `docker compose logs`.

These commands cover the full local lifecycle: build, run, inspect, debug, stop, and clean up.

```bash
docker build -t myapp .
docker run -d --name myapp-container myapp
docker logs myapp-container
docker exec -it myapp-container sh
```

## Git

### Question: What does git pull do?

Answer:

`git pull` is effectively `git fetch` followed by an integration step, usually `merge` by default unless configured otherwise. It updates your local branch with changes from the remote.

Internally, Git first updates remote-tracking references and then integrates the changes into your current branch. The exact behavior depends on repository configuration.

```bash
# Basic pull
git pull origin main
```

What `git pull` actually does under the hood:

```bash
# git pull = git fetch + git merge (by default)

# Step 1: Fetch remote changes (does NOT modify your working tree)
git fetch origin

# Step 2: See what changed before integrating
git log HEAD..origin/main --oneline

# Step 3: Choose how to integrate
git merge origin/main    # creates merge commit
# OR
git rebase origin/main   # replays your commits on top
```

Configure pull behavior globally:

```bash
# Always rebase on pull (cleaner history)
git config --global pull.rebase true

# Or per-pull:
git pull --rebase origin main
```

Key takeaway: `git pull` is a shortcut. Understanding it as `fetch + merge/rebase` gives you more control and fewer surprises.

### Question: When should you use git pull carefully?

Answer:

Use `git pull` carefully when you want explicit control over integration strategy. In many teams, `git fetch` followed by an intentional `git rebase` or `git merge` is safer and easier to reason about.

The pitfall is running `git pull` mechanically and creating unnecessary merge commits or integrating remote changes before reviewing them.

```bash
git fetch origin
git rebase origin/main
```

### Question: What is git rebase?

Answer:

Rebase rewrites the current branch so its commits are replayed on top of another base commit. The result is a cleaner, more linear history.

```bash
git rebase main
```

Interactive rebase (cleaning up commits before PR):

```bash
# Rebase last 3 commits interactively
git rebase -i HEAD~3

# In the editor, you can:
# pick   abc123 Add user model        <- keep as-is
# squash def456 Fix typo in model     <- merge into previous
# reword ghi789 Add user API          <- change commit message
# drop   jkl012 WIP debug stuff       <- delete this commit

# Result: clean, logical commits ready for code review
```

Handling rebase conflicts:

```bash
# When a conflict occurs during rebase:
git status                    # see conflicting files
# Fix conflicts in your editor, then:
git add <resolved-file>
git rebase --continue         # continue replaying commits

# If you want to abort and go back to the original state:
git rebase --abort
```

Key takeaway: use interactive rebase to clean up local history before pushing. Never rebase commits that have already been pushed to a shared branch.

### Question: How does git rebase differ from merge?

Answer:

Merge combines histories and preserves the branch structure, often with a merge commit. Rebase rewrites commits so the branch appears to have started from a newer base.

Rebase is often cleaner for local work. Merge is often better when you want to preserve exact collaboration history. The pitfall is rebasing public shared history and forcing teammates to reconcile rewritten commits.

```bash
git merge feature-branch
git rebase main
```

### Question: When would you use git cherry-pick?

Answer:

Use `git cherry-pick` when you need one specific commit on another branch without merging the entire branch history. It is common for hotfixes, selective backports, or moving a small change between release branches.

Best practice is to use it intentionally and remember that it duplicates the change as a new commit. Overusing cherry-pick can fragment history and make future merges harder.

```bash
git cherry-pick a1b2c3d
```

## AWS / Cloud

### Question: What is an AWS VPC?

Answer:

An Amazon VPC is a logically isolated virtual network in AWS where you launch resources. It lets you define IP ranges, routing, subnets, gateways, and security boundaries.

Best practice is to design VPCs with clear network boundaries, least-privilege security groups, and private subnets by default for sensitive workloads.

```hcl
resource "aws_vpc" "main" {
    cidr_block = "10.0.0.0/16"
}
```

### Question: What are subnets used for in AWS?

Answer:

Subnets are smaller network segments inside a VPC, usually tied to a specific availability zone. They are used to separate public-facing and private internal resources.

For example, load balancers may sit in public subnets while application servers and databases stay in private subnets. The pitfall is exposing internal infrastructure publicly when it should be reachable only through controlled network paths.

```hcl
resource "aws_subnet" "public_a" {
    vpc_id     = aws_vpc.main.id
    cidr_block = "10.0.1.0/24"
}
```

### Question: What is the difference between EC2 and Lambda?

Answer:

EC2 gives you virtual machines where you manage the operating system, runtime, and scaling model. Lambda is a serverless compute service where you provide code and AWS manages the underlying infrastructure.

EC2 is better when you need long-running processes, full runtime control, or specialized system behavior. Lambda is better for event-driven, short-lived workloads where operational simplicity matters.

```python
# Basic Lambda handler
def lambda_handler(event, context):
    return {"statusCode": 200, "body": "ok"}
```

Real Lambda handler with input validation and error handling:

```python
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info(f"Event: {json.dumps(event)}")

    try:
        # Parse input (API Gateway sends body as string)
        body = json.loads(event.get("body", "{}"))
        user_id = body.get("user_id")

        if not user_id:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "user_id is required"}),
            }

        # Process
        result = process_user(user_id)

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"data": result}),
        }

    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"}),
        }
```

Lambda with SQS trigger (event-driven pattern):

```python
def sqs_handler(event, context):
    """Process messages from SQS queue."""
    failed_records = []

    for record in event["Records"]:
        try:
            message = json.loads(record["body"])
            process_order(message["order_id"])
        except Exception as e:
            logger.error(f"Failed to process {record['messageId']}: {e}")
            failed_records.append({"itemIdentifier": record["messageId"]})

    # Return failed records for partial batch retry
    return {"batchItemFailures": failed_records}
```

Key takeaway: Lambda handlers should parse input, validate, process, and return proper HTTP responses. Use structured logging and handle partial failures for queue triggers.

### Question: What is the Lambda execution duration limit?

Answer:

AWS Lambda has a maximum execution duration of 15 minutes per invocation.

That matters architecturally. If the workload runs longer, needs stable long-lived connections, or needs heavy runtime control, Lambda may be the wrong fit.

```hcl
resource "aws_lambda_function" "worker" {
    function_name = "worker"
    timeout       = 900
}
```

### Question: What are the core AWS services a backend engineer should know?

Answer:

At a minimum, a backend engineer should understand EC2, S3, RDS, DynamoDB, Lambda, VPC, IAM, CloudWatch, SQS, SNS, and API Gateway. These cover compute, storage, relational data, NoSQL, networking, security, observability, messaging, and public API exposure.

Best practice is to understand them as design tools, not just as names. The real skill is matching the workload to the right managed service.

```bash
aws s3 ls
aws dynamodb list-tables
aws sqs list-queues
```

### Question: How would you create a billing alert in AWS?

Answer:

The usual approach is to create a billing metric alarm in CloudWatch and send notifications through SNS when cost crosses a threshold. In many organizations, AWS Budgets is an even better choice because it is designed specifically for cost alerts and budget tracking.

The important operational point is to set thresholds early and route alerts to the team that can act on them.

```bash
aws budgets create-budget --account-id 123456789012 --budget file://budget.json
```

## Machine Learning

### Question: What is the difference between supervised and unsupervised learning?

Answer:

Supervised learning uses labeled data, meaning each training example includes the expected output. The goal is to learn a mapping from inputs to outputs. Unsupervised learning uses unlabeled data and tries to discover structure such as clusters, latent dimensions, or associations.

Classification and regression are supervised problems. Clustering and dimensionality reduction are common unsupervised problems. In practice, supervised learning is used when historical labeled outcomes exist, such as spam detection or price prediction. Unsupervised learning is used for customer segmentation, anomaly detection, or exploratory analysis.

Best practice is to frame the business problem first and only then choose the learning setup. The pitfall is applying ML before verifying that rules, analytics, or simpler models would already solve the problem.

```python
from sklearn.linear_model import LogisticRegression
from sklearn.cluster import KMeans

supervised_model = LogisticRegression()
unsupervised_model = KMeans(n_clusters=3)
```

Full supervised learning pipeline (the real interview answer):

```python
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import numpy as np

# Step 1: Prepare data
X = np.array([[25, 50000], [30, 60000], [35, 80000], [22, 30000], [45, 120000]])
y = np.array([0, 0, 1, 0, 1])  # Labels: 0=no, 1=yes

# Step 2: Split into train/test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Step 3: Scale features (critical for many algorithms)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)  # use same scaler, don't refit!

# Step 4: Train
model = LogisticRegression()
model.fit(X_train_scaled, y_train)

# Step 5: Evaluate
predictions = model.predict(X_test_scaled)
print(f"Accuracy: {accuracy_score(y_test, predictions):.2f}")
print(classification_report(y_test, predictions))
```

Key takeaway: ML is a pipeline, not just `model.fit()`. Data splitting, feature scaling, and proper evaluation are as important as the model choice.

### Question: How does K-Means work?

Answer:

K-Means is an unsupervised clustering algorithm that groups points by iteratively assigning them to the nearest centroid and recalculating those centroids until the assignments stabilize.

The algorithm is simple and efficient, but it assumes cluster shapes that are reasonably compact. That assumption matters when choosing whether it is a good fit.

```python
from sklearn.cluster import KMeans

model = KMeans(n_clusters=3, random_state=42)
model.fit(customer_features)
```

Elbow method to find optimal K:

```python
from sklearn.cluster import KMeans
import numpy as np

# Generate sample data
X = np.random.rand(200, 2)

# Try different values of k and measure inertia (within-cluster sum of squares)
inertias = []
for k in range(1, 11):
    model = KMeans(n_clusters=k, random_state=42, n_init=10)
    model.fit(X)
    inertias.append(model.inertia_)
    print(f"k={k}: inertia={model.inertia_:.2f}")

# Plot inertias vs k — look for the "elbow" (point of diminishing returns)
# The elbow point suggests the optimal number of clusters
```

Inspecting cluster assignments and centroids:

```python
model = KMeans(n_clusters=3, random_state=42, n_init=10)
model.fit(X)

print(model.labels_)          # cluster assignment for each point
print(model.cluster_centers_)  # centroid coordinates
print(model.inertia_)          # total within-cluster variance

# Predict cluster for new data
new_customer = np.array([[0.5, 0.5]])
print(model.predict(new_customer))  # which cluster?
```

Key takeaway: K-Means requires you to choose K upfront. Use the elbow method, silhouette scores, or domain knowledge to pick the right number of clusters.

### Question: When would you use K-Means?

Answer:

Use K-Means for segmentation problems such as customer grouping, usage clustering, or exploratory pattern discovery when clusters are reasonably compact and you want a relatively simple unsupervised baseline.

Best practice is to scale features and validate the cluster count with data analysis rather than guessing. The pitfall is forcing K-Means onto irregular or non-spherical cluster structures.

```python
segments = model.predict(customer_features)
```

### Question: How does KNN work?

Answer:

KNN, or K-Nearest Neighbors, is a supervised algorithm that predicts by looking at the labels or values of the nearest data points in feature space.

It is a lazy learner, which means most of the work happens at prediction time rather than during a heavy training phase. Because distance drives the result, feature scaling matters a lot.

```python
from sklearn.neighbors import KNeighborsClassifier

model = KNeighborsClassifier(n_neighbors=5)
model.fit(X_train, y_train)
```

KNN with proper preprocessing (scaling is critical for distance-based algorithms):

```python
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score

# Pipeline ensures scaling + KNN are always applied together
pipeline = Pipeline([
    ("scaler", StandardScaler()),   # MUST scale — KNN uses distance
    ("knn", KNeighborsClassifier(n_neighbors=5)),
])

# Cross-validation to evaluate properly
scores = cross_val_score(pipeline, X, y, cv=5, scoring="accuracy")
print(f"Accuracy: {scores.mean():.3f} (+/- {scores.std():.3f})")

# Find optimal k
for k in [3, 5, 7, 11]:
    pipe = Pipeline([("scaler", StandardScaler()), ("knn", KNeighborsClassifier(n_neighbors=k))])
    score = cross_val_score(pipe, X, y, cv=5).mean()
    print(f"k={k}: accuracy={score:.3f}")
```

Key takeaway: KNN without feature scaling gives garbage results because features with larger ranges dominate the distance calculation.

### Question: When would you use KNN?

Answer:

Use KNN when you want a simple, interpretable baseline on smaller datasets and the neighborhood structure of the data is meaningful.

It is often useful for introductory classification or regression baselines. The tradeoff is that inference can become expensive on large datasets.

```python
prediction = model.predict(X_test[:1])
```

### Question: How does SVM work?

Answer:

Support Vector Machine finds a decision boundary that maximizes the margin between classes. With kernels, it can model non-linear boundaries as well.

The intuition is that a larger margin often generalizes better. Kernel methods extend this idea to more complex decision boundaries.

```python
from sklearn.svm import SVC

model = SVC(kernel="rbf")
model.fit(X_train, y_train)
```

SVM with hyperparameter tuning using GridSearchCV:

```python
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("svm", SVC()),
])

# Grid search over key hyperparameters
param_grid = {
    "svm__C": [0.1, 1, 10],           # regularization strength
    "svm__kernel": ["linear", "rbf"],  # decision boundary shape
    "svm__gamma": ["scale", "auto"],   # kernel coefficient
}

grid_search = GridSearchCV(pipeline, param_grid, cv=5, scoring="accuracy", verbose=1)
grid_search.fit(X_train, y_train)

print(f"Best params: {grid_search.best_params_}")
print(f"Best score: {grid_search.best_score_:.3f}")

# Use best model for predictions
best_model = grid_search.best_estimator_
predictions = best_model.predict(X_test)
```

Key takeaway: SVM performance depends heavily on C, kernel, and gamma. Always scale features and tune hyperparameters with cross-validation.

### Question: When would you use SVM?

Answer:

Use SVM for classification tasks where the data is high-dimensional, the dataset is not extremely large, and a strong margin-based classifier is a reasonable fit.

Best practice is to normalize features and tune kernel and regularization carefully. The pitfall is applying SVM to very large datasets without considering training cost.

```python
predictions = model.predict(X_test)
```

### Question: How does PCA work?

Answer:

PCA, or Principal Component Analysis, reduces dimensionality by projecting data onto directions of highest variance.

It does not use labels. Instead, it finds orthogonal directions that preserve as much variance as possible in fewer dimensions.

```python
from sklearn.decomposition import PCA

pca = PCA(n_components=2)
reduced = pca.fit_transform(X)
```

Analyzing explained variance (how much information is retained):

```python
from sklearn.decomposition import PCA
import numpy as np

# Fit PCA with all components first to see variance distribution
pca_full = PCA()
pca_full.fit(X)

# Cumulative explained variance
cumulative_variance = np.cumsum(pca_full.explained_variance_ratio_)
for i, var in enumerate(cumulative_variance[:10], 1):
    print(f"{i} components: {var:.2%} variance explained")

# Choose n_components that retain >= 95% variance
n_optimal = np.argmax(cumulative_variance >= 0.95) + 1
print(f"Optimal components for 95% variance: {n_optimal}")

# Apply with optimal components
pca = PCA(n_components=n_optimal)
X_reduced = pca.fit_transform(X)
print(f"Original shape: {X.shape} -> Reduced shape: {X_reduced.shape}")
```

PCA as preprocessing before another model:

```python
from sklearn.pipeline import Pipeline
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression

pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("pca", PCA(n_components=0.95)),  # keep 95% variance
    ("classifier", LogisticRegression()),
])
pipeline.fit(X_train, y_train)
print(f"Accuracy: {pipeline.score(X_test, y_test):.3f}")
```

Key takeaway: don't just blindly set `n_components=2`. Analyze explained variance to make an informed decision about how many dimensions to keep.

### Question: When would you use PCA?

Answer:

Use PCA when you want dimensionality reduction, noise reduction, visualization, or preprocessing before another model.

It is especially useful when the feature space is large and correlated. The tradeoff is that transformed components are usually less interpretable than the original features.

Best practice across all four algorithms is to choose based on the data shape, scale, and objective rather than familiarity.

```python
visual_features = pca.transform(X_test)
```

### Question: What is the difference between machine learning and deep learning?

Answer:

Machine learning is the broader field of algorithms that learn patterns from data. Deep learning is a subset of machine learning that uses multi-layer neural networks to learn hierarchical representations automatically.

Traditional ML often relies more on hand-engineered features and smaller models such as trees, linear models, or SVMs. Deep learning shines when data is large, unstructured, and high-dimensional, such as text, images, audio, and video.

Best practice is to choose the simplest model that meets the requirement. The pitfall is jumping to deep learning without the data volume, compute budget, or evaluation discipline needed to justify it.

```python
# Traditional ML
from sklearn.ensemble import RandomForestClassifier

# Deep learning
import torch.nn as nn

network = nn.Sequential(nn.Linear(128, 64), nn.ReLU(), nn.Linear(64, 10))
```

Complete deep learning training loop (what interviewers expect you to understand):

```python
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

# Define model
class SimpleClassifier(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3),        # regularization
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, output_dim),
        )

    def forward(self, x):
        return self.layers(x)


# Training loop
model = SimpleClassifier(input_dim=128, hidden_dim=64, output_dim=10)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

for epoch in range(10):
    model.train()
    total_loss = 0
    for batch_x, batch_y in train_loader:
        optimizer.zero_grad()          # reset gradients
        predictions = model(batch_x)   # forward pass
        loss = criterion(predictions, batch_y)  # compute loss
        loss.backward()                # backward pass (compute gradients)
        optimizer.step()               # update weights
        total_loss += loss.item()

    # Evaluation
    model.eval()
    with torch.no_grad():
        correct = 0
        total = 0
        for batch_x, batch_y in test_loader:
            outputs = model(batch_x)
            _, predicted = torch.max(outputs, 1)
            total += batch_y.size(0)
            correct += (predicted == batch_y).sum().item()

    print(f"Epoch {epoch+1}: Loss={total_loss:.4f}, Accuracy={correct/total:.3f}")
```

Key takeaway: traditional ML works well on structured/tabular data with engineered features. Deep learning shines on unstructured data (text, images, audio) with enough volume. Always start simple.

## GenAI / LLM / RAG

### Question: How would you explain the end-to-end flow of a GenAI or RAG project in an interview?

Answer:

I would describe the flow as a pipeline. Documents are ingested from sources such as PDFs, databases, or internal tools. The content is cleaned, chunked, enriched with metadata, and converted into embeddings. Those embeddings are stored in a vector database. At query time, the user question is embedded, relevant chunks are retrieved, and the LLM receives a prompt containing the question, system instructions, and retrieved context.

The answer generated by the model is then post-processed, optionally grounded with citations, logged, and monitored for latency, cost, and answer quality. Best practice is to explain the architecture as a sequence of engineering decisions rather than as a loose list of AI tools.

```python
chunks = splitter.split_documents(documents)
vector_store.add_documents(chunks)
retrieved = vector_store.similarity_search(user_query, k=4)
answer = llm.invoke(build_prompt(user_query, retrieved))
```

Complete RAG pipeline implementation:

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFLoader


# Step 1: Ingest documents
def ingest(file_path):
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    # Step 2: Chunk with overlap for context continuity
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". ", " "],  # split at natural boundaries
    )
    chunks = splitter.split_documents(documents)

    # Step 3: Add metadata for filtering
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_index"] = i
        chunk.metadata["source"] = file_path

    # Step 4: Create vector store
    embeddings = OpenAIEmbeddings()
    vector_store = FAISS.from_documents(chunks, embeddings)
    return vector_store


# Step 5: Query with retrieval
def ask(vector_store, question):
    # Retrieve relevant chunks
    retrieved = vector_store.similarity_search(question, k=4)
    context = "\n\n".join([doc.page_content for doc in retrieved])

    # Build prompt with system instruction + context + question
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Answer based ONLY on the provided context. If the context doesn't contain the answer, say so."),
        ("human", "Context:\n{context}\n\nQuestion: {question}"),
    ])

    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    chain = prompt | llm
    answer = chain.invoke({"context": context, "question": question})

    return {
        "answer": answer.content,
        "sources": [doc.metadata for doc in retrieved],
    }


# Usage
store = ingest("company_handbook.pdf")
result = ask(store, "What is the refund policy?")
print(result["answer"])
print(f"Sources: {result['sources']}")
```

Key takeaway: a complete RAG pipeline involves loading, chunking, embedding, storing, retrieving, prompt engineering, and response generation. Each step has tunable parameters that affect final quality.

### Question: How should you explain your contribution to a GenAI project?

Answer:

Be specific about decisions you personally made. For example: you designed the ingestion pipeline, chose the chunking strategy, added metadata filters, built the API layer, improved caching, added observability, or evaluated retrieval quality.

Senior-level answers are concrete about tradeoffs. Instead of saying "I worked on the GenAI project," explain what you changed, why it mattered, and how you measured whether it improved the system.

```python
retrieved = vector_store.similarity_search(query, k=8, filter={"source": "handbook"})
latency_ms = timer.stop()
```

### Question: What is the difference between LangChain and LangGraph?

Answer:

LangChain is a framework for building LLM applications with reusable components such as prompts, tools, retrievers, and chains. LangGraph is designed for stateful graph-based workflows where branching, looping, checkpoints, or multi-step orchestration matter.

In practice, LangChain fits simpler linear flows, while LangGraph fits workflows that need explicit state transitions. The pitfall is introducing orchestration complexity before validating that a simpler pipeline is insufficient.

```python
# LangChain-style linear flow
answer = chain.invoke({"question": user_query})

# LangGraph-style stateful node flow
state = graph.invoke({"question": user_query})
```

### Question: What is a vector database?

Answer:

A vector database stores embeddings and supports similarity search so semantically related content can be retrieved efficiently.

Internally, the database indexes high-dimensional vectors using approximate nearest neighbor techniques so retrieval remains fast even at scale. In LLM systems, that is what makes semantic retrieval practical.

```python
vector_store.add_texts(["FastAPI uses ASGI", "JWT tokens carry claims"])
results = vector_store.similarity_search("How does FastAPI work?", k=2)
```

Vector database with metadata filtering and similarity scores:

```python
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

# Add documents with rich metadata
texts = [
    "FastAPI is an ASGI web framework for Python",
    "JWT tokens contain header, payload, and signature",
    "Docker containers share the host kernel",
    "K-Means clusters data by minimizing inertia",
]
metadatas = [
    {"source": "backend", "topic": "framework", "difficulty": "beginner"},
    {"source": "security", "topic": "auth", "difficulty": "intermediate"},
    {"source": "devops", "topic": "containers", "difficulty": "beginner"},
    {"source": "ml", "topic": "clustering", "difficulty": "intermediate"},
]

vector_store = FAISS.from_texts(texts, OpenAIEmbeddings(), metadatas=metadatas)

# Basic similarity search
results = vector_store.similarity_search("How does FastAPI work?", k=2)

# Search with metadata filter
backend_results = vector_store.similarity_search(
    "web framework", k=3, filter={"source": "backend"}
)

# Search with relevance scores (to set quality threshold)
results_with_scores = vector_store.similarity_search_with_score(
    "How does authentication work?", k=3
)
for doc, score in results_with_scores:
    print(f"Score: {score:.4f} | {doc.page_content[:60]}")
    # Lower score = more similar (for L2 distance)
```

Key takeaway: metadata filters turn a vector DB from "find anything similar" into "find similar content within a specific scope" — critical for multi-tenant or multi-source RAG systems.

### Question: What is chunking?

Answer:

Chunking is the process of breaking larger documents into smaller pieces before embedding or retrieval. The size and overlap of chunks strongly affect retrieval quality.

If chunks are too small, they lose context. If they are too large, retrieval becomes noisy and prompt cost increases. That is why chunking strategy is a real engineering decision, not just a preprocessing detail.

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_text(document_text)
```

Comparing chunking strategies:

```python
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    TokenTextSplitter,
    MarkdownHeaderTextSplitter,
)

text = "Your long document content here..."

# Strategy 1: Recursive character splitting (most common, good default)
recursive = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", ". ", " "],  # tries natural boundaries first
)
chunks_recursive = recursive.split_text(text)

# Strategy 2: Token-based splitting (more precise for LLM context limits)
token_splitter = TokenTextSplitter(
    chunk_size=200,      # 200 tokens per chunk
    chunk_overlap=20,    # 20 token overlap
)
chunks_token = token_splitter.split_text(text)

# Strategy 3: Structure-aware splitting (for Markdown/HTML)
md_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=[
        ("#", "h1"),
        ("##", "h2"),
        ("###", "h3"),
    ],
)
chunks_structured = md_splitter.split_text(markdown_text)
```

Chunk size analysis:

```python
def analyze_chunks(chunks):
    lengths = [len(c) for c in chunks]
    print(f"Total chunks: {len(chunks)}")
    print(f"Avg length: {sum(lengths)/len(lengths):.0f} chars")
    print(f"Min: {min(lengths)}, Max: {max(lengths)}")
    # Check for very short chunks (may lack context)
    tiny = [c for c in chunks if len(c) < 100]
    print(f"Chunks < 100 chars: {len(tiny)} (may need larger chunk_size)")

analyze_chunks(chunks_recursive)
```

Key takeaway: chunking is the single most impactful parameter in RAG quality. Too small = no context. Too large = noisy retrieval. Test with your actual data.

### Question: Why do vector databases matter in LLM systems?

Answer:

Vector databases matter because they make semantic retrieval practical at scale. Without them, searching large embedding collections efficiently becomes difficult and expensive.

In RAG systems, they are the retrieval engine that brings relevant context into the prompt. Best practice is to evaluate retrieval quality with real queries instead of assuming nearest-neighbor search is automatically good enough.

```python
results = vector_store.similarity_search("refund policy", k=3)
```

### Question: Why does chunking matter in LLM systems?

Answer:

Chunking matters because it defines the unit of retrieval. If the chunk is too small, it loses context. If it is too large, retrieval becomes noisy and prompt cost increases.

That makes chunk size, overlap, and metadata strategy real engineering decisions. The pitfall is applying one chunking rule blindly to every corpus.

```python
splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
```

### Question: What is Retrieval-Augmented Generation?

Answer:

Retrieval-Augmented Generation, or RAG, combines retrieval and LLM generation. Instead of answering only from pretraining, the system retrieves relevant external context and includes it in the prompt.

Internally, a RAG system usually includes ingestion, chunking, embedding generation, vector storage, retrieval, prompt assembly, and answer generation.

```python
context = retriever.invoke(question)
answer = llm.invoke(f"Answer using only this context: {context}")
```

Complete RAG with evaluation and citation:

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


def rag_with_citations(retriever, question):
    # Retrieve
    docs = retriever.invoke(question)

    # Build context with source tracking
    context_parts = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "unknown")
        page = doc.metadata.get("page", "?")
        context_parts.append(f"[Source {i}: {source}, page {page}]\n{doc.page_content}")
    context = "\n\n".join(context_parts)

    # Prompt with citation instruction
    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "Answer the question based ONLY on the provided context. "
            "Cite sources using [Source N] notation. "
            "If the context doesn't contain enough information, say 'I don't have enough information.'"
        )),
        ("human", "Context:\n{context}\n\nQuestion: {question}"),
    ])

    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    chain = prompt | llm
    answer = chain.invoke({"context": context, "question": question})

    return {
        "answer": answer.content,
        "sources": [doc.metadata for doc in docs],
        "num_chunks_retrieved": len(docs),
    }


# Evaluation: check retrieval quality
def evaluate_retrieval(retriever, test_questions, expected_sources):
    """Measure how often the retriever finds the right documents."""
    hits = 0
    for question, expected in zip(test_questions, expected_sources):
        docs = retriever.invoke(question)
        retrieved_sources = {doc.metadata.get("source") for doc in docs}
        if expected in retrieved_sources:
            hits += 1
    recall = hits / len(test_questions)
    print(f"Retrieval recall: {recall:.2%}")
    return recall
```

Key takeaway: RAG without evaluation is guesswork. Measure retrieval recall (did it find the right chunks?) and answer quality (did the LLM use them correctly?) separately.

### Question: What problems does RAG solve?

Answer:

RAG improves factual grounding, reduces hallucination risk, allows the model to work with proprietary or current data, and avoids retraining for every knowledge update.

Best practice is to evaluate both retrieval quality and answer quality. The pitfall is assuming RAG guarantees correctness; if retrieval is weak, the final answer will still be weak.

```python
grounded_prompt = {
    "question": question,
    "context": retrieved_chunks,
}
```

### Question: What is Transformer architecture?

Answer:

The Transformer is a neural network architecture built around self-attention instead of recurrence. Self-attention lets each token weigh the relevance of other tokens when building its representation.

Internally, tokens are projected into queries, keys, and values. Attention scores determine how much one token attends to others. Multi-head attention, feed-forward layers, residual connections, normalization, and positional encoding complete the architecture.

```python
import torch.nn as nn

attention = nn.MultiheadAttention(embed_dim=128, num_heads=8, batch_first=True)
```

Self-attention step by step (what interviewers want you to explain):

```python
import torch
import torch.nn.functional as F
import math

def self_attention(query, key, value):
    """
    Scaled dot-product attention.
    query, key, value: (batch, seq_len, d_model)
    """
    d_k = query.size(-1)

    # Step 1: Compute attention scores (how much each token attends to others)
    scores = torch.matmul(query, key.transpose(-2, -1)) / math.sqrt(d_k)
    # scores shape: (batch, seq_len, seq_len)

    # Step 2: Apply softmax to get attention weights (probabilities)
    weights = F.softmax(scores, dim=-1)
    # Each row sums to 1.0

    # Step 3: Weighted sum of values
    output = torch.matmul(weights, value)
    return output, weights


# Example: 1 batch, 4 tokens, 8-dim embeddings
seq_len, d_model = 4, 8
x = torch.randn(1, seq_len, d_model)

output, attention_weights = self_attention(x, x, x)  # self-attention: Q=K=V=X
print(f"Output shape: {output.shape}")          # (1, 4, 8)
print(f"Attention weights shape: {attention_weights.shape}")  # (1, 4, 4)
print(f"Attention weights:\n{attention_weights[0]}")
# Each row shows how much one token attends to every other token
```

Simplified Transformer block:

```python
import torch.nn as nn

class TransformerBlock(nn.Module):
    def __init__(self, d_model, num_heads, d_ff, dropout=0.1):
        super().__init__()
        self.attention = nn.MultiheadAttention(d_model, num_heads, batch_first=True)
        self.norm1 = nn.LayerNorm(d_model)
        self.ff = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.ReLU(),
            nn.Linear(d_ff, d_model),
        )
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        # Self-attention + residual connection + layer norm
        attended, _ = self.attention(x, x, x)
        x = self.norm1(x + self.dropout(attended))

        # Feed-forward + residual connection + layer norm
        fed_forward = self.ff(x)
        x = self.norm2(x + self.dropout(fed_forward))
        return x
```

Key takeaway: attention computes a weighted combination of all tokens, where the weights are learned from the data. This is why Transformers capture long-range dependencies better than RNNs.

### Question: Why is Transformer architecture important for modern LLMs?

Answer:

Transformers scale well, parallelize efficiently on modern hardware, and capture long-range dependencies better than older sequence architectures. That is why they became the foundation of modern language models.

Best practice in interviews is to explain the intuition first and then the mechanics. The pitfall is reciting terminology such as queries and keys without explaining why attention is useful.

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("gpt2")
model = AutoModelForCausalLM.from_pretrained("gpt2")
```

## Project / Documentation

### Question: How should you walk an interviewer through the README?

Answer:

Start with the purpose of the project, not with commands. Explain what the system solves, who uses it, and the main technical building blocks.

Then describe how the README supports a new developer: prerequisites, environment variables, install steps, run steps, and verification steps. A strong answer adds engineering context instead of reading the README line by line.

```md
# Project Name
## Prerequisites
## Setup
## Run
## Test
```

### Question: How should you explain project setup in an interview?

Answer:

Explain setup as a developer workflow: clone the code, configure environment variables, install dependencies, start required services, run the app, and verify it with tests or sample endpoints.

The important part is not just listing commands. Explain why the setup is structured that way, such as why Docker is used, why a `.env` file exists, or what external dependencies are required.

```bash
git clone <repo>
cp .env.example .env
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Question: How should you explain your project code in an interview?

Answer:

Explain the code from the main entry point inward. Walk through the API layer, service layer, data access layer, and key integrations so the listener understands how a request flows through the system.

Focus on responsibilities rather than file names alone. Interviewers usually care more about boundaries and decisions than about directory memorization.

```text
app/
    api/
    services/
    repositories/
    models/
```

### Question: How should you explain system architecture in an interview?

Answer:

Explain architecture in terms of components, responsibilities, and tradeoffs. Start with the request path, then describe storage, external services, async jobs, logging, testing, and deployment concerns.

For your own contribution, be explicit about what you designed, implemented, improved, or debugged. Mention one or two concrete technical decisions and the tradeoffs involved. For example, why you chose async I/O, why you added caching, why you changed schema design, or how you improved retrieval quality in a GenAI pipeline.

Best practice is to speak in terms of responsibilities, boundaries, and tradeoffs. The pitfall is staying too high level and never demonstrating ownership, or going too low level and getting lost in code details without explaining why they matter.

```text
Client -> API -> Service -> Repository -> Database
                 |
                 -> Queue -> Worker
```