from .program import ProgramTranslator
from ..translator import Translator, Assembly
from ..nodes.node import AbstractSyntaxTreeNode as ASTNode
from ..nodes.expression import LiteralNode, StringReferenceNode
from .sizeof import sizeof
from ..errors import NotImplementedError, NadLabemError
from ..tokenizer.symbols import StringLiteralToken, NumberToken, BoolLiteralToken, CharLiteralToken
from .allocator import Variable, StackFrame
from .program import ProgramI8086Translator


class LiteralTranslator(Translator):

    node_type = LiteralNode

    def make(self) -> None:
        self.node: LiteralNode

        register = "ax"

        if NumberToken.match(self.node.token):
            self.assemble("mov", [register, self.node.token.value])

        elif StringLiteralToken.match(self.node.token):
            raise NotImplementedError("String literals are not supported as part of an expression in i8086.", self.node.token.line)

        elif CharLiteralToken.match(self.node.token):
            self.assemble("mov", [register, self.node.token.value])

        elif BoolLiteralToken.match(self.node.token):
            self.assemble("mov", [register, "1" if self.node.token.value else "0"])

        self.assemble("push", ["ax"])



class StringReferenceTranslator(Translator):

    node_type = StringReferenceNode

    def make(self) -> None:
        self.node: StringReferenceNode

        str_bytes = self.node.string_literal.bytes
        vals = self.assembly_string(self.node.string_literal)

        literal_label = self.node.scope.generate_id("_str")

        declaration = [
            Assembly(self.config, "db", vals, label=literal_label)
        ]

        self.assemble("lea", ["ax", f"[{literal_label}]"])
        self.assemble("push", ["ax"])

        self.program: ProgramI8086Translator
        self.program.declare(declaration)

    @staticmethod
    def assembly_string(string_token: StringLiteralToken) -> list[str]:

        result: list[str] = []
        current_string = ""
        
        for byte in string_token.bytes:
            # Check if the byte is a printable ASCII character
            if 32 <= byte <= 126:
                current_string += chr(byte)
            else:
                # If there's a current string, add it to the result
                if current_string:
                    result.append(f'"{current_string}"')
                    current_string = ""
                
                # Add the non-printable byte as a number
                result.append(str(byte))
        
        # Add any remaining string
        if current_string:
            result.append(f'"{current_string}"')
        
        return result