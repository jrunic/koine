from dataclasses import dataclass


@dataclass
class Usuario:
    nome: str = ""
    idioma: str = ""
    timezone: str = ""

    @classmethod
    def from_fm(cls, fm: dict) -> "Usuario":
        return cls(nome=fm.get("nome", ""), idioma=fm.get("idioma", ""),
                   timezone=fm.get("timezone", ""))


@dataclass
class Escopo:
    nome: str = ""
    pasta_referencias: str = ""

    @classmethod
    def from_fm(cls, fm: dict) -> "Escopo":
        return cls(nome=fm.get("nome", ""),
                   pasta_referencias=fm.get("pasta-referencias", ""))


@dataclass
class Dominio:
    title: str = ""
    sinopse: str = ""

    @classmethod
    def from_fm(cls, fm: dict) -> "Dominio":
        return cls(title=fm.get("title", ""), sinopse=fm.get("sinopse", ""))
