#from collections import deque
import time
import random

##Пример работы со стеком:
class Stack:
    def __init__(self):  # Правильная инициализация
        self.items = []  # Инициализируем список для хранения элементов

    def is_empty(self):
        return self.items == []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def peek(self):
        return self.items[-1]

# Пример использования класса Stack
expression = Stack()
print(f"Сначала стек пустой: {expression.is_empty()}")  # Вывод: True

expression.push("{")
expression.push("[")
expression.push("(")
expression.push(")")
expression.push("(")

print(expression.peek())  # Вывод: "("
print(f"Удалим: {expression.pop()}")  # Вывод и удаление: "("

expression.push("]")
expression.push("}")

print(f"Теперь стек пустой? {expression.is_empty()}")  # Вывод: False
print(f"Все скобки парные для стека? {expression.items}: ")

def is_balanced(expression):
    stack = []
    brackets = {')': '(', '}': '{', ']': '['}

    for char in expression:
        if char in brackets.values():  # Если открывающая скобка
            stack.append(char)
        elif char in brackets.keys():  # Если закрывающая скобка
            if not stack or stack.pop() != brackets[char]:  # Проверка на соответствие
                return False

    return not stack  # Если стек пуст, скобки сбалансированы

# Пример использования функции is_balanced
#expression_str = "{[()()]}"
print(is_balanced(expression.items))  # Вывод: True
expression_str = "{[(()]}"
print(f"Для стека {expression_str} все скобки парные? {is_balanced(expression_str)}")  # Вывод: False

# Пример работы с очередью:
class Queue:
    def __init__(self):  # Правильная инициализация
        self.items = []  # Инициализируем список для хранения элементов

    def is_empty(self):
        return self.items == []

    def enqueue(self, item):
        self.items.insert(0, item)

    def dequeue(self):
        return self.items.pop()

    def size(self):
        return len(self.items)

queue = Queue()

print(f"\nОчередь пуста? {queue.is_empty()} ")
queue.enqueue("Задача 0")
queue.enqueue("Задача 1")
queue.enqueue("Задача 2")
queue.enqueue("Задача 3")
queue.enqueue("Задача 4")

print(f"Добавили {queue.size()} элементов. Очередь теперь пуста? {queue.is_empty()}")
print(f"Удалили задачу: {queue.dequeue()} . Теперь в очереди следующие задачи:")
print(queue.items)

def worker(task_queue):
    while not task_queue.is_empty():  # Проверяем, есть ли задачи в очереди
        task = task_queue.dequeue()  # Извлекаем задачу из очереди
        print(f"Выполняется задача: {task}")
        time.sleep(random.uniform(0.5, 1.5))  # Симуляция времени выполнения задачи
    print("Все задачи выполнены!")

# Пример использования worker
worker(queue)  # Передаем очередь в worker
