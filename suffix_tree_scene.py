# -*- coding: utf-8 -*-
"""
suffix_tree_scene.py — Animacion profesional Manim CE para Suffix Tree.
Proyecto 1 AED — UTEC 2026-2

Ejecucion:
    manim -pql suffix_tree_scene.py SuffixTreeScene   # 480p rapido
    manim -pqh suffix_tree_scene.py SuffixTreeScene   # 1080p entrega
"""

from manim import *
from suffix_tree import SuffixTree, SuffixTreeNode
import numpy as np

# === CONFIGURACION ===
config.background_color = "#000000"

# === DATOS DEL PROYECTO ===
INTEGRANTES = ["Axel Portal", "Dayron Cueva", "Mariel Reyes"]
TITULO = "Suffix Tree"
SUBTITULO = "Arbol de Sufijos"
PROYECTO = "Proyecto 1 - Algoritmos y Estructuras de Datos"
UNIVERSIDAD = "Universidad de Ingenieria y Tecnologia - UTEC"

# === PALETA DE COLORES ===
C_TEXT = "#FFFFFF"
C_TEXT2 = "#CCCCCC"
C_ACCENT = "#58a6ff"
C_GREEN = "#3fb950"
C_RED = "#f85149"
C_ORANGE = "#d29922"
C_ROOT = "#da3633"
C_INTERNAL = "#1f6feb"
C_LEAF = "#238636"
C_EDGE = "#888888"
C_ELABEL = "#79c0ff"
CODE_FONT = "Consolas"

def MyText(text, **kwargs):
    if 'font' not in kwargs:
        kwargs['font'] = 'Arial'
    return Text(text, **kwargs)


# =====================================================================
# FUNCIONES AUXILIARES
# =====================================================================

def build_tree_n(text, n):
    """Construye un SuffixTree con solo los primeros n sufijos."""
    tree = SuffixTree()
    if n <= 0:
        return tree, []
    evts = []
    count = 0
    for ev in tree.insert(text):
        evts.append(ev)
        if ev[0] == "end_suffix":
            count += 1
            if count >= n:
                break
    return tree, evts


def tree_layout(root, xl=-5.5, xr=5.5, yt=2.0, ys=1.3):
    """Calcula posiciones con layout proporcional al ancho del subarbol."""
    pos = {}
    widths = {}

    def calc_w(node):
        if not node.children:
            widths[node.node_id] = 1
            return 1
        t = 0
        for c in sorted(node.children.keys()):
            _, ch = node.children[c]
            t += calc_w(ch)
        widths[node.node_id] = t
        return t

    calc_w(root)

    def assign(node, left, right, depth):
        pos[node.node_id] = np.array([(left + right) / 2, yt - depth * ys, 0.0])
        if not node.children:
            return
        kids = [(c, node.children[c]) for c in sorted(node.children.keys())]
        tw = sum(widths[ch.node_id] for _, (_, ch) in kids)
        cl = left
        for _, (_, ch) in kids:
            cw = widths[ch.node_id]
            cr = cl + (right - left) * cw / tw
            assign(ch, cl, cr, depth + 1)
            cl = cr

    assign(root, xl, xr, 0)
    return pos


def render_tree(root, pos, rid, efs=13, nfs=13):
    """Crea VGroup del arbol completo. Retorna (vgroup, node_map, edge_map)."""
    edges_g = VGroup()
    nodes_g = VGroup()
    nmap = {}
    emap = {}

    def trav(node, pid=None, elbl=""):
        nid = node.node_id
        p = pos[nid]
        if nid == rid:
            r, fill, stroke, lbl = 0.28, C_ROOT, WHITE, "R"
        elif node.is_leaf():
            r, fill, stroke, lbl = 0.22, C_LEAF, C_GREEN, str(node.suffix_index)
        else:
            r, fill, stroke, lbl = 0.22, C_INTERNAL, C_ACCENT, ""

        circ = Circle(radius=r, color=stroke, fill_color=fill,
                      fill_opacity=0.9, stroke_width=2.5).move_to(p)
        if lbl:
            txt = MyText(lbl, font_size=nfs + (2 if nid == rid else 0),
                       color=WHITE).move_to(p)
        else:
            txt = VGroup()
        nvg = VGroup(circ, txt)
        nmap[nid] = nvg
        nodes_g.add(nvg)

        if pid is not None:
            pp = pos[pid]
            pr = 0.28 if pid == rid else 0.22
            d = p - pp
            ln = np.linalg.norm(d)
            if ln > 0:
                u = d / ln
                ls, le = pp + u * (pr + 0.04), p - u * (r + 0.04)
            else:
                ls, le = pp, p
            line = Line(ls, le, stroke_width=2, color=C_EDGE)
            mid = (ls + le) / 2
            perp = np.array([-d[1], d[0], 0.0])
            pn = np.linalg.norm(perp)
            if pn > 0:
                perp = perp / pn * 0.22
            else:
                perp = UP * 0.22
            if perp[1] < 0:
                perp = -perp
            el = MyText(elbl, font=CODE_FONT, font_size=efs,
                      color=C_ELABEL, weight=BOLD).move_to(mid + perp)
            evg = VGroup(line, el)
            emap[(pid, nid)] = evg
            edges_g.add(evg)

        for c in sorted(node.children.keys()):
            ce, cn = node.children[c]
            trav(cn, nid, ce)

    trav(root)
    return VGroup(edges_g, nodes_g), nmap, emap


def get_suffix_events(all_evts, idx):
    """Extrae eventos de la insercion del sufijo con indice idx."""
    res = []
    rec = False
    for e in all_evts:
        if e[0] == "start_suffix" and e[2] == idx:
            rec = True
        if rec:
            res.append(e)
        if rec and e[0] == "end_suffix" and e[1] == idx:
            break
    return res


# =====================================================================
# ESCENA PRINCIPAL
# =====================================================================

class SuffixTreeScene(Scene):

    def construct(self):
        self._title()
        self._intro()
        self._insertion()
        self._search()
        self._dfs()
        self._edge_cases()
        self._complexity()
        self._credits()

    # ── Helpers ──────────────────────────────────────────────────────

    def _header(self, text):
        h = MyText(text, font_size=32, color=WHITE, weight=BOLD).to_edge(UP, buff=0.5)
        ln = Line(h.get_left() + DOWN * 0.2, h.get_right() + DOWN * 0.2,
                  color=C_ACCENT, stroke_width=2)
        g = VGroup(h, ln)
        self.play(Write(h), Create(ln), run_time=1.4)
        return g

    def _fade(self, *m):
        if m:
            self.play(*[FadeOut(x) for x in m], run_time=1.0)
        self.wait(0.75)

    def _reset_edges(self, emap):
        anims = [e[0].animate.set_color(C_EDGE).set_stroke(width=2)
                 for e in emap.values()]
        if anims:
            self.play(*anims, run_time=0.6)

    # ── 1. TITULO ────────────────────────────────────────────────────

    def _title(self):
        t1 = MyText(TITULO, font_size=56, color=WHITE, weight=BOLD)
        t2 = MyText(SUBTITULO, font_size=28, color=C_TEXT2).next_to(t1, DOWN, buff=0.2)
        t3 = MyText(PROYECTO, font_size=22, color=C_ACCENT).next_to(t2, DOWN, buff=0.5)
        t4 = MyText(UNIVERSIDAD, font_size=18, color=C_TEXT2).next_to(t3, DOWN, buff=0.2)
        deco = Line(LEFT * 3, RIGHT * 3, color=C_ACCENT,
                    stroke_width=1.5).next_to(t4, DOWN, buff=0.4)

        self.play(Write(t1), run_time=2.4)
        self.play(FadeIn(t2, shift=UP * 0.2), run_time=1.2)
        self.wait(1.25)
        self.play(FadeIn(t3), FadeIn(t4), Create(deco), run_time=1.6)
        self.wait(6.25)
        self._fade(t1, t2, t3, t4, deco)

    # ── 2. INTRODUCCION ──────────────────────────────────────────────

    def _intro(self):
        hg = self._header("Que es un Suffix Tree?")

        lines = VGroup(
            MyText("Es una estructura de datos avanzada que almacena todos", font_size=24, color=C_TEXT),
            MyText("los sufijos de una cadena de texto dada.", font_size=24, color=C_TEXT),
            MyText("Es, en esencia, un Trie comprimido donde las claves", font_size=24, color=C_TEXT),
            MyText("indexadas son cada uno de los sufijos de una palabra", font_size=24, color=C_TEXT),
            MyText("o texto de longitud n.", font_size=24, color=C_TEXT),
        )
        lines.arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        lines.next_to(hg, DOWN, buff=0.7).to_edge(LEFT, buff=1.0)

        self.play(AnimationGroup(*[FadeIn(l, shift=RIGHT * 0.2) for l in lines],
                                 lag_ratio=0.3), run_time=3.5)
        self.wait(3.75)

        tda_h = MyText("Tipo de Dato Abstracto:", font_size=22,
                     color=C_ACCENT, weight=BOLD)
        tda_h.next_to(lines, DOWN, buff=0.6, aligned_edge=LEFT)
        
        tda_lines = VGroup(
            MyText("- Funcionalmente: Indice de Texto completo (Full Text Index)", font_size=20, color=C_TEXT),
            MyText("- Estructuralmente: Arbol", font_size=20, color=C_TEXT)
        )
        tda_lines.arrange(DOWN, buff=0.15, aligned_edge=LEFT)
        tda_lines.next_to(tda_h, DOWN, buff=0.25, aligned_edge=LEFT)

        self.play(Write(tda_h), run_time=0.8)
        self.play(FadeIn(tda_lines), run_time=1.2)
        self.wait(2.5)

        ah = MyText("Aplicaciones practicas:", font_size=22,
                  color=C_ACCENT, weight=BOLD)
        ah.next_to(tda_lines, DOWN, buff=0.6, aligned_edge=LEFT)
        apps = VGroup(
            MyText("- Bioinformatica: busqueda en ADN", font_size=20, color=C_TEXT2),
            MyText("- Motores de busqueda de texto", font_size=20, color=C_TEXT2),
            MyText("- Compresion de datos (LZ77)", font_size=20, color=C_TEXT2),
            MyText("- Deteccion de plagios", font_size=20, color=C_TEXT2),
        )
        apps.arrange(DOWN, buff=0.15, aligned_edge=LEFT)
        apps.next_to(ah, DOWN, buff=0.25, aligned_edge=LEFT)

        self.play(Write(ah), run_time=0.8)
        self.play(AnimationGroup(*[FadeIn(a, shift=RIGHT * 0.15) for a in apps],
                                 lag_ratio=0.25), run_time=3.0)
        self.wait(6.25)
        self._fade(hg, lines, tda_h, tda_lines, ah, apps)

    # ── 3. INSERCION DE BANANA$ ──────────────────────────────────────

    def _insertion(self):
        hg = self._header('Construccion: "BANANA$"')
        word = "BANANA$"
        suffixes = [word[i:] for i in range(len(word))]

        # Panel de sufijos (izquierda)
        pt = MyText("Sufijos:", font=CODE_FONT, font_size=18,
                  color=C_ACCENT, weight=BOLD)
        pt.to_edge(LEFT, buff=0.3).shift(UP * 0.8)
        sitems = VGroup()
        for i, s in enumerate(suffixes):
            sitems.add(MyText(f" {i}: {s}", font=CODE_FONT, font_size=15, color=C_TEXT2))
        sitems.arrange(DOWN, buff=0.1, aligned_edge=LEFT)
        sitems.next_to(pt, DOWN, buff=0.15, aligned_edge=LEFT)

        self.play(Write(pt), run_time=0.8)
        self.play(FadeIn(sitems), run_time=1.2)
        self.wait(2.5)

        prev_mob = None
        op_label = MyText("", font_size=1).to_edge(DOWN, buff=0.4)
        self.add(op_label)

        for n in range(1, len(word) + 1):
            # Resaltar sufijo actual
            self.play(sitems[n - 1].animate.set_color(YELLOW), run_time=0.6)
            self.wait(0.75)

            # Construir arbol parcial
            tree, evts = build_tree_n(word, n)
            sevts = get_suffix_events(evts, n - 1)

            # Describir operacion desde los eventos reales
            desc, col = "", C_GREEN
            new_nids = []
            for e in sevts:
                if e[0] == "create_leaf":
                    desc = f"Nueva hoja: '{e[3]}'"
                    new_nids.append(e[2])
                elif e[0] == "split_edge":
                    desc = f"Division: '{e[5]}' + ['{e[6]}', '{e[7]}']"
                    col = C_ORANGE
                    new_nids.extend([e[3], e[4]])

            new_op = MyText(desc, font=CODE_FONT, font_size=15, color=col)
            new_op.to_edge(DOWN, buff=0.4)
            self.play(FadeOut(op_label), FadeIn(new_op, shift=UP * 0.1), run_time=0.6)
            op_label = new_op

            # Renderizar arbol
            positions = tree_layout(tree.root, xl=-0.5, xr=6.5, yt=1.8, ys=1.3)
            tmob, nmap, emap = render_tree(tree.root, positions, tree.root.node_id)

            if prev_mob is not None:
                self.play(FadeOut(prev_mob), run_time=0.6)
            self.play(FadeIn(tmob), run_time=1.0)

            # Resaltar nodos nuevos
            for nid in new_nids:
                if nid in nmap:
                    self.play(Indicate(nmap[nid], color=YELLOW,
                                       scale_factor=1.3), run_time=0.8)

            has_split = any(e[0] == "split_edge" for e in sevts)
            self.wait(1.8 if has_split else 0.8)

            self.play(sitems[n - 1].animate.set_color(C_GREEN), run_time=0.4)
            prev_mob = tmob

        self.wait(3.75)
        self._tree = tree
        self._fade(pt, sitems, hg, op_label, tmob)

    # ── 4. BUSQUEDA ──────────────────────────────────────────────────

    def _search(self):
        hg = self._header("Busqueda de Patrones")

        # Arbol centrado
        tree = self._tree
        pos = tree_layout(tree.root, -5.0, 5.0, 1.5, 1.3)
        tmob, nmap, emap = render_tree(tree.root, pos, tree.root.node_id)
        self.play(FadeIn(tmob), run_time=1.2)
        self.wait(1.25)

        # Caso 1: "ANA" (encontrado)
        cl = MyText('Caso 1: Buscar "ANA"', font_size=20, color=C_ACCENT)
        cl.next_to(hg, DOWN, buff=0.25)
        self.play(FadeIn(cl), run_time=0.6)
        self._animate_search(tree, "ANA", nmap, emap)
        self._reset_edges(emap)
        self.play(FadeOut(cl), run_time=0.6)
        self.wait(1.25)

        # Caso 2: "BANS" (fallo parcial)
        cl2 = MyText('Caso 2: Buscar "BANS" (fallo parcial)', font_size=20, color=C_ACCENT)
        cl2.next_to(hg, DOWN, buff=0.25)
        self.play(FadeIn(cl2), run_time=0.6)
        self._animate_search(tree, "BANS", nmap, emap)
        self._reset_edges(emap)
        self.play(FadeOut(cl2), run_time=0.6)

        self.wait(1.25)
        # Guardar para DFS (no quitar arbol)
        self._tmob = tmob
        self._nmap = nmap
        self._emap = emap
        self._pos = pos
        self._fade(hg)

    def _animate_search(self, tree, pattern, nmap, emap):
        status = None
        for ev in tree.search(pattern):
            if ev[0] == "search_start":
                ns = MyText(f'Patron: "{ev[1]}"', font_size=18, color=C_ACCENT)
                ns.to_edge(DOWN, buff=0.5)
                if status:
                    self.play(FadeOut(status), FadeIn(ns), run_time=0.6)
                else:
                    self.play(FadeIn(ns), run_time=0.6)
                status = ns

            elif ev[0] == "traverse_edge":
                k = (ev[1], ev[2])
                if k in emap:
                    self.play(emap[k][0].animate.set_color(YELLOW).set_stroke(width=4),
                              run_time=0.8)

            elif ev[0] == "compare_char":
                nid, ch, el, p, m = ev[1], ev[2], ev[3], ev[4], ev[5]
                c = C_GREEN if m else C_RED
                sym = "=" if m else "!="
                ns = MyText(f"'{ch}' {sym} '{el[p]}'  {'Match' if m else 'Fallo'}",
                         font_size=18, color=c)
                ns.to_edge(DOWN, buff=0.5)
                anims = [FadeOut(status), FadeIn(ns)]
                if nid in nmap:
                    anims.append(Indicate(nmap[nid], color=c,
                                          scale_factor=1.2, run_time=0.8))
                self.play(*anims, run_time=0.8)
                status = ns
                self.wait(1.25)

            elif ev[0] == "search_found":
                ns = MyText(f'"{ev[1]}" ENCONTRADO', font_size=22,
                         color=C_GREEN, weight=BOLD)
                ns.to_edge(DOWN, buff=0.5)
                self.play(FadeOut(status), FadeIn(ns), run_time=0.8)
                status = ns
                self.wait(5.0)

            elif ev[0] == "search_not_found":
                ns = MyText(f'"{ev[1]}" NO encontrado', font_size=22,
                         color=C_RED, weight=BOLD)
                ns.to_edge(DOWN, buff=0.5)
                self.play(FadeOut(status), FadeIn(ns), run_time=0.8)
                status = ns
                self.wait(5.0)

        if status:
            self.play(FadeOut(status), run_time=0.6)

    # ── 5. RECORRIDO DFS ─────────────────────────────────────────────

    def _dfs(self):
        hg = self._header("Recorrido en Profundidad (DFS)")
        tree = self._tree
        tmob, nmap, emap, pos = self._tmob, self._nmap, self._emap, self._pos

        # Reset colores
        for _, evg in emap.items():
            evg[0].set_color(C_EDGE)
            evg[0].set_stroke(width=2)

        # Panel de sufijos recuperados
        ph = MyText("Sufijos recuperados:", font_size=18, color=C_ORANGE, weight=BOLD)
        ph.to_edge(LEFT, buff=0.3).shift(DOWN * 1.5)
        self.play(FadeIn(ph), run_time=0.6)

        # Tracker
        rp = pos[tree.root.node_id]
        tracker = Dot(color=C_ORANGE, radius=0.15).move_to(rp)
        self.play(FadeIn(tracker, scale=2), run_time=0.8)

        entries = VGroup()
        for ev in tree.dfs_traversal():
            if ev[0] == "dfs_enter":
                nid = ev[1]
                if nid in pos:
                    self.play(tracker.animate.move_to(pos[nid]), run_time=0.5)
                if nid in nmap:
                    self.play(nmap[nid][0].animate.set_stroke(C_ORANGE, width=4),
                              run_time=0.3)

            elif ev[0] == "dfs_leaf":
                nid, sidx, suf = ev[1], ev[2], ev[3]
                entry = MyText(f"[{sidx}] {suf}", font=CODE_FONT,
                            font_size=14, color=C_TEXT2)
                if len(entries) == 0:
                    entry.next_to(ph, DOWN, buff=0.15, aligned_edge=LEFT)
                else:
                    entry.next_to(entries[-1], DOWN, buff=0.08, aligned_edge=LEFT)
                entries.add(entry)
                self.play(
                    FadeIn(entry, shift=RIGHT * 0.2),
                    nmap[nid][0].animate.set_fill(C_ORANGE, opacity=0.7),
                    run_time=0.7,
                )
                self.wait(1.0)

        self.wait(5.0)
        self._fade(tracker, tmob, hg, ph, entries)

    # ── 6. CASOS BORDE ───────────────────────────────────────────────

    def _edge_cases(self):
        hg = self._header("Casos Borde")

        # -- Caso 1: falta el $ --
        c1t = MyText('Caso 1: Falta el caracter "$"', font_size=28,
                   color=C_ORANGE, weight=BOLD)
        c1t.next_to(hg, DOWN, buff=0.8, aligned_edge=LEFT).shift(RIGHT * 0.5)
        self.play(Write(c1t), run_time=1.0)

        l1_p1 = VGroup(
            MyText('Sin "$", el sufijo "A" es prefijo de "ANA"', font_size=22, color=C_TEXT2),
            MyText('y "ANA" es prefijo de "ANANA".', font_size=22, color=C_TEXT2),
            MyText("Los sufijos NO terminan en hojas unicas.", font_size=22, color=C_RED)
        ).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        l1_p1.next_to(c1t, DOWN, buff=0.6, aligned_edge=LEFT)

        l1_p2 = VGroup(
            MyText('Solucion: agregar "$" como centinela.', font_size=22, color=C_GREEN),
            MyText("Nuestro algoritmo lo agrega automaticamente:", font_size=22, color=C_GREEN)
        ).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        l1_p2.next_to(l1_p1, DOWN, buff=0.6, aligned_edge=LEFT)

        self.play(AnimationGroup(*[FadeIn(l, shift=RIGHT * 0.15) for l in l1_p1], lag_ratio=0.25), run_time=2.5)
        self.wait(2.5)
        self.play(AnimationGroup(*[FadeIn(l, shift=RIGHT * 0.15) for l in l1_p2], lag_ratio=0.25), run_time=2.0)
        self.wait(1.5)

        # Demo: insertar sin $
        demo_tree = SuffixTree()
        list(demo_tree.insert("BANANA"))
        demo_txt = MyText(f'insert("BANANA") -> texto = "{demo_tree.text}"',
                       font=CODE_FONT, font_size=20, color=C_ACCENT)
        demo_txt.next_to(l1_p2, DOWN, buff=0.8, aligned_edge=LEFT)
        self.play(FadeIn(demo_txt), run_time=1.0)
        self.wait(5.0)
        self.play(FadeOut(VGroup(c1t, l1_p1, l1_p2, demo_txt)), run_time=0.8)

        # -- Caso 2: AAAA$ --
        c2t = MyText('Caso 2: Caracteres repetidos "AAAA$"', font_size=28,
                   color=C_ORANGE, weight=BOLD)

        l2 = VGroup(
            MyText("Cada sufijo comparte un prefijo largo.", font_size=22, color=C_TEXT2),
            MyText("Multiples divisiones consecutivas.", font_size=22, color=C_TEXT2),
            MyText("Arbol degenerado: forma de cadena lineal.", font_size=22, color=C_ORANGE),
            MyText("El algoritmo lo maneja correctamente.", font_size=22, color=C_GREEN),
        )
        l2.arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        
        # Agrupar y posicionar a la derecha
        text_group2 = VGroup(c2t, l2).arrange(DOWN, buff=0.6, aligned_edge=LEFT)
        text_group2.next_to(hg, DOWN, buff=0.8).shift(RIGHT * 2.5)

        self.play(Write(c2t), run_time=1.0)
        self.play(AnimationGroup(*[FadeIn(l, shift=RIGHT * 0.15) for l in l2],
                                  lag_ratio=0.25), run_time=3.0)
        self.wait(2.0)

        # Mostrar arbol AAAA$ real en la izquierda
        aaaa = SuffixTree()
        list(aaaa.insert("AAAA$"))
        ap = tree_layout(aaaa.root, xl=-6.0, xr=-1.0, yt=1.0, ys=0.75)
        am, _, _ = render_tree(aaaa.root, ap, aaaa.root.node_id, efs=12, nfs=11)
        self.play(FadeIn(am), run_time=1.2)
        self.wait(7.5)
        self._fade(text_group2, am, hg)

    # ── 7. COMPLEJIDAD TEMPORAL ──────────────────────────────────────

    def _complexity(self):
        hg = self._header("Complejidad Temporal")

        vn = MyText("n = longitud del texto    m = longitud del patrón",
                  font_size=18, color=C_TEXT2)
        vn.next_to(hg, DOWN, buff=0.4)
        self.play(FadeIn(vn), run_time=0.6)

        # Tabla manual
        data = [
            ("Operacion", "Complejidad", "Nota"),
            ("Construccion (naive)", "O(n²)", "Inserta n sufijos"),
            ("Construccion (Ukkonen)", "O(n)", "Algoritmo optimo"),
            ("Busqueda", "O(m)", "Independiente de n"),
            ("Recorrido DFS", "O(n)", "Visita cada arista"),
        ]
        cw = [3.0, 2.2, 3.0]
        rows = VGroup()
        for ri, row in enumerate(data):
            rv = VGroup()
            xo = 0
            for ci, cell in enumerate(row):
                if ri == 0:
                    t = MyText(cell, font_size=17, color=C_ACCENT, weight=BOLD)
                elif ci == 1:
                    c = C_RED if "^2" in cell else C_GREEN
                    t = MyText(cell, font_size=17, color=c, weight=BOLD)
                else:
                    t = MyText(cell, font_size=15, color=C_TEXT2)
                t.move_to(np.array([xo + cw[ci] / 2, 0, 0]))
                xo += cw[ci]
                rv.add(t)
            rows.add(rv)
        rows.arrange(DOWN, buff=0.3)
        rows.next_to(vn, DOWN, buff=0.4).center().shift(DOWN * 0.2)

        sep = Line(rows[0].get_left() + DOWN * 0.18,
                   rows[0].get_right() + DOWN * 0.18,
                   color=C_TEXT2, stroke_width=1)

        self.play(FadeIn(rows[0]), Create(sep), run_time=1.0)
        for r in rows[1:]:
            self.play(FadeIn(r, shift=UP * 0.1), run_time=0.8)
        self.wait(3.75)

        summ = MyText(
            "El Suffix Tree sacrifica O(n²) en construcción\n"
            "para lograr búsquedas en O(m) - óptimo para texto estático.",
            font_size=18, color=WHITE,
        )
        summ.next_to(rows, DOWN, buff=0.5)
        self.play(FadeIn(summ, shift=UP * 0.2), run_time=1.2)
        self.wait(7.5)
        self._fade(hg, vn, rows, sep, summ)

    # ── 8. CREDITOS ──────────────────────────────────────────────────

    def _credits(self):
        th = MyText("Integrantes", font_size=36, color=WHITE, weight=BOLD)
        th.shift(UP * 1.5)
        self.play(Write(th), run_time=1.2)

        names = VGroup()
        for name in INTEGRANTES:
            names.add(MyText(name, font_size=26, color=C_ACCENT))
        names.arrange(DOWN, buff=0.25)
        names.next_to(th, DOWN, buff=0.5)
        self.play(AnimationGroup(*[FadeIn(n, shift=LEFT * 0.3) for n in names],
                                  lag_ratio=0.3), run_time=2.0)
        self.wait(2.5)

        uni = MyText(UNIVERSIDAD, font_size=18, color=C_TEXT2)
        uni.next_to(names, DOWN, buff=0.5)
        curso = MyText(PROYECTO, font_size=18, color=C_TEXT2)
        curso.next_to(uni, DOWN, buff=0.15)
        self.play(FadeIn(uni), FadeIn(curso), run_time=1.0)
        self.wait(1.25)

        gracias = MyText("Gracias!", font_size=48, color=C_ACCENT, weight=BOLD)
        gracias.next_to(curso, DOWN, buff=0.6)
        self.play(Write(gracias), run_time=1.6)
        self.wait(7.5)
        self._fade(th, names, uni, curso, gracias)
