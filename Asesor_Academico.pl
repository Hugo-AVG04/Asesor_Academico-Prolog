/*
  Asesor academico: base de conocimiento y reglas para consultar
  las materias que cada estudiante puede cursar.

  Para cargar el archivo en SWI-Prolog:
      ?- [Asesor_Academico].

  Los comentarios de bloque pueden ocupar varias lineas.
  Los comentarios de una sola linea comienzan con %.
*/

% Hechos: cada estudiante/1 identifica a un estudiante.
% Los nombres en minusculas son atomos (constantes) de Prolog.
estudiante(ana).
estudiante(luis).
estudiante(carlos).
estudiante(maria).
estudiante(jose).
estudiante(sofia).
estudiante(diego).
estudiante(valentina).
estudiante(mateo).
estudiante(camila).
estudiante(sebastian).
estudiante(isabella).
estudiante(daniel).
estudiante(gabriela).
estudiante(alejandro).
estudiante(paula).
estudiante(fernando).
estudiante(lucia).
estudiante(andres).
estudiante(victoria).

% Hechos: materia/1 registra todas las materias que ofrece el plan.
materia(programacion).
materia(matematicas).
materia(estructuras_datos).
materia(bases_datos).
materia(ia). % Abreviatura de Inteligencia Artificial.
materia(estadistica).
materia(aprendizaje_automatico).

% Hechos: aprobo/2 relaciona estudiante y materia ya aprobada.
% El primer argumento es el estudiante; el segundo, la materia.
aprobo(ana, programacion).
aprobo(ana, matematicas).
aprobo(luis, programacion).
aprobo(carlos, programacion).
aprobo(carlos, matematicas).
aprobo(maria, programacion).
aprobo(jose, matematicas).
aprobo(sofia, programacion).
aprobo(sofia, matematicas).
aprobo(valentina, programacion).
aprobo(mateo, programacion).
aprobo(mateo, matematicas).
aprobo(camila, matematicas).
aprobo(sebastian, programacion).
aprobo(isabella, programacion).
aprobo(isabella, matematicas).
aprobo(gabriela, programacion).
aprobo(alejandro, programacion).
aprobo(alejandro, matematicas).
aprobo(paula, matematicas).
aprobo(fernando, programacion).
aprobo(lucia, programacion).
aprobo(lucia, matematicas).
aprobo(victoria, programacion).
aprobo(victoria, matematicas).
aprobo(victoria, ia).
aprobo(victoria, estadistica).

% Hechos: prerrequisito/2 indica la materia que se debe aprobar
% antes de cursar la materia del primer argumento.
prerrequisito(estructuras_datos, programacion). %Se debe cursar programacion antes de estructuras de datos
prerrequisito(bases_datos, programacion).
prerrequisito(ia, programacion).
prerrequisito(ia, matematicas).
prerrequisito(aprendizaje_automatico, ia).
prerrequisito(aprendizaje_automatico, estadistica).

% Regla: un estudiante puede cursar una materia si:
% 1. Esta registrado como estudiante.
% 2. La materia existe en el plan.
% 3. Todavia no la aprobo.
% 4. Aprobo todos sus prerrequisitos directos.
%
% La coma (,) significa "y": todas las condiciones deben cumplirse.
% forall(Condicion, Prueba) exige que Prueba se cumpla para cada
% solucion de Condicion. Si no hay prerrequisitos, forall tiene exito.
% \+ significa negacion por falla: no se puede demostrar que ya aprobo.
puede_cursar(Estudiante, Materia) :-
    estudiante(Estudiante),
    materia(Materia),
    \+ aprobo(Estudiante, Materia),
    forall(
        prerrequisito(Materia, Requisito),
        aprobo(Estudiante, Requisito)
    ).

% Regla recursiva: prerrequisito_transitivo/2 encuentra tanto los
% prerrequisitos directos como los que estan mas arriba en la cadena.
%
% Caso base: un prerrequisito directo tambien es transitivo.
prerrequisito_transitivo(Materia, Requisito) :-
    prerrequisito(Materia, Requisito).

% Paso recursivo: si R1 es prerrequisito de Materia, cualquier requisito
% (Requisito) de R1 tambien es prerrequisito transitivo de Materia.
prerrequisito_transitivo(Materia, Requisito) :-
    prerrequisito(Materia, RequisitoIntermedio),
    prerrequisito_transitivo(RequisitoIntermedio, Requisito).
