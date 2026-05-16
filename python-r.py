# def logger(l_type):
#     def decorator(func):
#         def wrapper(*args):
#             print(l_type)
#             func(*args)

#         return wrapper

#     return decorator


# @logger("by")
# def add(a, b):
#     return a + b


# class Decorator:
#     def __init__(self, func):
#         self.func = func

#     def __call__(self, *args, **kwds):
#         print("adf")
#         return self.func(*args, **kwds)


# @Decorator
# def sub(a, b):
#     return a + b


# print(sub(2, 3))


# class My_context:
#     def __enter__(self):
#         print("start")

#     def __exit__(self, exc_type, exc, tb):
#         print("exiting context")


# with My_context():
#     print("hii")


# import threading


# def task(n):
#     print(n)


# t1 = threading.Thread(target=task, args=(1,))
# t2 = threading.Thread(target=task, args=(2,))

# t1.start()
# t2.start()

# t1.join()
# t2.join()


# import asyncio


# async def add(a, b):
#     await asyncio.sleep(1)
#     print(a + b)


# async def sub(a, b):
#     await asyncio.sleep(1)
#     print(a - b)


# async def multiply(a, b):
#     await asyncio.sleep(1)
#     print(a * b)


# async def main():
#     await asyncio.gather(  # run multiple task together => .gather
#         add(1, 2),
#         sub(1, 2),
#         multiply(1, 2),
#     )


# asyncio.run(main())


# import time
# from multiprocessing import Process


# def task(n):
#     print(time.time())
#     print(n)


# if __name__ == "__main__":
#     processes = []

#     for i in range(3):
#         p = Process(target=task, args=(i,))
#         processes.append(p)
#         p.start()

#     for p in processes:
#         p.join()


# class Count:
#     def __init__(self, n):
#         self.n = n
#         self.index = 0

#     def __iter__(self):
#         return self

#     def __next__(self):
#         if self.index < self.n:
#             self.index += 1
#             return self.index
#         else:
#             raise StopIteration


# count = Count(5)

# for c in count:
#     print(c)


# def task():
#     for i in range(10):
#         yield i


# g = task()
# print(next(g))
# print(next(g))
# print(next(g))

# a = [1, 2, 3]
# b = ["a", "b", "c"]

# data = {a: b for a, b in zip(a, b)}
# print(data)

# from pathlib import Path


# class MyContextManager:
#     def __init__(self, file_path):
#         self.file_path = file_path
#         self.file = None

#     def __enter__(self):
#         p = Path(self.file_path)

#         if not p.exists():
#             raise FileNotFoundError(f"{self.file_path} not found")

#         self.file = open(self.file_path, "r")
#         print("Entering context")
#         return self.file

#     def __exit__(self, exc_type, exc, tb):
#         print("Inside __exit__")
#         print("Exception Type :", exc_type)
#         print("Exception Value:", exc)
#         print("Traceback      :", tb)

#         if self.file:
#             self.file.close()
#             print("File closed")

#         return False  # re-raise exception if occurred


# with MyContextManager("test.py") as f:
#     print("Inside with block")
#     print(f.read())


# import time
# from contextlib import contextmanager


# @contextmanager
# def Timer(label):
#     start = time.perf_counter()
#     yield
#     end = time.perf_counter()
#     elapsed = end - start
#     print(f"{label}: {elapsed:.4f}s")


# with Timer("Time Taken"):
#     total = sum(range(1_000_000_00))


# def fibonacci(n):
#     a, b = 0, 1
#     for _ in range(n):
#         yield a
#         a, b = b, a + b


# print(list(fibonacci(1)))
# print(list(fibonacci(2)))
# print(list(fibonacci(7)))


# MRO


class P:
    _x = 0

    def __init__(self):
        self.__y = 5


class X(P):
    pass


class Y(P):
    pass


class Z(P):
    pass


class A(X, Y):
    pass


class B(Y, Z):
    pass


class C(A, B):
    pass


# print(C.mro())
# for cls in C.__mro__:
#     print(f"{cls.__name__}: {[m for m in cls.__dict__ if not m.startswith('_')]}")
# c = C()
# print(c._P__y)


# import tracemalloc

# tracemalloc.start()
# for _ in range(1000):
#     print("hii")
# snapshot = tracemalloc.take_snapshot()
# for stat in snapshot.statistics("lineno")[:5]:
#     print(stat)

# import time


# class CustomCM:
#     def __init__(self):
#         pass

#     def __enter__(self):
#         start = time.time()
#         print(f"Started at: {start}")

#     def __exit__(self, exc_type, exc, tb):
#         print(f"End: {time.time()}")


# with CustomCM():
#     print("hii")

# from dataclasses import dataclass


# @dataclass(frozen=True, slots=True)
# class Uesr:
#     name: str
#     age: int

#     def __post_init__(self):
#         if not isinstance(self.name, str):
#             raise TypeError("name must be a string")
#         if not isinstance(self.age, int):
#             raise TypeError("age must be an integer")
#         if self.age < 0:
#             raise ValueError("age must be a non-negative integer")


# u = Uesr("ismail", 20)
# print(dir(u))


# class User:
#     def __init__(self, name, age):
#         self.name = name
#         self.age = age


# print("=" * 50)
# x = User("ismail", 20)
# print(dir(x))
# import sys

# print(sys.getsizeof(u), sys.getsizeof(x))

# import gc
# import tracemalloc
# from dataclasses import dataclass


# # Normal class
# class User:
#     def __init__(self, name, age):
#         self.name = name
#         self.age = age


# # Slotted dataclass
# @dataclass(slots=True, frozen=True)
# class UserSlot:
#     name: str
#     age: int


# def measure(label, creator):
#     gc.collect()
#     tracemalloc.start()

#     before = tracemalloc.take_snapshot()

#     objs = creator()

#     after = tracemalloc.take_snapshot()

#     stats = after.compare_to(before, "lineno")
#     total = sum(stat.size_diff for stat in stats)

#     print(f"{label}: {total / 1024 / 1024:.2f} MB")

#     tracemalloc.stop()
#     return objs


# # Create 100,000 objects
# normal_objs = measure(
#     "Normal class", lambda: [User("ismail", 20) for _ in range(100000)]
# )

# slot_objs = measure(
#     "Slots dataclass", lambda: [UserSlot("ismail", 20) for _ in range(100000)]
# )


# import threading
# import time


# def work():
#     time.sleep(2)
#     print("Work Done!")


# t = threading.Thread(target=work)
# t.daemon = True
# t.start()

# # t.join()  # Wait until t completes

# print("Main thread continues")


# import logging
# import threading
# import time

# logging.basicConfig(level=logging.DEBUG, format=f"%(message)s")

# # print is not thread safe

# start = time.perf_counter()


# def do_something(a):
#     logging.info(
#         f"{threading.current_thread().name} - {a + 1} --- sleeping for 1 second"
#     )
#     time.sleep(1)
#     logging.info(f"{threading.current_thread().name} - {a + 1} --- Done")


# threads = []

# for i in range(10):
#     t = threading.Thread(target=do_something, args=(i,))
#     t.start()
#     threads.append(t)
#     print("=" * 50)
#     print("=" * 50)


# for thread in threads:
#     thread.join()

# finish = time.perf_counter()

# print(f"Finished {round(finish - start, 2)} seconds")


# import multiprocessing
# from multiprocessing import Lock, Process, Value


# def task(x, lock, iterations):
#     for _ in range(iterations):
#         with lock:
#             x.value += 1


# if __name__ == "__main__":
#     x = Value("i", 0)
#     lock = Lock()

#     # Use fewer processes, but give them more work
#     num_processes = 4
#     total_increments = 1000
#     increments_per_process = total_increments // num_processes

#     processes = []
#     for _ in range(num_processes):
#         # Pass x and lock explicitly to the process
#         p = Process(target=task, args=(x, lock, increments_per_process))
#         p.start()
#         processes.append(p)

#     for p in processes:
#         p.join()

#     print(f"Final Value: {x.value}")  # Access the .value attribute
# from multiprocessing import Pipe, Process


# def child_process(conn):
#     data = conn.recv()
#     print(f"Child received: {data}")
#     conn.send("Message received!")
#     conn.close()


# if __name__ == "__main__":
#     parent_conn, child_conn = Pipe()

#     p = Process(target=child_process, args=(child_conn,))
#     p.start()

#     parent_conn.send("Hello child!")
#     print(parent_conn.recv())

#     p.join()
# import multiprocessing

# print(multiprocessing.cpu_count())
# import os

# print(os.process_cpu_count())

nums = (i for i in range(1000000))
for n in nums:
    print(n)
