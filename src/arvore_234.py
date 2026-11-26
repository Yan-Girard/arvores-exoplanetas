"""Árvore 2-3-4 (B-Tree de ordem 4) implementada com nós de múltiplas chaves.

Cada nó tem de 1 a 3 chaves (2-nó, 3-nó ou 4-nó) e, se for interno, de 2 a 4
filhos. Todas as folhas ficam sempre na mesma profundidade.

- Inserção top-down: todo 4-nó encontrado na descida é dividido (split)
  antes de descer, então sempre há espaço na folha.
- Remoção top-down: antes de descer para um filho com só 1 chave, ele recebe
  uma chave por empréstimo de um irmão (rotação) ou por fusão com um irmão.

Elementos repetidos: uma chave por ano; registros com a mesma chave ficam na
lista `valores` paralela às chaves do nó (sem alterar a estrutura).
"""

from .rubro_negra import ArvoreRubroNegra, NoRN, PRETO, VERMELHO


class No234:
    def __init__(self, chaves=None, valores=None, filhos=None):
        self.chaves = chaves if chaves is not None else []
        self.valores = valores if valores is not None else []  # lista de listas
        self.filhos = filhos if filhos is not None else []

    @property
    def folha(self):
        return not self.filhos

    def tipo(self):
        return f"{len(self.chaves) + 1}-nó"


def _posicao(no, chave):
    i = 0
    while i < len(no.chaves) and chave > no.chaves[i]:
        i += 1
    return i


class Arvore234:
    def __init__(self, observador=None):
        self.raiz = None
        self.num_chaves = 0
        self.observador = observador

    def __len__(self):
        return self.num_chaves

    def _passo(self, descricao, destaque=None):
        if self.observador:
            self.observador(self, descricao, destaque or [])

    # ------------------------------------------------------------------ busca
    def _buscar_no(self, chave):
        no = self.raiz
        while no:
            i = _posicao(no, chave)
            if i < len(no.chaves) and no.chaves[i] == chave:
                return no, i
            if no.folha:
                break
            no = no.filhos[i]
        return None, -1

    def buscar(self, chave):
        no, i = self._buscar_no(chave)
        return None if no is None else list(no.valores[i])

    def caminho_busca(self, chave):
        caminho, no = [], self.raiz
        while no:
            caminho.append(list(no.chaves))
            i = _posicao(no, chave)
            if (i < len(no.chaves) and no.chaves[i] == chave) or no.folha:
                break
            no = no.filhos[i]
        return caminho

    def em_ordem(self):
        def visitar(no):
            if no is None:
                return
            for i, chave in enumerate(no.chaves):
                if not no.folha:
                    yield from visitar(no.filhos[i])
                yield chave, list(no.valores[i])
            if not no.folha:
                yield from visitar(no.filhos[-1])

        yield from visitar(self.raiz)

    def intervalo(self, a, b):
        resultado = []

        def visitar(no):
            if no is None:
                return
            for i, chave in enumerate(no.chaves):
                if not no.folha and a < chave:
                    visitar(no.filhos[i])
                if a <= chave <= b:
                    resultado.append((chave, list(no.valores[i])))
            if not no.folha and no.chaves[-1] < b:
                visitar(no.filhos[-1])

        visitar(self.raiz)
        return resultado

    def altura(self):
        h, no = 0, self.raiz
        while no:
            h += 1
            no = no.filhos[0] if no.filhos else None
        return h

    def num_nos(self):
        def contar(no):
            return 0 if no is None else 1 + sum(contar(f) for f in no.filhos)
        return contar(self.raiz)

    # --------------------------------------------------------------- inserção
    def inserir(self, chave, valor=None):
        """Insere com split preventivo. Retorna True se criou uma chave nova."""
        no, i = self._buscar_no(chave)
        if no is not None:
            no.valores[i].append(valor)
            self._passo(f"Chave {chave} repetida: registro anexado "
                        f"(sem alteração estrutural)", [chave])
            return False

        if self.raiz is None:
            self.raiz = No234([chave], [[valor]])
            self.num_chaves += 1
            self._passo(f"Inserir {chave} na raiz", [chave])
            return True

        if len(self.raiz.chaves) == 3:
            nova = No234(filhos=[self.raiz])
            self.raiz = nova
            self._dividir(nova, 0, raiz=True)

        no = self.raiz
        while not no.folha:
            i = _posicao(no, chave)
            if len(no.filhos[i].chaves) == 3:
                self._dividir(no, i)
                if chave > no.chaves[i]:
                    i += 1
            no = no.filhos[i]

        i = _posicao(no, chave)
        no.chaves.insert(i, chave)
        no.valores.insert(i, [valor])
        self.num_chaves += 1
        self._passo(f"Inserir {chave} na folha (agora é um {no.tipo()})", [chave])
        return True

    def _dividir(self, pai, i, raiz=False):
        """Split do 4-nó pai.filhos[i]: a chave do meio sobe para o pai."""
        cheio = pai.filhos[i]
        meio = cheio.chaves[1]
        esq = No234(cheio.chaves[:1], cheio.valores[:1], cheio.filhos[:2])
        dir_ = No234(cheio.chaves[2:], cheio.valores[2:], cheio.filhos[2:])
        pai.chaves.insert(i, meio)
        pai.valores.insert(i, cheio.valores[1])
        pai.filhos[i] = esq
        pai.filhos.insert(i + 1, dir_)
        extra = " (raiz dividida: altura cresce)" if raiz else ""
        self._passo(f"Split do 4-nó {cheio.chaves}: {meio} sobe{extra}", [meio])

    # ---------------------------------------------------------------- remoção
    def remover(self, chave, valor=None):
        no, i = self._buscar_no(chave)
        if no is None:
            return False
        if valor is not None:
            if valor not in no.valores[i]:
                return False
            if len(no.valores[i]) > 1:
                no.valores[i].remove(valor)
                self._passo(f"Chave {chave}: removido um registro repetido "
                            f"(sem alteração estrutural)", [chave])
                return True

        self._remover(self.raiz, chave)
        self.num_chaves -= 1
        if not self.raiz.chaves:
            self.raiz = self.raiz.filhos[0] if self.raiz.filhos else None
            if self.raiz:
                self._passo("Raiz ficou vazia e foi descartada: altura diminui")
        return True

    def _remover(self, no, chave):
        i = _posicao(no, chave)
        if i < len(no.chaves) and no.chaves[i] == chave:
            if no.folha:
                no.chaves.pop(i)
                no.valores.pop(i)
                self._passo(f"Remover {chave} da folha")
                return
            esq, dir_ = no.filhos[i], no.filhos[i + 1]
            if len(esq.chaves) >= 2:
                pk, pv = self._maximo(esq)
                no.chaves[i], no.valores[i] = pk, pv
                self._passo(f"{chave} está em nó interno: substituído pelo "
                            f"predecessor {pk}", [pk])
                self._remover(esq, pk)
            elif len(dir_.chaves) >= 2:
                sk, sv = self._minimo(dir_)
                no.chaves[i], no.valores[i] = sk, sv
                self._passo(f"{chave} está em nó interno: substituído pelo "
                            f"sucessor {sk}", [sk])
                self._remover(dir_, sk)
            else:
                self._fundir(no, i)
                self._remover(esq, chave)
            return

        if no.folha:
            return  # chave não existe
        i = self._garantir_minimo(no, i)
        self._remover(no.filhos[i], chave)

    def _garantir_minimo(self, no, i):
        """Garante que no.filhos[i] tenha >= 2 chaves antes de descer."""
        filho = no.filhos[i]
        if len(filho.chaves) >= 2:
            return i
        if i > 0 and len(no.filhos[i - 1].chaves) >= 2:
            irmao = no.filhos[i - 1]
            filho.chaves.insert(0, no.chaves[i - 1])
            filho.valores.insert(0, no.valores[i - 1])
            no.chaves[i - 1] = irmao.chaves.pop()
            no.valores[i - 1] = irmao.valores.pop()
            if irmao.filhos:
                filho.filhos.insert(0, irmao.filhos.pop())
            self._passo(f"Empréstimo do irmão esquerdo: {no.chaves[i - 1]} sobe, "
                        f"{filho.chaves[0]} desce", [no.chaves[i - 1], filho.chaves[0]])
            return i
        if i < len(no.filhos) - 1 and len(no.filhos[i + 1].chaves) >= 2:
            irmao = no.filhos[i + 1]
            filho.chaves.append(no.chaves[i])
            filho.valores.append(no.valores[i])
            no.chaves[i] = irmao.chaves.pop(0)
            no.valores[i] = irmao.valores.pop(0)
            if irmao.filhos:
                filho.filhos.append(irmao.filhos.pop(0))
            self._passo(f"Empréstimo do irmão direito: {no.chaves[i]} sobe, "
                        f"{filho.chaves[-1]} desce", [no.chaves[i], filho.chaves[-1]])
            return i
        if i < len(no.chaves):
            self._fundir(no, i)
            return i
        self._fundir(no, i - 1)
        return i - 1

    def _fundir(self, no, i):
        """Une filhos[i], chaves[i] e filhos[i+1] em um único 4-nó."""
        esq = no.filhos[i]
        dir_ = no.filhos.pop(i + 1)
        chave = no.chaves.pop(i)
        valor = no.valores.pop(i)
        esq.chaves += [chave] + dir_.chaves
        esq.valores += [valor] + dir_.valores
        esq.filhos += dir_.filhos
        self._passo(f"Fusão: {chave} desce e une os irmãos em {esq.chaves}", [chave])

    @staticmethod
    def _maximo(no):
        while not no.folha:
            no = no.filhos[-1]
        return no.chaves[-1], no.valores[-1]

    @staticmethod
    def _minimo(no):
        while not no.folha:
            no = no.filhos[0]
        return no.chaves[0], no.valores[0]

    # -------------------------------------------------------------- validação
    def validar(self):
        if self.raiz is None:
            assert self.num_chaves == 0
            return True
        profundidades, total = set(), [0]

        def verificar(no, minimo, maximo, prof):
            assert 1 <= len(no.chaves) <= 3, f"nó com {len(no.chaves)} chaves"
            assert len(no.valores) == len(no.chaves)
            assert no.chaves == sorted(no.chaves), "chaves fora de ordem no nó"
            assert minimo is None or no.chaves[0] > minimo, "ordem violada"
            assert maximo is None or no.chaves[-1] < maximo, "ordem violada"
            total[0] += len(no.chaves)
            if no.folha:
                profundidades.add(prof)
                return
            assert len(no.filhos) == len(no.chaves) + 1, "nº de filhos inválido"
            limites = [minimo] + no.chaves + [maximo]
            for j, filho in enumerate(no.filhos):
                verificar(filho, limites[j], limites[j + 1], prof + 1)

        verificar(self.raiz, None, None, 0)
        assert len(profundidades) == 1, "folhas em profundidades diferentes"
        assert total[0] == self.num_chaves, "contagem inconsistente"
        return True

    # ---------------------------------------- equivalência com a Rubro-Negra
    def para_rubro_negra(self):
        """Converte para a Rubro-Negra equivalente.

        2-nó -> nó preto; 3-nó -> preto com 1 filho vermelho;
        4-nó -> preto (chave do meio) com 2 filhos vermelhos.
        """
        rn = ArvoreRubroNegra()
        nil = rn.NIL

        def novo(chave, valores, cor, esq, dir_):
            n = NoRN(chave, list(valores), cor, nil)
            n.esq, n.dir = esq, dir_
            for f in (esq, dir_):
                if f is not nil:
                    f.pai = n
            rn.num_nos += 1
            return n

        def converter(no):
            c = [converter(f) for f in no.filhos] or [nil] * (len(no.chaves) + 1)
            k, v = no.chaves, no.valores
            if len(k) == 1:
                return novo(k[0], v[0], PRETO, c[0], c[1])
            if len(k) == 2:
                verm = novo(k[0], v[0], VERMELHO, c[0], c[1])
                return novo(k[1], v[1], PRETO, verm, c[2])
            e = novo(k[0], v[0], VERMELHO, c[0], c[1])
            d = novo(k[2], v[2], VERMELHO, c[2], c[3])
            return novo(k[1], v[1], PRETO, e, d)

        if self.raiz:
            rn.raiz = converter(self.raiz)
            rn.raiz.pai = nil
        return rn
