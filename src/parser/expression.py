from .parsing import Parser
from ..tokenizer import (Token, ComparisonToken, LogicalToken, AdditiveToken, MultiplicativeToken,
                        UnaryToken, LiteralToken, NameToken, OpenParenToken, CloseParenToken,
                        ArrayBeginToken, ArrayEndToken, CommaToken, NewLineToken, BinaryToken)
from typing import Type
from ..nodes.expression import (ExpressionNode, ComparisonNode, AdditiveNode, MultiplicativeNode, VariableReferenceNode, LogicalNode, BinaryNode,
                    UnaryOperationNode, LiteralNode, FunctionCallNode, IndexRetrievalNode, ArrayLiteralNode)
from ..errors import SyntaxError


class ExpressionParser(Parser):

    def parse(self) -> ExpressionNode:
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
        
        primary = self.primary()

        while self.is_ahead(ArrayBeginToken):
            #index retrieval
            token = self.devour(ArrayBeginToken)

            index = self.expression()

            self.devour(ArrayEndToken)
            
            primary = IndexRetrievalNode(token, primary, index, parser=self)
        
        return primary
    
    def primary(self) -> ExpressionNode:

        if self.is_ahead(LiteralToken):
            return LiteralNode(self.devour(LiteralToken), parser=self)

        elif self.is_ahead(ArrayBeginToken):
            begin = self.devour(ArrayBeginToken)
            elements: list[ExpressionNode] = []

            if not self.is_ahead(ArrayEndToken):

                elements.append(self.expression())

                while self.is_ahead(CommaToken):
                    self.devour(CommaToken)
                    elements.append(self.expression())

                self.devour(ArrayEndToken)

            return ArrayLiteralNode(begin, elements, parser=self)

        
        elif self.is_ahead(NameToken):
            name_token = self.devour(NameToken)

            if self.is_ahead(OpenParenToken):
                #function call
                self.devour(OpenParenToken)
                arguments = []
                
                if not self.is_ahead(CloseParenToken):
                    arguments.append(self.expression())
                    while self.is_ahead(CommaToken):
                        self.devour(CommaToken)  # consume ','
                        arguments.append(self.expression())
                
                self.devour(CloseParenToken)

                return FunctionCallNode(name_token, arguments, parser=self)
            
            return VariableReferenceNode(name_token, parser=self)

        
        elif self.is_ahead(OpenParenToken):
            self.devour(OpenParenToken)  # consume '('
            expr = self.expression()
            
            self.devour(CloseParenToken)
            
            return expr
        
        raise SyntaxError(f"Unexpected end of expression: {self.look_ahead()}", self.look_ahead().line)
