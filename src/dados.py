"""Leitura do catálogo de exoplanetas (CSV)."""

import csv
from dataclasses import dataclass
from pathlib import Path

CAMINHO_PADRAO = Path(__file__).resolve().parent.parent / "dados" / "exoplanetas.csv"


@dataclass(frozen=True)
class Exoplaneta:
    nome: str
    distancia_al: float
    ano: int
    ascensao_reta: float
    declinacao: float
    metodo: str

    @property
    def coordenadas(self):
        return (self.ascensao_reta, self.declinacao)

    def __str__(self):
        return (f"{self.nome:<20} {self.distancia_al:>8.1f} al  {self.ano}  "
                f"(AR {self.ascensao_reta:6.1f}°, Dec {self.declinacao:+6.1f}°)  "
                f"{self.metodo}")


def carregar(caminho=CAMINHO_PADRAO):
    with open(caminho, encoding="utf-8") as f:
        return [Exoplaneta(l["nome"], float(l["distancia_al"]),
                           int(l["ano_descoberta"]), float(l["ascensao_reta"]),
                           float(l["declinacao"]), l["metodo"])
                for l in csv.DictReader(f)]
