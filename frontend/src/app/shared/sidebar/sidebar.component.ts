import { Component } from '@angular/core';
import { ModalFormComponent } from '../../features/upload/file-upload-modal/file-upload-modal.component';
import { CommonModule } from '@angular/common'; 
import { MatDialog } from '@angular/material/dialog';
import { FileUploadService } from '../../core/services/file-upload.service';
@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.scss'],
  imports: [CommonModule],
})
export class SidebarComponent {
  
  uploadedFiles = [
    { name: 'file1.txt' },
    { name: 'file2.jpg' },
    { name: 'file3.pdf' },
  ];

  constructor(private dialog: MatDialog,private fileUploadService: FileUploadService) {}

  openModal() {
    const dialogRef = this.dialog.open(ModalFormComponent, {
      width: '500px',
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        console.log('Datos recibidos del formulario:', result);

        // Llamar al servicio para subir los datos y el archivo
        this.fileUploadService
          .uploadTemario(result.titulo, result.descripcion, result.profesorId, result.archivo)
          .subscribe({
            next: (response) => {
              console.log('Archivo subido con éxito:', response);
            },
            error: (error) => {
              console.error('Error al subir el archivo:', error);
            },
          });
      } else {
        console.log('El modal fue cerrado sin enviar datos.');
      }
    });
  }
  
  //Logica ocultar sidebar
  isCollapsed = false;

    toggleSidebar() {
      this.isCollapsed = !this.isCollapsed;
    }
}
