from machine import Timer, Pin

timer_count = 0 # global variable

def interruption_handler(pin):
    global timer_count
    timer_count += 1


if __name__ == "__main__":
    timer_count_old = 0
    soft_timer = Timer(mode=Timer.PERIODIC, period=100, callback=interruption_handler)

    while True:
        if timer_count > 10:
            timer_count = 0
            print("10x")
            # heavy task here