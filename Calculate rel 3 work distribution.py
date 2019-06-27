import sys

num = 632706
parts = 7

divider = [2 * i for i in range(1, parts)]

divider.insert(0, 0)
divider.append(num)

def calc_work(i):
    return (divider[i + 1] - divider[i]) * (num - (divider[i] + divider[i + 1] - 1) / 2) / num

work = [0] * parts
for i in range(parts):
    work[i] = calc_work(i)

min_work = min(work)
max_work = max(work)

while(max_work - min_work > 3):
    
    min_work = min(work)
    max_work = max(work)

    sys.stdout.flush()
    sys.stdout.write("%d \r" % (max_work - min_work))

    max_ind = work.index(max_work)
    
    div = max([int(160000 / (max_work - min_work)), 4])
    tweak = int((divider[max_ind + 1] - divider[max_ind]) / div)
    
    if max_ind > 0:
        divider[max_ind] += tweak
        work[max_ind - 1] = calc_work(max_ind - 1)

    if max_ind < parts - 1:
        divider[max_ind + 1] -= tweak
        work[max_ind + 1] = calc_work(max_ind + 1)

    work[max_ind] = calc_work(max_ind)

print(divider)
