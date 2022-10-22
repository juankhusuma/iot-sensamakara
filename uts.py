def my_median(lst):
    if len(lst) == 0:
        return None
    else:
        x = lst
        if len(x) % 2 != 0:
            return float(x[(len(x)-1)//2])
        else:
            return (x[len(x)//2-1] + x[len(x)//2]) / 2


print(my_median([]))
print(my_median([1, 2, 3]))
print(my_median([1, 2, 3, 4]))
print(my_median([1, 2, 2, 4]))
