import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideClientHydration, withEventReplay } from '@angular/platform-browser';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { provideHttpClient, withInterceptors, withFetch } from '@angular/common/http'; // Importar withFetch
import { authInterceptor } from './interceptors/auth.interceptor'; // Ejemplo de interceptor

import { routes } from './app.routes';

export const appConfig: ApplicationConfig = {
  providers: [
    // Proveedores existentes
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),
    provideClientHydration(withEventReplay()),
    provideAnimationsAsync(),

    // Nuevo proveedor de HttpClient con soporte para fetch
    provideHttpClient(
      withFetch(), // Habilitar fetch API
      withInterceptors([authInterceptor]) // Configuración de interceptores (opcional)
    ),
  ],
};
