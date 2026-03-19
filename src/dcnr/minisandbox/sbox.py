import ast
import operator
from dataclasses import dataclass


class SandboxError(Exception):
    pass


class SandboxSyntaxError(SandboxError):
    pass


class SandboxRuntimeError(SandboxError):
    pass


class _BreakSignal(Exception):
    pass


class _ContinueSignal(Exception):
    pass


@dataclass
class _ReturnValue:
    value: object


class _SandboxInterpreter:
    def __init__(self, variables: dict | None = None):
        self.env = dict(variables or {})
        self.allowed_functions = {
            "abs": abs,
            "min": min,
            "max": max,
            "sum": sum,
            "len": len,
            "range": range,
            "int": int,
            "float": float,
            "str": str,
            "bool": bool,
            "list": list,
            "tuple": tuple,
            "dict": dict,
            "set": set,
            "sorted": sorted,
        }

        self.bin_ops = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.FloorDiv: operator.floordiv,
            ast.Mod: operator.mod,
            ast.Pow: operator.pow,
        }

        self.unary_ops = {
            ast.UAdd: operator.pos,
            ast.USub: operator.neg,
            ast.Not: operator.not_,
        }

        self.compare_ops = {
            ast.Eq: operator.eq,
            ast.NotEq: operator.ne,
            ast.Lt: operator.lt,
            ast.LtE: operator.le,
            ast.Gt: operator.gt,
            ast.GtE: operator.ge,
            ast.In: lambda a, b: a in b,
            ast.NotIn: lambda a, b: a not in b,
            ast.Is: operator.is_,
            ast.IsNot: operator.is_not,
        }

    def execute(self, code: str) -> dict:
        try:
            tree = ast.parse(code, mode="exec")
        except SyntaxError as exc:
            raise SandboxSyntaxError(str(exc)) from exc

        self._validate_tree(tree)
        self._exec_block(tree.body)
        return self.env

    def _validate_tree(self, tree: ast.AST) -> None:
        allowed_nodes = (
            ast.Module,
            ast.Expr,
            ast.Assign,
            ast.AugAssign,
            ast.Name,
            ast.Load,
            ast.Store,
            ast.Constant,
            ast.List,
            ast.Tuple,
            ast.Dict,
            ast.Set,
            ast.BinOp,
            ast.UnaryOp,
            ast.BoolOp,
            ast.Compare,
            ast.Subscript,
            ast.Slice,
            ast.If,
            ast.While,
            ast.For,
            ast.Break,
            ast.Continue,
            ast.Call,
            ast.keyword,
            ast.Pass,
            ast.Attribute,
        )

        allowed_binops = tuple(self.bin_ops.keys())
        allowed_unaryops = tuple(self.unary_ops.keys())
        allowed_boolops = (ast.And, ast.Or)
        allowed_cmpops = tuple(self.compare_ops.keys())

        for node in ast.walk(tree):
            if isinstance(node, ast.stmt | ast.expr | ast.slice | ast.boolop | ast.operator | ast.unaryop | ast.cmpop):
                pass

            if isinstance(node, ast.Attribute):
                self._validate_attribute_access(node)

            if isinstance(node, (ast.Import, ast.ImportFrom)):
                raise SandboxSyntaxError("Import is not allowed")

            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
                raise SandboxSyntaxError("Function/class definitions are not allowed")

            if isinstance(node, (ast.Try, ast.With, ast.AsyncWith, ast.Raise)):
                raise SandboxSyntaxError("Exception handling is not allowed")

            if isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
                raise SandboxSyntaxError("Comprehensions are not allowed")

            if isinstance(node, (ast.Delete, ast.NamedExpr, ast.Global, ast.Nonlocal, ast.Yield, ast.YieldFrom, ast.Await)):
                raise SandboxSyntaxError(f"{type(node).__name__} is not allowed")

            if isinstance(node, ast.BinOp) and not isinstance(node.op, allowed_binops):
                raise SandboxSyntaxError(f"Operator {type(node.op).__name__} is not allowed")

            if isinstance(node, ast.UnaryOp) and not isinstance(node.op, allowed_unaryops):
                raise SandboxSyntaxError(f"Unary operator {type(node.op).__name__} is not allowed")

            if isinstance(node, ast.BoolOp) and not isinstance(node.op, allowed_boolops):
                raise SandboxSyntaxError(f"Boolean operator {type(node.op).__name__} is not allowed")

            if isinstance(node, ast.Compare):
                for op in node.ops:
                    if not isinstance(op, allowed_cmpops):
                        raise SandboxSyntaxError(f"Comparison operator {type(op).__name__} is not allowed")

            base_ok = isinstance(node, allowed_nodes)
            extra_ok = isinstance(
                node,
                (
                    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow,
                    ast.UAdd, ast.USub, ast.Not,
                    ast.And, ast.Or,
                    ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE,
                    ast.In, ast.NotIn, ast.Is, ast.IsNot,
                ),
            )
            if not (base_ok or extra_ok):
                raise SandboxSyntaxError(f"Node {type(node).__name__} is not allowed")

    def _validate_attribute_access(self, node: ast.Attribute) -> None:
        """Validate that attribute access is safe."""
        # List of dangerous attributes that should never be accessed
        dangerous_attrs = {
            '__class__', '__dict__', '__doc__', '__module__', '__weakref__',
            '__getattr__', '__getattribute__', '__setattr__', '__delattr__',
            '__init__', '__new__', '__reduce__', '__reduce_ex__', '__sizeof__',
            '__subclasshook__', '__import__', '__builtins__', '__globals__',
            '__locals__', '__code__', '__func__', '__self__', '__qualname__',
            '__annotations__', '__closure__', '__defaults__', '__kwdefaults__'
        }
        
        if node.attr in dangerous_attrs:
            raise SandboxSyntaxError(f"Attribute '{node.attr}' is not allowed for security reasons")
        
        # Don't allow attributes starting with underscore (except specific safe ones)
        if node.attr.startswith('_') and node.attr not in {'__len__', '__str__', '__repr__'}:
            raise SandboxSyntaxError(f"Attribute '{node.attr}' starting with underscore is not allowed")

    def _exec_block(self, statements: list[ast.stmt]) -> None:
        for stmt in statements:
            self._exec_stmt(stmt)

    def _exec_stmt(self, stmt: ast.stmt) -> None:
        if isinstance(stmt, ast.Expr):
            self._eval_expr(stmt.value)
            return

        if isinstance(stmt, ast.Assign):
            value = self._eval_expr(stmt.value)
            for target in stmt.targets:
                self._assign(target, value)
            return

        if isinstance(stmt, ast.AugAssign):
            current = self._eval_expr(stmt.target)
            delta = self._eval_expr(stmt.value)
            op_type = type(stmt.op)
            if op_type not in self.bin_ops:
                raise SandboxRuntimeError(f"Unsupported augmented operator: {op_type.__name__}")
            new_value = self.bin_ops[op_type](current, delta)
            self._assign(stmt.target, new_value)
            return

        if isinstance(stmt, ast.If):
            if self._truthy(self._eval_expr(stmt.test)):
                self._exec_block(stmt.body)
            else:
                self._exec_block(stmt.orelse)
            return

        if isinstance(stmt, ast.While):
            iterations = 0
            max_iterations = 100_000
            while self._truthy(self._eval_expr(stmt.test)):
                iterations += 1
                if iterations > max_iterations:
                    raise SandboxRuntimeError("while loop exceeded iteration limit")
                try:
                    self._exec_block(stmt.body)
                except _ContinueSignal:
                    continue
                except _BreakSignal:
                    break
            return

        if isinstance(stmt, ast.For):
            iterable = self._eval_expr(stmt.iter)
            if not isinstance(iterable, range | list | tuple | set | dict | str):
                raise SandboxRuntimeError("for-loop iterable type is not allowed")

            iterations = 0
            max_iterations = 100_000
            for item in iterable:
                iterations += 1
                if iterations > max_iterations:
                    raise SandboxRuntimeError("for loop exceeded iteration limit")
                self._assign(stmt.target, item)
                try:
                    self._exec_block(stmt.body)
                except _ContinueSignal:
                    continue
                except _BreakSignal:
                    break
            return

        if isinstance(stmt, ast.Break):
            raise _BreakSignal()

        if isinstance(stmt, ast.Continue):
            raise _ContinueSignal()

        if isinstance(stmt, ast.Pass):
            return

        raise SandboxRuntimeError(f"Unsupported statement: {type(stmt).__name__}")

    def _assign(self, target: ast.expr, value: object) -> None:
        if isinstance(target, ast.Name):
            self.env[target.id] = value
            return

        if isinstance(target, ast.Tuple):
            if not isinstance(value, (list, tuple)):
                raise SandboxRuntimeError("Cannot unpack non-sequence")
            if len(target.elts) != len(value):
                raise SandboxRuntimeError("Unpack length mismatch")
            for sub_target, item in zip(target.elts, value):
                self._assign(sub_target, item)
            return

        if isinstance(target, ast.List):
            if not isinstance(value, (list, tuple)):
                raise SandboxRuntimeError("Cannot unpack non-sequence")
            if len(target.elts) != len(value):
                raise SandboxRuntimeError("Unpack length mismatch")
            for sub_target, item in zip(target.elts, value):
                self._assign(sub_target, item)
            return

        if isinstance(target, ast.Subscript):
            container = self._eval_expr(target.value)
            key = self._eval_subscript_index(target.slice)
            try:
                container[key] = value
            except Exception as exc:
                raise SandboxRuntimeError(f"Subscript assignment failed: {exc}") from exc
            return

        if isinstance(target, ast.Attribute):
            obj = self._eval_expr(target.value)
            try:
                setattr(obj, target.attr, value)
            except Exception as exc:
                raise SandboxRuntimeError(f"Attribute assignment failed: {exc}") from exc
            return

        raise SandboxRuntimeError(f"Assignment target not allowed: {type(target).__name__}")

    def _eval_expr(self, expr: ast.expr) -> object:
        if isinstance(expr, ast.Constant):
            return expr.value

        if isinstance(expr, ast.Name):
            if expr.id in self.env:
                return self.env[expr.id]
            if expr.id in self.allowed_functions:
                return self.allowed_functions[expr.id]
            raise SandboxRuntimeError(f"Unknown name: {expr.id}")

        if isinstance(expr, ast.List):
            return [self._eval_expr(e) for e in expr.elts]

        if isinstance(expr, ast.Tuple):
            return tuple(self._eval_expr(e) for e in expr.elts)

        if isinstance(expr, ast.Set):
            return {self._eval_expr(e) for e in expr.elts}

        if isinstance(expr, ast.Dict):
            return {
                self._eval_expr(k): self._eval_expr(v)
                for k, v in zip(expr.keys, expr.values)
            }

        if isinstance(expr, ast.BinOp):
            left = self._eval_expr(expr.left)
            right = self._eval_expr(expr.right)
            op_type = type(expr.op)
            if op_type not in self.bin_ops:
                raise SandboxRuntimeError(f"Unsupported operator: {op_type.__name__}")
            try:
                return self.bin_ops[op_type](left, right)
            except Exception as exc:
                raise SandboxRuntimeError(str(exc)) from exc

        if isinstance(expr, ast.UnaryOp):
            operand = self._eval_expr(expr.operand)
            op_type = type(expr.op)
            if op_type not in self.unary_ops:
                raise SandboxRuntimeError(f"Unsupported unary operator: {op_type.__name__}")
            try:
                return self.unary_ops[op_type](operand)
            except Exception as exc:
                raise SandboxRuntimeError(str(exc)) from exc

        if isinstance(expr, ast.BoolOp):
            if isinstance(expr.op, ast.And):
                result = True
                for v in expr.values:
                    result = self._eval_expr(v)
                    if not self._truthy(result):
                        return result
                return result

            if isinstance(expr.op, ast.Or):
                result = False
                for v in expr.values:
                    result = self._eval_expr(v)
                    if self._truthy(result):
                        return result
                return result

            raise SandboxRuntimeError("Unsupported boolean operator")

        if isinstance(expr, ast.Compare):
            left = self._eval_expr(expr.left)
            for op, comparator in zip(expr.ops, expr.comparators):
                right = self._eval_expr(comparator)
                op_type = type(op)
                if op_type not in self.compare_ops:
                    raise SandboxRuntimeError(f"Unsupported comparison: {op_type.__name__}")
                if not self.compare_ops[op_type](left, right):
                    return False
                left = right
            return True

        if isinstance(expr, ast.Subscript):
            container = self._eval_expr(expr.value)
            key = self._eval_subscript_index(expr.slice)
            try:
                return container[key]
            except Exception as exc:
                raise SandboxRuntimeError(f"Subscript access failed: {exc}") from exc

        if isinstance(expr, ast.Call):
            return self._eval_call(expr)

        if isinstance(expr, ast.Attribute):
            obj = self._eval_expr(expr.value)
            try:
                return getattr(obj, expr.attr)
            except Exception as exc:
                raise SandboxRuntimeError(f"Attribute access failed: {exc}") from exc

        raise SandboxRuntimeError(f"Unsupported expression: {type(expr).__name__}")

    def _eval_subscript_index(self, node: ast.AST) -> object:
        if isinstance(node, ast.Slice):
            lower = self._eval_expr(node.lower) if node.lower else None
            upper = self._eval_expr(node.upper) if node.upper else None
            step = self._eval_expr(node.step) if node.step else None
            return slice(lower, upper, step)
        return self._eval_expr(node)

    def _eval_call(self, expr: ast.Call) -> object:
        # Handle direct function calls (e.g., len(...), max(...))
        if isinstance(expr.func, ast.Name):
            func_name = expr.func.id
            if func_name not in self.allowed_functions:
                raise SandboxRuntimeError(f"Function not allowed: {func_name}")

            func = self.allowed_functions[func_name]
            args = [self._eval_expr(a) for a in expr.args]
            kwargs = {kw.arg: self._eval_expr(kw.value) for kw in expr.keywords}

            try:
                return func(*args, **kwargs)
            except Exception as exc:
                raise SandboxRuntimeError(f"Call to {func_name} failed: {exc}") from exc

        # Handle method calls (e.g., obj.method(...))
        elif isinstance(expr.func, ast.Attribute):
            obj = self._eval_expr(expr.func.value)
            method_name = expr.func.attr
            
            # Get the method from the object
            try:
                method = getattr(obj, method_name)
            except Exception as exc:
                raise SandboxRuntimeError(f"Method access failed: {exc}") from exc
            
            # Check if it's callable
            if not callable(method):
                raise SandboxRuntimeError(f"Attribute '{method_name}' is not callable")
            
            args = [self._eval_expr(a) for a in expr.args]
            kwargs = {kw.arg: self._eval_expr(kw.value) for kw in expr.keywords}

            try:
                return method(*args, **kwargs)
            except Exception as exc:
                raise SandboxRuntimeError(f"Call to {method_name} failed: {exc}") from exc

        else:
            raise SandboxRuntimeError("Only direct function calls and method calls are allowed")

    @staticmethod
    def _truthy(value: object) -> bool:
        return bool(value)


def sandbox_exec(python_code: str, variables: dict) -> dict:
    """
    Execute a restricted subset of Python code in a sandboxed AST interpreter.

    Parameters
    ----------
    python_code : str
        Source code to execute.
    variables : dict
        Initial variables exposed to the sandbox.

    Returns
    -------
    dict
        Updated variable mapping after execution.

    Raises
    ------
    SandboxError
        On syntax violations or runtime errors inside the sandbox.
    """
    interpreter = _SandboxInterpreter(variables)
    return interpreter.execute(python_code)