Tutorial: Cómo subir el Bot de Control de Gastos a
  GitHub

  Introducción

  Este tutorial te guiará paso a paso para subir tu bot
  de control de gastos a GitHub desde tu sistema Linux.

  Paso 1: Preparación del Proyecto Local

  1.1 Verifica tu directorio de trabajo

   1 cd /home/b4ki/bot

  1.2 Verifica que tienes un repositorio Git local

   1 git status

  Paso 2: Crear el Repositorio en GitHub

   1. Ve a https://github.com (https://github.com) y
      asegúrate de estar logueado
   2. Haz clic en el botón verde "New" o en el símbolo "+"
      en la parte superior derecha
   3. Selecciona "New repository"
   4. Asigna un nombre al repositorio (por ejemplo:
      telegram-gasto-bot)
   5. Selecciona "Private" o "Public" según tu preferencia
   6. NO marques las casillas "Add a README file", "Add
      .gitignore", ni "Choose a license" (ya tienes estos
      archivos)
   7. Haz clic en "Create repository"

  Paso 3: Conectar tu Repositorio Local con GitHub

  3.1 Copia la URL del repositorio

  La URL se verá así:
  https://github.com/TU_USUARIO/telegram-gasto-bot.git

  3.2 Agrega el repositorio remoto

   1 git remote add origin
     https://github.com/TU_USUARIO/telegram-gasto-b
     ot.git

  Reemplaza TU_USUARIO con tu nombre de usuario de
  GitHub.

  3.3 Si recibes un error de historias no relacionadas

  Si al intentar empujar recibes un error como:

   1 fatal: refusing to merge unrelated histories

  Puedes resolverlo con:

   1 git pull origin main
     --allow-unrelated-histories

  Durante este proceso, si hay conflictos en archivos
  como README.md, puedes:

   1. Verificar qué archivos están en conflicto:

   1 git status

   2. Resolver el conflicto manteniendo tu versión local:

   1 git checkout --ours README.md
   2 git add README.md
   3 git commit

  Paso 4: Empujar tu Código a GitHub

  4.1 Empuja la rama principal

   1 git push -u origin main

  La primera vez que usas git push, el flag -u establece
  la rama remota como upstream, lo que permite futuros
  git push sin argumentos.

  Paso 5: Verificar la Subida

   1. Ve al repositorio en tu navegador
   2. Verifica que todos los archivos estén presentes
   3. Asegúrate de que la estructura del proyecto se vea
      bien

  Estructura del Proyecto

  Tu bot debe tener esta estructura:

    1 telegram-gasto-bot/
    2 ├── .gitignore
    3 ├── ARCHITECTURE.md
    4 ├── LICENSE
    5 ├── README.md
    6 ├── TUTORIAL.md
    7 ├── bot/
    8 │   ├── __init__.py
    9 │   ├── charts.py
   10 │   ├── database/
   11 │   │   ├── __init__.py
   12 │   │   └── connection.py
   13 │   ├── handlers/
   14 │   │   ├── __init__.py
   15 │   │   ├── budget_handlers.py
   16 │   │   ├── chart_handlers.py
   17 │   │   ├── export_handlers.py
   18 │   │   ├── start_handler.py
   19 │   │   ├── summary_handlers.py
   20 │   │   └── transaction_handlers.py
   21 │   ├── main.py
   22 │   ├── models/
   23 │   │   ├── __init__.py
   24 │   │   └── transaction.py
   25 │   ├── services/
   26 │   │   ├── __init__.py
   27 │   │   ├── reminder_service.py
   28 │   │   └── transaction_service.py
   29 │   ├── ui/
   30 │   │   ├── __init__.py
   31 │   │   └── keyboards.py
   32 │   └── utils/
   33 │       ├── __init__.py
   34 │       ├── constants.py
   35 │       └── validators.py
   36 ├── config/
   37 │   ├── __init__.py
   38 │   └── settings.py
   39 └── requirements.txt

  Paso 6: Configurar tu Bot de Telegram

  6.1 Configurar el archivo .env

  Crea un archivo .env en el directorio raíz de tu
  proyecto:

   1 TELEGRAM_TOKEN=tu_token_de_bot_aqui
   2 DB_NAME=movimientos.db
   3 CHART_WIDTH=800
   4 CHART_HEIGHT=600
   5 BUDGET_NOTIFICATION_HOUR=20
   6 REMINDER_HOUR=18

  6.2 Conseguir un Token de Bot de Telegram

   1. Busca @BotFather en Telegram
   2. Envía /newbot
   3. Sigue las instrucciones para crear tu bot
   4. Copia el token que te proporciona BotFather

  Paso 7: Instalar Dependencias y Ejecutar el Bot

  7.1 Instalar las dependencias

   1 pip install -r requirements.txt

  7.2 Ejecutar el bot

   1 python -m bot.main

  Solución de Problemas Comunes

  Problema: "Permission denied"

   - Verifica que tienes permisos para escribir en el
     repositorio
   - Asegúrate de haber iniciado sesión en GitHub

  Problema: "Updates were rejected because the remote
  contains work"

   - Esto ocurre si GitHub creó archivos automáticamente
     (como README)
   - Ejecuta: git pull origin main
     --allow-unrelated-histories

  Problema: "fatal: not a git repository"

   - Asegúrate de estar en el directorio correcto
   - Si no está inicializado como repositorio Git,
     ejecuta: git init

  Consejo de Seguridad

  NUNCA subas tu archivo .env a GitHub. El archivo
  .gitignore ya está configurado para excluirlo, lo cual
  es correcto.

  Conclusión

  ¡Felicitaciones! Has subido exitosamente tu bot de
  control de gastos a GitHub. Ahora puedes:

   1. Compartir tu proyecto con otros desarrolladores
   2. Aceptar contribuciones mediante pull requests
   3. Mantener un historial de versiones de tu código
   4. Usar GitHub Pages si necesitas documentación web
   5. Integrar con servicios de CI/CD para automatizar
      pruebas y despliegue

  Tu proyecto está listo para ser mantenido, mejorado y
  compartido en la comunidad de desarrollo.
