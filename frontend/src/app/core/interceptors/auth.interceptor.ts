import { HttpHandlerFn, HttpInterceptorFn, HttpRequest, HttpErrorResponse } from '@angular/common/http';
import { isPlatformBrowser } from '@angular/common';
import { PLATFORM_ID, inject } from '@angular/core';
import { catchError, throwError } from 'rxjs';
import { AuthService } from '../services/auth.service';

export const authInterceptor: HttpInterceptorFn = (
  req: HttpRequest<unknown>,
  next: HttpHandlerFn
) => {
  const platformId = inject(PLATFORM_ID);
  const authService = inject(AuthService);
  let token: string | null = null;
  
  if (isPlatformBrowser(platformId)) {
    token = localStorage.getItem('auth_token');
  }
  
  if (token) {
    const authReq = req.clone({
      headers: req.headers.set('Authorization', `Bearer ${token}`)
    });
    
    return next(authReq).pipe(
      catchError((error: HttpErrorResponse) => {
        // Si el token ha expirado o no es válido (401), hacer logout y redirigir al login
        if (error.status === 401) {
          authService.logoutDueToExpiredToken();
        }
        return throwError(() => error);
      })
    );
  }
  
  return next(req);
};
