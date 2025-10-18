# Tutorial: Bot de Finanzas Personales para Telegram

¡Bienvenido a tu asistente de finanzas personales! Este bot te ayudará a llevar un registro claro y sencillo de tus ingresos y gastos directamente desde Telegram.

A continuación se explica cómo usar cada una de sus funciones paso a paso.

## 1. Iniciar el Bot y Ayuda

Para empezar a interactuar con el bot y activar todas sus funciones (incluyendo los resúmenes diarios), simplemente búscalo en Telegram y envíale el comando:

```
/start
```

El bot te saludará. Para ver una lista completa de los comandos disponibles en cualquier momento, usa:
```
/help
```

## 2. Registrar Movimientos Manualmente

Puedes añadir ingresos o gastos de forma rápida con un simple mensaje de texto. Usa el siguiente formato:

`tipo categoría monto`

- **`tipo`**: Puede ser `ingreso` o `gasto`.
- **`categoría`**: Una o varias palabras que describan el movimiento (ej: `salario`, `compra supermercado`, `transporte`).
- **`monto`**: El valor numérico. Puedes usar `.` o `,` para los decimales.

**Ejemplos:**

- Para registrar un gasto de supermercado:
  ```
  gasto compra supermercado 350.50
  ```

- Para registrar un ingreso por tu salario:
  ```
  ingreso salario 15000
  ```

El bot te confirmará que el movimiento ha sido guardado.

## 3. Registrar un Gasto con una Foto (OCR)

Si tienes una factura o un ticket, el bot puede leerlo por ti.

1.  **Envía la foto**: Abre el chat con el bot y adjunta la imagen de la factura.
2.  **Confirma el monto**: El bot analizará la imagen, encontrará el monto total y te preguntará si es correcto.
    > "He encontrado un monto de $1,250.00. ¿Es correcto?"
3.  **Elige la categoría**: Si confirmas el monto, el bot te mostrará botones con categorías comunes (🍔 Comida, 🚗 Transporte, etc.). También puedes presionar "✍️ Escribir otra" para definir tu propia categoría.
4.  **Registro completado**: Una vez elegida la categoría, el gasto se guardará automáticamente.

## 4. Consultar tus Finanzas

El bot tiene varios comandos para darte un resumen de tus finanzas:

- `/hoy`: Muestra un resumen de los ingresos, gastos y balance del día actual.
- `/total`: Muestra el balance final histórico (Total de Ingresos - Total de Gastos).
- `/export`: Te envía un archivo `.csv` con todos tus movimientos, ideal para abrir en Excel o Google Sheets.

## 5. Visualizar tus Datos con Gráficos

Para obtener una vista más visual de tus finanzas, usa el comando:

```
/grafico
```

El bot te enviará dos imágenes:
- Un **gráfico de pastel** que muestra la distribución de tus gastos por categoría.
- Un **gráfico de barras** que compara tus ingresos y gastos de la última semana.

## 6. Editar y Eliminar Registros

Si te equivocaste al registrar un movimiento, puedes corregirlo. Primero, necesitarás el **ID** del movimiento. Puedes encontrarlo en el archivo que generas con `/export`.

- **Para editar el monto de un registro**:
  ```
  /editar <ID> <nuevo_monto>
  ```
  > Ejemplo: `/editar 15 450.50`

- **Para eliminar un registro**:
  ```
  /borrar <ID>
  ```
  > Ejemplo: `/borrar 21`

En ambos casos, el bot te pedirá una confirmación final antes de aplicar el cambio.

## 7. Resúmenes Diarios Automáticos

Después de usar `/start` por primera vez, el bot te enviará automáticamente un resumen de tus finanzas **todos los días a las 21:00**. Este resumen incluye tu total de ingresos, gastos y el balance general hasta la fecha.

¡Y eso es todo! Con estas herramientas, puedes mantener un control total de tus finanzas personales directamente desde Telegram.