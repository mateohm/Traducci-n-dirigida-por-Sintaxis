# Traducción dirigida por Sintaxis

## Introducción

El presente proyecto implementa un Esquema de Traducción Dirigida por la Sintaxis (EDTS) basado en una Gramática Independiente de Contexto (GIC) que permite analizar y evaluar expresiones aritméticas que incluyen operaciones de suma, resta, multiplicación, división, así como el uso de paréntesis, números e identificadores.

1. Diseño de la Gramática

El lenguaje soporta expresiones aritméticas básicas, por lo cual la gramática definida parte de los no terminales:

- E → Expresión

- T → Término

- F → Factor

La gramática original presenta recursión izquierda, estructura típica de lenguajes aritméticos:

```
1. E → E + T
2. E → E - T
3. E → T
4. T → T * F
5. T → T / F
6. T → F
7. F → ( E )
8. F → id
9. F → num
```

Sin embargo, para ser procesada mediante descenso recursivo, se transforma a una forma equivalente, eliminando la recursión izquierda:

```
expr  → term ((+|-) term)*
term  → factor ((*|/) factor)*
factor → (expr) | id | num
```
Esta transformación permite implementar el parser de forma sencilla.


2. Definición de Atributos

El lenguaje requiere únicamente atributos sintetizados, utilizados para:

- Calcular valores numéricos

- Construir nodos del AST

- Propagar información hacia arriba del árbol

Los atributos definidos:

| No Terminal | Atributos | Propósito                          |
|-------------|-----------|-------------------------------------|
| E, T, F     | .val      | Valor numérico de la expresión      |
| E, T, F     | .nodo     | Nodo del AST correspondiente        |


Los tokens numéricos tienen atributos:

- num.valor
- id.lexema

3. Cálculo de FIRST, FOLLOW y Predicción

Se calculan los conjuntos para garantizar que la gramática es válida y entendible por el parser.

FIRST:

Todos los no terminales comparten:

```
FIRST(E) = FIRST(T) = FIRST(F) = { id, num, ( }
```

FOLLOW:

Determinan cómo se cierran subexpresiones:

```
FOLLOW(E) = { ), $ }
FOLLOW(T) = { +, -, ), $ }
FOLLOW(F) = { *, /, +, -, ), $ }
```

Predicción:

La gramática transformada es LL(1), por lo que la tabla de predicción es válida.


4. Construcción del AST Decorado

- Durante el análisis sintáctico se construye un Árbol de Sintaxis Abstracta (AST):

- Cada nodo BinOp representa un operador

- Cada NumberNode representa un valor numérico

- Cada IdNode representa un identificador

- El evaluador recorre el árbol y calcula los valores (.val)

Ejemplo:

Para la entrada:

```
3 + 5 * 2
```

El AST queda:

```
          (+)
         /   \
       3     (*)
             / \
            5   2

```


5. Tabla de Símbolos

La tabla de símbolos contiene los identificadores encontrados y sus valores.

Se implementa con una clase SymbolTable que almacena:

- nombre
- tipo
- valor

La evaluación del AST consulta esta tabla para obtener el valor de cada identificador.

6. Gramática de Atributos

Se asocian acciones semánticas (EDTS) a las reglas de la gramática.
Ejemplo:

```
E → E1 + T
      E.val   = E1.val + T.val
      E.nodo  = Nodo('+', E1.nodo, T.nodo)
```

Para operaciones:

```
T → T1 * F
      T.val   = T1.val * F.val
      T.nodo  = Nodo('*', T1.nodo, F.nodo)
```

Para elementos básicos:

```
F → num
      F.val  = num.valor
      F.nodo = NodoNum(num.valor)
```


La implementación en Python replica estas reglas.

7. Construcción del EDTS

Un EDTS (Esquema de Traducción Dirigido por la Sintaxis) especifica:

- Dónde se deben ejecutar acciones semánticas

- Qué valores se calculan

- Cómo se construyen los nodos

- Cómo se decoran los atributos

Ejemplo para suma:

```
E → E1 + T { E.val = E1.val + T.val }
```

En Python se implementa en la clase Evaluator, donde cada nodo calcula:

```
if node.op == "+":
    node.val = left_val + right_val
```

Ese es el equivalente del EDTS en código.


8. Implementación del Parser en Python

El código final se compone de:

- Lexer

Convierte la entrada en tokens: números, paréntesis, operadores, identificadores.

- Parser (descenso recursivo)

Procesa la entrada según la gramática LL(1) y construye el AST.

- AST Nodes

Clases para representar expresiones:

  - NumberNode
  - IdNode
  - BinOpNode

- Evaluador

Recorre el AST y asigna .val a cada nodo.

- Tabla de símbolos

Estructura que almacena valores asociados a identificadores.

- Impresor del árbol

Muestra el AST decorado en consola.

- Ejemplos de prueba

Incluye expresiones con y sin identificadores.

