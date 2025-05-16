import { Injectable, Inject, PLATFORM_ID } from '@angular/core';
import { Router } from '@angular/router';
import { BehaviorSubject } from 'rxjs';
import { UserProfile } from '../shared/components/header/header.component';
import { isPlatformBrowser } from '@angular/common';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private currentUserSubject = new BehaviorSubject<UserProfile | null>(null);
  currentUser$ = this.currentUserSubject.asObservable();
  
  constructor(
    private router: Router,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {
    // Intentar recuperar usuario del almacenamiento local solo en el navegador
    if (isPlatformBrowser(this.platformId)) {
      this.loadUserFromLocalStorage();
    }
  }
  
  private loadUserFromLocalStorage(): void {
    const userData = localStorage.getItem('currentUser');
    if (userData) {
      try {
        const user = JSON.parse(userData);
        this.currentUserSubject.next({
          name: user.name,
          role: user.role,
          avatar: user.role === 'teacher' ? 'assets/images/teacher-avatar.svg' : 
                 user.role === 'admin' ? 'assets/images/admin-avatar.svg' : 'assets/images/student-avatar.svg'
        });
      } catch (error) {
        console.error('Error al parsear los datos del usuario:', error);
        localStorage.removeItem('currentUser');
      }
    }
  }
  
  login(email: string, password: string): void {
    // En un escenario real, aquí se haría una llamada al API de autenticación
    let userData: UserProfile;
    
    // El rol vendrá determinado por el backend según las credenciales
    userData = {
      name: 'Usuario',
      role: 'student', // Este valor vendrá del backend
      avatar: 'assets/images/student-avatar.svg'
    };
    
    // Guardar datos en localStorage solo en el navegador
    if (isPlatformBrowser(this.platformId)) {
      localStorage.setItem('currentUser', JSON.stringify({
        email,
        role: userData.role,
        name: userData.name
      }));
    }
    
    // Actualizar el BehaviorSubject
    this.currentUserSubject.next(userData);
    
    // Redirigir según el rol
    if (userData.role === 'admin') {
      this.router.navigate(['/admin']);
    } else if (userData.role === 'teacher') {
      this.router.navigate(['/teacher']);
    } else {
      this.router.navigate(['/subject-selection']);
    }
  }
  
  register(email: string, role: 'student' | 'teacher' | 'admin'): void {
    // En un escenario real, aquí se registraría al usuario en el backend
    let userData: UserProfile;
    
    if (role === 'admin') {
      userData = {
        name: 'Administrador Nuevo',
        role: role,
        avatar: 'assets/images/admin-avatar.svg'
      };
    } else {
      userData = {
        name: role === 'teacher' ? 'Profesor Nuevo' : 'Estudiante Nuevo',
        role: role,
        avatar: role === 'teacher' ? 'assets/images/teacher-avatar.svg' : 'assets/images/student-avatar.svg'
      };
    }
    
    // Guardar datos en localStorage solo en el navegador
    if (isPlatformBrowser(this.platformId)) {
      localStorage.setItem('currentUser', JSON.stringify({
        email,
        role,
        name: userData.name
      }));
    }
    
    // Actualizar el BehaviorSubject
    this.currentUserSubject.next(userData);
    
    // Redirigir según el rol
    if (role === 'admin') {
      this.router.navigate(['/admin']);
    } else if (role === 'teacher') {
      this.router.navigate(['/teacher']);
    } else {
      this.router.navigate(['/subject-selection']);
    }
  }
  
  logout(): void {
    // Eliminar usuario del localStorage solo en el navegador
    if (isPlatformBrowser(this.platformId)) {
      localStorage.removeItem('currentUser');
    }
    
    // Actualizar el BehaviorSubject
    this.currentUserSubject.next(null);
    
    // Redireccionar al login
    this.router.navigate(['/login']);
  }
  
  getCurrentUser(): UserProfile | null {
    return this.currentUserSubject.value;
  }
  
  isLoggedIn(): boolean {
    return !!this.currentUserSubject.value;
  }
  
  isTeacher(): boolean {
    return this.currentUserSubject.value?.role === 'teacher';
  }
  
  isStudent(): boolean {
    return this.currentUserSubject.value?.role === 'student';
  }
  
  isAdmin(): boolean {
    // Verificar si el usuario tiene rol de administrador
    return this.currentUserSubject.value?.role === 'admin';
  }
}
