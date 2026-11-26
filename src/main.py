"""Catálogo de exoplanetas com Rubro-Negra, 2-3-4 e k-D (menu interativo).

Execute a partir da raiz do projeto:  python -m src.main
"""

from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt

from . import visualizacao as vis
from .arvore_234 import Arvore234
from .dados import Exoplaneta, carregar
from .kd_tree import ArvoreKD
from .rubro_negra import ArvoreRubroNegra

SAIDA = Path(__file__).resolve().parent.parent / "saida"
BACKENDS_SEM_JANELA = {"agg", "pdf", "svg", "ps", "cairo", "template"}


class Catalogo:
    """Mantém o mesmo conjunto de planetas indexado em três árvores."""

    def __init__(self, planetas):
        self.por_distancia = ArvoreRubroNegra()   # chave: distância (anos-luz)
        self.por_ano = Arvore234()                # chave: ano de descoberta
        for p in planetas:
            self.por_distancia.inserir(p.distancia_al, p)
            self.por_ano.inserir(p.ano, p)
        self._reconstruir_kd()

    def planetas(self):
        for _, registros in self.por_distancia.em_ordem():
            yield from registros

    def _reconstruir_kd(self):
        self.por_coordenada = ArvoreKD.construir(
            [(p.coordenadas, p) for p in self.planetas()])

    def inserir(self, p):
        self.por_distancia.inserir(p.distancia_al, p)
        self.por_ano.inserir(p.ano, p)
        self.por_coordenada.inserir(p.coordenadas, p)

    def encontrar(self, nome):
        for p in self.planetas():
            if p.nome.lower() == nome.strip().lower():
                return p
        return None

    def remover(self, p):
        self.por_distancia.remover(p.distancia_al, p)
        self.por_ano.remover(p.ano, p)
        # A k-D é só demonstrativa: após remoção ela é reconstruída pela mediana.
        self._reconstruir_kd()


# ----------------------------------------------------------------- utilitários
def ler_numero(msg, tipo=float):
    while True:
        try:
            return tipo(input(msg).replace(",", "."))
        except ValueError:
            print("Valor inválido, tente de novo.")


def exibir(fig, nome_arquivo):
    caminho = SAIDA / nome_arquivo
    caminho.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(caminho, dpi=120, bbox_inches="tight")
    print(f"Imagem salva em {caminho}")
    if plt.get_backend().lower() not in BACKENDS_SEM_JANELA:
        plt.show()
    plt.close(fig)


def imprimir_registros(registros):
    if not registros:
        print("Nenhum resultado.")
        return
    for p in registros:
        print("  ", p)


# ---------------------------------------------------------------------- ações
def listar(cat):
    print(f"\nCatálogo em ordem de distância ({cat.por_distancia.num_nos} nós na RN):")
    imprimir_registros(list(cat.planetas()))


def buscar_distancia(cat):
    d = ler_numero("Distância (anos-luz): ")
    print("Caminho percorrido na RN:", " -> ".join(vis.fmt(c) for c in
                                                    cat.por_distancia.caminho_busca(d)))
    imprimir_registros(cat.por_distancia.buscar(d))


def intervalo_distancia(cat):
    a = ler_numero("Distância mínima: ")
    b = ler_numero("Distância máxima: ")
    imprimir_registros([p for _, regs in cat.por_distancia.intervalo(a, b) for p in regs])


def buscar_ano(cat):
    ano = ler_numero("Ano de descoberta: ", int)
    print("Nós visitados na 2-3-4:", " -> ".join(str(n) for n in cat.por_ano.caminho_busca(ano)))
    imprimir_registros(cat.por_ano.buscar(ano))


def intervalo_ano(cat):
    a = ler_numero("Ano inicial: ", int)
    b = ler_numero("Ano final: ", int)
    imprimir_registros([p for _, regs in cat.por_ano.intervalo(a, b) for p in regs])


def inserir(cat):
    nome = input("Nome: ").strip()
    if not nome:
        print("Nome obrigatório.")
        return
    if cat.encontrar(nome):
        print("Já existe um planeta com esse nome.")
        return
    p = Exoplaneta(nome, ler_numero("Distância (anos-luz): "),
                   ler_numero("Ano de descoberta: ", int),
                   ler_numero("Ascensão reta (0 a 360°): "),
                   ler_numero("Declinação (-90 a 90°): "),
                   input("Método de detecção: ").strip() or "Desconhecido")
    cat.inserir(p)
    print(f"'{p.nome}' inserido nas três árvores.")


def remover(cat):
    p = cat.encontrar(input("Nome do planeta a remover: "))
    if p is None:
        print("Planeta não encontrado.")
        return
    cat.remover(p)
    print(f"'{p.nome}' removido.")


def vizinho_kd(cat):
    alvo = (ler_numero("Ascensão reta do ponto (0 a 360°): "),
            ler_numero("Declinação do ponto (-90 a 90°): "))
    no, dist, visitados, podados = cat.por_coordenada.vizinho_mais_proximo(alvo)
    print(f"Mais próximo: {', '.join(p.nome for p in no.valores)} "
          f"(distância {dist:.2f}° no plano AR x Dec)")
    print(f"Nós visitados: {len(visitados)} de {len(list(cat.planetas()))} registros; "
          f"subárvores podadas: {len(podados)}")
    exibir(vis.desenhar_kd(cat.por_coordenada, alvo, (no, dist), visitados, podados,
                           f"Vizinho mais próximo de {alvo}"), "kd_vizinho.png")


def validar(cat):
    for nome, arvore in (("Rubro-Negra", cat.por_distancia), ("2-3-4", cat.por_ano)):
        try:
            arvore.validar()
            print(f"{nome}: todas as propriedades OK (altura {arvore.altura()}).")
        except AssertionError as e:
            print(f"{nome}: VIOLAÇÃO -> {e}")


def alternar_passos(cat, estado):
    if estado["pasta"] is None:
        pasta = SAIDA / f"passos_{datetime.now():%Y%m%d_%H%M%S}"
        cat.por_distancia.observador = vis.GravadorPassos(pasta / "rubro_negra")
        cat.por_ano.observador = vis.GravadorPassos(pasta / "arvore_234")
        estado["pasta"] = pasta
        print(f"Modo passo a passo ATIVADO. Imagens em {pasta}")
    else:
        cat.por_distancia.observador = cat.por_ano.observador = None
        for sub in ("rubro_negra", "arvore_234"):
            gif = vis.gerar_gif(estado["pasta"] / sub, estado["pasta"] / f"{sub}.gif")
            if gif:
                print(f"GIF gerado: {gif}")
        estado["pasta"] = None
        print("Modo passo a passo DESATIVADO.")


MENU = """
================ CATÁLOGO DE EXOPLANETAS ================
 1. Listar catálogo (percurso em ordem da Rubro-Negra)
 2. Buscar por distância            [Rubro-Negra]
 3. Buscar por intervalo de distância [Rubro-Negra]
 4. Buscar por ano de descoberta     [2-3-4]
 5. Buscar por intervalo de anos     [2-3-4]
 6. Inserir exoplaneta (nas 3 árvores)
 7. Remover exoplaneta por nome
 8. Plotar Rubro-Negra
 9. Plotar 2-3-4
10. Plotar a 2-3-4 convertida em Rubro-Negra (equivalência)
11. k-D: vizinho mais próximo de um ponto do céu
12. Validar propriedades das árvores
13. Ativar/desativar modo passo a passo (salva cada passo como imagem)
 0. Sair
=========================================================="""


def main():
    cat = Catalogo(carregar())
    estado = {"pasta": None}
    print(f"{cat.por_distancia.num_nos} nós na Rubro-Negra, {len(cat.por_ano)} chaves "
          f"na 2-3-4 ({cat.por_ano.num_nos()} nós).")
    acoes = {
        "1": listar, "2": buscar_distancia, "3": intervalo_distancia,
        "4": buscar_ano, "5": intervalo_ano, "6": inserir, "7": remover,
        "8": lambda c: exibir(vis.desenhar_rn(c.por_distancia), "rubro_negra.png"),
        "9": lambda c: exibir(vis.desenhar_234(c.por_ano), "arvore_234.png"),
        "10": lambda c: exibir(vis.desenhar_rn(c.por_ano.para_rubro_negra(),
                                               "2-3-4 convertida em Rubro-Negra"),
                               "equivalencia_234_rn.png"),
        "11": vizinho_kd, "12": validar,
        "13": lambda c: alternar_passos(c, estado),
    }
    while True:
        print(MENU)
        opcao = input("Opção: ").strip()
        if opcao == "0":
            if estado["pasta"] is not None:
                alternar_passos(cat, estado)
            break
        acao = acoes.get(opcao)
        if acao:
            acao(cat)
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()
