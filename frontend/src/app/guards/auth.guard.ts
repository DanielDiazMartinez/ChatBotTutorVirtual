import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const authGuard = () => {
  const authService = inject(AuthService);
  const router = inject(Router);
  
  if (authService.isLoggedIn()) {
    return true;
  }
  
  // Redirigir al login
  return router.parseUrl('/login');
};

export const teacherGuard = () => {
  const authService = inject(AuthService);
  const router = inject(Router);
  
  if (authService.isTeacher()) {
    return true;
  }
  
  if (authService.isLoggedIn()) {
    // Si está logueado pero no es profesor, redirigir a la selección de asignaturas
    return router.parseUrl('/subject-selection');
  }
  
  // Si no está logueado, redirigir al login
  return router.parseUrl('/login');
};

export const studentGuard = () => {
  const authService = inject(AuthService);
  const router = inject(Router);
  
  if (authService.isStudent()) {
    return true;
  }
  
  if (authService.isLoggedIn() && authService.isTeacher()) {
    // Si está logueado pero es profesor, redirigir al dashboard de profesor
    return router.parseUrl('/teacher');
  }
  
  // Si no está logueado, redirigir al login
  return router.parseUrl('/login');
};

export const adminGuard = () => {
  const authService = inject(AuthService);
  const router = inject(Router);
  
  if (authService.isAdmin()) {
    return true;
  }
  
  if (authService.isLoggedIn()) {
    // Si está logueado pero no es administrador, redirigir según su rol
    if (authService.isTeacher()) {
      return router.parseUrl('/teacher');
    } else {
      return router.parseUrl('/subject-selection');
    }
  }
  
  // Si no está logueado, redirigir al login
  return router.parseUrl('/login');
};
