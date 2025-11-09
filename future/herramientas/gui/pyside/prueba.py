import time

i = 0
seguir = True
while seguir:
    i += 1
    print(i)
    time.sleep(1)
    if i >= 10:
        seguir = False