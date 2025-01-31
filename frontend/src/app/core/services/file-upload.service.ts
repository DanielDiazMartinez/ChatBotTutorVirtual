import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { catchError, throwError } from 'rxjs';

@Injectable({
  providedIn: 'root', 
})
export class FileUploadService {
  private apiUrl = 'http://0.0.0.0:8000/profesor/registrar-temario/';
  private getFilesUrl = 'http://0.0.0.0:8000/profesor/obtener-temarios/'; // URL para obtener los archivos

  constructor(private http: HttpClient) {}

  uploadTemario(titulo: string, descripcion: string, profesorId: number, archivo: File) {
    const formData = new FormData();
  
    // Campos del formulario
    formData.append('titulo', titulo);
    formData.append('descripcion', descripcion);
    formData.append('profesor_id', profesorId.toString()); // Convertir el ID a string
    formData.append('archivo', archivo); // Archivo subido
  
    // Enviar los datos al endpoint
    return this.http.post(this.apiUrl, formData).pipe(
      catchError((error: HttpErrorResponse) => {
        console.error('Error uploading file:', error);
        return throwError(() => new Error('Error uploading file.'));
      })
    );
  }

  getFiles() {
    return this.http.get<{ name: string }[]>(this.getFilesUrl).pipe(
      catchError((error: HttpErrorResponse) => {
        console.error('Error fetching files:', error);
        return throwError(() => new Error('Error fetching files.'));
      })
    );
  }
}
