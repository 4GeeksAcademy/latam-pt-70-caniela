from enum import Enum as pyEnum

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Date, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }


class Torneo(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(90), unique=True, nullable=True)

    sede: Mapped[str] = mapped_column(String(120), nullable=False)

    fecha_inicio: Mapped[Date] = mapped_column(Date())
    fecha_final: Mapped[Date] = mapped_column(Date())

    premios: Mapped[list["Premios"]] = relationship(
        back_populates="torneo", cascade="all, delete-orphan")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "sede": self.sede,
            "finicio": self.fecha_inicio,
            "ffinal": self.fecha_final,

            "premios": [premio.serialize() for premio in self.premios]
        }


class Subscripciones(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped[User] = relationship()

    torneo_id: Mapped[int] = mapped_column(ForeignKey("torneo.id"))
    torneo: Mapped[Torneo] = relationship()


class Resultado(pyEnum):
    EMPATE = 0
    GANA_LOCAL = 1
    GANA_VISITANTE = 2


class Partidos(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)

    equipo_local: Mapped[str] = mapped_column(String(120))
    equipo_visitante: Mapped[str] = mapped_column(String(120))
    fecha: Mapped[Date] = mapped_column(Date())
    etapa: Mapped[str] = mapped_column(String(24))

    resultado: Mapped[Resultado] = mapped_column(Enum(Resultado))

    torneo_id: Mapped[int] = mapped_column(ForeignKey("torneo.id"))
    torneo: Mapped[Torneo] = relationship()


class Premios(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120))
    descripcion: Mapped[str] = mapped_column(String(360))

    torneo_id: Mapped[int] = mapped_column(ForeignKey("torneo.id"))
    torneo: Mapped[Torneo] = relationship(back_populates="premios")

    def serialize(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
        }


class Prediccion(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)

    user_prediction: Mapped[Resultado] = mapped_column(Enum(Resultado))

    partido_id: Mapped[int] = mapped_column(ForeignKey("partidos.id"))
    partido: Mapped[Partidos] = relationship()

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped[User] = relationship()
