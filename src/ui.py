import time

def progress_bar(name: str, iteration: int, total: int, length=40, refuse_finish: bool = False):
    
    percent = 100 * (iteration / float(total))
    
    filled_length = int(length * iteration // total)
    bar = '■' * filled_length + '-' * (length - filled_length)
    
    extended_name = name + ": " + ' ' * (12 - len(name))
    
    print(f'\r{extended_name}[{bar}] {percent:.0f}% Complete', end='\r')
    
    #wait one second total
    time.sleep(0.33 / total)
    
    if iteration == total and not refuse_finish:
        print()
        time.sleep(0.15)