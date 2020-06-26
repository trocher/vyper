import copy
import types

from vyper.settings import VYPER_ERROR_CONTEXT_LINES, VYPER_ERROR_LINE_NUMBERS


class ExceptionList(list):
    """
    List subclass for storing exceptions.
    To deliver multiple compilation errors to the user at once, append each
    raised Exception to this list and call raise_if_not_empty once the task
    is completed.
    """

    def raise_if_not_empty(self):
        if len(self) == 1:
            raise self[0]
        elif len(self) > 1:
            if len(set(type(i) for i in self)) > 1:
                err_type = StructureException
            else:
                err_type = type(self[0])
            err_msg = ["Compilation failed with the following errors:"]
            err_msg += [f"{type(i).__name__}: {i}" for i in self]
            raise err_type("\n\n".join(err_msg))


class VyperException(Exception):
    """
    Base Vyper exception class.

    This exception is not raised directly. Other exceptions inherit it in
    order to display source annotations in the error string.
    """

    def __init__(self, message="Error Message not found.", *items):
        """
        Exception initializer.

        Arguments
        ---------
        message : str
            Error message to display with the exception.
        *items : VyperNode | tuple, optional
            Vyper ast node(s) indicating where the exception occured. Source
            annotation is generated in the order the nodes are given. A single
            tuple of (lineno, col_offset) is also understood to support the old
            API, but new exceptions should not use this approach.
        """
        self.message = message
        self.lineno = None
        self.col_offset = None

        if len(items) == 1 and isinstance(items[0], tuple):
            self.lineno, self.col_offset = items[0][:2]
        else:
            self.nodes = items
            if items:
                self.source_code = items[0].full_source_code

    def with_annotation(self, *nodes):
        """
        Creates a copy of this exception with a modified source annotation.

        Arguments
        ---------
        *node : VyperNode
            AST node(s) to use in the annotation.

        Returns
        -------
        A copy of the exception with the new node offset(s) applied.
        """
        exc = copy.copy(self)
        exc.source_code = nodes[0].full_source_code
        exc.nodes = nodes
        return exc

    def __str__(self):
        from vyper import ast as vy_ast
        from vyper.utils import annotate_source_code

        if not hasattr(self, "source_code"):
            if self.lineno is not None and self.col_offset is not None:
                return f"line {self.lineno}:{self.col_offset} {self.message}"
            else:
                return self.message

        msg = f"{self.message}\n"
        for node in self.nodes:
            try:
                source_annotation = annotate_source_code(
                    self.source_code,
                    node.lineno,
                    node.col_offset,
                    context_lines=VYPER_ERROR_CONTEXT_LINES,
                    line_numbers=VYPER_ERROR_LINE_NUMBERS,
                )
            except Exception:
                # necessary for certian types of syntax exceptions
                return msg

            if isinstance(node, vy_ast.VyperNode):
                fn_node = node.get_ancestor(vy_ast.FunctionDef)
                if fn_node:
                    msg += f"function '{fn_node.name}', "

            col_offset_str = "" if node.col_offset is None else str(node.col_offset)
            msg += f"line {node.lineno}:{col_offset_str} \n{source_annotation}\n"

        return msg


class SyntaxException(VyperException):

    """Invalid syntax."""

    def __init__(self, message, source_code, lineno, col_offset):
        item = types.SimpleNamespace()  # TODO: Create an actual object for this
        item.lineno = lineno
        item.col_offset = col_offset
        item.full_source_code = source_code
        super().__init__(message, item)


class NatSpecSyntaxException(SyntaxException):
    """Invalid syntax within NatSpec docstring."""


class StructureException(VyperException):
    """Invalid structure for parsable syntax."""


class VersionException(VyperException):
    """Version string is malformed or incompatible with this compiler version."""


class VariableDeclarationException(VyperException):
    """Invalid variable declaration."""


class FunctionDeclarationException(VyperException):
    """Invalid function declaration."""


class EventDeclarationException(VyperException):
    """Invalid event declaration."""


class UnknownType(VyperException):
    """Reference to a type that does not exist."""


class UnknownAttribute(VyperException):
    """Reference to an attribute that does not exist."""


class UndeclaredDefinition(VyperException):
    """Reference to a definition that has not been declared."""


class NamespaceCollision(VyperException):
    """Assignment to a name that is already in use."""


class InvalidLiteral(VyperException):
    """Invalid literal value."""


class InvalidAttribute(VyperException):
    """Reference to an attribute that does not exist."""


class InvalidReference(VyperException):
    """Invalid reference to an existing definition."""


class InvalidOperation(VyperException):
    """Invalid operator for a given type."""


class InvalidType(VyperException):
    """Type is invalid for an action."""


class TypeMismatch(VyperException):
    """Attempt to perform an action between multiple objects of incompatible types."""


class ArgumentException(VyperException):
    """Call to a function with invalid arguments."""


class CallViolation(VyperException):
    """Illegal function call."""


class ConstancyViolation(VyperException):
    """State-changing action in a constant context."""


class NonPayableViolation(VyperException):
    """msg.value in a nonpayable function."""


class InterfaceViolation(VyperException):
    """Interface is not fully implemented."""


class ArrayIndexException(VyperException):
    """Array index out of range."""


class ZeroDivisionException(VyperException):
    """Second argument to a division or modulo operation was zero."""


class OverflowException(VyperException):
    """Numeric value out of range for the given type."""


class EvmVersionException(VyperException):
    """Invalid action for the active EVM ruleset."""


class JSONError(Exception):

    """Invalid compiler input JSON."""

    def __init__(self, msg, lineno=None, col_offset=None):
        super().__init__(msg)
        self.lineno = lineno
        self.col_offset = col_offset


class ParserException(Exception):
    """Contract source cannot be parsed."""


class VyperInternalException(Exception):
    """
    Base Vyper internal exception class.

    This exception is not raised directly, it is subclassed by other internal
    exceptions.

    Internal exceptions are raised as a means of passing information between
    compiler processes. They should never be exposed to the user.
    """

    def __init__(self, message=""):
        self.message = message

    def __str__(self):
        return (
            f"{self.message}\n\nThis is an unhandled internal compiler error. "
            "Please create an issue on Github to notify the developers.\n"
            "https://github.com/vyperlang/vyper/issues/new?template=bug.md"
        )


class CompilerPanic(VyperInternalException):
    """General unexpected error during compilation."""


class UnexpectedNodeType(VyperInternalException):
    """Unexpected AST node type."""


class UnexpectedValue(VyperInternalException):
    """Unexpected Value."""


class UnfoldableNode(VyperInternalException):
    """Constant folding logic cannot be applied to an AST node."""


class TypeCheckFailure(VyperInternalException):
    """An issue was not caught during type checking that should have been."""
