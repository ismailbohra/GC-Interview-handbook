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
