# Informe de Investigación: Arquitectura y Desarrollo de un Sistema de Inteligencia de Inversiones Personal (SIIP)

## 1. Resumen Ejecutivo y Visión Estratégica
En el ecosistema financiero contemporáneo, la asimetría de información entre los inversores institucionales y los inversores minoristas se ha reducido drásticamente, no debido a una simplificación de los mercados, sino gracias a la democratización del acceso a datos fundamentales de grado institucional y herramientas de procesamiento computacional avanzado. El presente informe detalla la arquitectura, metodología y estrategia de implementación para desarrollar una aplicación web de gestión de portafolio de inversiones ("SIIP - Sistema de Inteligencia de Inversiones Personal") que trascienda las capacidades de las hojas de cálculo convencionales y los rastreadores de mercado pasivos.

El objetivo central del sistema propuesto es la integración de un ciclo de retroalimentación "quantamental" (cuantitativo y fundamental) automatizado. A diferencia de las plataformas comerciales que priorizan la ejecución de órdenes o el análisis técnico superficial, este sistema se diseñará para monitorear la salud intrínseca de los activos mediante métricas predictivas —específicamente el Ratio Precio-Beneficio de los Próximos Doce Meses (PE NTM) y el Flujo de Caja Libre por Acción (FCF/Share)— y para sintetizar el flujo incesante de información noticiosa mediante inteligencia artificial generativa.

La arquitectura recomendada se basa en un enfoque "Serverless" y "Python-First", utilizando el framework Reflex para la interfaz web, Supabase para la persistencia de datos relacional, GitHub Actions para la orquestación de tareas diarias de bajo costo, y una arquitectura híbrida de APIs financieras que combina la profundidad fundamental de Financial Modeling Prep (FMP) con la cobertura de mercado de yfinance. Este informe proporciona un análisis exhaustivo de cada componente, justificando las decisiones técnicas y financieras para garantizar un sistema robusto, escalable y económicamente viable para un inversor individual sofisticado.

## 2. Ingeniería Financiera: Definición y Cálculo de Métricas Críticas
La efectividad de un sistema de gestión de inversiones no reside en la cantidad de datos que muestra, sino en la calidad de las señales que genera. Para satisfacer los requisitos de monitoreo de valoración y rentabilidad real, es imperativo establecer definiciones rigurosas de las métricas seleccionadas y entender sus implicaciones en la arquitectura de datos.

### 2.1. Valoración Predictiva: Ratio Precio-Beneficio Forward (PE NTM)
El Ratio Precio-Beneficio (P/E) es la métrica de valoración más ubicua, pero su versión estándar (Trailing P/E o TTM) sufre de un defecto crítico: mira hacia el pasado. En mercados eficientes, los precios de los activos descuentan flujos de caja futuros, no históricos. Por lo tanto, para una aplicación de gestión activa, el uso del PE NTM (Next Twelve Months) es obligatorio.

#### 2.1.1. Metodología de Cálculo
El PE NTM no es un dato estático que se pueda obtener simplemente leyendo un campo de una base de datos histórica; es una construcción derivada de las expectativas del consenso de analistas.
$$PE_{NTM} = \frac{P_{t}}{\sum_{i=1}^{4} E}$$
Donde:
- $P_{t}$ es el precio actual del activo.
- $E$ es la estimación de consenso del beneficio por acción para los próximos cuatro trimestres fiscales no reportados.

**Implicaciones para la Arquitectura:** El sistema debe ser capaz de ingerir datos de estimaciones de analistas ("Analyst Estimates"). Esto descarta APIs que solo proveen estados financieros históricos. La API seleccionada debe proporcionar el desglose trimestral de estimaciones futuras para poder realizar una suma rodante (rolling sum) de los próximos cuatro periodos, ajustándose dinámicamente conforme las empresas reportan sus resultados.

#### 2.1.2. Interpretación y Señalización
Un PE NTM significativamente inferior al PE TTM sugiere que el mercado anticipa un crecimiento en los beneficios, lo que podría indicar una oportunidad de compra si el precio no ha reaccionado acorde. Inversamente, un PE NTM superior al histórico puede señalar un deterioro esperado en los fundamentales. El dashboard debe visualizar esta divergencia (Spread PE TTM vs NTM) como un indicador de primer nivel.

### 2.2. La Verdad del Efectivo: Flujo de Caja Libre por Acción (FCF/Share)
Mientras que los beneficios netos pueden ser manipulados mediante prácticas contables devengadas (accrual accounting), el Flujo de Caja Libre (FCF) representa la capacidad real de una empresa para generar efectivo distribuible a los accionistas, pagar deuda o reinvertir en crecimiento.

#### 2.2.1. Desglose de la Fórmula
Para calcular el FCF/Share con precisión de grado institucional, el sistema debe realizar la siguiente operación aritmética sobre los datos brutos del Estado de Flujos de Efectivo:

**Cálculo del FCF Absoluto:**
$$FCF = OCF - CAPEX$$
Donde $OCF$ es el Flujo de Efectivo Operativo y $CAPEX$ son los Gastos de Capital (Propiedad, Planta y Equipo).

**Normalización por Acción:**
$$FCF_{Share} = \frac{FCF}{Diluted\ Shares\ Outstanding}$$
Es crítico utilizar el número de acciones diluidas (que incluye opciones sobre acciones y bonos convertibles) y no las básicas, para reflejar la verdadera propiedad del inversor minorista.

**Desafíos de Datos:** Algunas APIs entregan el FCF ya calculado, pero a menudo ignoran matices como el CAPEX de mantenimiento versus crecimiento. Para este proyecto, se recomienda ingerir los componentes brutos ($OCF$ y $CAPEX$) para tener control sobre la fórmula y permitir ajustes manuales si el usuario lo desea en el futuro.

### 2.3. Medición del Rendimiento de Portafolio: TWR vs. MWR
Uno de los errores más comunes en las apps personales es calcular el rendimiento simplemente como $\frac{Valor\ Final}{Costo\ Total} - 1$. Esto es erróneo cuando hay flujos de entrada y salida de dinero (depósitos/retiros), ya que distorsiona la habilidad del inversor.

El sistema implementará dos métricas de rendimiento distintas:
- **Retorno Ponderado por Tiempo (TWR - Time-Weighted Return):** Esta métrica elimina el efecto de los flujos de efectivo externos. Es la única forma válida de comparar el rendimiento del portafolio contra un índice de referencia (Benchmark) como el S&P 500 (SPY).
  $$TWR = [(1 + r_1) \times (1 + r_2) \times... \times (1 + r_n)] - 1$$
  Donde $r_n$ es el rendimiento del sub-periodo entre flujos de caja.
- **Retorno Ponderado por Dinero (MWR - Money-Weighted Return):** Calculado típicamente usando la Tasa Interna de Retorno Extendida (XIRR). Esta métrica refleja la experiencia real del inversor, penalizando o recompensando el "timing" de los depósitos. Si el usuario agrega dinero justo antes de una caída del mercado, su MWR sufrirá más que su TWR.

## 3. Análisis del Ecosistema de Datos (Selección de APIs)
La viabilidad técnica del proyecto depende de la selección de proveedores de datos que ofrezcan granularidad fundamental (específicamente estimaciones y calendarios) a un costo accesible para un individuo. Se han evaluado los principales proveedores del mercado bajo estos criterios.

### 3.1. Evaluación Comparativa de Proveedores
A continuación se presenta un análisis detallado de las capacidades de las APIs candidatas para satisfacer los requisitos específicos del usuario: PE NTM, FCF, Noticias, Earnings Calendar.

| Característica | Financial Modeling Prep (FMP) | Finnhub | Alpha Vantage | yfinance (Yahoo Libre) |
| :--- | :--- | :--- | :--- | :--- |
| **Estimaciones (EPS NTM)** | Excelente. Endpoint dedicado `/analyst-estimates` con desglose anual/trimestral. | Limitado en capa gratuita. Enfocado más en datos alternativos. | Existente en capa Premium, muy limitado en capa gratuita. | Irregular. Scrapeo de HTML propenso a errores y datos incompletos. |
| **Flujo de Caja (FCF)** | Excelente. Estados financieros completos (`/cash-flow-statement`) hasta 30 años. | Bueno, pero con límites de tasa estrictos en cuentas gratuitas. | Bueno, pero requiere múltiples llamadas para construir la historia. | Bueno para datos recientes, pero sin garantía de estabilidad. |
| **Noticias y Sentimiento** | Bueno. Endpoint `/fmp/articles` y RSS feed. | Excelente. API `/news-sentiment` clasifica noticias por tono. | Regular. API de "Sentiment" añadida recientemente, pero consume muchos créditos. | No estructurado. Solo titulares sin cuerpo para análisis. |
| **Calendario Earnings** | Excelente. Endpoint `/earning-calendar` con filtros de fechas futuras. | Bueno, cubre mercados globales. | Aceptable, pero con menor profundidad histórica. | Disponible vía módulo calendar, pero básico. |
| **Precios Históricos** | Bueno, pero consume cuota diaria. | Bueno para tiempo real (Websockets). | Muy limitado (25 req/día). | Excelente. Ilimitado (razonable) y rápido para OHLCV. |
| **Costo/Valor** | Alto valor. Plan "Starter" cubre necesidades o Free limitado. | Fuerte en capa gratuita para precios/noticias, caro para fundamentales. | Capa gratuita inutilizable para portafolios >5 activos. | Gratuito (Open Source). Sin soporte. |

### 3.2. Estrategia de Adquisición de Datos Recomendada: Modelo Híbrido
Para optimizar la robustez y minimizar el costo operativo, se rechaza la dependencia de un solo proveedor. Se propone una arquitectura de ingesta de datos híbrida:
- **Capa Fundamental (Financial Modeling Prep - FMP):** Actuará como la fuente de la verdad para las métricas de valoración. Su estructura JSON limpia y la disponibilidad de "Analyst Estimates" son insustituibles para calcular el PE NTM correctamente. Se recomienda utilizar una clave API gratuita (limitada a 250 llamadas/día) o el plan básico, programando las actualizaciones de fundamentales para que ocurran semanalmente o bajo demanda, en lugar de en tiempo real, para conservar cuota.
- **Capa de Mercado (yfinance):** Se utilizará para la actualización masiva de precios de cierre diarios y la generación de gráficos históricos de rendimiento. Dado que es gratuito y eficiente para series temporales, permite refrescar el valor del portafolio frecuentemente sin coste.
- **Capa de Inteligencia (Finnhub + IA):** Para las noticias, Finnhub ofrece una excelente API de sentimiento y titulares generales en su capa gratuita. Estos titulares se utilizarán como insumo ("raw feed") para el motor de resumen de IA.

## 4. Arquitectura del Sistema y Selección Tecnológica
La arquitectura debe soportar una aplicación web reactiva, persistencia de datos segura, y procesos de automatización en segundo plano.

### 4.1. Framework Web: Reflex (Python-First)
Para un desarrollador individual o un entorno de finanzas personales donde Python es el lenguaje dominante, la separación tradicional Frontend (React/Vue) - Backend (Node/Django) introduce una complejidad innecesaria.

**Análisis: Reflex vs. Streamlit vs. FastAPI+React**
- **Streamlit:** Aunque popular en ciencia de datos, su modelo de ejecución (rerun script on interaction) lo hace inadecuado para aplicaciones complejas con estado persistente, autenticación de usuarios y múltiples vistas (Watchlist vs. Portafolio). Se vuelve lento y difícil de mantener a medida que crece el código.
- **FastAPI + React:** Ofrece máximo control pero requiere mantener dos bases de código en dos lenguajes distintos (Python y JS/TS), duplicando el esfuerzo de desarrollo.
- **Reflex (Elección Recomendada):** Reflex compila código Python puro en una aplicación React (Frontend) y FastAPI (Backend). Permite gestionar el estado del usuario, la interfaz y la lógica de negocio en un solo lenguaje. Su capacidad de manejar WebSockets facilita actualizaciones en tiempo real y su integración con bibliotecas como Pandas y Plotly es nativa. Además, facilita el despliegue como una aplicación web completa (PWA), cumpliendo el requisito de "app web personal".

### 4.2. Persistencia de Datos: Supabase (PostgreSQL)
El manejo de transacciones financieras y series temporales históricas exige una base de datos relacional con integridad referencial (ACID). Las soluciones NoSQL (como MongoDB) no son ideales para estructuras de portafolio altamente interconectadas.

**Por qué Supabase:**
- **PostgreSQL como Servicio:** Ofrece toda la potencia de Postgres sin la gestión de servidores.
- **API Data:** Expone automáticamente una API RESTful sobre las tablas, lo que simplifica la conexión desde los scripts de automatización (GitHub Actions) sin necesidad de mantener un backend intermedio para tareas simples.
- **Autenticación Integrada:** Maneja usuarios, sesiones y seguridad a nivel de fila (RLS). Esto asegura que si el proyecto escala a múltiples usuarios (ej. familiares), cada uno solo vea sus datos.

### 4.3. Automatización: GitHub Actions (Cron Serverless)
El sistema requiere una actualización diaria de métricas y envío de notificaciones. Ejecutar esto en un servidor VPS dedicado (EC2, DigitalOcean) implica costos fijos y mantenimiento (parches de seguridad).

**Estrategia "Git-Scraping":**
Se utilizará GitHub Actions como un programador de tareas (Cron Job). Un archivo de flujo de trabajo (`workflow.yml`) se configurará para ejecutarse diariamente (ej. a las 08:00 AM hora local). Este entorno efímero levantará un contenedor, instalará las dependencias Python, ejecutará el script de actualización (`daily_update.py`) y se apagará. Este enfoque es gratuito para repositorios públicos y tiene una asignación generosa para privados, eliminando el costo de infraestructura de automatización.

## 5. Estrategia de Inteligencia Artificial y Procesamiento de Noticias
El requisito de "usar IA para resumir lo más importante" implica implementar una arquitectura RAG (Retrieval-Augmented Generation) ligera. No basta con pedirle a un LLM que "hable sobre Apple", ya que su conocimiento está cortado en el pasado; se debe inyectar contexto reciente.

### 5.1. Pipeline de Procesamiento de Información
1. **Recolección (Extraction):** El script diario consulta la API de Finnhub o una búsqueda filtrada (ej. Bing News API vía RapidAPI) para obtener los últimos 10-15 artículos relevantes para cada ticker en el portafolio.
2. **Curación (Filtering):** Se aplica un filtro de palabras clave (ej. "Earnings", "Merger", "CEO", "Guidance") para eliminar ruido como análisis técnico genérico o publicidad.
3. **Síntesis (Generation):** Se agrupan los textos de los artículos y se envían a un LLM (OpenAI GPT-4o-mini o Claude 3 Haiku) con un prompt de sistema diseñado para analistas financieros.

### 5.2. Ingeniería de Prompts para Finanzas
El prompt no debe solicitar un resumen genérico. Debe estructurarse para extraer impacto y sentimiento.
- **System Prompt:** "Eres un analista de inversiones senior. Tu objetivo es filtrar ruido y destacar señales fundamentales."
- **Task:** "Para las siguientes noticias sobre, genera un resumen ejecutivo de máximo 3 puntos. Evalúa el sentimiento (Positivo/Negativo/Neutro) y clasifica el impacto (Alto/Medio/Bajo) en la tesis de inversión a largo plazo."
- **Output Format:** JSON estricto para facilitar la renderización en el frontend de Reflex.
Esta estrategia transforma una lista de noticias ininteligible en un tablero de control con semáforos de sentimiento.

## 6. Infraestructura de Notificaciones y Alertas
Para garantizar la ubicuidad del sistema (mail/móvil), se integrarán canales de empuje (push) y de archivo.

### 6.1. Telegram Bot (Canal Inmediato)
Telegram ofrece la mejor API de mensajería para desarrolladores.
- **Capacidades:** Permite enviar alertas instantáneas al móvil con formato Markdown (negritas, enlaces) e incluso gráficos generados con matplotlib o plotly (enviados como imágenes PNG).
- **Implementación:** Se utilizará la librería `python-telegram-bot`. El bot funcionará en modo "Webhook" o simplemente como emisor unidireccional desde el script de GitHub Actions.
- **Interactividad:** El usuario puede solicitar un "Snapshot" del portafolio en cualquier momento enviando el comando `/status` al bot.

### 6.2. Email Digest (Canal de Profundidad)
Para el resumen diario completo (que puede ser extenso), el correo electrónico es superior.
- **Herramienta:** `smtplib` de Python (estándar) conectado a una cuenta de Gmail (usando App Passwords) o SendGrid (capa gratuita).
- **Formato:** HTML/CSS responsivo que incluya tablas de rendimiento y los resúmenes de IA bien formateados.

## 7. Plan de Implementación y Prompt Maestro
A continuación, se detalla la hoja de ruta para la construcción del sistema y el prompt maestro para generar el código base.

### 7.1. Esquema de Base de Datos (Modelo Relacional)
El diseño de la base de datos en Supabase debe seguir la Tercera Forma Normal (3NF) para asegurar integridad.

**Tablas Principales:**
- `users`: Extiende la tabla `auth.users` de Supabase. Campos: `telegram_chat_id`, `risk_profile`.
- `assets`: Tabla maestra de instrumentos. Campos: `symbol` (PK), `name`, `sector`, `asset_type` (Stock, ETF).
- `portfolios`: Contenedor de posiciones. Campos: `id` (PK), `user_id` (FK), `name`, `cash_balance`.
- `positions`: Estado actual. Campos: `portfolio_id` (FK), `asset_id` (FK), `quantity`, `avg_cost_basis`.
- `transactions`: Historial inmutable (Log). Campos: `id`, `portfolio_id`, `asset_id`, `type` (BUY/SELL/DIVIDEND), `quantity`, `price`, `date`, `fees`. Vital para el cálculo de TWR/MWR.
- `daily_metrics`: Serie temporal. Campos: `asset_id`, `date`, `closing_price`, `pe_ntm`, `fcf_share`.
- `watchlist`: Seguimiento. Campos: `user_id`, `asset_id`, `target_price`, `notes`.
- `news_cache`: Almacenamiento temporal de resúmenes IA para no regenerarlos constantemente. Campos: `asset_id`, `date`, `summary`, `sentiment_score`.

### 7.2. Prompt Detallado para Generación de Código
Este prompt está diseñado para ser ingresado en un asistente de codificación (Claude 3.5 Sonnet, GPT-4o) para producir un "scaffold" completo y funcional.

**PROMPT PARA EL ASISTENTE DE IA:**

> **Rol:** Actúa como Arquitecto de Software Principal experto en Python, Fintech y Desarrollo Full-Stack Moderno.
>
> **Objetivo:** Generar el código base completo, estructura de archivos y scripts de configuración para una aplicación web de gestión de inversiones llamada "SmartFolio".
>
> **Stack Tecnológico:**
> - **Frontend/Backend:** Reflex (Python puro).
> - **Base de Datos:** Supabase (PostgreSQL). Usa `supabase-py` para el cliente.
> - **APIs:** Financial Modeling Prep (FMP) para fundamentales, `yfinance` para precios, OpenAI para NLP.
> - **Notificaciones:** Telegram Bot API.
> - **CI/CD:** GitHub Actions.
>
> **Requerimientos Funcionales Detallados:**
>
> 1. **Módulo de Datos (`data_engine`):**
>    - Implementa una clase `DataManager` que obtenga el PE NTM consultando el endpoint de estimaciones de FMP y sumando los EPS de los próximos 4 trimestres.
>    - Implementa el cálculo de FCF/share obteniendo OCF y Capex del Cash Flow Statement y dividiendo por `weightedAverageShsOutDil`.
>    - Manejo de errores robusto (retry logic) para fallos de API.
>
> 2. **Módulo de Inteligencia (`ai_engine`):**
>    - Función que acepte una lista de textos de noticias y use OpenAI para devolver un objeto JSON con: `summary` (string), `sentiment` (float -1 a 1), `impact_level` (high/med/low).
>
> 3. **Lógica Financiera (`finance_core`):**
>    - Implementa la función `calculate_twr(transactions_df, current_value)` que calcule el Retorno Ponderado por Tiempo usando pandas.
>
> 4. **Interfaz de Usuario (Reflex):**
>    - **Página Dashboard:** KPIs principales, Gráfico de Valor de Portafolio vs Benchmark (SPY) usando Plotly.
>    - **Página Portfolio:** Tabla interactiva con formato condicional (verde/rojo) para métricas de valoración (PE NTM, FCF).
>    - **Página Watchlist:** Lista de seguimiento con alertas de precio.
>
> 5. **Automatización (`scripts/daily_sync.py`):**
>    - Script fuera del contexto de Reflex para ejecutarse en GitHub Actions. Debe actualizar precios en Supabase, generar resúmenes IA y enviar alerta a Telegram.
>
> **Entregables Requeridos:**
> - **SQL Schema:** DDL completo para crear las tablas en Supabase con RLS habilitado.
> - **Python Code:**
>   - `reflex_app/state.py`: Lógica de estado y eventos.
>   - `reflex_app/pages/dashboard.py`: UI del dashboard.
>   - `utils/finance.py`: Cálculos de PE, FCF y TWR.
> - **GitHub Workflow:** Archivo `.github/workflows/daily_job.yml` configurado para correr a las 22:00 UTC.
> - **Environment:** Plantilla `.env.example`.
>
> **Restricciones de Estilo:**
> - Usa Type Hinting en todo el código Python.
> - Sigue los principios SOLID.
> - Usa Pandas para manipulación de datos tabulares.
> - Añade docstrings explicando la lógica financiera de los cálculos.

## 8. Conclusión
El sistema "SmartFolio" descrito en este informe representa una convergencia entre la ingeniería de software moderna y el análisis financiero avanzado. Al rechazar las soluciones "caja negra" y optar por una arquitectura modular propia, el inversor obtiene control total sobre la lógica de valoración, eliminando los sesgos inherentes a las herramientas gratuitas que a menudo utilizan datos retrasados o métricas simplificadas.

La integración de métricas "Forward-looking" (PE NTM) y de "Calidad" (FCF/Share), combinada con la capacidad de síntesis de la IA, otorga una ventaja competitiva significativa. La elección de Reflex y Supabase asegura que el proyecto sea mantenible y scalables, mientras que el uso de GitHub Actions para la orquestación garantiza un costo operativo cercano a cero. Este plan proporciona una hoja de ruta clara para transformar una necesidad de gestión personal en una plataforma de inteligencia de inversiones de nivel profesional.

