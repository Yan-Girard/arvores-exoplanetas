"""Demo da Rubro-Negra: inserção passo a passo, repetidos, remoção e busca.

Execute: python -m demos.demo_rubro_negra
"""
import random
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

from src.dados import carregar
from src.rubro_negra import ArvoreRubroNegra
from src import visualizacao as vis

SAIDA = Path(__file__).resolve().parent.parent / "saida" / "demo_rubro_negra"

planetas = carregar()
repetido = next(p for p in planetas if p.nome == "TRAPPIST-1 f")
demais = [p for p in planetas if p is not repetido]
random.Random(3).shuffle(demais)  # ordem fixa que exercita todos os casos

print("== 1) Inserção passo a passo dos 10 primeiros ==")
rn = ArvoreRubroNegra(observador=vis.GravadorPassos(SAIDA / "insercao"))
for p in demais[:10]:
    rn.inserir(p.distancia_al, p)

rn.observador = None
for p in demais[10:]:
    rn.inserir(p.distancia_al, p)

print("\n== 2) Elemento repetido ==")
rn.observador = vis.GravadorPassos(SAIDA / "repetido")
rn.inserir(repetido.distancia_al, repetido)
print("  registros com chave 40.7:", [p.nome for p in rn.buscar(40.7)])

rn.observador = None
vis.salvar(vis.desenhar_rn(rn), SAIDA / "arvore_completa.png")
rn.validar()
print(f"\nÁrvore completa: {len(rn)} nós, altura {rn.altura()} -> {SAIDA / 'arvore_completa.png'}")

print("\n== 3) Busca ==")
print("  caminho até 635:", " -> ".join(vis.fmt(c) for c in rn.caminho_busca(635.0)))
print("  intervalo [10, 25] al:", [p.nome for _, regs in rn.intervalo(10, 25) for p in regs])

print("\n== 4) Remoção passo a passo ==")
rn.observador = vis.GravadorPassos(SAIDA / "remocao")
for chave in (rn.raiz.chave, 4.2, 6.0, 11.0, 133.0):
    print(f" remover {chave}:")
    rn.remover(chave)
    rn.validar()
rn.observador = None
vis.salvar(vis.desenhar_rn(rn, "Após as remoções"), SAIDA / "apos_remocoes.png")

for sub in ("insercao", "remocao"):
    vis.gerar_gif(SAIDA / sub, SAIDA / f"{sub}.gif")
print(f"\nImagens e GIFs em {SAIDA}")
