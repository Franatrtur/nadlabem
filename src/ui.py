
def progress_bar(name: str, iteration: int, total: int, length=40):
    percent = 100 * (iteration / float(total))
    filled_length = int(length * iteration // total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    print(f'\r{name}: 	|{bar}| {percent:.2f}% Complete', end='\r')
    if iteration == total:
        print()