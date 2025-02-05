from collections import deque
import time
import random

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

# Пример использования
expression = "{[()()]}"
print(is_balanced(expression))  # Вывод: True
expression = "{[(()]}"
print(is_balanced(expression))  # Вывод: False

def worker(task_queue):
    while task_queue:
        task = task_queue.popleft()  # Извлекаем задачу из очереди
        print(f"Выполняется задача: {task}")
        time.sleep(random.uniform(0.5, 1.5))  # Симуляция времени выполнения задачи
    print("Все задачи выполнены!")

# Пример использования
task_queue = deque(['Задача 1', 'Задача 2', 'Задача 3', 'Задача 4'])

worker(task_queue)