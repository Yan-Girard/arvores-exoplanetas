"""Plotagem das árvores com matplotlib (desenho feito do zero, nó a nó)."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle

from .rubro_negra import ArvoreRubroNegra, VERMELHO
from .arvore_234 import Arvore234

COR_VERMELHO = "#d62728"
COR_PRETO = "#1f1f1f"
COR_DESTAQUE = "#f5b400"
COR_234_FUNDO = "#e8eef7"
COR_234_BORDA = "#2b4c7e"


def fmt(chave):
    return f"{chave:g}" if isinstance(chave, float) else str(chave)


# --------------------------------------------------------------- Rubro-Negra
def _layout_rn(arvore):
    """x = posição no percurso em ordem, y = -profundidade."""
    pos, idx = {}, [0]

    def visitar(no, prof):
        if no is arvore.NIL:
            return
        visitar(no.esq, prof + 1)
        pos[no] = (idx[0], -prof)
        idx[0] += 1
        visitar(no.dir, prof + 1)

    visitar(arvore.raiz, 0)
    return pos


def desenhar_rn(arvore, titulo="", destaque=(), ax=None):
    pos = _layout_rn(arvore)
    n = len(pos)
    h = max((-y for _, y in pos.values()), default=0) + 1
    if ax is None:
        _, ax = plt.subplots(figsize=(max(6, 0.6 * (n + 1)), max(3, 1.0 * h + 1)))

    for no, (x, y) in pos.items():
        for filho in (no.esq, no.dir):
            if filho in pos:
                fx, fy = pos[filho]
                ax.plot([x, fx], [y, fy], color="#999", lw=1.3, zorder=1)

    for no, (x, y) in pos.items():
        cor = COR_VERMELHO if no.cor == VERMELHO else COR_PRETO
        marcado = no.chave in destaque
        ax.add_patch(Circle((x, y), 0.4, facecolor=cor, zorder=2,
                            edgecolor=COR_DESTAQUE if marcado else "white",
                            lw=3.5 if marcado else 1))
        rotulo = fmt(no.chave)
        ax.text(x, y, rotulo, color="white", ha="center", va="center", zorder=3,
                fontsize=8 if len(rotulo) > 3 else 9, weight="bold")
        if len(no.valores) > 1:
            ax.text(x + 0.32, y + 0.36, f"×{len(no.valores)}", fontsize=8,
                    color="#444", ha="left", zorder=3)

    ax.set_xlim(-1, max(n, 1))
    ax.set_ylim(-(h - 1) - 0.8, 0.8)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(titulo or f"Rubro-Negra ({n} nós, altura {h})", fontsize=11)
    return ax.figure


# ---------------------------------------------------------------------- 2-3-4
LARG_CHAVE, ALT_NO, ESPACO, NIVEL = 0.9, 0.6, 0.6, 1.6


def _layout_234(raiz):
    pos, cursor = {}, [0.0]

    def visitar(no, prof):
        w = LARG_CHAVE * max(len(no.chaves), 1)
        if no.folha:
            x = cursor[0] + w / 2
            cursor[0] += w + ESPACO
        else:
            for f in no.filhos:
                visitar(f, prof + 1)
            x = (pos[no.filhos[0]][0] + pos[no.filhos[-1]][0]) / 2
        pos[no] = (x, -prof * NIVEL, w)

    if raiz:
        visitar(raiz, 0)
    return pos, cursor[0]


def desenhar_234(arvore, titulo="", destaque=(), ax=None):
    pos, largura = _layout_234(arvore.raiz)
    h = arvore.altura()
    if ax is None:
        _, ax = plt.subplots(figsize=(max(6, 0.6 * largura + 1), max(3, 1.0 * h * NIVEL + 1)))

    for no, (x, y, w) in pos.items():
        for j, filho in enumerate(no.filhos):
            fx, fy, _ = pos[filho]
            ax.plot([x - w / 2 + j * LARG_CHAVE, fx], [y - ALT_NO / 2, fy + ALT_NO / 2],
                    color="#999", lw=1.3, zorder=1)

    for no, (x, y, w) in pos.items():
        x0 = x - w / 2
        ax.add_patch(Rectangle((x0, y - ALT_NO / 2), w, ALT_NO, facecolor=COR_234_FUNDO,
                               edgecolor=COR_234_BORDA, lw=1.5, zorder=2))
        if not no.chaves:
            ax.text(x, y, "∅", ha="center", va="center", zorder=3)
        for i, chave in enumerate(no.chaves):
            cx = x0 + i * LARG_CHAVE
            if chave in destaque:
                ax.add_patch(Rectangle((cx, y - ALT_NO / 2), LARG_CHAVE, ALT_NO,
                                       facecolor=COR_DESTAQUE, edgecolor=COR_234_BORDA,
                                       lw=1.5, zorder=2))
            if i > 0:
                ax.plot([cx, cx], [y - ALT_NO / 2, y + ALT_NO / 2], color=COR_234_BORDA,
                        lw=1, zorder=3)
            ax.text(cx + LARG_CHAVE / 2, y, fmt(chave), ha="center", va="center",
                    fontsize=8.5, weight="bold", color=COR_234_BORDA, zorder=4)
            if len(no.valores[i]) > 1:
                ax.text(cx + LARG_CHAVE / 2, y - ALT_NO / 2 - 0.18, f"×{len(no.valores[i])}",
                        ha="center", va="top", fontsize=7.5, color="#444", zorder=4)

    ax.set_xlim(-0.5, max(largura, 1))
    ax.set_ylim(-(max(h, 1) - 1) * NIVEL - 0.9, 0.7)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(titulo or f"Árvore 2-3-4 ({len(arvore)} chaves, {arvore.num_nos()} nós, "
                           f"altura {h})", fontsize=11)
    return ax.figure


# ------------------------------------------------------------------------ k-D
def _rotulo_kd(no, limite=None):
    v = no.valores[0]
    texto = getattr(v, "nome", str(no.ponto))
    if limite and len(texto) > limite:
        texto = texto[:limite - 1] + "…"
    return texto


def desenhar_kd(arvore, alvo=None, resultado=None, visitados=(), podados=(),
                titulo="", limites=(0, 360, -90, 90), rotulos_eixos=("AR", "Dec")):
    def contar(no):
        return 0 if no is None else 1 + contar(no.esq) + contar(no.dir)

    n = contar(arvore.raiz)
    larg_arvore = max(9, 0.62 * n)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9 + larg_arvore, 7.5),
                                   gridspec_kw={"width_ratios": [9, larg_arvore]})
    visitados = set(map(id, visitados))

    # Painel 1: plano com as partições
    def particionar(no, xmin, xmax, ymin, ymax):
        if no is None:
            return
        x, y = no.ponto
        if no.eixo == 0:
            ax1.plot([x, x], [ymin, ymax], color="#1f77b4", lw=1.2, alpha=0.8)
            particionar(no.esq, xmin, x, ymin, ymax)
            particionar(no.dir, x, xmax, ymin, ymax)
        else:
            ax1.plot([xmin, xmax], [y, y], color="#9467bd", lw=1.2, alpha=0.8)
            particionar(no.esq, xmin, xmax, ymin, y)
            particionar(no.dir, xmin, xmax, y, ymax)

    particionar(arvore.raiz, *limites)

    def todos(no):
        return [] if no is None else todos(no.esq) + [no] + todos(no.dir)

    nos = todos(arvore.raiz)
    for no in nos:
        cor = "#ff7f0e" if id(no) in visitados else "#333"
        ax1.scatter(*no.ponto, s=30, color=cor, zorder=3)
        # com muitos pontos, só rotula os visitados para não poluir o plano
        if n <= 20 or id(no) in visitados:
            ax1.annotate(_rotulo_kd(no), no.ponto, fontsize=7, xytext=(3, 3),
                     textcoords="offset points", color="#333")
    if alvo is not None:
        ax1.scatter(*alvo, marker="X", s=140, color=COR_VERMELHO, zorder=5, label="alvo")
    if resultado is not None:
        no_res, dist = resultado
        ax1.scatter(*no_res.ponto, marker="*", s=300, color="#2ca02c", zorder=5,
                    label=f"mais próximo: {_rotulo_kd(no_res)}")
        ax1.plot([alvo[0], no_res.ponto[0]], [alvo[1], no_res.ponto[1]], "--",
                 color="#2ca02c")
        ax1.add_patch(Circle(alvo, dist, fill=False, ls=":", color="#2ca02c"))
    ax1.set_xlim(limites[0], limites[1])
    ax1.set_ylim(limites[2], limites[3])
    ax1.set_aspect("equal")
    ax1.set_xlabel(f"{rotulos_eixos[0]} (eixo 0) — linhas azuis")
    ax1.set_ylabel(f"{rotulos_eixos[1]} (eixo 1) — linhas roxas")
    ax1.set_title("Partições do plano")
    if alvo is not None:
        ax1.legend(loc="upper left", fontsize=8)

    # Painel 2: a árvore
    pos, idx = {}, [0]

    def layout(no, prof):
        if no is None:
            return
        layout(no.esq, prof + 1)
        pos[id(no)] = (idx[0], -prof)
        idx[0] += 1
        layout(no.dir, prof + 1)

    layout(arvore.raiz, 0)
    for no in nos:
        x, y = pos[id(no)]
        for f in (no.esq, no.dir):
            if f is not None:
                ax2.plot([x, pos[id(f)][0]], [y, pos[id(f)][1]], color="#999", lw=1, zorder=1)
    podados_ids = set(map(id, podados))
    for no in nos:
        x, y = pos[id(no)]
        borda = "#1f77b4" if no.eixo == 0 else "#9467bd"
        fundo = "#fff"
        if id(no) in visitados:
            fundo = "#ffe2c4"
        if resultado is not None and no is resultado[0]:
            fundo = "#c7f0c7"
        texto = f"{_rotulo_kd(no, 12)}\n{rotulos_eixos[no.eixo]}={no.ponto[no.eixo]:g}"
        if id(no) in podados_ids:
            texto += "\n✂ poda"
        ax2.text(x, y, texto, ha="center", va="center", fontsize=6.5, zorder=3,
                 bbox=dict(boxstyle="round,pad=0.3", fc=fundo, ec=borda, lw=1.5))
    ax2.set_xlim(-1, max(len(nos), 1))
    ax2.set_ylim(-arvore.altura() + 0.4, 0.6)
    ax2.axis("off")
    ax2.set_title(f"Árvore k-D (borda azul: corta em {rotulos_eixos[0]}, roxa: corta em "
                  f"{rotulos_eixos[1]}; laranja: visitado; verde: resposta)", fontsize=10)

    fig.suptitle(titulo or "Árvore k-D (k = 2)", fontsize=13)
    fig.tight_layout()
    return fig


# ------------------------------------------------------------------ utilidades
def desenhar(arvore, titulo="", destaque=()):
    if isinstance(arvore, ArvoreRubroNegra):
        return desenhar_rn(arvore, titulo, destaque)
    if isinstance(arvore, Arvore234):
        return desenhar_234(arvore, titulo, destaque)
    raise TypeError("tipo de árvore não suportado")


def salvar(fig, caminho, dpi=120):
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(caminho, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    return caminho


class GravadorPassos:
    """Observador que salva uma imagem por passo do algoritmo."""

    def __init__(self, pasta, verbose=True):
        self.pasta = Path(pasta)
        self.pasta.mkdir(parents=True, exist_ok=True)
        self.n = 0
        self.verbose = verbose

    def __call__(self, arvore, descricao, destaque):
        self.n += 1
        fig = desenhar(arvore, f"Passo {self.n}: {descricao}", destaque)
        salvar(fig, self.pasta / f"passo_{self.n:03d}.png", dpi=100)
        if self.verbose:
            print(f"  [passo {self.n:03d}] {descricao}")


def gerar_gif(pasta, saida, duracao_ms=1300):
    """Junta os PNGs de uma pasta num GIF animado (usa Pillow, se instalado)."""
    try:
        from PIL import Image
    except ImportError:
        print("Pillow não instalado: GIF não gerado.")
        return None
    arquivos = sorted(Path(pasta).glob("passo_*.png"))
    if not arquivos:
        return None
    imagens = [Image.open(a).convert("RGB") for a in arquivos]
    w = max(i.width for i in imagens)
    h = max(i.height for i in imagens)
    quadros = []
    for img in imagens:
        fundo = Image.new("RGB", (w, h), "white")
        fundo.paste(img, ((w - img.width) // 2, 0))
        quadros.append(fundo)
    quadros[0].save(saida, save_all=True, append_images=quadros[1:],
                    duration=duracao_ms, loop=0)
    return saida
