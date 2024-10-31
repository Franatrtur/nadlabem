def detect() -> Bool:
    pass


def translate(line: str, token: str) -> list[str]:
    pass

# x=5;
# ---
# MVI A,<8bit data> - loads constant into register A (or ADI)
# STA <target>