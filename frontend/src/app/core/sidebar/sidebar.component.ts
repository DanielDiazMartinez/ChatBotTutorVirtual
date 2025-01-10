import { Component } from '@angular/core';
import { FileUploadService } from '../service/file-upload.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-sidebar',
  standalone: true,
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

  //Logica para subir archivos
  constructor(private fileUploadService: FileUploadService) {}

  async onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;

    if (input.files && input.files.length > 0) {
      const file = input.files[0];
      try {
        const response = await this.fileUploadService.uploadFile(file).toPromise();
        console.log('File uploaded successfully:', response);
      } catch (error) {
        console.error('Error uploading file:', error);
      }
    }

    
  }
  //Logica ocultar sidebar
  isCollapsed = false;

    toggleSidebar() {
      this.isCollapsed = !this.isCollapsed;
    }
}
