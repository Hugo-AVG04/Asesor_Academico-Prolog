# Asesor Académico

Interfaz de escritorio en Python y PySide6 para consultar las materias que un
estudiante puede cursar. **SWI-Prolog es el motor de decisiones**: la aplicación
ejecuta consultas contra `Asesor_Academico.pl`, incluida la regla
`puede_cursar/2`. Python se limita a presentar los resultados en la interfaz;
no reimplementa las reglas ni necesita PySwip.

## Requisitos

- Python 3.10 o posterior.
- SWI-Prolog instalado: <https://www.swi-prolog.org/download/stable>.
- PySide6, instalable desde `requirements.txt`.

El programa busca `swipl` en el `PATH` y en las ubicaciones habituales de
instalación de Windows. Si está instalado en otra ubicación, configura
`SWIPL_EXECUTABLE` con la ruta completa a `swipl.exe`.

## Ejecutar en Windows

Desde esta carpeta, instala la dependencia gráfica y ejecuta la aplicación:

```powershell
py -m pip install -r requirements.txt
py main.py
```

La ventana permite seleccionar un estudiante, ver materias aprobadas,
disponibles o bloqueadas, y consultar los prerrequisitos pendientes. El botón
«RECARGAR REGLAS» vuelve a ejecutar consultas con el archivo Prolog.

## Verificar SWI-Prolog y sus consultas

Debajo de la tabla, el indicador «SWI-PROLOG RESPONDIÓ» muestra la hora y
duración de la última consulta completada correctamente. «VER CONSULTAS» abre
la traza con el ejecutable utilizado, el archivo `.pl`, cada objetivo enviado,
su salida y los errores, si los hubiera. Cambiar el estudiante genera una
nueva consulta a `puede_cursar/2`.

La integración actual inicia un proceso de SWI-Prolog por consulta y lo cierra
al terminar; no es un servicio persistente. El indicador confirma que la
última ejecución respondió, no que exista un proceso de Prolog corriendo en
segundo plano entre consultas. Desde PowerShell se puede comprobar el
ejecutable con `swipl --version`.

## Ejecutar las pruebas

```powershell
py -m unittest -v
```

Las pruebas ejecutan consultas reales de SWI-Prolog; no sustituyen el motor por
una implementación de las reglas en Python.
