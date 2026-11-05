from __future__ import annotations

import unittest

from motor_decisiones import MotorProlog


class PruebasMotorProlog(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.motor = MotorProlog()

    def estados_de(self, estudiante: str) -> dict[str, str]:
        return {
            resultado.identificador: resultado.estado
            for resultado in self.motor.consultar_materias(estudiante)
        }

    def test_lista_de_estudiantes_y_materias_procede_de_prolog(self) -> None:
        self.assertIn("ana", self.motor.estudiantes)
        self.assertIn("aprendizaje_automatico", self.motor.materias)

    def test_puede_cursar_para_ana_y_luis_se_resuelve_en_prolog(self) -> None:
        ana = self.estados_de("ana")
        self.assertEqual(ana["estructuras_datos"], "disponible")
        self.assertEqual(ana["ia"], "disponible")
        self.assertEqual(ana["programacion"], "aprobada")
        self.assertEqual(ana["aprendizaje_automatico"], "bloqueada")

        luis = self.estados_de("luis")
        self.assertEqual(luis["matematicas"], "disponible")
        self.assertEqual(luis["ia"], "bloqueada")

    def test_prerrequisitos_pendientes_se_consultan_en_prolog(self) -> None:
        resultados = {
            resultado.identificador: resultado
            for resultado in self.motor.consultar_materias("luis")
        }
        self.assertEqual(resultados["ia"].requisitos_pendientes, ("matematicas",))

    def test_regla_transitiva_se_consulta_en_prolog(self) -> None:
        self.assertEqual(
            set(self.motor.consultar_prerrequisitos_transitivos("aprendizaje_automatico")),
            {"ia", "estadistica", "programacion", "matematicas"},
        )

    def test_rechaza_estudiante_o_materia_no_registrados(self) -> None:
        with self.assertRaises(ValueError):
            self.motor.consultar_materias("desconocido")
        with self.assertRaises(ValueError):
            self.motor.consultar_prerrequisitos_transitivos("desconocida")

    def test_historial_registra_la_consulta_y_su_resultado(self) -> None:
        self.motor.consultar_materias("ana")
        registro = self.motor.historial[-1]
        self.assertTrue(registro.correcta)
        self.assertIn("puede_cursar(ana, M)", registro.objetivo)
        self.assertIn("ia|disponible", registro.salida)


if __name__ == "__main__":
    unittest.main()
