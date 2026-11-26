"""Testes das invariantes com operações aleatórias.

Execute: python -m unittest testes.test_arvores -v
"""
import random
import unittest

from src.arvore_234 import Arvore234
from src.dados import carregar
from src.kd_tree import ArvoreKD
from src.rubro_negra import ArvoreRubroNegra


class TesteArvoresBalanceadas(unittest.TestCase):
    def _operacoes_aleatorias(self, arvore, semente):
        rng = random.Random(semente)
        referencia = {}
        for _ in range(1500):
            chave = rng.randint(0, 300)
            if rng.random() < 0.6:
                arvore.inserir(chave, f"v{chave}")
                referencia.setdefault(chave, []).append(f"v{chave}")
            else:
                existia = chave in referencia
                self.assertEqual(arvore.remover(chave), existia)
                referencia.pop(chave, None)
            arvore.validar()
        self.assertEqual([k for k, _ in arvore.em_ordem()], sorted(referencia))
        for k, vals in referencia.items():
            self.assertEqual(arvore.buscar(k), vals)

    def test_rubro_negra(self):
        for semente in range(5):
            self._operacoes_aleatorias(ArvoreRubroNegra(), semente)

    def test_234(self):
        for semente in range(5):
            self._operacoes_aleatorias(Arvore234(), semente)

    def test_repetidos(self):
        for arvore in (ArvoreRubroNegra(), Arvore234()):
            arvore.inserir(10, "a")
            arvore.inserir(10, "b")
            self.assertEqual(arvore.buscar(10), ["a", "b"])
            arvore.remover(10, "a")
            self.assertEqual(arvore.buscar(10), ["b"])
            arvore.remover(10, "b")
            self.assertIsNone(arvore.buscar(10))
            arvore.validar()

    def test_conversao_234_para_rn(self):
        arv = Arvore234()
        for k in random.Random(1).sample(range(1000), 200):
            arv.inserir(k, k)
        rn = arv.para_rubro_negra()
        rn.validar()
        self.assertEqual([k for k, _ in rn.em_ordem()], [k for k, _ in arv.em_ordem()])

    def test_catalogo_minimo_21_nos(self):
        rn = ArvoreRubroNegra()
        for p in carregar():
            rn.inserir(p.distancia_al, p)
        self.assertGreaterEqual(len(rn), 21)
        rn.validar()

    def test_kd_vizinho_igual_forca_bruta(self):
        rng = random.Random(0)
        pontos = [(rng.uniform(0, 100), rng.uniform(0, 100)) for _ in range(300)]
        kd = ArvoreKD.construir([(p, i) for i, p in enumerate(pontos)])
        for _ in range(100):
            alvo = (rng.uniform(0, 100), rng.uniform(0, 100))
            _, dist, _, _ = kd.vizinho_mais_proximo(alvo)
            esperado = min(((p[0] - alvo[0]) ** 2 + (p[1] - alvo[1]) ** 2) ** 0.5 for p in pontos)
            self.assertAlmostEqual(dist, esperado)


if __name__ == "__main__":
    unittest.main()
