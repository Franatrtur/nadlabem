from .parsing import Parser
from ..tokenizer import (Token, NameToken, OpenParenToken, CloseParenToken, TypeToken, IfToken,
                        OpenBraceToken, CloseBraceToken,
                        StatementBeginToken, CommaToken, NewLineToken, BinaryToken)
from typing import Type
from .expression import ExpressionParser
from .nodes import (FunctionCallNode, AbstractSyntaxTreeNode as ASTNode, IfNode, StatementNode)
from ..errors import SyntaxError


class CodeBlockParser(Parser):

    def __init__(self, parent: Parser, force_multiline: bool = False):
        super().__init__(parent)
        self.force_multiline = force_multiline

    def _multiline_stop(self) -> bool:
        if self.force_multiline:
            return self.is_done
        return self.is_ahead(CloseBraceToken)

    def parse(self) -> StatementNode:
        if not self.force_multiline and not self.is_ahead(OpenBraceToken):
            return StatementParser(self).parse()

        statements: list[StatementNode] = []
        self.braced: bool = self.is_ahead(OpenBraceToken)
        
        if self.braced:
            self.devour(OpenBraceToken)
        
        while not self._multiline_stop():
            self.devour(NewLineToken)
            statement = StatementParser(self).parse()
            statements.append(statement)

        if self.braced:
            self.devour(CloseBraceToken)

        return CodeBlockNode(statements, parser=self)
            

class IfParser(Parser):

    def parse(self) -> IfNode:
        self.devour(IfToken)
        self.devour(OpenParenToken)
        condition = ExpressionParser(self).parse()
        self.devour(CloseParenToken)
        body = CodeBlockParser(self).parse()
        return IfNode(condition, body, parser=self)



class StatementParser(Parser):

    def parse(self) -> StatementNode:
        if not self.is_ahead(StatementBeginToken):
            actual = self.look_ahead()
            raise SyntaxError(f"Expected a statement, but found {actual} instead", actual.line)


STATEMENTS: dict[Type[Token], Type[StatementParser]] = {
    IfToken: IfParser
}

        


