import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { StudentViewComponent } from './features/student-view/student-view.component'; // Ajusta la ruta según tu estructura de carpetas
@Component({
  selector: 'app-root',
  imports: [RouterOutlet,StudentViewComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  title = 'frontend';
}
