def detect() -> Bool:
    pass


def translate(line: str, token: str) -> list[str]:
    pass

# x=x-y;
# ---
# LDA <target1>
# MOV B,A
# LDA <target2>
# CMA
# INR A
# ADD B
# STA <target1>