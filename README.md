# Árvores Balanceadas aplicadas a um Catálogo de Exoplanetas

Implementação, em Python puro, de **Árvore Rubro-Negra**, **Árvore 2-3-4** e
**Árvore k-D**, aplicadas a um catálogo de exoplanetas. Nenhuma biblioteca de
árvores é usada: todas as estruturas são feitas do zero, com nós encadeados.
O `matplotlib` serve só para plotar.

| Árvore | Chave | Consulta resolvida | Operações |
|---|---|---|---|
| Rubro-Negra | distância da Terra (anos-luz) | busca exata e por intervalo de distância | inserção + balanceamento, remoção + balanceamento, busca |
| 2-3-4 | ano de descoberta | busca por ano e por intervalo de anos | inserção + split, remoção + empréstimo/fusão, busca |
| k-D (k=2) | (ascensão reta, declinação) | planeta mais próximo de um ponto do céu | construção pela mediana, inserção, busca, vizinho mais próximo (demonstração) |

O catálogo (`dados/exoplanetas.csv`) tem **35 exoplanetas**, e a Rubro-Negra
fica com **34 nós** (o mínimo exigido é 21). Os valores são aproximados e servem
apenas para fins didáticos.

---

## Como executar

Requisitos: Python 3.10+.

```bash
git clone <url-do-repositorio>
cd arvores-exoplanetas
pip install -r requirements.txt
```

**Menu interativo** (inserir, remover, buscar, plotar, modo passo a passo):

```bash
python -m src.main
```

**Demos prontas para a apresentação** (geram imagens e GIFs em `saida/`):

```bash
python -m demos.demo_rubro_negra    # casos de inserção/remoção, repetidos, busca
python -m demos.demo_234            # split, empréstimo, fusão, raiz encolhendo
python -m demos.demo_kd             # exemplo didático + vizinho mais próximo no céu
python -m demos.demo_equivalencia   # 2-3-4 convertida na Rubro-Negra equivalente
```

**Testes** (milhares de inserções/remoções aleatórias, validando as propriedades
a cada operação):

```bash
python -m unittest testes.test_arvores -v
```

> Todos os comandos são executados a partir da pasta raiz do projeto.

---

## Estrutura

```
├── dados/exoplanetas.csv
├── src/
│   ├── rubro_negra.py     # Rubro-Negra (nós com pai/esq/dir + sentinela NIL)
│   ├── arvore_234.py      # 2-3-4 (nós com até 3 chaves e 4 filhos) + conversão p/ RN
│   ├── kd_tree.py         # k-D 2D (construção, inserção, busca, vizinho mais próximo)
│   ├── visualizacao.py    # desenho das árvores, gravação passo a passo, GIF
│   ├── dados.py           # leitura do CSV
│   └── main.py            # menu interativo
├── demos/                 # scripts de demonstração
├── testes/                # testes automatizados das invariantes
└── docs/apresentacao.md   # roteiro e conceitos para a apresentação
```

---

## Método de inserção e de tratamento de elementos repetidos

**Inserção:** segue a regra da árvore de busca: chaves menores vão para a
esquerda e maiores para a direita. Na 2-3-4, a chave entra na posição ordenada
dentro do nó.

**Repetidos: um nó por chave, com uma lista de registros.** Cada nó (ou cada
chave, na 2-3-4) guarda uma lista `valores`.

- **Inserir uma chave que já existe:** o registro é anexado à lista. Nenhum nó
  é criado, a estrutura não muda e **não há balanceamento**. Exemplo: TRAPPIST-1 e
  e TRAPPIST-1 f estão ambos a 40,7 anos-luz, então ficam no mesmo nó (`×2` no gráfico).
- **Remover um registro:** se a chave tem mais de um registro, só aquele sai
  da lista. O nó é excluído (com rebalanceamento) apenas quando a lista fica vazia.
- **k-D:** um empate na coordenada do eixo de corte vai para a **direita**. Um
  ponto idêntico tem o registro anexado ao nó já existente.

Por que essa escolha: o catálogo tem muitas chaves repetidas (vários planetas
descobertos no mesmo ano). Duplicar nós aumentaria a altura sem necessidade e
complicaria a remoção.

---

## Estruturas de dados auxiliares

- **Listas do Python** guardam os registros repetidos de cada nó e, na 2-3-4,
  as chaves e os filhos de cada nó (no máximo 3 e 4 elementos).
- **Pilha** (lista) no percurso em ordem iterativo da Rubro-Negra.
- **Sentinela NIL**: um único nó preto representa todas as folhas nulas da
  Rubro-Negra, o que evita testes de `None` nas rotações.

---

## Comparação dos métodos de balanceamento

| | Rubro-Negra | 2-3-4 | k-D |
|---|---|---|---|
| Ideia | cores + rotações mantêm a altura preta igual em todos os caminhos | nós crescem/encolhem (1–3 chaves); folhas sempre no mesmo nível | divide o espaço pela mediana, alternando o eixo |
| Inserção | nó vermelho; corrige com recoloração (tio vermelho) ou 1–2 rotações | split preventivo de 4-nós na descida; cresce pela raiz | sem rebalanceamento (só desce até uma folha) |
| Remoção | casos do “duplo preto” (até 3 rotações) | empréstimo do irmão ou fusão na descida; encolhe pela raiz | normalmente reconstrói a subárvore |
| Altura | ≤ 2·log₂(n+1) | ≤ log₂(n+1) | ≈ log₂ n se construída pela mediana |
| Busca | O(log n) | O(log n) | exata O(log n); vizinho mais próximo ~O(log n) em média |

Uma Rubro-Negra é exatamente uma 2-3-4 representada com nós binários: um nó preto
somado aos seus filhos vermelhos forma um nó da 2-3-4. Veja `demo_equivalencia`.

**Simplificação na k-D:** a distância no céu é calculada como distância
euclidiana no plano (AR × Dec), sem considerar a curvatura da esfera celeste.
