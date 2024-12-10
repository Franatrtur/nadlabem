from .program import ProgramTranslator
from ..translator import Translator
from ..nodes.node import AbstractSyntaxTreeNode as ASTNode
from ..nodes.statement import AssemblyNode
from ..nodes.expression import AssemblyExpressionNode
from ..errors import NotImplementedError, SyntaxError, NameError
from ..tokenizer.symbols import AtToken, NameToken
from .allocator import Variable
import re

class AssemblyTranslator(Translator):

    node_type = AssemblyNode

    def process_template(self, code_line: str) -> str:

        def replace(match) -> str:
            # Extract the placeholder name from the match (i.e., {customer})
            placeholder = match.group(1)
            symbol = self.node.scope.resolve_symbol(NameToken(placeholder, self.node.token.line))
            replacement = Variable.variables.get(symbol, None)
            if replacement is None:
                raise NameError(f"Variable for placeholder {placeholder} not found in assembly template.", self.node.token.line)
            return replacement.location()
    
        # Split the string at the semicolon
        parts = code_line.split(';', 1)
        
        # If there's content before the semicolon, replace placeholders
        if parts[0]:
            parts[0] = re.sub(r'\{([a-zA-Z0-9_]+)\}', replace, parts[0])
        
        # Reassemble the string with the semicolon and content after it
        return ';'.join(parts)

    def make(self) -> None:
        self.node: AssemblyNode

        # if the command starts with a space its unlabeled instruction  $ mov
        # otherwise treat it as labeled                                 $label mov

        code_line = self.process_template(self.node.token.line.string)

        instruction = "$".join(code_line.split("$")[1:])

        if not instruction:
            raise SyntaxError("Assembly node without instruction", self.node.token.line)

        label = None
        cmd = instruction[1:]

        if instruction[0] != " ":
            label = instruction.split(" ")[0]
            cmd = " ".join(instruction.split(" ")[1:])

        self.assemble(cmd, [], mapping=True, label=label)


class AssemblyExpressionTranslator(AssemblyTranslator):

    node_type = AssemblyExpressionNode

    def make(self) -> None:
        self.node: AssemblyExpressionNode

        onebyte = True if (self.node.assembly_expression.startswith("byte[") or
                            self.node.assembly_expression.endswith("h") or
                            self.node.assembly_expression.endswith("l")) else False

        self.assemble("mov", ["al" if onebyte else "ax", self.node.assembly_expression])
        if onebyte:
            self.assemble("mov", ["ah", "0"])
        self.assemble("push", ["ax"])
