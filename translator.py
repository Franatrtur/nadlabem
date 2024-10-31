import src.tokenizer

# TODO: logika pro celý proces:
# input je jen string source kódu ✓
# rozdělit na lines ✓
# tokenize lines ✓
# apply lexer on tokens in each line
# run detectors on token lists, while ignoring ones not ending with ;
# call each minitranslator on each line
# replace the lines with the minitranslated lines ✓

def translate(code: str) -> list[str]:
    result: list[str] = [] # string je ratardova hodnota. list bude prehlednejsi a peknejsi podle me

    lines = code.split()
    for line in lines:
        if not line.rstrip().endswith(';'):
            result.append(line)
            continue

        tokens = tokenizer.tokenize(line)
        # implementovat lexer
        # zavolat minitranslatory s tokenama lexeru
        # dat do vysledku

    return result
    