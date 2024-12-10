from ..translator import AssemblyInstruction
from ..errors import NadLabemError
from ..config import CompilationConfig
from ..ui import progress_bar
import time

class Optimizer:

    def __init__(self,
            config: CompilationConfig,
            instructions: list[AssemblyInstruction],
            program_begin: int,
            program_end: int):

        self.config = config
        self.code: list[AssemblyInstruction] = instructions
        self.program_begin: int = program_begin
        self.program_end: int = program_end
        self.iteration: int = 1

    def optimize(self) -> list[AssemblyInstruction]:
        
        last_length: int = len(self.code)

        # iterate until no more optimizations are possible
        while(self.iteration):
            result = self.optimize_round()
            if last_length <= len(result):
                break
            self.code = result
            last_length = len(self.code)
            self.iteration += 1
            
            if self.config.verbose:
                time.sleep(0.1)

        print()     # flush the last progress bar

        return self.code

    
    def optimize_round(self) -> list[AssemblyInstruction]:
        self.i: int = 0

        result: list[AssemblyInstruction] = []

        def get_last() -> AssemblyInstruction | None:
            if self.i > 0 and result[-1].assembled:
                return result[-1]
            return None

        def add(operation: AssemblyInstruction) -> None:
            result.append(operation)
            self.i += 1

        def skip() -> None:
            self.i += 1

        
        while self.i < self.program_begin:
            add(self.code[self.i])


        #################### OPTIMIZATION BEGIN ####################


        while self.i < self.program_end:

            if self.config.verbose:
                progress_bar(f"Optimizing.{self.iteration}", self.i - self.program_begin + 1, self.program_end - self.program_begin, refuse_finish=True)

            op = self.code[self.i]

            last: AssemblyInstruction | None = get_last()

            # skip special instructions
            if not op.assembled:
                add(op)
                continue

            # 1) Handle push-then-pop operations
            if last and last.operation == "push" and op.operation == "pop":
                if last.arguments == op.arguments:
                    result.pop()
                    skip()
                    continue
                else:
                    result[-1].operation = "mov"
                    result[-1].arguments.insert(0, op.arguments[0])
                    skip()
                    continue

            # 2) ... ? 

            add(op) # add to result unmodified if we didnt skip and continue

            
        #################### OPTIMIZATION END ####################


        self.program_end = len(result)

        while self.i < len(self.code):
            add(self.code[self.i])

        return result