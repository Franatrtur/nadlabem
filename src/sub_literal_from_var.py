def detect() -> Bool:
    pass


def translate(line: str, token: str) -> list[str]:
    pass

# x=y-2;
# ---
# LDA <target2>
# MVI B,<8bit data>
# CMA
# INR A
# ADD B
# STA <target1>