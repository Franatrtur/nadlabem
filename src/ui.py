import time
def progress_bar(name: str, iteration: int, total: int, length=40):
    percent = 100 * (iteration / float(total))
    filled_length = int(length * iteration // total)
    bar = '■' * filled_length + '-' * (length - filled_length)
    extended_name = name + ": " + ' ' * (15 - len(name))
    print(f'\r{extended_name}[{bar}] {percent:.0f}% Complete', end='\r')
    #wait one second total
    time.sleep(0.33 / total)
    if iteration == total:
        print()
        time.sleep(0.2)