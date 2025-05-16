import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { User } from '../models/user.model';
import { map, take } from 'rxjs/operators';

export const authGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isLoggedIn()) {
    return true;
  }

  return router.parseUrl('/login');
};

export const adminGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);
  
  if (!authService.isLoggedIn()) {
    return router.parseUrl('/login');
  }
  
  return authService.currentUser$.pipe(
    take(1),
    map(user => {
      if (user?.role === 'admin') {
        return true;
      } else if (user?.role === 'teacher') {
        return router.parseUrl('/teacher');
      } else {
        return router.parseUrl('/subject-selection');
      }
    })
  );
};

export const teacherGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);
  
  if (!authService.isLoggedIn()) {
    return router.parseUrl('/login');
  }
  
  return authService.currentUser$.pipe(
    take(1),
    map(user => {
      if (user?.role === 'teacher' || user?.role === 'admin') {
        return true;
      } else {
        return router.parseUrl('/subject-selection');
      }
    })
  );
};