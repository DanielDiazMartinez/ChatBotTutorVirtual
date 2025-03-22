/src/app/
  /features/
    /dashboard/
      dashboard.component.ts    // Componente contenedor principal
      dashboard.component.html  // Plantilla que organiza todo
      dashboard.component.scss
      
      /sidebar/
        sidebar.component.ts    // Lista de documentos/conversaciones
        sidebar.component.html
        sidebar.component.scss
      
      /content-area/           // Área principal dividida en dos
        content-area.component.ts
        content-area.component.html
        content-area.component.scss
        
        /pdf-viewer/          // Visualizador de PDF
          pdf-viewer.component.ts
          pdf-viewer.component.html
          pdf-viewer.component.scss
        
        /chat-area/           // Área de chat completa
          chat-area.component.ts
          chat-area.component.html
          chat-area.component.scss
          
          /message-list/      // Lista de mensajes
            message-list.component.ts
            message-list.component.html
            message-list.component.scss
          
          /message-input/     // Input para nuevos mensajes
            message-input.component.ts
            message-input.component.html
            message-input.component.scss