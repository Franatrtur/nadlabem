from .parsing import Parser
from ..tokenizer import (Token, ComparisonToken, LogicalToken, AdditiveToken, MultiplicativeToken,
                        UnaryToken, LiteralToken, NameToken, OpenParenToken, CloseParenToken,
                        ArrayBeginToken, ArrayEndToken, CommaToken, NewLineToken)
from typing import Type
from .nodes import (ComparisonNode, AdditiveNode, MultiplicativeNode, VariableReferenceNode,
                    UnaryOperationNode, LiteralNode, FunctionCallNode, IndexRetrievalNode, AbstractSyntaxTreeNode)
from ..errors import SyntaxError


class ExpressionParser(Parser):
    
    def parse(self) -> AbstractSyntaxTreeNode:
        self.nested: bool = False
        return self.comparison()
    
    def expression(self) -> AbstractSyntaxTreeNode:
        self.nested: bool = True
        return self.comparison()
        self.nested = False

    def eat(self, token_type: Type[Token]) -> Token:
        return super().eat(token_type, skip_newline=self.nested)
    def is_ahead(self, token_type: Type[Token]) -> bool:
        return super().is_ahead(token_type, skip_newline=self.nested)
    
    def comparison(self) -> AbstractSyntaxTreeNode:
        left = self.additive()
        
        while self.is_ahead(ComparisonToken):
            operator = self.eat(ComparisonToken)
            right = self.additive()
            left = ComparisonNode(operator, left, right, parser=self)
        
        return left

    def additive(self) -> AbstractSyntaxTreeNode:
        left = self.multiplicative()
        
        while self.is_ahead(AdditiveToken):
            operator = self.eat(AdditiveToken)
            right = self.multiplicative()
            left = AdditiveNode(operator, left, right, parser=self)
        
        return left
    
    def multiplicative(self) -> AbstractSyntaxTreeNode:
        left = self.unary()
        
        while self.is_ahead(MultiplicativeToken):
            operator = self.eat(MultiplicativeToken)
            right = self.unary()
            left = MultiplicativeNode(operator, left, right, parser=self)
        
        return left
    
    def unary(self) -> AbstractSyntaxTreeNode:
        if self.is_ahead(UnaryToken):
            operator = self.eat(UnaryToken)
            operand = self.unary()
            return UnaryOperationNode(operator, operand, parser=self)
        
        return self.primary()
    
    def primary(self) -> AbstractSyntaxTreeNode:

        if self.is_ahead(LiteralToken):
            return LiteralNode(self.eat(LiteralToken), parser=self)
        
        elif self.is_ahead(NameToken):
            name_token = self.eat(NameToken)

            if self.is_ahead(OpenParenToken):
                #function call
                self.eat(OpenParenToken)
                arguments = []
                
                if not self.is_ahead(CloseParenToken):
                    arguments.append(self.expression())
                    while self.is_ahead(CommaToken):
                        self.eat(CommaToken)  # consume ','
                        arguments.append(self.expression())
                
                self.eat(CloseParenToken)

                return FunctionCallNode(name_token, arguments, parser=self)

            elif self.is_ahead(ArrayBeginToken):
                #index retrieval
                self.eat(ArrayBeginToken)

                index = self.expression()

                self.eat(ArrayEndToken)
                
                return IndexRetrievalNode(name_token, index, parser=self)
            
            return VariableReferenceNode(name_token, parser=self)

        
        elif self.is_ahead(OpenParenToken):
            self.eat(OpenParenToken)  # consume '('
            expr = self.expression()
            
            self.eat(CloseParenToken)
            
            return expr
        
        raise SyntaxError(f"Unexpected end of expression: {self.look_ahead()}", self.look_ahead().line)
