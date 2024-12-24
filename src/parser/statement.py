from .parsing import Parser
from ..tokenizer import (Token, NameToken, OpenParenToken, CloseParenToken, TypeToken, IfToken, ForToken, ElseToken,
                         StringLiteralToken, IncludeToken, ModuleToken, AsToken, LogicalNotToken,
                        OpenBraceToken, CloseBraceToken, WhileToken, EqualsToken, AtToken, DefinitionToken, DoToken,
                        ColonToken, DollarToken, AtEqualsToken, ArrayBeginToken, ArrayEndToken, IncrementalToken,
                        BreakToken, ContinueToken, PassToken, CommaToken, NewLineToken, ArrowToken, ReturnToken)
from typing import Type
from .expression import ExpressionParser
from ..nodes.statement import (FunctionCallStatementNode, ASTNode, IfNode, StatementNode, ArgumentDeclarationNode,
                    CodeBlockNode, ForNode, PassNode, ReturnNode, ForNode, ContinueNode, BreakNode, AssemblyNode, IncludeNode,
                    WhileNode, AssignmentNode, VariableDeclarationNode, FunctionDefinitonNode, IncrementalNode, ModuleNode)
from pathlib import Path
from .dependency import Dependency
from .types import TypeParser
from ..errors import SyntaxError, NadLabemError
from ..tokenizer import Tokenizer


class CodeBlockParser(Parser):

    def __init__(self, parent: Parser, force_multiline: bool = False):
        super().__init__(parent)
        self.force_multiline = force_multiline
        self.braced: bool | None = None

    def _multiline_stop(self) -> bool:
        if self.force_multiline:
            return self.is_done
        return self.is_ahead(CloseBraceToken)

    def parse(self) -> CodeBlockNode:
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
            

class ModuleParser(Parser):

    def __init__(self, parent: Parser, started: Token | None = None):
        super().__init__(parent)
        self.started: Token | None = started
    
    def parse(self) -> ModuleNode:

        token = self.started if self.started is not None else self.devour(ModuleToken)

        name_token: NameToken | None = None
        if self.is_ahead(NameToken):
            name_token = self.devour(NameToken)
            parent = self
        else:
            parent = self.parent
        
        body: list[StatementNode] = CodeBlockParser(parent=parent).parse().children

        module_node = ModuleNode(token, name_token, body, parser=self)

        return module_node


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


class IncrementalParser(Parser):

    def parse(self) -> ASTNode:
        token = self.devour(IncrementalToken)
        name_token = self.devour(NameToken)
        return IncrementalNode(token, name_token, parser=self)


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
                raise SyntaxError(f"Declaration of {repr(name_token.string)} by reference must assign a reference", name_token.line)
            self.devour(AtEqualsToken)
            expression = ExpressionParser(parent=self).parse()
            return VariableDeclarationNode(name_token, expression, var_type, parser=self)

        # else
        if not self.is_ahead(EqualsToken):
            raise SyntaxError(f"Declaration of {repr(name_token.string)} by value must assign a value", name_token.line)
    
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


class IncludeParser(Parser):

    def parse(self) -> CodeBlockNode:
        
        if self.config.location is None:
            raise NadLabemError(f"Cannot include from an anonymous program", token.line)

        origin = self.root.current_location

        token = self.devour(IncludeToken)
        path_token = self.devour(StringLiteralToken)
        path_string = path_token.value

        module_path: Path = token.line.location.parent / path_string

        if not module_path.exists() or not module_path.is_file():
            raise NadLabemError(f"Cannot find module {module_path}", path_token.line)

        current_dependency: Dependency = self.root.dependencies[origin]

        if current_dependency.is_upstream(module_path):
            raise NadLabemError(f"Circular include of module {module_path} detected", token.line, suggestion="Keep tree structure when imporing")
        
        if self.is_ahead(LogicalNotToken):  # not as module
            self.devour(LogicalNotToken)
            self.devour(AsToken)
            self.devour(ModuleToken)
            self.config.warn(NadLabemError(f"Direct code includes (not as module) are dangerous", token.line))

            if module_path in self.root.dependencies:
                raise NadLabemError(f"Cannot directly include modularly loaded code from file {module_path}", token.line)

            tokens = Tokenizer(config=self.config, location=module_path).tokenize(
                source_code=module_path.read_text()
            )

            self.root.inject(tokens, next_line=True)
            return PassNode(token, parser=self)


        module_name: NameToken | None = None
        if self.is_ahead(AsToken):
            self.devour(AsToken)
            module_name = self.devour(NameToken)

        if module_path in self.root.dependencies:
            dependency: Dependency = self.root.dependencies[module_path]
            return IncludeNode(token, module_name, dependency.module.context, parser=self)
        
        dependency = Dependency(location=module_path, parent=current_dependency)
        self.root.dependencies[module_path] = dependency

        tokens = [
            OpenBraceToken("<virtual>", token.line),
            NewLineToken("<virtual>", token.line)
        ] + Tokenizer(config=self.config, location=module_path).tokenize(
            source_code=module_path.read_text()
        ) + [
            CloseBraceToken("<virtual>", token.line),
            NewLineToken("<virtual>", token.line)
        ]

        if module_name is not None:
            tokens.insert(0, module_name)

        self.root.inject(tokens, next_line=True)

        self.devour(NewLineToken)
        
        module_node = ModuleParser(parent=self, started=token).parse()

        dependency.module = module_node

        return module_node


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
    DefinitionToken: FunctionDefinitionParser,
    IncrementalToken: IncrementalParser,
    IncludeToken: IncludeParser,
    ModuleToken: ModuleParser
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

