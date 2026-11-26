# Roteiro da apresentação (cerca de 12 min)

| Tempo | Bloco | O que mostrar |
|---|---|---|
| 0:00–1:00 | Problema | catálogo de exoplanetas, as 3 consultas, por que árvores balanceadas |
| 1:00–5:00 | Rubro-Negra | propriedades, rotação, casos de inserção e remoção (`saida/demo_rubro_negra/*.gif`), repetidos, árvore com 34 nós |
| 5:00–8:30 | 2-3-4 | tipos de nó, split, empréstimo e fusão (`saida/demo_234/*.gif`), equivalência com a RN (`demo_equivalencia`) |
| 8:30–10:30 | k-D | construção pela mediana, partições do plano e vizinho mais próximo com poda (`saida/demo_kd`) |
| 10:30–12:00 | Fechamento | tabela comparativa dos balanceamentos, menu `python -m src.main` ao vivo, repositório |

Para a demonstração ao vivo, use o menu: opção 13 (passo a passo), opção 6
(inserir um planeta), opção 7 (remover), opção 8 ou 9 (plotar) e opção 12 (validar).

---

## 1. Árvore Rubro-Negra

É uma árvore binária de busca em que cada nó é **vermelho** ou **preto**, com 5 propriedades:

1. Todo nó é vermelho ou preto.
2. A raiz é preta.
3. Toda folha (NIL) é preta.
4. Um nó vermelho não tem filho vermelho.
5. Todo caminho de um nó até as folhas abaixo dele passa pelo mesmo número de nós pretos (a **altura preta**).

Consequência: o caminho mais longo (alternando preto e vermelho) tem no máximo o
dobro do mais curto (só pretos). Por isso a altura fica ≤ 2·log₂(n+1).

**Rotação** (esquerda ou direita): reorganiza três ponteiros, preserva a ordem
da árvore de busca e custa O(1).

### Inserção
O novo nó entra **vermelho**, o que não altera a altura preta. O único problema
possível é vermelho com vermelho (propriedade 4). Os casos dependem do **tio**:

| Caso | Situação | Ação |
|---|---|---|
| 1 | tio vermelho | pai e tio ficam pretos, avô fica vermelho; o problema sobe para o avô |
| 2 | tio preto, nó em “triângulo” | rotação no pai, o que transforma no caso 3 |
| 3 | tio preto, nó em “linha” | pai fica preto, avô fica vermelho, rotação no avô; fim |

No final, a raiz é pintada de preto.

### Remoção
Se o nó tem dois filhos, ele é trocado pelo **sucessor**. Quando o nó removido
era preto, um caminho perde um preto. O nó que assume o lugar carrega então um
“**duplo preto**”, resolvido pelos casos do **irmão** `w`:

| Caso | Situação | Ação |
|---|---|---|
| 1 | irmão vermelho | recolorir e rotacionar no pai, o que deixa o irmão preto |
| 2 | irmão preto, sobrinhos pretos | irmão fica vermelho; o duplo preto sobe para o pai |
| 3 | irmão preto, sobrinho próximo vermelho | rotação no irmão, o que transforma no caso 4 |
| 4 | irmão preto, sobrinho distante vermelho | rotação no pai e recoloração; fim |

---

## 2. Árvore 2-3-4 (não binária)

Cada nó tem 1, 2 ou 3 chaves (**2-nó, 3-nó, 4-nó**) e, se for interno,
2, 3 ou 4 filhos. **Todas as folhas ficam na mesma profundidade**: a árvore
é perfeitamente balanceada em altura. É uma B-Tree de ordem 4.

- **Inserção (top-down):** ao descer, todo 4-nó encontrado é **dividido**
  (a chave do meio sobe para o pai). Assim a folha sempre tem espaço. A
  árvore só cresce em altura quando a **raiz** é dividida.
- **Remoção (top-down):** antes de descer para um filho com 1 chave, ele
  recebe uma chave:
  - por **empréstimo** de um irmão com 2 ou mais chaves (uma chave do pai desce e uma do irmão sobe, como uma rotação); ou
  - por **fusão** com um irmão (uma chave do pai desce e une os dois em um 4-nó).

  Uma chave em nó interno é trocada pelo predecessor ou pelo sucessor. A árvore
  só perde altura quando a raiz fica vazia.

**Equivalência com a Rubro-Negra:** um 2-nó corresponde a um nó preto; um
3-nó, a um nó preto com um filho vermelho; um 4-nó, a um nó preto com dois filhos
vermelhos. O split da 2-3-4 corresponde à recoloração do caso 1 da RN, e os casos de
rotação correspondem a escolher qual chave do 3-nó ou 4-nó fica no topo.

---

## 3. Árvore k-D (explicação com exemplo)

É uma árvore binária para pontos em **k dimensões**. Cada nível divide o
espaço por um eixo diferente, de forma alternada: com k = 2, o nível 0 corta em `x`,
o nível 1 em `y`, o nível 2 em `x` de novo, e assim por diante. Cada nó é um ponto e define
um hiperplano de corte: os pontos com coordenada menor no eixo do nível vão para a
esquerda, e os maiores ou iguais vão para a direita.

**Balanceamento:** a k-D não usa rotações (uma rotação quebraria a alternância
dos eixos). O balanceamento acontece na **construção**: em cada nível, a raiz
da subárvore é a **mediana** dos pontos naquele eixo, o que gera altura ≈ log₂ n.
Depois de muitas inserções ou remoções, a solução comum é **reconstruir**.

### Exemplo (`demo_kd`, figura `exemplo_didatico.png`)
Pontos: (2,3), (5,4), (9,6), (4,7), (8,1), (7,2)

1. Nível 0 (eixo x): ordenando por x, temos 2, 4, 5, **7**, 8, 9. A mediana é (7,2), que vira a **raiz**.
   - Esquerda (x < 7): (2,3), (5,4), (4,7). Direita (x ≥ 7): (8,1), (9,6).
2. Nível 1 (eixo y), à esquerda: ordenando por y, temos 3, **4**, 7. A raiz é (5,4), com (2,3) à esquerda e (4,7) à direita.
3. Nível 1 (eixo y), à direita: ordenando por y, temos 1, **6**. A raiz é (9,6), com (8,1) à esquerda.

```
            (7,2) [x]
           /         \
      (5,4) [y]     (9,6) [y]
      /     \        /
  (2,3)   (4,7)   (8,1)
```

### Vizinho mais próximo de (9, 2)
1. Desce pelo lado do alvo: (7,2) → como 9 ≥ 7, vai para a direita, chega a (9,6) → como 2 < 6, vai para a esquerda, chega a (8,1).
   A melhor distância até aqui é d((8,1), (9,2)) = √2 ≈ 1,41.
2. Volta para (9,6): d = 4, então não melhora. Do outro lado não há filho.
3. Volta para (7,2): d = 2, então não melhora. A distância do alvo até o plano de corte x = 7 é
   |9 − 7| = 2, maior que 1,41. Logo, nenhum ponto à esquerda pode estar mais perto: **poda**,
   e a subárvore esquerda inteira é ignorada.
4. Resposta: **(8,1)**, após visitar só 3 dos 6 nós.

Na aplicação (`ceu_vizinho.png`), o alvo AR = 292°, Dec = 46° (campo do telescópio
Kepler) encontra o **Kepler-22 b** visitando 6 dos 35 planetas.
