def detect() -> Bool:
    pass


def translate(line: str, token: str) -> list[str]:
    pass

# x=x+y;
# ---
# LDA <target2>
# MOV B,A
# LDA <target1>
# ADD B
# STA <target1>