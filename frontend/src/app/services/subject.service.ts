import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { HttpClient } from '@angular/common/http';
import { Subject } from '../features/subject-selection/interfaces/subject.interface';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class SubjectService {
  private selectedSubjectsSource = new BehaviorSubject<string[]>([]);
  selectedSubjects$ = this.selectedSubjectsSource.asObservable();
  private storageKey = 'selectedSubjects';

  constructor(private http: HttpClient) {
    // Recuperar asignaturas seleccionadas del localStorage al inicializar el servicio
    const storedSubjects = localStorage.getItem(this.storageKey);
    if (storedSubjects) {
      try {
        const parsedSubjects = JSON.parse(storedSubjects);
        this.selectedSubjectsSource.next(parsedSubjects);
      } catch (e) {
        console.error('Error al parsear las asignaturas almacenadas:', e);
      }
    }
  }

  setSelectedSubjects(subjects: string[]) {
    // Guardar en localStorage para persistencia
    localStorage.setItem(this.storageKey, JSON.stringify(subjects));
    this.selectedSubjectsSource.next(subjects);
    console.log('Asignaturas seleccionadas guardadas:', subjects);
  }

  getSelectedSubjects() {
    return this.selectedSubjectsSource.value;
  }

  getAllSubjects(): Observable<Subject[]> {
    return this.http.get<{ data: Subject[] }>(`${environment.apiUrl}/subjects`).pipe(
      map((response) => (response.data || []).map(subject => ({
        ...subject,
        id: String(subject.id) // Garantizar que todos los IDs son strings
      })))
    );
  }

  getSubjectById(id: string): Observable<Subject> {
    return this.http.get<Subject>(`${environment.apiUrl}/subjects/${id}`).pipe(
      map(subject => ({
        ...subject,
        id: String(subject.id) // Garantizar que el ID es string
      }))
    );
  }

  getSubjectsByUserId(userId: string): Observable<{ data: Subject[] }> {
    return this.http.get<{ data: Subject[] }>(`${environment.apiUrl}/users/${userId}/subjects`).pipe(
      map(response => ({
        data: response.data.map(subject => ({
          ...subject,
          id: String(subject.id) // Garantizar que todos los IDs son strings
        }))
      }))
    );
  }
}
