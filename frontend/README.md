        /chatbot-frontend
        │── /src
        │   ├── /app
        │   │   ├── /core           # Servicios, interceptores, etc.
        │   │   │   ├── /services   # Llamadas HTTP, IA, subida de archivos
        │   │   │   ├── /guards     # Guards de autenticación o permisos
        │   │   │   ├── /interceptors # Interceptores HTTP
        │   │   ├── /shared         # Componentes y utilidades reutilizables
        │   │   │   ├── /components # Botones, modales, loaders
        │   │   │   ├── /pipes      # Pipes personalizados
        │   │   │   ├── /directives # Directivas útiles
        │   │   ├── /features       # Módulos por funcionalidad
        │   │   │   ├── /chat       # Módulo del chatbot
        │   │   │   │   ├── chat.module.ts
        │   │   │   │   ├── chat.component.ts
        │   │   │   │   ├── chat.component.html
        │   │   │   │   ├── chat.component.scss
        │   │   │   │   ├── chat.service.ts
        │   │   │   ├── /upload     # Módulo para subir archivos
        │   │   │   │   ├── upload.module.ts
        │   │   │   │   ├── upload.component.ts
        │   │   │   │   ├── upload.component.html
        │   │   │   │   ├── upload.component.scss
        │   │   │   │   ├── upload.service.ts
        │   │   │   ├── /dashboard  # Vista principal
        │   │   │   │   ├── dashboard.module.ts
        │   │   │   │   ├── dashboard.component.ts
        │   │   │   │   ├── dashboard.component.html
        │   │   │   │   ├── dashboard.component.scss
        │   │   ├── /assets         # Imágenes, iconos, estilos globales
        │   │   ├── /environments   # Variables de entorno
        │   │   ├── app.module.ts
        │   │   ├── app.component.ts
        │   │   ├── app.component.html
        │   │   ├── app.component.scss
        │   ├── /styles            # Estilos globales
        │   ├── main.ts
        │   ├── index.html
    