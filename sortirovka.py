global sch
sch = 0

def quick_sort(s):
    global sch
    if len(s) <= 1:
        return s

    center_element = s[0]
    left = list(filter(lambda i: i < center_element, s))
    center = [i for i in s if i == center_element]
    right = list(filter(lambda i: i > center_element, s))
    sch = sch + 1
    return quick_sort(left) + center + quick_sort(right)


print(quick_sort([10, 24, 95, 0, 12, 53, -43]), f"за {sch} прохода")