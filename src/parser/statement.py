from .parsing import Parser
from ..tokenizer import (Token, NameToken, OpenParenToken, CloseParenToken, TypeToken, IfToken, ForToken, ElseToken,
                        OpenBraceToken, CloseBraceToken, WhileToken, EqualsToken, AtToken, DefinitionToken, DoToken,
                        ColonToken, DollarToken, AtEqualsToken, ArrayBeginToken, ArrayEndToken,
                        ReturnToken, BreakToken, ContinueToken, PassToken, CommaToken, NewLineToken, BinaryToken, ArrowToken)
from typing import Type
from .expression import ExpressionParser
from ..nodes.statement import (FunctionCallStatementNode, ASTNode, IfNode, StatementNode, ArgumentDeclarationNode,
                    CodeBlockNode, ForNode, PassNode, ReturnNode, ForNode, ContinueNode, BreakNode, AssemblyNode,
                    WhileNode, AssignmentNode, VariableDeclarationNode, FunctionDefinitonNode)

from .types import TypeParser
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
        token = self.devour(IfToken)

        self.devour(OpenParenToken)
        condition = ExpressionParser(parent=self).parse()
        self.devour(CloseParenToken)
        body = CodeBlockParser(parent=self).parse()

        if not self.is_ahead(ElseToken):
            return IfNode(token, condition, body, else_body=None, parser=self)

        self.devour(ElseToken)
        else_body = CodeBlockParser(parent=self).parse()
        return IfNode(token, condition, body, else_body, parser=self)


class WhileParser(Parser):

    def _condition(self) -> None:
        self.devour(OpenParenToken)
        condition = ExpressionParser(parent=self).parse()
        self.devour(CloseParenToken)
        return condition

    def parse(self) -> WhileNode:
        if self.is_ahead(WhileToken):
            token = self.devour(WhileToken)
            condition = self._condition()
            body = CodeBlockParser(parent=self).parse()
        else:
            token = self.devour(DoToken)
            body = CodeBlockParser(parent=self).parse()
            self.devour(WhileToken)
            condition = self._condition()
        return WhileNode(token, condition, body, parser=self)


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

    def parse(self) -> ASTNode:
        name_token = self.devour(NameToken)
        
        if self.is_ahead(OpenParenToken):       # f(...)
            return self.parse_function_call(name_token)
        
        elif self.is_ahead(Token.any(ArrayBeginToken, EqualsToken, AtEqualsToken)): # f =, f =@=, f[i] =, f[x] =@= 
            return self.parse_assignment(name_token)
        
        elif self.is_ahead(ColonToken):         # f: int = , f: @bool =@=
            return self.parse_declaration(name_token)

        else:
            raise SyntaxError(f"Invalid assignment, unexpected name {repr(name_token.string)}", name_token.line)
    
    def parse_assignment(self, name_token: NameToken) -> AssignmentNode:
        index = None
        if self.is_ahead(ArrayBeginToken):
            self.devour(ArrayBeginToken)
            index = ExpressionParser(parent=self).parse()
            self.devour(ArrayEndToken)
        by_reference = self.is_ahead(AtEqualsToken)
        self.devour(Token)
        expression = ExpressionParser(parent=self).parse()
        return AssignmentNode(name_token, expression, index, by_reference=by_reference, parser=self)

    def parse_function_call(self, name_token: NameToken) -> FunctionCallStatementNode:
        self.devour(OpenParenToken)
        args = []
        if not self.is_ahead(CloseParenToken):
            args.append(ExpressionParser(parent=self).parse())
            while self.is_ahead(CommaToken):
                self.devour(CommaToken)
                args.append(ExpressionParser(parent=self).parse())
        self.devour(CloseParenToken)
        return FunctionCallStatementNode(name_token, args, parser=self)

    def parse_declaration(self, name_token: NameToken) -> VariableDeclarationNode:
        self.devour(ColonToken)
        var_type = TypeParser(parent=self).variable_type()

        if var_type.is_reference:
            if not self.is_ahead(AtEqualsToken):
                raise SyntaxError(f"Declaration of \"{name_token.string}\" by reference must assign a reference", name_token.line)
            self.devour(AtEqualsToken)
            expression = ExpressionParser(parent=self).parse()
            return VariableDeclarationNode(name_token, expression, var_type, parser=self)

        # else
        if not self.is_ahead(EqualsToken):
            raise SyntaxError(f"Declaration of \"{name_token.string}\" by value must assign a value", name_token.line)
    
        self.devour(EqualsToken)
        expression = ExpressionParser(parent=self).parse()
        return VariableDeclarationNode(name_token, expression, var_type, parser=self)


class FunctionDefinitionParser(Parser):

    def _parse_param(self) -> ArgumentDeclarationNode:
        name_token = self.devour(NameToken)
        self.devour(ColonToken)
        val_type = TypeParser(parent=self).variable_type()
        return ArgumentDeclarationNode(name_token, val_type, parser=self)

    def parse(self) -> FunctionDefinitonNode:
        self.devour(DefinitionToken)
        fn_name_token = self.devour(NameToken)

        self.devour(OpenParenToken)
        params: list[ArgumentDeclarationNode] = []
            
        if not self.is_ahead(CloseParenToken):
            params.append(self._parse_param())
            while self.is_ahead(CommaToken):
                self.devour(CommaToken)
                params.append(self._parse_param())
        
        self.devour(CloseParenToken)
        self.devour(ArrowToken)

        return_type = TypeParser(parent=self).return_type()

        body = CodeBlockParser(parent=self).parse()
        return FunctionDefinitonNode(fn_name_token, params, body, return_type, parser=self)


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
        tok = self.devour(DollarToken)
        code: list[Token] = []
        while not self.is_ahead(NewLineToken):
            code.append(self.devour(Token))
        return AssemblyNode(tok, code, parser=self)


STATEMENTS: dict[Type[Token], Type[Parser]] = {
    OpenBraceToken: CodeBlockParser,
    IfToken: IfParser,
    WhileToken: WhileParser,
    DoToken: WhileParser,
    ForToken: ForParser,
    NameToken: AssignmentParser,
    ReturnToken: ReturnParser,
    ContinueToken: ContinueParser,
    BreakToken: BreakParser,
    PassToken: PassParser,
    DollarToken: AssemblyParser,
    DefinitionToken: FunctionDefinitionParser
}

class StatementParser(Parser):

    def parse(self) -> StatementNode:
        if self.is_done:
            raise SyntaxError("Unexpected end of input, expected a statement after the statement", self.root.tokens[-1].line)
        
        if not self.is_ahead(Token.any(*STATEMENTS.keys())):
            actual = self.look_ahead()
            raise SyntaxError(f"Expected a statement, but found {actual} instead", actual.line)
        
        parser_class: Type[Parser] = None
        for token_class, parser_class in STATEMENTS.items():
            if self.is_ahead(token_class):
                break
        
        parser = parser_class(parent=self)
        return parser.parse()

