"""Demo da 2-3-4: inserção com split, repetidos, remoção com empréstimo/fusão.

Execute: python -m demos.demo_234
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

from src.dados import carregar
from src.arvore_234 import Arvore234
from src import visualizacao as vis

SAIDA = Path(__file__).resolve().parent.parent / "saida" / "demo_234"

planetas = carregar()

print("== 1) Inserção passo a passo (chave = ano de descoberta) ==")
arv = Arvore234(observador=vis.GravadorPassos(SAIDA / "insercao"))
for p in planetas[:12]:
    arv.inserir(p.ano, p)
arv.observador = None
for p in planetas[12:]:
    arv.inserir(p.ano, p)
arv.validar()
vis.salvar(vis.desenhar_234(arv), SAIDA / "arvore_completa.png")
print(f"\nÁrvore completa: {len(arv)} chaves em {arv.num_nos()} nós, altura {arv.altura()}")

print("\n== 2) Busca ==")
print("  nós visitados até 2011:", arv.caminho_busca(2011))
print("  descobertos em 2011:", [p.nome for p in arv.buscar(2011)])
print("  entre 1995 e 2000:", [p.nome for _, regs in arv.intervalo(1995, 2000) for p in regs])

print("\n== 3) Remoção ==")
arv.observador = vis.GravadorPassos(SAIDA / "remocao")
alvo = arv.buscar(2017)[0]
print(f" remover só um registro de 2017 ({alvo.nome}):")
arv.remover(2017, alvo)
# Sequência escolhida para mostrar: empréstimo (esq. e dir.), fusão,
# substituição por predecessor/sucessor e a raiz sendo descartada.
for ano in (2015, 2016, 2017, 2008, 2009, 2007, 2005, 2004, 2000, 1999, 2011):
    print(f" remover chave {ano}:")
    arv.remover(ano)
    arv.validar()
arv.observador = None
vis.salvar(vis.desenhar_234(arv, "Após as remoções"), SAIDA / "apos_remocoes.png")

for sub in ("insercao", "remocao"):
    vis.gerar_gif(SAIDA / sub, SAIDA / f"{sub}.gif")
print(f"\nImagens e GIFs em {SAIDA}")
