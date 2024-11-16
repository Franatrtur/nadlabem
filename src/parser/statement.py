from .parsing import Parser
from ..tokenizer import (Token, NameToken, OpenParenToken, CloseParenToken, TypeToken, IfToken, ForToken, ElseToken,
                        OpenBraceToken, CloseBraceToken, WhileToken, EqualsToken, HashToken,
                        ReturnToken, BreakToken, ContinueToken, PassToken, CommaToken, NewLineToken, BinaryToken)
from typing import Type
from .expression import ExpressionParser
from ..nodes.statement import (FunctionCallStatementNode, ASTNode, IfNode, StatementNode, ArgumentDeclarationNode,
                    CodeBlockNode, ForNode, PassNode, ReturnNode, ForNode, ContinueNode, BreakNode, AssemblyNode,
                    WhileNode, AssignmentNode, VariableDeclarationNode, FunctionDeclarationNode)

from ..nodes.types import TYPES
from ..errors import SyntaxError


class CodeBlockParser(Parser):

    def __init__(self, parent: Parser, force_multiline: bool = False):
        super().__init__(parent)
        self.force_multiline = force_multiline
        self.braced: bool | None = None

    def _multiline_stop(self) -> bool:
        if self.force_multiline:
            return self.is_done
        return self.is_ahead(CloseBraceToken)

    def parse(self) -> StatementNode:
        if not self.force_multiline and not self.is_ahead(OpenBraceToken):
            statement = StatementParser(self).parse()
            return CodeBlockNode(statement.token, [statement], parser=self)

        statements: list[StatementNode] = []
        self.braced = self.is_ahead(OpenBraceToken) and not self.force_multiline
        
        if self.braced:
            self.devour(OpenBraceToken)
            #TODO: add an optional name token here to name nested loops
            self.devour(NewLineToken)
        
        while not self._multiline_stop():
            statement = StatementParser(parent=self).parse()
            statements.append(statement)
            self.devour(NewLineToken)

        if self.braced:
            self.devour(CloseBraceToken)

        start_token = statements[0].token if statements else None
        return CodeBlockNode(start_token, statements, parser=self)
            

class IfParser(Parser):

    def parse(self) -> IfNode:
        self.devour(IfToken)

        self.devour(OpenParenToken)
        condition = ExpressionParser(parent=self).parse()
        self.devour(CloseParenToken)
        body = CodeBlockParser(parent=self).parse()

        if not self.is_ahead(ElseToken):
            return IfNode(condition, body, parser=self)

        self.devour(ElseToken)
        else_body = CodeBlockParser(parent=self).parse()
        return IfNode(condition, body, else_body, parser=self)


class WhileParser(Parser):

    def parse(self) -> WhileNode:
        self.devour(WhileToken)
        self.devour(OpenParenToken)
        condition = ExpressionParser(parent=self).parse()
        self.devour(CloseParenToken)
        body = CodeBlockParser(parent=self).parse()
        return WhileNode(condition, body, parser=self)


class ForParser(Parser):

    def parse(self) -> ForNode:
        tok = self.devour(ForToken)
        self.devour(OpenParenToken)
        initialization = StatementParser(parent=self).parse()
        self.devour(CommaToken)
        condition = ExpressionParser(parent=self).parse()
        self.devour(CommaToken)
        update = StatementParser(parent=self).parse()
        self.devour(CloseParenToken)
        body = CodeBlockParser(parent=self).parse()
        return ForNode(tok, initialization, condition, update, body, parser=self)


class AssignmentParser(Parser):

    def parse(self) -> AssignmentNode:
        name_token = self.devour(NameToken)
        
        if self.is_ahead(OpenParenToken):
            #function call
            self.devour(OpenParenToken)
            args = []
            if not self.is_ahead(CloseParenToken):
                args.append(ExpressionParser(parent=self).parse())
                while self.is_ahead(CommaToken):
                    self.devour(CommaToken)
                    args.append(ExpressionParser(parent=self).parse())
            self.devour(CloseParenToken)
            return FunctionCallStatementNode(name_token, args, parser=self)
        
        self.devour(EqualsToken)
        expression = ExpressionParser(parent=self).parse()
        return AssignmentNode(name_token, expression, parser=self)


class DeclarationParser(Parser):

    def _parse_param(self) -> ArgumentDeclarationNode:
        type_token = self.devour(TypeToken)
        name_token = self.devour(NameToken)
        return ArgumentDeclarationNode(type_token, name_token, parser=self)

    def parse(self) -> VariableDeclarationNode | FunctionDeclarationNode:
        type_token = self.devour(TypeToken)
        name_token = self.devour(NameToken)
        
        if self.is_ahead(EqualsToken):
            self.devour(EqualsToken)
            expression = ExpressionParser(parent=self).parse()
            return VariableDeclarationNode(name_token, expression, type_token, parser=self)

        elif self.is_ahead(OpenParenToken):
            self.devour(OpenParenToken)
            params: list[ArgumentDeclarationNode] = []
                
            if not self.is_ahead(CloseParenToken):
                params.append(self._parse_param())
                while self.is_ahead(CommaToken):
                    self.devour(CommaToken)
                    params.append(self._parse_param())
            
            self.devour(CloseParenToken)
            body = CodeBlockParser(parent=self).parse()
            return FunctionDeclarationNode(name_token, params, body, type_token, parser=self)

        else:
            raise SyntaxError("Declaration must assign a value or function", name_token.line)


class ReturnParser(Parser):

    def parse(self) -> ReturnNode:
        token = self.devour(ReturnToken)
        expression = None
        if not self.is_ahead(NewLineToken):
            expression = ExpressionParser(parent=self).parse()
        return ReturnNode(token, expression, parser=self)


class ContinueParser(Parser):
    def parse(self) -> ContinueNode:
        return ContinueNode(self.devour(ContinueToken), parser=self)

class BreakParser(Parser):
    def parse(self) -> BreakNode:
        return BreakNode(self.devour(BreakToken), parser=self)

class PassParser(Parser):
    def parse(self) -> PassNode:
        return PassNode(self.devour(PassToken), parser=self)

class AssemblyParser(Parser):
    def parse(self) -> AssemblyNode:
        tok = self.devour(HashToken)
        code: list[Token] = []
        while not self.is_ahead(NewLineToken):
            code.append(self.devour(Token))
        return AssemblyNode(tok, code, parser=self)


STATEMENTS: dict[Type[Token], Type[Parser]] = {
    OpenBraceToken: CodeBlockParser,
    IfToken: IfParser,
    WhileToken: WhileParser,
    NameToken: AssignmentParser,
    TypeToken: DeclarationParser,
    ReturnToken: ReturnParser,
    ContinueToken: ContinueParser,
    BreakToken: BreakParser,
    PassToken: PassParser,
    HashToken: AssemblyParser,
}

class StatementParser(Parser):

    def parse(self) -> StatementNode:
        if not self.is_ahead(Token.any(*STATEMENTS.keys())):
            actual = self.look_ahead()
            raise SyntaxError(f"Expected a statement, but found {actual} instead", actual.line)
        
        parser_class: Type[Parser] = None
        for token_class, parser_class in STATEMENTS.items():
            if self.is_ahead(token_class):
                break
        
        parser = parser_class(parent=self)
        return parser.parse()

