def detect() -> Bool:
    pass


def translate(line: str, token: str) -> list[str]:
    pass

# x=y+4;
# ---
# LDA <target2>
# MVI B,<8bit data>
# ADD B
# STA <target1>