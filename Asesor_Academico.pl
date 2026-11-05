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
% no_ha_aprobado/2 aplica negacion por falla: no se puede demostrar que ya
% aprobo la materia con los hechos disponibles.
puede_cursar(Estudiante, Materia) :-
    estudiante(Estudiante),
    materia(Materia),
    no_ha_aprobado(Estudiante, Materia),
    forall(
        prerrequisito(Materia, Requisito),
        aprobo(Estudiante, Requisito)
    ).

% Negacion por falla: esto no demuestra que la persona nunca aprobo la
% materia; solo que aprobo/2 no puede probarse a partir de esta base.
no_ha_aprobado(Estudiante, Materia) :-
    estudiante(Estudiante),
    materia(Materia),
    \+ aprobo(Estudiante, Materia).

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

% Listas como terminos: findall/3 reune en una lista las soluciones
% encontradas para cada estudiante registrado.
materias_aprobadas(Estudiante, Materias) :-
    estudiante(Estudiante),
    findall(Materia, aprobo(Estudiante, Materia), Materias).

materias_disponibles(Estudiante, Materias) :-
    estudiante(Estudiante),
    findall(Materia, puede_cursar(Estudiante, Materia), Materias).

% Arbol de prerrequisitos como termino recursivo:
% nodo(Materia, ListaDeNodosRequisito).
% Las materias sin prerrequisitos son hojas y tienen una lista vacia.
arbol_prerrequisitos(Materia, nodo(Materia, Requisitos)) :-
    materia(Materia),
    findall(
        ArbolRequisito,
        (
            prerrequisito(Materia, Requisito),
            arbol_prerrequisitos(Requisito, ArbolRequisito)
        ),
        Requisitos
    ).

% Clasifica una materia para identificadores concretos. Los cortes evitan
% que Prolog pruebe las clasificaciones posteriores una vez determinado el
% primer estado aplicable.
estado_materia(Estudiante, Materia, Estado) :-
    ground(Estudiante-Materia),
    estado_materia_conocida(Estudiante, Materia, Estado).

estado_materia_conocida(Estudiante, _, estudiante_no_registrado) :-
    \+ estudiante(Estudiante),
    !.
estado_materia_conocida(Estudiante, Materia, materia_inexistente) :-
    estudiante(Estudiante),
    \+ materia(Materia),
    !.
estado_materia_conocida(Estudiante, Materia, aprobada) :-
    aprobo(Estudiante, Materia),
    !.
estado_materia_conocida(Estudiante, Materia, disponible) :-
    puede_cursar(Estudiante, Materia),
    !.
estado_materia_conocida(Estudiante, Materia, bloqueada) :-
    estudiante(Estudiante),
    materia(Materia).
