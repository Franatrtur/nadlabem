# I8086 - SPECIFIC CONSTANTS

from ..nodes.types import Int, Char, Bool, Void, Array, ExpressionType

#size in bytes for i8086
SIZE: dict[Type[ExpressionType], int] = {
    Int: 2,
    Char: 1,
    Bool: 1,
    Void: 0,
}

def sizeof(expr_type: ExpressionType) -> int:
    """
    Calculate the size in bytes for a given expression type.
    
    Args:
        expr_type (ExpressionType): The type to calculate size for
    
    Returns:
        int: Size of the type in bytes
    """
    # Handle basic value types
    if expr_type in SIZE:
        return SIZE[expr_type]
    
    # Handle array types
    if isinstance(expr_type, Array):
        # If size is not defined, raise an error
        if expr_type.size is None:
            raise ValueError(f"Array size is not defined for type: {expr_type}")
        
        # Recursively calculate size of element type and multiply by array size
        element_size = sizeof(expr_type.element_type)
        return element_size * expr_type.size
    
    # If type is not recognized, return 0
    return 0