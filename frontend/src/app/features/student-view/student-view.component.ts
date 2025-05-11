import { Component } from '@angular/core';
import { SidebarComponent } from './components/sidebar/sidebar.component'; // Ajusta la ruta

@Component({
  selector: 'app-student-view',
  standalone: true,
  imports: [SidebarComponent], // Importa el componente standalone
  templateUrl: './student-view.component.html',
  styleUrls: ['./student-view.component.scss']
})
export class StudentViewComponent { }