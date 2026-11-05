"""Interfaz gráfica del asesor académico."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from motor_decisiones import ARCHIVO_PROLOGICO, MotorProlog


NOMBRES = {
    "programacion": "Programación",
    "matematicas": "Matemáticas",
    "estructuras_datos": "Estructuras de datos",
    "bases_datos": "Bases de datos",
    "ia": "Inteligencia artificial",
    "estadistica": "Estadística",
    "aprendizaje_automatico": "Aprendizaje automático",
}

ESTILOS = """
QMainWindow, QWidget#fondo {
    background-color: #111211;
    color: #ededeb;
    font-family: "Segoe UI";
}
QLabel { color: #ededeb; }
QLabel#sobrelinea { color: #ff5638; font-size: 11px; font-weight: 700; letter-spacing: 2px; }
QLabel#titulo { font-size: 30px; font-weight: 700; letter-spacing: 1px; }
QLabel#subtitulo, QLabel#secundario { color: #929590; }
QFrame#panel {
    background-color: #191b19;
    border: 1px solid #343734;
    border-radius: 8px;
}
QComboBox, QPushButton {
    background-color: #202320;
    border: 1px solid #454945;
    border-radius: 5px;
    padding: 9px 12px;
    color: #f2f2ef;
}
QComboBox:hover, QPushButton:hover { border-color: #ff5638; }
QComboBox QAbstractItemView {
    background-color: #202320;
    color: #f2f2ef;
    selection-background-color: #383b38;
}
QPushButton { color: #ff7259; font-weight: 600; }
QTableWidget {
    background-color: #191b19;
    alternate-background-color: #1d201d;
    color: #ededeb;
    border: 0;
    gridline-color: #303330;
    selection-background-color: #303530;
}
QHeaderView::section {
    background-color: #191b19;
    color: #929590;
    border: 0;
    border-bottom: 1px solid #454945;
    padding: 9px 6px;
    font-size: 10px;
    font-weight: 700;
}
QTableWidget::item { padding: 8px 6px; border-bottom: 1px solid #292c29; }
QPlainTextEdit {
    background-color: #111211;
    color: #c8cbc6;
    border: 1px solid #343734;
    border-radius: 5px;
    font-family: Consolas, monospace;
    font-size: 11px;
}
"""


def nombre_visible(identificador: str) -> str:
    return NOMBRES.get(identificador, identificador.replace("_", " ").capitalize())


class PanelMatriz(QFrame):
    """Panel con patrón de puntos tenue, inspirado en una pantalla de matriz."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("panel")
        self.setFixedHeight(146)
        contenido = QHBoxLayout(self)
        contenido.setContentsMargins(22, 16, 22, 16)

        texto = QVBoxLayout()
        eyebrow = QLabel("SISTEMA DE ORIENTACIÓN  /  ACADEMIA")
        eyebrow.setObjectName("sobrelinea")
        titulo = QLabel("ASESOR\nACADÉMICO")
        titulo.setObjectName("titulo")
        texto.addWidget(eyebrow)
        texto.addWidget(titulo)
        contenido.addLayout(texto)
        contenido.addStretch(1)

        self.indicador = QLabel("RULESET // PROLOG\nEN LÍNEA")
        self.indicador.setObjectName("sobrelinea")
        self.indicador.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        contenido.addWidget(self.indicador)

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.RenderHint.Antialiasing)
        for columna, x in enumerate(range(12, self.width(), 12)):
            for fila, y in enumerate(range(12, self.height(), 12)):
                distancia = (columna * 7 + fila * 11) % 17
                if distancia < 5:
                    color = QColor(255, 86, 56, 75 if distancia == 0 else 35)
                else:
                    color = QColor(220, 225, 220, 24)
                pintor.setBrush(color)
                pintor.setPen(Qt.PenStyle.NoPen)
                pintor.drawEllipse(x, y, 2, 2)


class VentanaAsesor(QMainWindow):
    def __init__(self, motor: MotorProlog) -> None:
        super().__init__()
        self.motor = motor
        self.setWindowTitle("Asesor Académico // Motor de decisiones")
        self.resize(920, 740)
        self.setMinimumSize(760, 620)
        self.setStyleSheet(ESTILOS)

        fondo = QWidget()
        fondo.setObjectName("fondo")
        self.setCentralWidget(fondo)
        principal = QVBoxLayout(fondo)
        principal.setContentsMargins(30, 26, 30, 22)
        principal.setSpacing(18)

        principal.addWidget(PanelMatriz())

        controles = QFrame()
        controles.setObjectName("panel")
        fila = QHBoxLayout(controles)
        fila.setContentsMargins(18, 12, 18, 12)
        etiqueta = QLabel("PERFIL DEL ESTUDIANTE")
        etiqueta.setObjectName("sobrelinea")
        self.estudiante = QComboBox()
        self.estudiante.addItems([nombre.capitalize() for nombre in motor.estudiantes])
        self.estudiante.currentIndexChanged.connect(self.actualizar)
        recargar = QPushButton("RECARGAR REGLAS")
        recargar.clicked.connect(self.recargar_base)
        fila.addWidget(etiqueta)
        fila.addWidget(self.estudiante, 1)
        fila.addWidget(recargar)
        principal.addWidget(controles)

        resumen = QHBoxLayout()
        resumen.setSpacing(12)
        self.disponibles = self._crear_tarjeta("MATERIAS DISPONIBLES")
        self.aprobadas = self._crear_tarjeta("MATERIAS APROBADAS")
        resumen.addWidget(self.disponibles[0])
        resumen.addWidget(self.aprobadas[0])
        principal.addLayout(resumen)

        titulo_materias = QHBoxLayout()
        encabezado = QLabel("MAPA DE MATERIAS")
        encabezado.setObjectName("sobrelinea")
        ayuda = QLabel("Elegibilidad según los prerrequisitos registrados")
        ayuda.setObjectName("secundario")
        titulo_materias.addWidget(encabezado)
        titulo_materias.addStretch(1)
        titulo_materias.addWidget(ayuda)
        principal.addLayout(titulo_materias)

        self.tabla = QTableWidget(0, 3)
        self.tabla.setHorizontalHeaderLabels(["MATERIA", "ESTADO", "PRERREQUISITOS PENDIENTES"])
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.tabla.setAlternatingRowColors(True)
        principal.addWidget(self.tabla, 1)

        barra_diagnostico = QHBoxLayout()
        self.estado_prolog = QLabel("COMPROBANDO SWI-PROLOG…")
        self.estado_prolog.setObjectName("secundario")
        self.boton_consultas = QPushButton("VER CONSULTAS")
        self.boton_consultas.setCheckable(True)
        self.boton_consultas.toggled.connect(self.alternar_diagnostico)
        barra_diagnostico.addWidget(self.estado_prolog)
        barra_diagnostico.addStretch(1)
        barra_diagnostico.addWidget(self.boton_consultas)
        principal.addLayout(barra_diagnostico)

        self.panel_diagnostico = QFrame()
        self.panel_diagnostico.setObjectName("panel")
        diagnostico_layout = QVBoxLayout(self.panel_diagnostico)
        diagnostico_layout.setContentsMargins(12, 10, 12, 10)
        diagnostico_titulo = QLabel("TRAZA DEL MOTOR DE INFERENCIA")
        diagnostico_titulo.setObjectName("sobrelinea")
        self.traza_consultas = QPlainTextEdit()
        self.traza_consultas.setReadOnly(True)
        self.traza_consultas.setMaximumBlockCount(1200)
        self.traza_consultas.setFixedHeight(170)
        diagnostico_layout.addWidget(diagnostico_titulo)
        diagnostico_layout.addWidget(self.traza_consultas)
        self.panel_diagnostico.setVisible(False)
        principal.addWidget(self.panel_diagnostico)

        pie = QLabel(f"SWI-PROLOG  ·  {Path(ARCHIVO_PROLOGICO.name).name}  ·  {len(motor.estudiantes):02} ESTUDIANTES")
        pie.setObjectName("secundario")
        principal.addWidget(pie)
        self.actualizar()

    def alternar_diagnostico(self, visible: bool) -> None:
        self.panel_diagnostico.setVisible(visible)
        self.boton_consultas.setText("OCULTAR CONSULTAS" if visible else "VER CONSULTAS")

    def actualizar_diagnostico(self) -> None:
        historial = self.motor.historial
        if not historial:
            self.estado_prolog.setText("SIN CONSULTAS A SWI-PROLOG")
            return

        ultima = historial[-1]
        hora = ultima.hora.strftime("%H:%M:%S")
        if ultima.correcta:
            self.estado_prolog.setText(
                f"SWI-PROLOG RESPONDIÓ · {hora} · {ultima.duracion_ms} ms"
            )
            color = "#8cbd94"
        else:
            self.estado_prolog.setText(f"ERROR DE SWI-PROLOG · {hora}")
            color = "#ff7259"
        self.estado_prolog.setStyleSheet(f"color: {color}; font-weight: 700;")

        lineas = [
            f"Ejecutable: {self.motor._ejecutable}",
            f"Base de reglas: {self.motor.archivo}",
            "Modo: proceso SWI-Prolog independiente por consulta (no es un servicio persistente).",
            "",
        ]
        for registro in historial:
            estado = "OK" if registro.correcta else "ERROR"
            lineas.append(
                f"[{registro.hora.strftime('%H:%M:%S')}] {estado} · "
                f"{registro.duracion_ms} ms"
            )
            lineas.append(f"?- {registro.objetivo}.")
            if registro.salida:
                lineas.append(f"Salida: {registro.salida}")
            if registro.error:
                lineas.append(f"Detalle: {registro.error}")
            lineas.append("")
        self.traza_consultas.setPlainText("\n".join(lineas))
        barra = self.traza_consultas.verticalScrollBar()
        barra.setValue(barra.maximum())

    @staticmethod
    def _crear_tarjeta(titulo: str) -> tuple[QFrame, QLabel]:
        tarjeta = QFrame()
        tarjeta.setObjectName("panel")
        contenido = QVBoxLayout(tarjeta)
        contenido.setContentsMargins(18, 12, 18, 12)
        encabezado = QLabel(titulo)
        encabezado.setObjectName("sobrelinea")
        numero = QLabel("00")
        numero.setStyleSheet("font-size: 25px; font-weight: 700;")
        contenido.addWidget(encabezado)
        contenido.addWidget(numero)
        return tarjeta, numero

    def estudiante_actual(self) -> str:
        return self.motor.estudiantes[self.estudiante.currentIndex()]

    def actualizar(self, *_args: object) -> None:
        estudiante = self.estudiante_actual()
        try:
            resultados = self.motor.consultar_materias(estudiante)
        except RuntimeError as error:
            self.tabla.setRowCount(0)
            self.disponibles[1].setText("—")
            self.aprobadas[1].setText("—")
            self.actualizar_diagnostico()
            QMessageBox.critical(self, "Error al consultar Prolog", str(error))
            return
        self.disponibles[1].setText(
            f"{sum(resultado.estado == 'disponible' for resultado in resultados):02}"
        )
        self.aprobadas[1].setText(
            f"{sum(resultado.estado == 'aprobada' for resultado in resultados):02}"
        )

        self.tabla.setRowCount(len(resultados))
        etiquetas_estado = {
            "aprobada": ("APROBADA", "#8cbd94"),
            "disponible": ("DISPONIBLE", "#ff7259"),
            "bloqueada": ("BLOQUEADA", "#929590"),
        }
        for fila, resultado in enumerate(resultados):
            estado, color_estado = etiquetas_estado[resultado.estado]
            valores = (
                nombre_visible(resultado.identificador),
                estado,
                ", ".join(
                    nombre_visible(item) for item in resultado.requisitos_pendientes
                )
                or "—",
            )
            for columna, valor in enumerate(valores):
                elemento = QTableWidgetItem(valor)
                if columna == 1:
                    elemento.setForeground(QColor(color_estado))
                self.tabla.setItem(fila, columna, elemento)
        self.tabla.resizeRowsToContents()
        self.actualizar_diagnostico()

    def recargar_base(self) -> None:
        try:
            nuevo_motor = MotorProlog()
            estudiante_anterior = self.estudiante.currentText().lower()
            if estudiante_anterior not in nuevo_motor.estudiantes:
                estudiante_anterior = nuevo_motor.estudiantes[0]
            nuevo_motor.consultar_materias(estudiante_anterior)
        except (OSError, RuntimeError, ValueError) as error:
            QMessageBox.critical(self, "No se pudieron cargar las reglas", str(error))
            return

        self.motor = nuevo_motor
        self.estudiante.blockSignals(True)
        self.estudiante.clear()
        self.estudiante.addItems([nombre.capitalize() for nombre in nuevo_motor.estudiantes])
        if estudiante_anterior in nuevo_motor.estudiantes:
            self.estudiante.setCurrentIndex(nuevo_motor.estudiantes.index(estudiante_anterior))
        self.estudiante.blockSignals(False)
        self.actualizar()
        QMessageBox.information(self, "Reglas actualizadas", "Se recargó el archivo y las reglas de Prolog.")


def main() -> int:
    aplicacion = QApplication(sys.argv)
    try:
        motor = MotorProlog()
    except (OSError, RuntimeError, ValueError) as error:
        QMessageBox.critical(None, "No se pudo iniciar el asesor", str(error))
        return 1
    ventana = VentanaAsesor(motor)
    ventana.show()
    return aplicacion.exec()


if __name__ == "__main__":
    raise SystemExit(main())
