from ..translator import Assembly
from ..errors import NadLabemError
from ..config import CompilationConfig
from ..ui import progress_bar
import time

class Optimizer:

    def __init__(self,
            config: CompilationConfig,
            instructions: list[Assembly],
            program_begin: int,
            program_end: int):

        self.config = config
        self.code: list[Assembly] = instructions
        self.result: list[Assembly] = []
        self.program_begin: int = program_begin
        self.program_end: int = program_end
        self.iteration: int = 1
        self.i: int = 0

    def optimize_round(self) -> None:
        self.i: int = self.program_begin
        self.result = self.code[0:self.program_begin]

        while self.i < self.program_end:

            if self.config.verbose:
                progress_bar(f"Optimizing.{self.iteration}", self.i - self.program_begin + 1, self.program_end - self.program_begin, refuse_finish=True)

            op = self.code[self.i]

            last: Assembly | None = self.get_last()

            # skip special instructions
            if not op.assembled:
                self.add(op)
                continue

            # 1) Handle push-then-pop operations
            if last and last.operation == "push" and op.operation == "pop":
                if last.arguments == op.arguments:
                    self.result.pop()
                    self.skip()
                    continue
                else:
                    self.result[-1].operation = "mov"
                    self.result[-1].arguments.insert(0, op.arguments[0])
                    self.skip()
                    continue

            # 2) ... ?

            # ideas:
            #  - labeled nops: nops can be removed and their label given to the next instruction
            #    if it is unlabeled
            #  - things like mov ax, val   and then   mov bx, ax
            #  - things like sub  sp, 0

            self.add(op) # add to result unmodified if we didnt skip and continue


        self.program_end = len(self.result)

        self.result.extend(self.code[self.i:])

    def optimize(self) -> list[Assembly]:
        
        last_length: int = len(self.code)

        # iterate until no more optimizations are possible
        while(self.iteration):
            
            self.optimize_round()
            
            if last_length <= len(self.result):
                break
            
            self.code = self.result
            last_length = len(self.code)
            self.iteration += 1
            
            if self.config.verbose:
                time.sleep(0.1)

        if self.config.verbose:
            print()     # flush the last progress bar

        return self.result

    def get_last(self) -> Assembly | None:
        if self.i > 0 and self.result[-1].assembled:
            return self.result[-1]
        return None

    def add(self, operation: Assembly) -> None:
        self.result.append(operation)
        self.i += 1

    def skip(self) -> None:
        self.i += 1