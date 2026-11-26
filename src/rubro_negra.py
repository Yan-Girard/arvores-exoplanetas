"""Árvore Rubro-Negra (Red-Black Tree) implementada com nós encadeados.

Cada nó guarda ponteiros para pai, filho esquerdo e filho direito (estilo lista
duplamente encadeada). Um único nó sentinela NIL (preto) representa todas as
folhas nulas, o que simplifica as rotações e os casos de remoção.

Elementos repetidos: um nó por chave. Se a chave já existe, o novo registro é
anexado à lista `valores` do nó, sem alterar a estrutura (não há balanceamento).
"""

VERMELHO = "VERMELHO"
PRETO = "PRETO"


class NoRN:
    def __init__(self, chave=None, valores=None, cor=VERMELHO, nil=None):
        self.chave = chave
        self.valores = valores if valores is not None else []
        self.cor = cor
        self.esq = nil
        self.dir = nil
        self.pai = nil


class ArvoreRubroNegra:
    def __init__(self, observador=None):
        self.NIL = NoRN(cor=PRETO)
        self.NIL.esq = self.NIL.dir = self.NIL.pai = self.NIL
        self.raiz = self.NIL
        self.num_nos = 0
        # observador(arvore, descricao, destaque) é chamado a cada passo
        # importante (inserção, recoloração, rotação...). Usado para plotar.
        self.observador = observador

    def __len__(self):
        return self.num_nos

    def _passo(self, descricao, destaque=None):
        if self.observador:
            self.observador(self, descricao, destaque or [])

    # ------------------------------------------------------------------ busca
    def _buscar_no(self, chave):
        x = self.raiz
        while x is not self.NIL and chave != x.chave:
            x = x.esq if chave < x.chave else x.dir
        return x

    def buscar(self, chave):
        """Retorna a lista de registros com a chave, ou None."""
        no = self._buscar_no(chave)
        return None if no is self.NIL else list(no.valores)

    def caminho_busca(self, chave):
        """Chaves visitadas até encontrar (ou não) a chave."""
        caminho, x = [], self.raiz
        while x is not self.NIL:
            caminho.append(x.chave)
            if chave == x.chave:
                break
            x = x.esq if chave < x.chave else x.dir
        return caminho

    def intervalo(self, a, b):
        """Lista (chave, valores) com a <= chave <= b, em ordem."""
        resultado = []

        def visitar(no):
            if no is self.NIL:
                return
            if a < no.chave:
                visitar(no.esq)
            if a <= no.chave <= b:
                resultado.append((no.chave, list(no.valores)))
            if no.chave < b:
                visitar(no.dir)

        visitar(self.raiz)
        return resultado

    def em_ordem(self):
        pilha, x = [], self.raiz
        while pilha or x is not self.NIL:
            while x is not self.NIL:
                pilha.append(x)
                x = x.esq
            x = pilha.pop()
            yield x.chave, list(x.valores)
            x = x.dir

    def altura(self, no=None):
        no = self.raiz if no is None else no
        if no is self.NIL:
            return 0
        return 1 + max(self.altura(no.esq), self.altura(no.dir))

    # --------------------------------------------------------------- rotações
    def _rotacionar_esquerda(self, x):
        y = x.dir
        x.dir = y.esq
        if y.esq is not self.NIL:
            y.esq.pai = x
        y.pai = x.pai
        if x.pai is self.NIL:
            self.raiz = y
        elif x is x.pai.esq:
            x.pai.esq = y
        else:
            x.pai.dir = y
        y.esq = x
        x.pai = y

    def _rotacionar_direita(self, x):
        y = x.esq
        x.esq = y.dir
        if y.dir is not self.NIL:
            y.dir.pai = x
        y.pai = x.pai
        if x.pai is self.NIL:
            self.raiz = y
        elif x is x.pai.dir:
            x.pai.dir = y
        else:
            x.pai.esq = y
        y.dir = x
        x.pai = y

    # --------------------------------------------------------------- inserção
    def inserir(self, chave, valor=None):
        """Insere e rebalanceia. Retorna True se criou um nó novo."""
        y, x = self.NIL, self.raiz
        while x is not self.NIL:
            y = x
            if chave == x.chave:
                x.valores.append(valor)
                self._passo(f"Chave {chave} repetida: registro anexado ao nó "
                            f"(sem balanceamento)", [chave])
                return False
            x = x.esq if chave < x.chave else x.dir

        z = NoRN(chave, [valor], VERMELHO, self.NIL)
        z.pai = y
        if y is self.NIL:
            self.raiz = z
        elif chave < y.chave:
            y.esq = z
        else:
            y.dir = z
        self.num_nos += 1
        self._passo(f"Inserir {chave} como nó VERMELHO", [chave])
        self._corrigir_insercao(z)
        return True

    def _corrigir_insercao(self, z):
        while z.pai.cor == VERMELHO:
            pai, avo = z.pai, z.pai.pai
            lado_esq = pai is avo.esq
            tio = avo.dir if lado_esq else avo.esq

            if tio.cor == VERMELHO:
                # Caso 1: tio vermelho -> recolorir e subir o problema
                pai.cor = tio.cor = PRETO
                avo.cor = VERMELHO
                self._passo(f"Caso 1 (tio {tio.chave} vermelho): recolorir "
                            f"pai, tio e avô", [pai.chave, tio.chave, avo.chave])
                z = avo
                continue

            # Caso 2: "triângulo" -> rotação no pai para virar "linha"
            if lado_esq and z is pai.dir:
                self._rotacionar_esquerda(pai)
                self._passo(f"Caso 2 (triângulo): rotação à esquerda em {pai.chave}",
                            [pai.chave, z.chave])
                z, pai = pai, z
            elif not lado_esq and z is pai.esq:
                self._rotacionar_direita(pai)
                self._passo(f"Caso 2 (triângulo): rotação à direita em {pai.chave}",
                            [pai.chave, z.chave])
                z, pai = pai, z

            # Caso 3: "linha" -> recolorir e rotação no avô
            pai.cor = PRETO
            avo.cor = VERMELHO
            if lado_esq:
                self._rotacionar_direita(avo)
                sentido = "direita"
            else:
                self._rotacionar_esquerda(avo)
                sentido = "esquerda"
            self._passo(f"Caso 3 (linha): recolorir e rotação à {sentido} "
                        f"em {avo.chave}", [pai.chave, avo.chave])

        if self.raiz.cor == VERMELHO:
            self.raiz.cor = PRETO
            self._passo(f"Raiz {self.raiz.chave} recolorida para PRETO",
                        [self.raiz.chave])

    # ---------------------------------------------------------------- remoção
    def remover(self, chave, valor=None):
        """Remove a chave (ou só um registro dela, se houver repetidos).

        - valor=None: remove o nó inteiro.
        - valor dado: remove só esse registro; o nó sai quando a lista esvazia.
        """
        z = self._buscar_no(chave)
        if z is self.NIL:
            return False
        if valor is not None:
            if valor not in z.valores:
                return False
            if len(z.valores) > 1:
                z.valores.remove(valor)
                self._passo(f"Chave {chave}: removido um registro repetido "
                            f"(nó permanece, sem balanceamento)", [chave])
                return True
        self._remover_no(z)
        self.num_nos -= 1
        return True

    def _transplantar(self, u, v):
        if u.pai is self.NIL:
            self.raiz = v
        elif u is u.pai.esq:
            u.pai.esq = v
        else:
            u.pai.dir = v
        v.pai = u.pai

    def _minimo(self, x):
        while x.esq is not self.NIL:
            x = x.esq
        return x

    def _remover_no(self, z):
        chave = z.chave
        y, cor_original = z, z.cor
        if z.esq is self.NIL:
            x = z.dir
            self._transplantar(z, z.dir)
            info = ""
        elif z.dir is self.NIL:
            x = z.esq
            self._transplantar(z, z.esq)
            info = ""
        else:
            y = self._minimo(z.dir)  # sucessor
            cor_original = y.cor
            x = y.dir
            if y.pai is z:
                x.pai = y
            else:
                self._transplantar(y, y.dir)
                y.dir = z.dir
                y.dir.pai = y
            self._transplantar(z, y)
            y.esq = z.esq
            y.esq.pai = y
            y.cor = z.cor
            info = f" (substituído pelo sucessor {y.chave})"

        self._passo(f"Remover {chave}{info}", [y.chave] if y is not z else [])
        if cor_original == PRETO:
            self._corrigir_remocao(x)
        self.NIL.pai = self.NIL

    def _corrigir_remocao(self, x):
        # x carrega um "preto extra" (duplo preto) até o problema ser resolvido
        while x is not self.raiz and x.cor == PRETO:
            lado_esq = x is x.pai.esq
            pai = x.pai
            w = pai.dir if lado_esq else pai.esq  # irmão

            if w.cor == VERMELHO:
                # Caso 1: irmão vermelho -> rotação para obter irmão preto
                w.cor = PRETO
                pai.cor = VERMELHO
                if lado_esq:
                    self._rotacionar_esquerda(pai)
                    w = pai.dir
                else:
                    self._rotacionar_direita(pai)
                    w = pai.esq
                self._passo(f"Remoção caso 1 (irmão vermelho): recolorir e "
                            f"rotacionar em {pai.chave}", [pai.chave])

            perto, longe = (w.esq, w.dir) if lado_esq else (w.dir, w.esq)
            if perto.cor == PRETO and longe.cor == PRETO:
                # Caso 2: irmão preto com filhos pretos -> recolorir e subir
                w.cor = VERMELHO
                self._passo(f"Remoção caso 2 (irmão {w.chave} preto, sobrinhos "
                            f"pretos): irmão fica vermelho, sobe o duplo preto",
                            [w.chave])
                x = pai
                continue

            if longe.cor == PRETO:
                # Caso 3: sobrinho próximo vermelho -> rotação no irmão
                perto.cor = PRETO
                w.cor = VERMELHO
                if lado_esq:
                    self._rotacionar_direita(w)
                    w = pai.dir
                else:
                    self._rotacionar_esquerda(w)
                    w = pai.esq
                self._passo(f"Remoção caso 3 (sobrinho próximo vermelho): "
                            f"rotação no irmão", [w.chave])

            # Caso 4: sobrinho distante vermelho -> rotação no pai, fim
            w.cor = pai.cor
            pai.cor = PRETO
            longe = w.dir if lado_esq else w.esq
            longe.cor = PRETO
            if lado_esq:
                self._rotacionar_esquerda(pai)
            else:
                self._rotacionar_direita(pai)
            self._passo(f"Remoção caso 4 (sobrinho distante vermelho): "
                        f"rotação em {pai.chave}, árvore balanceada",
                        [pai.chave, w.chave])
            x = self.raiz

        if x.cor != PRETO:
            x.cor = PRETO
            if x is not self.NIL:
                self._passo(f"Nó {x.chave} recolorido para PRETO", [x.chave])

    # -------------------------------------------------------------- validação
    def validar(self):
        """Verifica as 5 propriedades. Lança AssertionError se violadas."""
        assert self.raiz.cor == PRETO, "raiz deve ser preta"
        assert self.NIL.cor == PRETO, "folhas (NIL) devem ser pretas"
        contador = [0]

        def verificar(no, minimo, maximo):
            if no is self.NIL:
                return 1
            contador[0] += 1
            assert minimo is None or no.chave > minimo, "ordem de BST violada"
            assert maximo is None or no.chave < maximo, "ordem de BST violada"
            if no.cor == VERMELHO:
                assert no.esq.cor == PRETO and no.dir.cor == PRETO, \
                    f"nó vermelho {no.chave} com filho vermelho"
            for filho in (no.esq, no.dir):
                assert filho is self.NIL or filho.pai is no, "ponteiro pai errado"
            he = verificar(no.esq, minimo, no.chave)
            hd = verificar(no.dir, no.chave, maximo)
            assert he == hd, f"altura preta diferente em {no.chave}"
            return he + (1 if no.cor == PRETO else 0)

        verificar(self.raiz, None, None)
        assert contador[0] == self.num_nos, "contagem de nós inconsistente"
        return True
