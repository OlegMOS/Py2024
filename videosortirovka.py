# Эта Видео-программа визуализирует процесс быстрой сортировки pivot
# и одновременно предоставляет текстовые пояснения на русском языке в отдельном окне.

import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def quick_sort_visualization(arr, start, end, bar_rects, ax, colors, info_label):
    if start < end:
        pivot_index = partition(arr, start, end, bar_rects, ax, colors, info_label)
        quick_sort_visualization(arr, start, pivot_index - 1, bar_rects, ax, colors, info_label)
        quick_sort_visualization(arr, pivot_index + 1, end, bar_rects, ax, colors, info_label)

def partition(arr, start, end, bar_rects, ax, colors, info_label):
    pivot = arr[end]
    pivot_index = start
    info_label.config(text=f"Опорный элемент: {pivot}")
    for i in range(start, end):
        if arr[i] < pivot:
            arr[i], arr[pivot_index] = arr[pivot_index], arr[i]
            update_bars(bar_rects, arr, ax, colors, info_label)
            pivot_index += 1
    arr[pivot_index], arr[end] = arr[end], arr[pivot_index]
    update_bars(bar_rects, arr, ax, colors, info_label)
    return pivot_index

def update_bars(bar_rects, arr, ax, colors, info_label):
    for rect, val, color in zip(bar_rects, arr, colors):
        rect.set_height(val)
        rect.set_color(color)
    ax.set_title("Визуализация быстрой сортировки")
    info_label.config(text=f"Текущий массив: {arr}")
    plt.pause(0.8)  # Пауза для анимационного эффекта

def main():
    # Создаем главное окно
    root = tk.Tk()
    root.title("Визуализация Быстрой Сортировки")

    # Создаем фигуру и ось для графика
    fig, ax = plt.subplots()

    # Генерируем случайный массив
    n = 10
    arr = np.random.randint(1, 100, n)
    colors = ['blue'] * n

    # Создаем график
    bar_rects = ax.bar(range(n), arr, color=colors, align='center')
    ax.set_xlim(0, n)
    ax.set_ylim(0, int(1.1 * max(arr)))

    # Интегрируем график в Tkinter
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    # Создаем информационное окно
    info_frame = tk.Frame(root)
    info_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=1)

    info_label = tk.Label(info_frame, text="Начало сортировки...", font=('Arial', 12), justify=tk.LEFT)
    info_label.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    # Запускаем сортировку
    quick_sort_visualization(arr, 0, n - 1, bar_rects, ax, colors, info_label)

    # Запуск главного цикла Tkinter
    root.mainloop()

if __name__ == "__main__":
    main()