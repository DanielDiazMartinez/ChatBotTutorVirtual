from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import expression
from sqlalchemy.types import UserDefinedType

# Definición del tipo Vector para SQLAlchemy
class Vector(UserDefinedType):
    def __init__(self, dimensions):
        self.dimensions = dimensions

    def get_col_spec(self, **kw):
        return f"vector({self.dimensions})"

    def bind_processor(self, dialect):
        def process(value):
            if value is None:
                return None
            return value
        return process

    def result_processor(self, dialect, coltype):
        def process(value):
            return value
        return process

# Definición de funciones SQL para pgvector
class CosineDistance(expression.FunctionElement):
    type = None
    name = 'cosine_distance'
    inherit_cache = True

@compiles(CosineDistance)
def _compile_cosine_distance(element, compiler, **kw):
    return "%s <=> %s" % (
        compiler.process(element.clauses.clauses[0]),
        compiler.process(element.clauses.clauses[1])
    )

class EuclideanDistance(expression.FunctionElement):
    type = None
    name = 'euclidean_distance'
    inherit_cache = True

@compiles(EuclideanDistance)
def _compile_euclidean_distance(element, compiler, **kw):
    return "%s <-> %s" % (
        compiler.process(element.clauses.clauses[0]),
        compiler.process(element.clauses.clauses[1])
    )

class InnerProduct(expression.FunctionElement):
    type = None
    name = 'inner_product'
    inherit_cache = True

@compiles(InnerProduct)
def _compile_inner_product(element, compiler, **kw):
    return "%s <#> %s" % (
        compiler.process(element.clauses.clauses[0]),
        compiler.process(element.clauses.clauses[1])
    )