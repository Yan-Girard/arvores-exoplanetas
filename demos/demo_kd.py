"""Demo da k-D: exemplo didático 2D e aplicação no céu (vizinho mais próximo).

Execute: python -m demos.demo_kd
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

from src.dados import carregar
from src.kd_tree import ArvoreKD
from src import visualizacao as vis

SAIDA = Path(__file__).resolve().parent.parent / "saida" / "demo_kd"

print("== 1) Exemplo didático: 6 pontos no plano ==")
pontos = [(2, 3), (5, 4), (9, 6), (4, 7), (8, 1), (7, 2)]
kd = ArvoreKD.construir([(p, None) for p in pontos])
alvo = (9, 2)
no, dist, visitados, podados = kd.vizinho_mais_proximo(alvo)
print(f"  raiz: {kd.raiz.ponto} | vizinho mais próximo de {alvo}: {no.ponto} (dist {dist:.2f})")
print(f"  visitados: {[n.ponto for n in visitados]} | podas em: {[n.ponto for n in podados]}")
vis.salvar(vis.desenhar_kd(kd, alvo, (no, dist), visitados, podados,
                           f"Exemplo didático: vizinho mais próximo de {alvo}",
                           limites=(0, 10, 0, 10), rotulos_eixos=("x", "y")),
           SAIDA / "exemplo_didatico.png")

print("\n== 2) Aplicação: planeta mais próximo de um ponto do céu ==")
planetas = carregar()
kd = ArvoreKD.construir([(p.coordenadas, p) for p in planetas])
alvo = (292.0, 46.0)  # região do campo de visão do telescópio Kepler
no, dist, visitados, podados = kd.vizinho_mais_proximo(alvo)
print(f"  mais próximo de {alvo}: {no.valores[0].nome} (dist {dist:.2f}°)")
print(f"  visitou {len(visitados)} de {len(planetas)} planetas ({len(podados)} podas)")
vis.salvar(vis.desenhar_kd(kd, alvo, (no, dist), visitados, podados,
                           f"Catálogo no céu: vizinho mais próximo de AR={alvo[0]}°, Dec={alvo[1]}°"),
           SAIDA / "ceu_vizinho.png")
print(f"\nImagens em {SAIDA}")
