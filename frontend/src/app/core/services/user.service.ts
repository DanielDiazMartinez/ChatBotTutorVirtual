import { Injectable, inject } from '@angular/core';
import { ApiService } from './api.service';
import { Observable } from 'rxjs';
import { User, UserCreate } from '../models/user.model';
import { ApiResponse } from '../models/api-response.model';

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private api = inject(ApiService);

  getUsersByRole(role: 'admin' | 'teacher' | 'student'): Observable<ApiResponse<User[]>> {
    return this.api.get<User[]>(`users/list/${role}`);
  }

  getAllUsers(): Observable<ApiResponse<User[]>> {
    return this.api.get<User[]>('users/list');
  }
  
  getUserById(userId: number): Observable<ApiResponse<User>> {
    return this.api.get<User>(`users/${userId}`);
  }

  createUser(user: UserCreate): Observable<ApiResponse<User>> {
    return this.api.post<User>('users/register', user);
  }

  updateUser(userId: number, userData: Partial<User>): Observable<ApiResponse<User>> {
    return this.api.put<User>(`users/${userId}`, userData);
  }

  deleteUser(userId: number): Observable<ApiResponse<any>> {
    return this.api.delete(`users/${userId}`);
  }

  getAllSubjectsbyUserId(userId: number): Observable<ApiResponse<any>> {
    return this.api.get<any>(`users/${userId}/subjects`);
  }
}
