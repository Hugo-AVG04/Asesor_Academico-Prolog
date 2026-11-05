"""Adaptador entre la interfaz y el motor de inferencia SWI-Prolog."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


ARCHIVO_PROLOGICO = Path(__file__).with_name("Asesor_Academico.pl")
_ATOMO = re.compile(r"[a-z][a-z0-9_]*\Z")


@dataclass(frozen=True)
class ResultadoMateria:
    identificador: str
    estado: str
    requisitos_pendientes: tuple[str, ...]


@dataclass(frozen=True)
class RegistroConsulta:
    hora: datetime
    objetivo: str
    duracion_ms: int
    correcta: bool
    salida: str
    error: str


class MotorProlog:
    """Ejecuta las consultas académicas en SWI-Prolog, nunca en Python."""

    def __init__(self, archivo: Path = ARCHIVO_PROLOGICO) -> None:
        self.archivo = archivo.resolve()
        if not self.archivo.is_file():
            raise RuntimeError(f"No se encontró la base Prolog: {self.archivo}")
        self._ejecutable = self._buscar_ejecutable()
        self.historial: list[RegistroConsulta] = []
        self.estudiantes = self._consultar_lista("estudiante(E)", "E")
        self.materias = self._consultar_lista("materia(M)", "M")
        if not self.estudiantes or not self.materias:
            raise RuntimeError(f"La base Prolog no contiene estudiantes o materias: {self.archivo}")

    def _registrar_consulta(self, registro: RegistroConsulta) -> None:
        self.historial.append(registro)
        del self.historial[:-100]

    @staticmethod
    def _buscar_ejecutable() -> Path:
        configurado = os.environ.get("SWIPL_EXECUTABLE")
        if configurado:
            ejecutable = Path(configurado).expanduser()
            if ejecutable.is_file():
                return ejecutable
            raise RuntimeError(f"SWIPL_EXECUTABLE no apunta a un archivo: {ejecutable}")

        encontrado = shutil.which("swipl")
        if encontrado:
            return Path(encontrado)

        raices = (
            Path(os.environ.get("ProgramFiles", r"C:\Program Files")),
            Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")),
            Path(os.environ.get("LOCALAPPDATA", Path.home())),
        )
        ubicaciones = (
            Path("swipl/bin/swipl.exe"),
            Path("SWI-Prolog/bin/swipl.exe"),
            Path("Programs/swipl/bin/swipl.exe"),
        )
        for raiz in raices:
            for ubicacion in ubicaciones:
                candidato = raiz / ubicacion
                if candidato.is_file():
                    return candidato
        raise RuntimeError(
            "No se encontró SWI-Prolog. Instálalo desde https://www.swi-prolog.org/ "
            "o configura la variable SWIPL_EXECUTABLE con la ruta a swipl.exe."
        )

    def _consultar(self, objetivo: str) -> str:
        inicio = time.perf_counter()
        try:
            resultado = subprocess.run(
                [
                    str(self._ejecutable),
                    "-q",
                    "-s",
                    self.archivo.name,
                    "-g",
                    objetivo,
                    "-t",
                    "halt",
                ],
                cwd=self.archivo.parent,
                capture_output=True,
                check=False,
                encoding="utf-8",
                timeout=15,
            )
        except subprocess.TimeoutExpired as error:
            self._registrar_consulta(
                RegistroConsulta(
                    datetime.now(),
                    objetivo,
                    round((time.perf_counter() - inicio) * 1000),
                    False,
                    "",
                    "SWI-Prolog excedió el tiempo máximo de consulta.",
                )
            )
            raise RuntimeError("SWI-Prolog excedió el tiempo máximo de consulta.") from error
        except OSError as error:
            self._registrar_consulta(
                RegistroConsulta(
                    datetime.now(),
                    objetivo,
                    round((time.perf_counter() - inicio) * 1000),
                    False,
                    "",
                    str(error),
                )
            )
            raise RuntimeError(f"No se pudo iniciar SWI-Prolog: {error}") from error
        if resultado.returncode != 0:
            detalle = resultado.stderr.strip() or resultado.stdout.strip()
            self._registrar_consulta(
                RegistroConsulta(
                    datetime.now(),
                    objetivo,
                    round((time.perf_counter() - inicio) * 1000),
                    False,
                    resultado.stdout.strip(),
                    detalle or f"SWI-Prolog terminó con código {resultado.returncode}.",
                )
            )
            raise RuntimeError(f"Falló la consulta en SWI-Prolog: {detalle}")
        self._registrar_consulta(
            RegistroConsulta(
                datetime.now(),
                objetivo,
                round((time.perf_counter() - inicio) * 1000),
                True,
                resultado.stdout.strip(),
                resultado.stderr.strip(),
            )
        )
        return resultado.stdout

    def _consultar_lista(self, generador: str, variable: str) -> tuple[str, ...]:
        objetivo = (
            f"forall(({generador}), format('~w~n', [{variable}]))"
        )
        return tuple(linea for linea in self._consultar(objetivo).splitlines() if linea)

    def consultar_materias(self, estudiante: str) -> tuple[ResultadoMateria, ...]:
        if estudiante not in self.estudiantes or not _ATOMO.fullmatch(estudiante):
            raise ValueError(f"Estudiante no registrado: {estudiante}")

        objetivo = (
            f"forall(materia(M), "
            f"((aprobo({estudiante}, M) -> Estado = aprobada ; "
            f"(puede_cursar({estudiante}, M) -> Estado = disponible ; Estado = bloqueada)), "
            f"findall(R, (prerrequisito(M, R), \\+ aprobo({estudiante}, R)), Rs), "
            "atomic_list_concat(Rs, ',', Pendientes), "
            "format('~w|~w|~w~n', [M, Estado, Pendientes])))"
        )
        resultados: list[ResultadoMateria] = []
        for linea in self._consultar(objetivo).splitlines():
            partes = linea.split("|")
            if len(partes) != 3 or partes[1] not in {
                "aprobada",
                "disponible",
                "bloqueada",
            }:
                raise RuntimeError(f"Respuesta inesperada de SWI-Prolog: {linea!r}")
            materia, estado, pendientes = partes
            requisitos = tuple(pendientes.split(",")) if pendientes else ()
            resultados.append(ResultadoMateria(materia, estado, requisitos))
        if len(resultados) != len(self.materias):
            raise RuntimeError(
                "SWI-Prolog no devolvió un resultado para cada materia de la base."
            )
        return tuple(resultados)

    def consultar_prerrequisitos_transitivos(self, materia: str) -> tuple[str, ...]:
        if materia not in self.materias or not _ATOMO.fullmatch(materia):
            raise ValueError(f"Materia no registrada: {materia}")
        objetivo = (
            f"forall(prerrequisito_transitivo({materia}, R), format('~w~n', [R]))"
        )
        return tuple(linea for linea in self._consultar(objetivo).splitlines() if linea)
