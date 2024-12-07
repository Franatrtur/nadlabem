# I8086 - SPECIFIC CONSTANTS

from ..nodes.types import Int, Char, Bool, Void, Array, ExpressionType, VariableType, Pointer, Double
from typing import Type

#size in bytes for i8086
SIZE: dict[Type[ExpressionType], int] = {
    Int: 2,
    Char: 1,
    Bool: 1,
    Void: 0,
    Double: 4
}

def sizeof(node_type: ExpressionType | VariableType) -> int:
    """
    Calculate the size in bytes for a given expression type.
    
    Args:
        node_type (ExpressionType): The type to calculate size for
    
    Returns:
        int: Size of the type in bytes
    """

    if isinstance(node_type, VariableType):
        if node_type.is_reference:
            return sizeof(Int)

        return sizeof(node_type.expression_type)
    
    if isinstance(node_type, Pointer):
        return sizeof(Int)

    # Handle basic value types
    if node_type in SIZE:
        return SIZE[node_type]
    
    # Handle array types
    if isinstance(node_type, Array):
        # If size is not defined, raise an error
        if node_type.size is None:
            raise ValueError(f"Array size is not defined for type: {node_type}")
        
        # Recursively calculate size of element type and multiply by array size
        element_size = sizeof(node_type.element_type)
        return element_size * node_type.size
    
    # If type is not recognized, return 0
    return 0