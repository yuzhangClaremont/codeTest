
# Review 1: 
# 问题：my_list=[] 在函数定义时创建一次, 其他调用会共享它
# def add_to_list(value, my_list=[]):
#     my_list.append(value)
#     return my_list

# 问题演示：
# add_to_list(1)  -> [1]
# add_to_list(2)  -> [1, 2]  (we want [2])
# add_to_list(3)  -> [1, 2, 3]

# 修正版本：
def add_to_list(value, my_list=None):
    if my_list is None:
        my_list = []
    my_list.append(value)
    return my_list


# Review 2: 
# 问题：字符串中的 {name} 和 {age} 没有被替换，只是普通字符串
# def format_greeting(name, age):
#     return "Hello, my name is {name} and I am {age} years old."

# 问题演示：
# format_greeting("Alice", 25) -> "Hello, my name is {name} and I am {age} years old."
# (变量没有被替换！)

# 修正版本：
def format_greeting(name, age):
    return f"Hello, my name is {name} and I am {age} years old."


# Review 3:
# 问题：counter 的实例共享同一个count
# class Counter:
#     count = 0
#     def __init__(self):
#         self.count += 1
#     def get_count(self):
#         return self.count

# 问题演示：
# c1 = Counter()  -> count = 1
# c2 = Counter()  -> count = 2 (c1 的 count 也变成 2！)
# c1.get_count()  -> 2 (不是 1)

# 修正版本：
class Counter:
    def __init__(self):
        self.count = 1
    def get_count(self):
        return self.count


# Review 4: 线程不安全
# 问题：虽然类名叫 SafeCounter，但 increment 不是原子操作，多线程会有竞态条件
import threading

# 原始版本：
# class SafeCounter:
#     def __init__(self):
#         self.count = 0
#     def increment(self):
#         self.count += 1
# 
# def worker(counter):
#     for _ in range(1000):
#         counter.increment()
# 
# counter = SafeCounter()
# threads = []
# for _ in range(10):
#     t = threading.Thread(target=worker, args=(counter,))
#     t.start()
#     threads.append(t)
# 
# for t in threads:
#     t.join()
# 
# print(counter.count)  # 期望 10000，实际可能小于 10000

# 问题：count += 1 实际上是三步操作：
# 1. 读取 count
# 2. 加 1
# 3. 写回 count
# 多线程同时执行会导致丢失更新

# 修正版本（使用锁）：
class SafeCounter:
    def __init__(self):
        self.count = 0
        self.lock = threading.Lock()
    
    def increment(self):
        with self.lock:
            self.count += 1

def worker(counter):
    for _ in range(1000):
        counter.increment()

counter = SafeCounter()
threads = []
for _ in range(10):
    t = threading.Thread(target=worker, args=(counter,))
    t.start()
    threads.append(t)

for t in threads:
    t.join()
print(counter.count)  


# Review 5: 赋值运算符错误
# 问题：=+ 是赋值正数，不是累加。应该是 +=
# def count_occurrences(lst):
#     counts = {}
#     for item in lst:
#         if item in counts:
#             counts[item] =+ 1  # 这是 counts[item] = (+1)
#         else:
#             counts[item] = 1
#     return counts

# 问题演示：
# count_occurrences([1, 1, 1]) -> {1: 1} (应该是 {1: 3})

# 修正版本：
def count_occurrences(lst):
    counts = {}
    for item in lst:
        if item in counts:
            counts[item] += 1
        else:
            counts[item] = 1
    return counts
