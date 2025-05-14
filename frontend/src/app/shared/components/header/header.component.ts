import { Component, Input, EventEmitter, Output, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../../services/auth.service';

export interface UserProfile {
  name: string;
  role: 'student' | 'teacher' | 'admin';
  avatar?: string;
}

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss'],
  standalone: true,
  imports: [CommonModule, RouterModule]
})
export class HeaderComponent implements OnInit {
  @Input() showDocumentsButton = false;
  @Input() isDocumentsModalVisible = false;
  @Input() currentUser: UserProfile = {
    name: 'Usuario',
    role: 'student'
  };
  @Output() toggleDocuments = new EventEmitter<void>();
  
  isProfileMenuOpen = false;
  isNotificationsOpen = false;
  hasNewNotifications = true;
  
  notificationItems = [
    {
      id: '1',
      title: 'Nuevo examen disponible',
      message: 'Se ha publicado un nuevo examen de Matemáticas',
      time: '10 min',
      read: false
    },
    {
      id: '2',
      title: 'Pregunta respondida',
      message: 'El profesor ha respondido a tu pregunta sobre límites',
      time: '1h',
      read: false
    },
    {
      id: '3',
      title: 'Documento compartido',
      message: 'Se ha compartido un nuevo documento en la asignatura de Física',
      time: '2h',
      read: true
    }
  ];
  
  constructor(private router: Router, private authService: AuthService) {}
  
  ngOnInit(): void {
    if (!this.currentUser || this.currentUser.name === 'Usuario') {
      const user = this.authService.getCurrentUser();
      if (user) {
        this.currentUser = user;
      }
    }
  }
  
  goToLogin(): void {
    this.router.navigate(['/login'], { replaceUrl: true });
  }
  
  goToDashboard(): void {
    if (this.currentUser.role === 'teacher') {
      this.router.navigate(['/teacher/dashboard']);
    } else {
      this.router.navigate(['/subject-selection']);
    }
  }
  
  onToggleDocuments(): void {
    this.toggleDocuments.emit();
  }
  
  toggleProfileMenu(): void {
    this.isProfileMenuOpen = !this.isProfileMenuOpen;
    if (this.isProfileMenuOpen) {
      this.isNotificationsOpen = false;
    }
  }
  
  toggleNotifications(): void {
    this.isNotificationsOpen = !this.isNotificationsOpen;
    if (this.isNotificationsOpen) {
      this.isProfileMenuOpen = false;
    }
  }
  
  markAllNotificationsAsRead(): void {
    this.notificationItems = this.notificationItems.map(item => ({
      ...item,
      read: true
    }));
    this.hasNewNotifications = false;
  }
  
  logout(): void {
    this.authService.logout();
  }

  handleAvatarError(event: Event): void {
    const imgElement = event.target as HTMLImageElement;
    imgElement.src = this.currentUser.role === 'teacher' 
      ? 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgd2lkdGg9IjI0IiBoZWlnaHQ9IjI0Ij48Y2lyY2xlIGN4PSIxMiIgY3k9IjEyIiByPSIxMCIgZmlsbD0iIzNmNTFiNSIvPjx0ZXh0IHg9IjEyIiB5PSIxNiIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjEyIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWxsPSJ3aGl0ZSI+UDwvdGV4dD48L3N2Zz4='
      : 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgd2lkdGg9IjI0IiBoZWlnaHQ9IjI0Ij48Y2lyY2xlIGN4PSIxMiIgY3k9IjEyIiByPSIxMCIgZmlsbD0iIzRjYWY1MCIvPjx0ZXh0IHg9IjEyIiB5PSIxNiIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjEyIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWxsPSJ3aGl0ZSI+RTwvdGV4dD48L3N2Zz4=';
  }
}
