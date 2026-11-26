"""Árvore k-D (k = 2) para demonstração: coordenadas no céu.

Cada nível divide o espaço por um eixo diferente (nível par: eixo 0 = ascensão
reta; nível ímpar: eixo 1 = declinação). A construção usa a mediana do eixo,
o que gera uma árvore balanceada sem precisar de rotações.

Repetidos: coordenada igual no eixo de corte vai para a direita; ponto
idêntico tem o registro anexado à lista do nó.
"""

import math


class NoKD:
    def __init__(self, ponto, valor, eixo):
        self.ponto = ponto
        self.valores = [valor]
        self.eixo = eixo
        self.esq = None
        self.dir = None


class ArvoreKD:
    def __init__(self, k=2):
        self.k = k
        self.raiz = None

    @classmethod
    def construir(cls, itens, k=2):
        """itens: lista de (ponto, valor). Constrói balanceada pela mediana."""
        arvore = cls(k)

        def montar(lista, prof):
            if not lista:
                return None
            eixo = prof % k
            lista = sorted(lista, key=lambda it: it[0][eixo])
            m = len(lista) // 2
            no = NoKD(lista[m][0], lista[m][1], eixo)
            no.esq = montar(lista[:m], prof + 1)
            no.dir = montar(lista[m + 1:], prof + 1)
            return no

        arvore.raiz = montar(list(itens), 0)
        return arvore

    def inserir(self, ponto, valor):
        if self.raiz is None:
            self.raiz = NoKD(ponto, valor, 0)
            return
        no, prof = self.raiz, 0
        while True:
            if no.ponto == ponto:
                no.valores.append(valor)
                return
            lado = "esq" if ponto[no.eixo] < no.ponto[no.eixo] else "dir"
            prox = getattr(no, lado)
            if prox is None:
                setattr(no, lado, NoKD(ponto, valor, (prof + 1) % self.k))
                return
            no, prof = prox, prof + 1

    def buscar(self, ponto):
        no = self.raiz
        while no:
            if no.ponto == ponto:
                return list(no.valores)
            no = no.esq if ponto[no.eixo] < no.ponto[no.eixo] else no.dir
        return None

    def vizinho_mais_proximo(self, alvo):
        """Retorna (no, distancia, visitados, podados).

        visitados: nós cuja distância foi calculada.
        podados: nós cuja subárvore "do outro lado" foi descartada porque a
        distância até o plano de corte já era maior que a melhor encontrada.
        """
        melhor = [None, math.inf]
        visitados, podados = [], []

        def dist(p):
            return math.dist(p, alvo)

        def visitar(no):
            if no is None:
                return
            visitados.append(no)
            d = dist(no.ponto)
            if d < melhor[1]:
                melhor[0], melhor[1] = no, d
            diff = alvo[no.eixo] - no.ponto[no.eixo]
            perto, longe = (no.esq, no.dir) if diff < 0 else (no.dir, no.esq)
            visitar(perto)
            if abs(diff) < melhor[1]:
                visitar(longe)
            elif longe is not None:
                podados.append(no)

        visitar(self.raiz)
        return melhor[0], melhor[1], visitados, podados

    def altura(self, no="raiz"):
        no = self.raiz if no == "raiz" else no
        if no is None:
            return 0
        return 1 + max(self.altura(no.esq), self.altura(no.dir))
