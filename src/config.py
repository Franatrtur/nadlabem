
class TranslationConfig:

    def __init__(self,
            target_cpu: str = "i8080",
            generate_mapping: bool = True,
            devmode: bool = False,
            erase_comments: bool = False,
            tabspaces: int = 8,
            verbose: bool = True):

        self.target_cpu = target_cpu
        self.generate_mapping = generate_mapping
        self.devmode = devmode
        self.erase_comments = erase_comments
        self.tabspaces = tabspaces
        self.verbose = verbose

    def __str__(self):
        return f"TranslationConfig(target_cpu={self.target_cpu}, generate_mapping={self.generate_mapping}, devmode={self.devmode}, erase_comments={self.erase_comments}, tabspaces={self.tabspaces}, verbose={self.verbose})"