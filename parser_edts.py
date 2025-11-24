import re
from typing import Optional, Any, Dict, List


TOKEN_SPEC = [
    ("NUMBER", r"\d+(\.\d+)?"),
    ("ID",     r"[a-zA-Z_]\w*"),
    ("PLUS",   r"\+"),
    ("MINUS",  r"-"),
    ("MUL",    r"\*"),
    ("DIV",    r"/"),
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("SKIP",   r"[ \t]+"),
    ("MISMATCH", r"."),
]

TOK_REGEX = "|".join("(?P<%s>%s)" % pair for pair in TOKEN_SPEC)

class Token:
    def __init__(self, type_: str, lexeme: str):
        self.type = type_
        self.lexeme = lexeme

    def __repr__(self):
        return f"Token({self.type}, '{self.lexeme}')"

class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.gen = self._tokenize()

    def _tokenize(self):
        for mo in re.finditer(TOK_REGEX, self.text):
            kind = mo.lastgroup
            value = mo.group()
            if kind == "NUMBER":
                yield Token("NUMBER", value)
            elif kind == "ID":
                yield Token("ID", value)
            elif kind in {"PLUS","MINUS","MUL","DIV","LPAREN","RPAREN"}:
                yield Token(kind, value)
            elif kind == "SKIP":
                continue
            elif kind == "MISMATCH":
                raise SyntaxError(f"Caracter inválido: {value!r}")
        yield Token("EOF", "")

    def next(self):
        return next(self.gen)

class ASTNode:
    def __init__(self):
        self.val: Optional[float] = None 

class NumberNode(ASTNode):
    def __init__(self, number_text: str):
        super().__init__()
        self.number_text = number_text
        self.val = float(number_text) if '.' in number_text else int(number_text)

    def __repr__(self):
        return f"Number({self.number_text})"

class IdNode(ASTNode):
    def __init__(self, name: str):
        super().__init__()
        self.name = name

    def __repr__(self):
        return f"Id({self.name})"

class BinOpNode(ASTNode):
    def __init__(self, op: str, left: ASTNode, right: ASTNode):
        super().__init__()
        self.op = op  # '+', '-', '*', '/'
        self.left = left
        self.right = right

    def __repr__(self):
        return f"BinOp({self.op}, {self.left}, {self.right})"

class Symbol:
    def __init__(self, name: str, tipo: str = "number", valor: Any = None):
        self.name = name
        self.tipo = tipo
        self.valor = valor

    def __repr__(self):
        return f"Symbol(name={self.name}, tipo={self.tipo}, valor={self.valor})"

class SymbolTable:
    def __init__(self):
        self.table: Dict[str, Symbol] = {}

    def add(self, name: str, tipo: str = "number", valor: Any = None):
        self.table[name] = Symbol(name, tipo, valor)

    def get(self, name: str) -> Optional[Symbol]:
        return self.table.get(name)

    def __repr__(self):
        lines = ["Tabla de símbolos:"]
        for k, s in self.table.items():
            lines.append(f"  {k} : tipo={s.tipo}, valor={s.valor}")
        return "\n".join(lines)

class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.lookahead: Token = self.lexer.next()

    def eat(self, token_type: str):
        if self.lookahead.type == token_type:
            # print("eat", self.lookahead)
            self.lookahead = self.lexer.next()
        else:
            raise SyntaxError(f"Se esperaba {token_type}, encontrado {self.lookahead}")

    def parse(self) -> ASTNode:
        node = self.expr()
        if self.lookahead.type != "EOF":
            raise SyntaxError(f"Token extra al final: {self.lookahead}")
        return node

    def expr(self) -> ASTNode:
        node = self.term()
        while self.lookahead.type in ("PLUS", "MINUS"):
            op = self.lookahead.lexeme
            if self.lookahead.type == "PLUS":
                self.eat("PLUS")
            else:
                self.eat("MINUS")
            right = self.term()
            node = BinOpNode(op, node, right)
        return node

    def term(self) -> ASTNode:
        node = self.factor()
        while self.lookahead.type in ("MUL", "DIV"):
            op = self.lookahead.lexeme
            if self.lookahead.type == "MUL":
                self.eat("MUL")
            else:
                self.eat("DIV")
            right = self.factor()
            node = BinOpNode(op, node, right)
        return node

    def factor(self) -> ASTNode:
        if self.lookahead.type == "LPAREN":
            self.eat("LPAREN")
            node = self.expr()
            self.eat("RPAREN")
            return node
        elif self.lookahead.type == "NUMBER":
            tok = self.lookahead
            self.eat("NUMBER")
            return NumberNode(tok.lexeme)
        elif self.lookahead.type == "ID":
            tok = self.lookahead
            self.eat("ID")
            return IdNode(tok.lexeme)
        else:
            raise SyntaxError(f"Factor inesperado: {self.lookahead}")

class Evaluator:
    def __init__(self, symtab: SymbolTable):
        self.symtab = symtab

    def eval(self, node: ASTNode) -> float:
        if isinstance(node, NumberNode):
            node.val = node.val  
            return node.val
        elif isinstance(node, IdNode):
            sym = self.symtab.get(node.name)
            if sym is None:
                raise NameError(f"Identificador no definido: {node.name}")
            node.val = sym.valor
            return node.val
        elif isinstance(node, BinOpNode):
            left_val = self.eval(node.left)
            right_val = self.eval(node.right)
            if node.op == "+":
                node.val = left_val + right_val
            elif node.op == "-":
                node.val = left_val - right_val
            elif node.op == "*":
                node.val = left_val * right_val
            elif node.op == "/":
                if right_val == 0:
                    raise ZeroDivisionError("División por cero detectada en la evaluación")
                node.val = left_val / right_val
            else:
                raise ValueError(f"Operador desconocido: {node.op}")
            return node.val
        else:
            raise TypeError("Nodo AST desconocido")

def print_ast(node: ASTNode, indent: str = ""):
    if isinstance(node, NumberNode):
        print(indent + f"Number({node.number_text}) -> val={node.val}")
    elif isinstance(node, IdNode):
        print(indent + f"Id({node.name}) -> val={node.val}")
    elif isinstance(node, BinOpNode):
        print(indent + f"BinOp({node.op}) -> val={node.val}")
        print(indent + "  L:")
        print_ast(node.left, indent + "    ")
        print(indent + "  R:")
        print_ast(node.right, indent + "    ")
    else:
        print(indent + f"Unknown node: {node}")

def main():
    print("EDTS - Parser y AST decorado para expresiones aritméticas\n")

    examples = [
        ("3 + 5 * 2", {}),
        ("(3 + 5) * 2 - 4 / 2", {}),
        ("3 + x * (2 + y)", {"x": 5, "y": 1}),
        ("a / b + 10", {"a": 20, "b": 4}),
    ]

    for expr_text, symbols in examples:
        print("="*60)
        print("Expresión:", expr_text)
        st = SymbolTable()
        for name, val in symbols.items():
            st.add(name, tipo="number", valor=val)

        print(st)

        lexer = Lexer(expr_text)
        parser = Parser(lexer)
        try:
            ast = parser.parse()
        except Exception as e:
            print("Error de parseo:", e)
            continue

        evaluator = Evaluator(st)
        try:
            value = evaluator.eval(ast)
        except Exception as e:
            print("Error en evaluación:", e)
            continue

        print("\nValor evaluado:", value)
        print("\nAST decorado (nodos con atributo .val):")
        print_ast(ast)
        print()

    print("="*60)
    expr_text = "z + 1"
    print("Expresión de ejemplo con error (identificador no definido):", expr_text)
    lexer = Lexer(expr_text)
    parser = Parser(lexer)
    try:
        ast = parser.parse()
        st = SymbolTable()  
        evaluator = Evaluator(st)
        evaluator.eval(ast)
    except Exception as e:
        print("Se capturó excepción:", type(e).__name__, "-", e)

if __name__ == "__main__":
    main()
