"""Demo: toda 2-3-4 corresponde a uma Rubro-Negra.

Execute: python -m demos.demo_equivalencia
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.dados import carregar
from src.arvore_234 import Arvore234
from src import visualizacao as vis

SAIDA = Path(__file__).resolve().parent.parent / "saida" / "demo_equivalencia"

arv = Arvore234()
for p in carregar():
    arv.inserir(p.ano, p)
rn = arv.para_rubro_negra()
rn.validar()

fig, (a1, a2) = plt.subplots(2, 1, figsize=(13, 8))
vis.desenhar_234(arv, "Árvore 2-3-4 (chave = ano)", ax=a1)
vis.desenhar_rn(rn, "Rubro-Negra equivalente: 2-nó = preto | 3-nó = preto + 1 vermelho | "
                    "4-nó = preto + 2 vermelhos", ax=a2)
vis.salvar(fig, SAIDA / "equivalencia.png")
print(f"Conversão válida ({len(rn)} nós). Imagem em {SAIDA / 'equivalencia.png'}")
