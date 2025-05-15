import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { HeaderComponent, UserProfile } from '../../shared/components/header/header.component';

@Component({
  selector: 'app-admin-view',
  standalone: true,
  imports: [CommonModule, RouterModule, HeaderComponent],
  templateUrl: './admin-view.component.html',
  styleUrls: ['./admin-view.component.scss']
})
export class AdminViewComponent implements OnInit {
  activeNav: string = 'dashboard';
  adminProfile: UserProfile = {
    name: 'Admin',
    role: 'admin',
    avatar: 'assets/images/admin-avatar.svg'
  };

  constructor() {}

  ngOnInit(): void {
    // Establecer la sección activa basada en la URL actual
    const path = window.location.pathname;
    if (path.includes('/admin/dashboard')) {
      this.activeNav = 'dashboard';
    } else if (path.includes('/admin/subjects')) {
      this.activeNav = 'subjects';
    } else if (path.includes('/admin/users')) {
      this.activeNav = 'users';
    } else if (path.includes('/admin/questions')) {
      this.activeNav = 'questions';
    } else if (path.includes('/admin/documents')) {
      this.activeNav = 'documents';
    } else if (path.includes('/admin/associations')) {
      this.activeNav = 'associations';
    }
  }

  setActive(navItem: string): void {
    this.activeNav = navItem;
  }
}
