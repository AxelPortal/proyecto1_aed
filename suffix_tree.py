"""
suffix_tree.py — Implementación del Suffix Tree en Python puro.

Proyecto 1 AED: Algoritmos y Estructuras de Datos
Estructura: Suffix Tree (Árbol de Sufijos Comprimido)

Esta implementación usa construcción naive (inserción sufijo a sufijo)
y emite eventos paso a paso mediante generadores (yield) para que
la capa de animación (Manim) pueda visualizar cada operación.
"""


class SuffixTreeNode:
    """Nodo del Suffix Tree.

    Cada nodo interno tiene un diccionario de hijos indexado por el
    primer carácter de la etiqueta de arista. Las hojas almacenan
    el índice del sufijo que representan.

    Attributes:
        children: Diccionario {char: (edge_label, child_node)}.
        suffix_index: Índice del sufijo (solo hojas). -1 si es interno.
        node_id: Identificador único para animación.
    """

    _counter = 0  # Contador global para asignar IDs únicos

    def __init__(self, suffix_index=-1):
        self.children: dict[str, tuple[str, "SuffixTreeNode"]] = {}
        self.suffix_index = suffix_index
        self.node_id = SuffixTreeNode._counter
        SuffixTreeNode._counter += 1

    @classmethod
    def reset_counter(cls):
        """Reinicia el contador de IDs (útil para múltiples árboles)."""
        cls._counter = 0

    def is_leaf(self) -> bool:
        return len(self.children) == 0


class SuffixTree:
    """Suffix Tree construido de forma naive (O(n²)).

    Inserta cada sufijo de la cadena uno por uno en un trie comprimido.
    Todos los métodos principales son generadores que emiten eventos
    descriptivos para la capa de visualización.

    Eventos emitidos por insert():
        ("start_suffix", suffix, suffix_index)
        ("create_leaf", parent_id, child_id, edge_label, suffix_index)
        ("split_edge", parent_id, old_child_id, new_internal_id, new_leaf_id,
         prefix, remaining_old, remaining_new, suffix_index)
        ("walk_edge", parent_id, child_id, edge_label)
        ("end_suffix", suffix_index)

    Eventos emitidos por search():
        ("search_start", pattern)
        ("compare_char", node_id, char, edge_label, position, match)
        ("traverse_edge", parent_id, child_id, edge_label)
        ("search_found", pattern)
        ("search_not_found", pattern, reason)

    Eventos emitidos por dfs_traversal():
        ("dfs_enter", node_id, depth, edge_label)
        ("dfs_leaf", node_id, suffix_index, suffix)
        ("dfs_backtrack", node_id)
    """

    def __init__(self):
        SuffixTreeNode.reset_counter()
        self.root = SuffixTreeNode()
        self.text = ""

    def insert(self, text: str):
        """Construye el suffix tree insertando todos los sufijos de `text`.

        Generador que emite eventos paso a paso para cada operación
        de inserción, división de arista, o creación de nodo.

        Args:
            text: Cadena a indexar. Debe terminar en '$' (carácter centinela).

        Yields:
            Tuplas con eventos descriptivos (ver docstring de clase).
        """
        if not text:
            yield ("empty_input",)
            return

        # Asegurar carácter centinela
        if text[-1] != "$":
            text = text + "$"
        self.text = text
        n = len(text)

        # Insertar cada sufijo text[i:] en el árbol
        for i in range(n):
            suffix = text[i:]
            yield ("start_suffix", suffix, i)
            yield from self._insert_suffix(suffix, i)
            yield ("end_suffix", i)

    def _insert_suffix(self, suffix: str, suffix_index: int):
        """Inserta un solo sufijo en el árbol, emitiendo eventos.

        Recorre el árbol desde la raíz. Si encuentra un prefijo compartido
        con una arista existente, divide la arista. Si no hay arista que
        coincida, crea una nueva hoja.
        """
        current = self.root
        pos = 0  # Posición actual dentro del sufijo

        while pos < len(suffix):
            first_char = suffix[pos]

            if first_char not in current.children:
                # --- Caso 1: No hay arista con este carácter → crear hoja ---
                leaf = SuffixTreeNode(suffix_index=suffix_index)
                edge_label = suffix[pos:]
                current.children[first_char] = (edge_label, leaf)
                yield ("create_leaf", current.node_id, leaf.node_id,
                       edge_label, suffix_index)
                return

            # Hay una arista que empieza con first_char
            edge_label, child = current.children[first_char]
            yield ("walk_edge", current.node_id, child.node_id, edge_label)

            # Comparar el sufijo restante con la etiqueta de la arista
            j = 0
            while j < len(edge_label) and pos < len(suffix) and edge_label[j] == suffix[pos]:
                j += 1
                pos += 1

            if j == len(edge_label):
                # La arista se consumió completa → continuar desde el hijo
                current = child
                continue

            # --- Caso 2: Mismatch dentro de la arista → dividir ---
            # Crear nodo interno en el punto de divergencia
            internal = SuffixTreeNode()
            new_leaf = SuffixTreeNode(suffix_index=suffix_index)

            prefix = edge_label[:j]         # Parte compartida
            remaining_old = edge_label[j:]  # Resto de la arista original
            remaining_new = suffix[pos:]    # Resto del sufijo nuevo

            # Reconectar: parent → internal → {old_child, new_leaf}
            current.children[first_char] = (prefix, internal)
            internal.children[remaining_old[0]] = (remaining_old, child)
            internal.children[remaining_new[0]] = (remaining_new, new_leaf)

            yield ("split_edge", current.node_id, child.node_id,
                   internal.node_id, new_leaf.node_id,
                   prefix, remaining_old, remaining_new, suffix_index)
            return

    def search(self, pattern: str):
        """Busca un patrón en el suffix tree.

        Generador que emite eventos de cada comparación y decisión
        durante el recorrido.

        Args:
            pattern: Patrón a buscar.

        Yields:
            Tuplas con eventos descriptivos.

        Returns (via último yield):
            Evento ("search_found", ...) o ("search_not_found", ...).
        """
        yield ("search_start", pattern)

        if not pattern:
            yield ("search_not_found", pattern, "patrón vacío")
            return

        if not self.text:
            yield ("search_not_found", pattern, "árbol vacío")
            return

        current = self.root
        pos = 0

        while pos < len(pattern):
            first_char = pattern[pos]

            if first_char not in current.children:
                yield ("search_not_found", pattern,
                       f"no hay arista con '{first_char}'")
                return

            edge_label, child = current.children[first_char]
            yield ("traverse_edge", current.node_id, child.node_id, edge_label)

            # Comparar carácter por carácter
            j = 0
            while j < len(edge_label) and pos < len(pattern):
                match = edge_label[j] == pattern[pos]
                yield ("compare_char", child.node_id, pattern[pos],
                       edge_label, j, match)
                if not match:
                    yield ("search_not_found", pattern,
                           f"mismatch: '{pattern[pos]}' ≠ '{edge_label[j]}'")
                    return
                j += 1
                pos += 1

            # Si consumimos todo el patrón (incluso a mitad de arista) → encontrado
            if pos == len(pattern):
                yield ("search_found", pattern)
                return

            # Avanzar al hijo
            current = child

        yield ("search_found", pattern)

    def dfs_traversal(self, node=None, depth=0, edge_label="", prefix=""):
        """Recorrido DFS (preorden) del suffix tree.

        Visita todos los nodos en orden lexicográfico de las aristas
        y emite eventos para cada nodo visitado.

        Args:
            node: Nodo actual (None = raíz).
            depth: Profundidad actual.
            edge_label: Etiqueta de la arista que llevó a este nodo.
            prefix: Concatenación de etiquetas de arista desde la raíz.

        Yields:
            Tuplas con eventos de recorrido DFS.
        """
        if node is None:
            node = self.root

        yield ("dfs_enter", node.node_id, depth, edge_label)

        if node.is_leaf():
            yield ("dfs_leaf", node.node_id, node.suffix_index, prefix)
        else:
            # Recorrer hijos en orden lexicográfico
            for char in sorted(node.children.keys()):
                child_edge, child_node = node.children[char]
                yield from self.dfs_traversal(
                    child_node, depth + 1, child_edge, prefix + child_edge
                )

        yield ("dfs_backtrack", node.node_id)


# =============================================================================
# Tests unitarios
# =============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("TESTS: Suffix Tree")
    print("=" * 60)

    # --- Test 1: Inserción de "ANA$" ---
    print("\n--- Test 1: Inserción de 'ANA$' ---")
    st = SuffixTree()
    events = list(st.insert("ANA$"))
    print(f"  Texto indexado: '{st.text}'")
    print(f"  Eventos emitidos: {len(events)}")
    for e in events:
        print(f"    {e}")

    # --- Test 2: Búsqueda exitosa de "NA" ---
    print("\n--- Test 2: Búsqueda de 'NA' ---")
    events = list(st.search("NA"))
    for e in events:
        print(f"    {e}")
    assert events[-1][0] == "search_found", "Debería encontrar 'NA'"

    # --- Test 3: Búsqueda fallida de "XY" ---
    print("\n--- Test 3: Búsqueda de 'XY' ---")
    events = list(st.search("XY"))
    for e in events:
        print(f"    {e}")
    assert events[-1][0] == "search_not_found", "No debería encontrar 'XY'"

    # --- Test 4: Búsqueda de "ANA" ---
    print("\n--- Test 4: Búsqueda de 'ANA' ---")
    events = list(st.search("ANA"))
    for e in events:
        print(f"    {e}")
    assert events[-1][0] == "search_found", "Debería encontrar 'ANA'"

    # --- Test 5: Recorrido DFS ---
    print("\n--- Test 5: Recorrido DFS ---")
    events = list(st.dfs_traversal())
    suffixes_found = []
    for e in events:
        print(f"    {e}")
        if e[0] == "dfs_leaf":
            suffixes_found.append((e[2], e[3]))  # (index, suffix)
    print(f"  Sufijos encontrados: {suffixes_found}")
    # "ANA$" tiene 4 sufijos: ANA$, NA$, A$, $
    assert len(suffixes_found) == 4, f"Esperados 4 sufijos, obtenidos {len(suffixes_found)}"

    # --- Test 6: Caso borde — cadena vacía ---
    print("\n--- Test 6: Inserción de cadena vacía ---")
    st2 = SuffixTree()
    events = list(st2.insert(""))
    for e in events:
        print(f"    {e}")
    assert events[0][0] == "empty_input", "Debería emitir evento de entrada vacía"

    # --- Test 7: Caso borde — un solo carácter ---
    print("\n--- Test 7: Inserción de 'A' ---")
    st3 = SuffixTree()
    events = list(st3.insert("A"))
    print(f"  Texto indexado: '{st3.text}'")
    for e in events:
        print(f"    {e}")

    print("\n" + "=" * 60)
    print("TODOS LOS TESTS PASARON [OK]")
    print("=" * 60)
