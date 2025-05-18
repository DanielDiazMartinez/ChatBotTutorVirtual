import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DocumentsComponent as SharedDocumentsComponent } from '../../../../shared/components/documents/documents.component';

@Component({
  selector: 'app-teacher-documents',
  standalone: true,
  imports: [CommonModule, SharedDocumentsComponent],
  template: '<app-documents [isAdminView]="false"></app-documents>'
})
export class DocumentsComponent {
  // Este componente simplemente utiliza el componente compartido de documentos
  // La funcionalidad de subir documentos está integrada en el componente compartido
}
