import { Component } from '@angular/core';
import { MatDialogRef, MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-modal-form',
  standalone: true,
  imports: [
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    FormsModule,
  ],
  templateUrl: './file-upload-modal.component.html',
  styleUrls: ['./file-upload-modal.component.scss'],
})
export class ModalFormComponent {
  titulo: string = '';
  descripcion: string = '';
  profesorId!: number;
  archivo!: File;

  constructor(private dialogRef: MatDialogRef<ModalFormComponent>) {}

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.archivo = input.files[0];
    }
  }

  onSubmit() {
    if (this.titulo && this.descripcion && this.profesorId && this.archivo) {
      // Cerrar el modal y pasar los datos al componente principal
      this.dialogRef.close({
        titulo: this.titulo,
        descripcion: this.descripcion,
        profesorId: this.profesorId,
        archivo: this.archivo,
      });
    } else {
      alert('Por favor, completa todos los campos.');
    }
  }
}
