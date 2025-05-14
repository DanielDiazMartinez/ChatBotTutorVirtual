import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { HeaderComponent, UserProfile } from '../../shared/components/header/header.component';

@Component({
  selector: 'app-teacher-view',
  standalone: true,
  imports: [CommonModule, RouterModule, HeaderComponent],
  templateUrl: './teacher-view.component.html',
  styleUrls: ['./teacher-view.component.scss']
})
export class TeacherViewComponent {
  // Navegación activa
  activeNav: string = 'dashboard';
  
  // Datos del usuario profesor
  teacherProfile: UserProfile = {
    name: 'Profesor Martínez',
    role: 'teacher',
    avatar: 'assets/images/teacher-avatar.svg'
  };

  setActive(navItem: string) {
    this.activeNav = navItem;
  }
  
  // Método para verificar si la URL actual contiene una ruta específica
  isActiveRoute(route: string): boolean {
    return window.location.href.includes(route);
  }
}
