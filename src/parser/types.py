from .parsing import Parser
from ..tokenizer import (Token, TypeToken, ArrayToken, StarToken, AmpersandToken)
from typing import Type
from ..nodes.types import TYPES, Int, Char, String, Bool, Void, ValueType
from ..errors import TypeError

#TODO: implement everthing lol
# not used at the moment
# would have to decide on how structured types and syntax would work

class TypeParser(Parser):

    def parse(self) -> ValueType:
        return self.expression()
    
    def expression(self) -> ValueType:
        return self.logical()

    def logical(self) -> ValueType:
        left = self.comparison()
        
        while self.is_ahead(LogicalToken):
            operator = self.devour(LogicalToken)
            right = self.comparison()
            left = LogicalNode(operator, left, right, parser=self)
        
        return left
    
    def primary(self) -> ValueType:

        if self.is_ahead(LiteralToken):
            return LiteralNode(self.devour(LiteralToken), parser=self)

        elif self.is_ahead(ArrayBeginToken):
            begin = self.devour(ArrayBeginToken)
            elements = []

            if not self.is_ahead(ArrayEndToken):

                elements = [self.expression()]

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

            elif self.is_ahead(ArrayBeginToken):
                #index retrieval
                self.devour(ArrayBeginToken)

                index = self.expression()

                self.devour(ArrayEndToken)
                
                return IndexRetrievalNode(name_token, index, parser=self)
            
            return VariableReferenceNode(name_token, parser=self)

        
        elif self.is_ahead(OpenParenToken):
            self.devour(OpenParenToken)  # consume '('
            expr = self.expression()
            
            self.devour(CloseParenToken)
            
            return expr
        
        raise SyntaxError(f"Unexpected end of expression: {self.look_ahead()}", self.look_ahead().line)
