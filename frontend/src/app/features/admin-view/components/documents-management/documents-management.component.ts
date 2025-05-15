import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DocumentsComponent as SharedDocumentsComponent } from '../../../../shared/components/documents/documents.component';

@Component({
  selector: 'app-documents-management',
  standalone: true,
  imports: [CommonModule, SharedDocumentsComponent],
  template: '<app-documents [isAdminView]="true"></app-documents>'
})
export class DocumentsManagementComponent {
  // Este componente simplemente utiliza el componente compartido de documentos con la vista de admin
}