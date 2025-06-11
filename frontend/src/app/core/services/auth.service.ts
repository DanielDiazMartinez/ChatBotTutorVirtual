import { Injectable, inject, PLATFORM_ID, Inject } from '@angular/core';
import { Router } from '@angular/router';
import { ApiService } from './api.service';
import { Observable } from 'rxjs';
import { ApiResponse } from '../models/api-response.model';
import { User, UserCreate, UserLogin } from '../models/user.model';
import { BehaviorSubject, tap } from 'rxjs';
import { isPlatformBrowser } from '@angular/common';

interface AuthResponse {
  user: User;
  access_token: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private api = inject(ApiService);
  private router = inject(Router);
  private readonly TOKEN_KEY = 'auth_token';
  private readonly USER_KEY = 'current_user';
  
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  currentUser$ = this.currentUserSubject.asObservable();

  constructor(@Inject(PLATFORM_ID) private platformId: Object) {
    if (isPlatformBrowser(this.platformId)) {
      this.currentUserSubject.next(this.getUserFromStorage());
    }
  }

  login(credentials: UserLogin): Observable<ApiResponse<AuthResponse>> {
    return this.api.post<AuthResponse>('auth/login', credentials).pipe(
      tap(response => {
        if (response.data) {
          this.setSession(response.data);
        }
      })
    );
  }

  register(user: UserCreate): Observable<ApiResponse<User>> {
    return this.api.post<User>('users/register', user);
  }

  logout(): void {
    if (isPlatformBrowser(this.platformId)) {
      localStorage.removeItem(this.TOKEN_KEY);
      localStorage.removeItem(this.USER_KEY);
    }
    this.currentUserSubject.next(null);
    this.router.navigate(['/login']);
  }

  // Método para manejar logout por token expirado
  logoutDueToExpiredToken(): void {
    if (isPlatformBrowser(this.platformId)) {
      localStorage.removeItem(this.TOKEN_KEY);
      localStorage.removeItem(this.USER_KEY);
    }
    this.currentUserSubject.next(null);
    this.router.navigate(['/login']);
  }

  isLoggedIn(): boolean {
    return !!this.getToken();
  }

  isAdmin(): boolean {
    return this.currentUserSubject.value?.role === 'admin';
  }

  isTeacher(): boolean {
    return this.currentUserSubject.value?.role === 'teacher';
  }

  isStudent(): boolean {
    return this.currentUserSubject.value?.role === 'student';
  }

  getToken(): string | null {
    if (isPlatformBrowser(this.platformId)) {
      return localStorage.getItem(this.TOKEN_KEY);
    }
    return null;
  }

  private setSession(authResult: AuthResponse): void {
    if (isPlatformBrowser(this.platformId)) {
      localStorage.setItem(this.TOKEN_KEY, authResult.access_token);
      localStorage.setItem(this.USER_KEY, JSON.stringify(authResult.user));
    }
    this.currentUserSubject.next(authResult.user);
    console.log('Usuario autenticado:', authResult.user);
  }
  
  private getUserFromStorage(): User | null {
    if (isPlatformBrowser(this.platformId)) {
      const user = localStorage.getItem(this.USER_KEY);
      return user ? JSON.parse(user) : null;
    }
    return null;
  }
}
