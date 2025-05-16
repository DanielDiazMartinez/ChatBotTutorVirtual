import { Component, OnInit } from '@angular/core';
import { UserService } from '../../../../core/services/user.service';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [RouterModule],
  templateUrl: './admin-dashboard.component.html',
  styleUrls: ['./admin-dashboard.component.scss']
})
export class AdminDashboardComponent implements OnInit {
  totalUsuarios = 0;
  totalProfesores = 0;
  totalEstudiantes = 0;

  // Valores fijos por ahora, listos para ser dinámicos
  totalAsignaturas = 18; // TODO: hacer dinámico en el futuro
  totalDocumentos = 234; // TODO: hacer dinámico en el futuro

  constructor(private userService: UserService) {}

  ngOnInit(): void {
    this.userService.getAllUsers().subscribe({
      next: (response) => {
        if (response.data) {
          this.totalUsuarios = response.data.length;
          this.totalProfesores = response.data.filter(u => u.role === 'teacher').length;
          this.totalEstudiantes = response.data.filter(u => u.role === 'student').length;
        }
      },
      error: () => {
        this.totalUsuarios = 0;
        this.totalProfesores = 0;
        this.totalEstudiantes = 0;
      }
    });
  }
} 