from ..parsing import Parser
from ...tokenizer import Token, NameToken, IntegerLiteralToken, MinusToken, PlusToken, MultiplyToken, DivideToken, OpenParenToken
from typing import Type

EXPRESSION_ENDINGS = [NewLineToken, CommaToken]


class AdditiveParser(Parser):

    def parse(self, expect_end: Type[Token] | None = None):
        left = self.multiplicative()

        while self.peek() in ['+', '-']:
            operator = self.consume()
            right = self.multiplicative()
            left = ASTNode(type='binary', value=operator, left=left, right=right)

        return left


class ComparisonParser(Parser):

    def parse(self, expect_end: Type[Token] | None = None):
        left = self.additive()
        
        while self.peek() in ['==', '!=', '>', '<', '>=', '<=']:
            operator = self.consume()
            right = self.additive()
            left = ASTNode(type='comparison', value=operator, left=left, right=right)
        
        return left
        


class ExpressionParser(Parser):

    token = Token.any(NameToken, IntegerLiteralToken)
    
    def parse(self):
        return self.expression()
    
    def expression(self):
        return self.comparison()
    
    def comparison(self):
    
    def additive(self):
        left = self.multiplicative()
        
        while self.peek() in ['+', '-']:
            operator = self.consume()
            right = self.multiplicative()
            left = ASTNode(type='binary', value=operator, left=left, right=right)
        
        return left
    
    def multiplicative(self):
        left = self.unary()
        
        while self.peek() in ['*', '/']:
            operator = self.consume()
            right = self.unary()
            left = ASTNode(type='binary', value=operator, left=left, right=right)
        
        return left
    
    def unary(self):
        if self.peek() in ['!', '-']:
            operator = self.consume()
            operand = self.unary()
            return ASTNode(type='unary', value=operator, right=operand)
        
        return self.primary()
    
    def primary(self):
        token = self.peek()
        
        if is_number_literal(token):
            self.consume()
            return ASTNode(type='literal', value=token)
        
        if is_name(token):
            self.consume()
            if self.peek() == '(':
                self.consume()  # consume '('
                args = []
                
                if self.peek() != ')':
                    args.append(self.expression())
                    while self.peek() == ',':
                        self.consume()  # consume ','
                        args.append(self.expression())
                
                if self.peek() != ')':
                    raise SyntaxError("Expected ')'")
                self.consume()  # consume ')'
                
                return ASTNode(type='call', value=token, left=args)
            return ASTNode(type='variable', value=token)
        
        if token == '(':
            self.consume()  # consume '('
            expr = self.expression()
            
            if self.peek() != ')':
                raise SyntaxError("Expected ')'")
            self.consume()  # consume ')'
            
            return expr
        
        raise SyntaxError(f"Unexpected token: {token}")

    def parse(self, expect_end: Type[Token] | None = None):
        
        if self.will_scan(OpenParenToken):
            self.scan(OpenParenToken)
