import time
import sys

def progress_bar(name, iteration, total, length=40):
    percent = 100 * (iteration / float(total))
    filled_length = int(length * iteration // total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    print(f'\r{name}: |{bar}| {percent:.2f}% Complete', end='\r')
    if iteration == total:
        print()

# Example usage
total = 100
for i in range(total + 1):
    progress_bar("test", i, total)
    time.sleep(0.1)