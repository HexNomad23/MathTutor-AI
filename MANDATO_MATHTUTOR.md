# MathTutor AI — Borrador de producto y mandato para Antigravity

Versión propuesta: 0.1 · Plataforma: PC Windows · Idioma inicial: español.

## 1. Encargo y objetivo

Actúa como desarrollador principal de MathTutor AI. Construye una primera aplicación de escritorio funcional, no solamente un diseño de pantallas, una página web ni un chatbot genérico.

El objetivo es ayudar al estudiante a comprender matemáticas: resolver ejercicios mostrando transformaciones justificadas, revisar procedimientos, dar pistas y generar nuevas prácticas adecuadas a su desempeño. El público inicial son estudiantes de secundaria y de primeros cursos universitarios.

La visión completa incluye álgebra, geometría, física y cálculo. La versión 0.1 debe resolver un conjunto pequeño y bien definido de ejercicios de las cuatro materias. No anuncies cobertura universal.

Prioridad de trabajo: corrección matemática, explicación comprensible, funcionamiento estable y, después, acabado visual. No detengas el trabajo al terminar el plan: continúa con la implementación y las pruebas dentro de los permisos disponibles.

## 2. Primera experiencia del estudiante

La aplicación debe abrirse sin exigir registro, tarjeta, conexión ni credenciales de IA. Permite usar un perfil local llamado “Estudiante” y cambiar su nombre sin pedir datos personales innecesarios.

El recorrido principal será: elegir materia y tipo de ejercicio; escribir una expresión o completar los datos de un formulario; comprobar la interpretación; elegir resolver o recibir pistas; estudiar los pasos; realizar un ejercicio parecido y consultar el progreso.

Incluye los botones “Resolver paso a paso”, “Dame una pista”, “Revisa mi procedimiento” y “Practicar algo parecido” donde realmente estén disponibles. Una función pendiente debe aparecer deshabilitada con una explicación; no debe fingir funcionamiento.

## 3. Alcance matemático obligatorio de la versión 0.1

| Materia | Contenido inicial | Entrada y límites |
| --- | --- | --- |
| Álgebra | Ecuaciones lineales de una incógnita con paréntesis y coeficientes racionales; ecuaciones cuadráticas mediante factorización o fórmula general. | Expresiones escritas; números reales por defecto. Incluye casos sin solución o con infinitas soluciones. |
| Geometría | Área y perímetro de rectángulos y círculos; área de triángulos; teorema de Pitágoras. | Formularios con medidas, unidades y variable buscada. No deducir medidas de una imagen. |
| Física | Movimiento rectilíneo uniforme con d = v·t; segunda ley de Newton con F = m·a; conversiones necesarias entre unidades compatibles. | Formularios de datos conocidos e incógnita. Explicar el modelo y no inventar datos faltantes. |
| Cálculo | Derivadas e integrales indefinidas de polinomios de una variable. | Expresión escrita; reglas de suma, constante y potencia. Añadir la constante de integración. |

En esta fase no son obligatorios sistemas de ecuaciones, trigonometría, límites, ecuaciones diferenciales, física avanzada, reconocimiento de escritura a mano ni comprensión universal de problemas redactados. Documenta el alcance y rechaza con claridad los ejercicios no soportados.

Las medidas geométricas deben ser físicamente válidas. En física distingue magnitudes, unidades y convenciones de signo; comprueba denominadores y datos insuficientes. En geometría, una figura ilustrativa no constituye evidencia de una medida.

## 4. Resolver enseñando

Cada solución debe mostrar el enunciado interpretado, los datos, el dominio o supuestos relevantes, una secuencia de pasos, el resultado exacto cuando proceda y una comprobación final.

Cada paso contendrá: expresión anterior, operación aplicada, expresión resultante, explicación breve de la regla y restricciones necesarias. No omitas transformaciones esenciales ni conviertas automáticamente un resultado final en un supuesto procedimiento verificado.

Ejemplo de comportamiento para 2x + 3 = 11:

1. Restar 3 en ambos miembros: 2x + 3 − 3 = 11 − 3.
2. Simplificar: 2x = 8.
3. Dividir ambos miembros entre 2: x = 4.
4. Sustituir en la ecuación original: 2·4 + 3 = 11.

Ofrece explicaciones “Breve” y “Detallada” que mantengan exactamente las mismas matemáticas. En modo guiado muestra una pista cada vez y permite que el alumno intente el siguiente paso antes de revelar la solución.

Para los temas soportados, genera el procedimiento mediante reglas programadas que produzcan tanto la transformación como su explicación. No dependas de una respuesta de texto libre para la corrección matemática.

## 5. Revisar errores del alumno

Implementa primero la revisión línea por línea para ecuaciones lineales de álgebra. Para otras materias, verifica inicialmente la respuesta final y sus unidades cuando corresponda; no anuncies revisión completa de procedimientos que aún no exista.

Ejemplo: si el alumno escribe “2x = 11 + 3” después de “2x + 3 = 11”, señala esa transición y explica: “Para eliminar el +3 del lado izquierdo, debes restar 3 en ambos lados. El paso correcto es 2x = 11 − 3”. Después permite reintentar.

Identifica la primera transición que no se pueda justificar, diferencia una transformación incorrecta de una que no se ha podido comprobar y acepta procedimientos alternativos válidos. No marques un método como incorrecto únicamente por diferir del procedimiento sugerido.

Si el alumno entrega solamente el resultado, indica si coincide con la solución, pero no inventes qué error cometió. Usa un tono respetuoso, sin burlas ni etiquetas sobre su capacidad.

## 6. Práctica adaptada y progreso

Genera ejercicios desde plantillas parametrizadas y verificadas, no solamente desde una lista fija ni desde texto generado sin validación. Cada plantilla debe registrar tema, dificultad, parámetros, solución, reglas y semilla para reproducir el ejercicio.

Empieza con tres niveles por tema. En álgebra, por ejemplo, aumenta gradualmente el número de operaciones, introduce negativos y después paréntesis o fracciones. Permite elegir manualmente el nivel.

Como heurística inicial propuesta, revisa bloques de cinco ejercicios del mismo tema respondidos sin pistas: con cuatro o cinco aciertos, sube un nivel; con tres, mantén; con cero, uno o dos, baja un nivel, respetando los límites. Los intentos asistidos deben registrarse aparte y no contarse como resolución independiente. Aplica cada bloque una sola vez.

Estas reglas son una decisión inicial de producto, no una medición validada de inteligencia o dominio académico. Permite ajustarlas mediante configuración y pruebas.

Guarda aciertos, errores, pistas usadas, intentos y nivel por tema. Con pocos datos muestra “Aún no hay suficientes ejercicios para valorar tu progreso”. No inventes porcentajes de aprendizaje, rankings ni progreso de demostración dentro del perfil real.

## 7. Pantallas y diseño

Usa una interfaz moderna y legible en español. Tema claro inicial, buen contraste, navegación por teclado y ventanas redimensionables. El modo oscuro es opcional y no debe retrasar la primera entrega.

Navegación lateral: Inicio, Resolver, Practicar, Mi progreso, Historial y Ajustes.

En Inicio muestra accesos a las cuatro materias, la última actividad y una recomendación basada únicamente en el historial disponible. En Resolver coloca la entrada y la vista previa del ejercicio arriba; debajo, los pasos desplegables y la comprobación. En Practicar muestra una pregunta, el campo de respuesta, la pista y la retroalimentación. En Historial permite volver a abrir y eliminar actividades con confirmación.

Incluye un teclado matemático sencillo con potencias, raíz, fracciones y paréntesis. Interpreta de forma controlada entradas como “2x”, “x^2” y “(x+1)/2”. Acepta coma decimal en los campos adecuados; ante notación ambigua, pide aclaración en vez de cambiarla silenciosamente. Muestra siempre “Interpreté tu ejercicio como…” antes de resolver.

Las fórmulas deben verse como matemáticas, no como comandos sin procesar. Permite copiar una versión de texto accesible. Añade gráficas sencillas para polinomios cuando resulten útiles, con ejes y escala visibles. No uses una gráfica como demostración matemática.

Prueba una ventana de 1366×768 y escalado de Windows al 125 % y al 150 %. Evita textos cortados, botones invisibles y paneles que obliguen a maximizar para usar funciones esenciales.

## 8. Arquitectura técnica propuesta

Usa Python con PySide6 para una aplicación de escritorio. Mantén separadas la interfaz, el motor matemático, el tutor, la generación de práctica y la persistencia. PySide6 permite construir interfaces Qt desde Python [T1].

Usa SymPy para las operaciones simbólicas y comprobaciones dentro del alcance implementado [T2]. Desarrolla un motor pedagógico propio basado en reglas: usar un solucionador simbólico no sustituye implementar y comprobar los pasos didácticos.

Usa Matplotlib integrado en Qt para gráficas; su renderizador Mathtext puede utilizarse para las fórmulas de este alcance, verificando los símbolos compatibles y sin exigir una instalación externa de LaTeX [T3]. Usa SQLite para el almacenamiento local y pytest para las pruebas.

No cambies a una arquitectura con servidor, cuentas y servicios remotos solo por comodidad. Evita Electron, Docker, bases de datos remotas y procesos innecesarios en esta primera versión, salvo que documentes un bloqueo real de la base propuesta.

Estructura orientativa:

```text
MathTutorAI/
  src/mathtutor/
    ui/
    math_engine/
    tutor/
    practice/
    storage/
  tests/
  docs/
  scripts/
  pyproject.toml
  README.md
  PROGRESO_MATHTUTOR.md
```

Define un formato compartido para cada ejercicio y solución: identificador, tema, entrada original, interpretación, dominio, unidades, pasos, resultado, estado de verificación y motivo. Cada paso debe conservar la regla aplicada. Los intentos deben referenciar la versión del ejercicio para poder reproducir lo ocurrido.

Selecciona versiones compatibles, consulta su documentación oficial y fija las dependencias probadas. Utiliza un entorno virtual del proyecto; no alteres las instalaciones globales del usuario.

## 9. Exactitud, seguridad e integración de IA

Separa el cálculo verificable de la explicación. Comprueba resultados respecto al ejercicio original, conserva restricciones de dominio y distingue soluciones exactas de aproximaciones. La coincidencia en unos pocos valores numéricos no autoriza a declarar probada una identidad general.

Usa estados claros como “Verificado”, “Comprobación numérica”, “No se pudo verificar” y “Fuera del alcance”. Explica qué se verificó. Un resultado no comprobado nunca debe mostrarse como matemáticamente certificado.

No ejecutes entradas del estudiante como código. Implementa un analizador de gramática limitada que construya objetos matemáticos autorizados; rechaza atributos, importaciones, llamadas arbitrarias y comandos. No uses eval o exec sobre texto del alumno ni pases ese texto a sympify o parse_expr sin un diseño seguro: la documentación de SymPy advierte del uso de eval al interpretar cadenas [T4].

Limita la longitud, profundidad, tamaño de exponentes y complejidad de las expresiones. Ejecuta cálculos potencialmente costosos en un proceso de trabajo cancelable, con tiempo máximo; no bloquees la interfaz ni declares resuelto un cálculo que ha expirado.

La versión inicial debe funcionar con un tutor local de reglas. Denomina ese estado “Modo local”, sin fingir que existe un modelo generativo instalado.

Prepara una interfaz independiente para añadir un proveedor de IA generativa. La conexión remota será opcional y se implementará únicamente con una API real y credenciales autorizadas. Antigravity es la herramienta de desarrollo: no diseñes la aplicación suponiendo que su sesión o sus credenciales estarán disponibles para los alumnos.

No inventes claves, endpoints ni respuestas de un proveedor. Cuando no exista conexión, conserva todas las funciones locales y marca la ampliación de IA como pendiente. La IA futura podrá explicar o proponer interpretaciones, pero sus transformaciones matemáticas deberán pasar por el verificador antes de recibir una etiqueta de verificación.

No envíes ejercicios o historiales fuera del equipo sin avisar y obtener consentimiento. No almacenes secretos en el código o los registros. Para la versión 0.1 no incluyas telemetría, anuncios ni pagos.

## 10. Guardado, rendimiento y distribución

Guarda perfiles, intentos, historial y ajustes en una ubicación de datos del usuario, como LocalAppData/MathTutorAI, nunca en una carpeta de instalación que pueda requerir permisos elevados. Usa consultas parametrizadas y migraciones de esquema identificadas.

La aplicación debe restaurar los datos al cerrarse y abrirse; un fallo no debe borrar el progreso. Incluye tratamiento de errores de lectura y escritura, y no registres información sensible innecesaria.

Prioriza Windows 11 x64. Valida la compatibilidad con Windows 10 antes de anunciarla; documenta qué sistemas se han probado. El modo local no debe depender de una GPU dedicada.

Entrega primero una distribución portable con MathTutorAI.exe y sus dependencias. Usa PyInstaller y construye el ejecutable de Windows en Windows: PyInstaller no es un compilador cruzado [T5]. No confundas una carpeta portable con un único ejecutable autocontenido.

Prepara scripts para iniciar desde el código y compilar. Si el entorno disponible no permite construir o probar en Windows, entrega el código y los scripts e indica explícitamente esa limitación; no afirmes haber ejecutado pruebas que no realizaste.

## 11. Pruebas y criterios de aceptación

Incluye pruebas automatizadas, sin sustituirlas por comprobaciones visuales. Como mínimo:

| Caso | Resultado o comportamiento esperado |
| --- | --- |
| 2x + 3 = 11 | x = 4, con pasos y sustitución final. |
| 3(x − 2) = 12 | x = 6, respetando los paréntesis. |
| x² − 5x + 6 = 0 | x = 2 y x = 3. |
| x² + 1 = 0 en números reales | Sin soluciones reales; no cambiar de dominio silenciosamente. |
| 2x + 3 = 2x + 3 | Infinitas soluciones reales. |
| 2x + 3 = 2x + 5 | Sin solución. |
| Paso erróneo 2x = 11 + 3 después de 2x + 3 = 11 | Detectar y explicar la transición incorrecta. |
| Paso alternativo 4x + 6 = 22 después de 2x + 3 = 11 | Aceptarlo como equivalente, aunque no sea el método preferido. |
| Hipotenusa con catetos de 3 cm y 4 cm | 5 cm. |
| Triángulo de base 10 cm y altura 6 cm | Área de 30 cm². |
| MRU: 150 m en 10 s | Rapidez de 15 m/s. |
| F = m·a, con m = 2 kg y a = 3 m/s² | 6 N. |
| Conversión de 72 km/h | 20 m/s. |
| Derivada de 3x² + 2x − 5 | 6x + 2. |
| Integral indefinida de 2x + 3 | x² + 3x + C. |

Añade casos de entrada vacía, paréntesis incompletos, división entre cero, datos faltantes, unidades incompatibles, valores geométricos imposibles, expresiones fuera de alcance, intentos de ejecutar código y cálculos que superan el límite de recursos. Ninguno debe bloquear o cerrar la aplicación.

Comprueba que las plantillas generan ejercicios válidos con múltiples semillas, que las reglas de dificultad respetan sus umbrales y que no procesan dos veces el mismo bloque. Prueba guardado y recuperación con bases de datos temporales, sin tocar los datos personales del usuario.

Realiza pruebas manuales de la interfaz y de la distribución portable en Windows: apertura, resolución, pistas, revisión, práctica, historial y reinicio. Registra resultados reales y fallos pendientes.

La primera versión se acepta cuando se puede abrir, resolver los casos del alcance con explicación, revisar errores lineales, practicar con dificultad ajustable y conservar el historial. Una pantalla atractiva sin estas funciones no cumple el encargo.

## 12. Orden de ejecución y entrega

Primero inspecciona la carpeta seleccionada. Conserva archivos existentes, trabaja únicamente dentro del proyecto y no ejecutes operaciones destructivas sobre otras carpetas o unidades. No publiques el código ni contrates servicios sin autorización.

Documenta el plan y las tareas. Antigravity permite utilizar artefactos para organizar y revisar el trabajo [T6]; úsalos cuando estén disponibles, sin depender de ellos como sustituto de los archivos del proyecto.

Hito 1: crea una aplicación que abra y complete de extremo a extremo el caso 2x + 3 = 11, incluyendo pasos, comprobación y guardado.

Hito 2: completa el alcance de álgebra, añade pistas y revisión de procedimientos lineales, con sus pruebas.

Hito 3: incorpora los formularios y motores de geometría, física y cálculo definidos en este borrador.

Hito 4: incorpora práctica parametrizada, adaptación por tema, progreso e historial real.

Hito 5: revisa interfaz, seguridad, límites de cálculo, persistencia y empaquetado; ejecuta las pruebas de aceptación.

Después de cada hito actualiza PROGRESO_MATHTUTOR.md con lo implementado, pruebas ejecutadas, fallos, decisiones y siguiente tarea. Al reanudar una sesión, lee ese archivo y continúa desde el último estado comprobado.

La entrega debe incluir código fuente organizado, dependencias fijadas, scripts, pruebas, README en español, documentación de alcance y un informe que distinga “Implementado y probado”, “Implementado sin probar” y “Pendiente”. Añade un ZIP del proyecto y la distribución Windows cuando realmente haya podido construirse. Indica rutas reales de los archivos.

Deja para una segunda versión las fotografías y capturas con confirmación de la transcripción, lectura de documentos, IA conversacional remota, sistemas de ecuaciones, trigonometría, límites, sincronización y funciones para profesores. No retrases la base funcional por intentar incluirlo todo ahora.

Empieza por el hito 1. Conserva una aplicación ejecutable entre hitos y no declares completado el proyecto mientras existan funciones anunciadas que solo sean simulaciones.

---

## Referencias técnicas para el agente

Consulta las versiones vigentes y compatibles antes de instalar dependencias. Referencias consultadas el 15 de octubre de 2026:

[T1] Qt for Python, documentación oficial: https://doc.qt.io/qtforpython-6/index.html

[T2] SymPy, Solving Guidance: https://docs.sympy.org/latest/guides/solving/solving-guidance.html

[T3] Matplotlib, integración Qt: https://matplotlib.org/stable/gallery/user_interfaces/embedding_in_qt_sgskip.html ; Mathtext: https://matplotlib.org/stable/gallery/text_labels_and_annotations/mathtext_demo.html

[T4] SymPy, Parsing y advertencias: https://docs.sympy.org/latest/modules/parsing.html ; Core / sympify: https://docs.sympy.org/latest/modules/core.html

[T5] PyInstaller, manual oficial: https://www.pyinstaller.org/

[T6] Google Antigravity, Artifacts: https://antigravity.google/docs/artifacts/
