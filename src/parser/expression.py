from .parsing import Parser
from ..tokenizer import (Token, ComparisonToken, LogicalToken, AdditiveToken, MultiplicativeToken, StringLiteralToken,
                        UnaryToken, LiteralToken, NameToken, OpenParenToken, CloseParenToken, DollarToken, AtToken, BinaryXorToken,
                        ArrayBeginToken, ArrayEndToken, CommaToken, NewLineToken, BinaryToken, TypeToken, StarToken)
from typing import Type
from ..nodes.expression import (ExpressionNode, ComparisonNode, AdditiveNode, MultiplicativeNode, CastNode,
                                VariableReferenceNode, LogicalNode, BinaryNode, UnaryOperationNode, StringReferenceNode,
                                LiteralNode, FunctionCallNode, ArrayLiteralNode, AssemblyExpressionNode)
from .types import TypeParser
from ..errors import SyntaxError


class ExpressionParser(Parser):

    def parse(self) -> ExpressionNode:
        return self.array()

    def array(self) -> ExpressionNode:
        
        if self.is_ahead(ArrayBeginToken):
            begin = self.devour(ArrayBeginToken)
            elements: list[ExpressionNode] = []

            if not self.is_ahead(ArrayEndToken):

                elements.append(self.expression())

                while self.is_ahead(CommaToken):
                    self.devour(CommaToken)
                    elements.append(self.expression())

            self.devour(ArrayEndToken)

            return ArrayLiteralNode(begin, elements, parser=self)
        
        else:
            return self.expression()
    
    def expression(self) -> ExpressionNode:
        return self.logical()

    def logical(self) -> ExpressionNode:
        left = self.comparison()
        
        while self.is_ahead(LogicalToken):
            operator = self.devour(LogicalToken)
            right = self.comparison()
            left = LogicalNode(operator, left, right, parser=self)
        
        return left
    
    def comparison(self) -> ExpressionNode:
        left = self.binary()
        
        while self.is_ahead(ComparisonToken):
            operator = self.devour(ComparisonToken)
            right = self.binary()
            left = ComparisonNode(operator, left, right, parser=self)

        return left

    def binary(self) -> ExpressionNode:
        left = self.additive()
        
        while self.is_ahead(BinaryToken):
            operator = self.devour(BinaryToken)
            right = self.additive()
            left = BinaryNode(operator, left, right, parser=self)
        
        return left

    def additive(self) -> ExpressionNode:
        left = self.multiplicative()
        
        while self.is_ahead(AdditiveToken):
            operator = self.devour(AdditiveToken)
            right = self.multiplicative()
            left = AdditiveNode(operator, left, right, parser=self)
        
        return left
    
    def multiplicative(self) -> ExpressionNode:
        left = self.unary()
        
        while self.is_ahead(MultiplicativeToken):
            operator = self.devour(MultiplicativeToken)
            right = self.unary()
            left = MultiplicativeNode(operator, left, right, parser=self)
        
        return left
    
    def unary(self) -> ExpressionNode:
        if self.is_ahead(UnaryToken):
            operator = self.devour(UnaryToken)
            operand = self.unary()
            return UnaryOperationNode(operator, operand, parser=self)
        
        return self.primary()
    
    def primary(self) -> ExpressionNode:

        if self.is_ahead(DollarToken):
            token = self.devour(DollarToken)
            if self.is_ahead(NameToken):
                name_str = self.devour(NameToken).string
            elif self.is_ahead(StringLiteralToken):
                name_str = self.devour(StringLiteralToken).value
            else:
                raise SyntaxError(f"Invalid assembly expression: {self.look_ahead()}", self.look_ahead().line, suggestion="Put the assembly expression in string quotes?")

            return AssemblyExpressionNode(token, name_str, parser=self)

        if self.is_ahead(LiteralToken):
            return LiteralNode(self.devour(LiteralToken), parser=self)
        
        elif self.is_ahead(Token.any(NameToken, StarToken, AtToken)):

            pointer: bool = False
            dereference: bool = False

            if self.is_ahead(StarToken):
                token = self.devour(StarToken)
                
                if self.is_ahead(StringLiteralToken):
                    str_token = self.devour(StringLiteralToken)
                    return StringReferenceNode(token, str_token, parser=self)

                pointer = True

            elif self.is_ahead(AtToken):
                token = self.devour(AtToken)
                dereference = True

            name_token = self.devour(NameToken)

            if self.is_ahead(OpenParenToken):
                #function call
                self.devour(OpenParenToken)
                arguments = []

                if pointer or dereference:
                    raise SyntaxError("Cannot use pointer or dereference with function calls", name_token.line)
                
                if not self.is_ahead(CloseParenToken):
                    arguments.append(self.expression())
                    while self.is_ahead(CommaToken):
                        self.devour(CommaToken)  # consume ','
                        arguments.append(self.expression())

                self.devour(CloseParenToken)

                return FunctionCallNode(name_token, arguments, parser=self)

            # if, not while, we only allow one dimensional arrays
            if self.is_ahead(ArrayBeginToken):
                #index retrieval
                token = self.devour(ArrayBeginToken)

                index = self.expression()

                self.devour(ArrayEndToken)

                return VariableReferenceNode(name_token, pointer, dereference, index, parser=self)
            
            return VariableReferenceNode(name_token, pointer, dereference, index=None, parser=self)

        
        elif self.is_ahead(TypeToken):
            token = self.look_ahead()
            value_type = TypeParser(parent=self).value_type()
            signed: bool = False
            if self.is_ahead(BinaryXorToken):
                self.devour(BinaryXorToken)
                signed = True
            expr = self.primary()
            return CastNode(token, value_type, expr, signed, parser=self)

        
        elif self.is_ahead(OpenParenToken):
            self.devour(OpenParenToken)  # consume '('
            expr = self.expression()
            
            self.devour(CloseParenToken)
            
            return expr
        
        raise SyntaxError(f"Unexpected end of expression: {self.look_ahead()}", self.look_ahead().line)
