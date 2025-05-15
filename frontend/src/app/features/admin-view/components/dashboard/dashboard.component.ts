import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <div class="dashboard-container">
      <div class="section-header">
        <h1>Dashboard de Administrador</h1>
      </div>
      
      <div class="stats-overview">
        <div class="stats-card">
          <div class="stats-icon users-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z" fill="currentColor"/>
            </svg>
          </div>
          <div class="stats-content">
            <h3>Usuarios Totales</h3>
            <p class="stats-value">125</p>
            <div class="stats-breakdown">
              <span>85 Estudiantes</span>
              <span>40 Profesores</span>
            </div>
          </div>
          <a [routerLink]="['/admin/users']" class="stats-link">Gestionar usuarios</a>
        </div>
        
        <div class="stats-card">
          <div class="stats-icon subjects-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M18 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM9 4h2v5l-1-.75L9 9V4zm9 16H6V4h1v9l3-2.25L13 13V4h5v16z" fill="currentColor"/>
            </svg>
          </div>
          <div class="stats-content">
            <h3>Asignaturas Activas</h3>
            <p class="stats-value">18</p>
            <div class="stats-breakdown">
              <span>12 Con documentos</span>
              <span>6 Sin documentos</span>
            </div>
          </div>
          <a [routerLink]="['/admin/subjects']" class="stats-link">Gestionar asignaturas</a>
        </div>
        
        <div class="stats-card">
          <div class="stats-icon documents-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z" fill="currentColor"/>
            </svg>
          </div>
          <div class="stats-content">
            <h3>Documentos</h3>
            <p class="stats-value">234</p>
            <div class="stats-breakdown">
              <span>95% Procesados</span>
              <span>5% En cola</span>
            </div>
          </div>
          <a [routerLink]="['/admin/documents']" class="stats-link">Gestionar documentos</a>
        </div>
      </div>
      
      <div class="admin-panels">
        <div class="panel">
          <div class="panel-header">
            <h2>Actividad Reciente</h2>
          </div>
          <div class="activity-list">
            <div class="activity-item">
              <div class="activity-icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                  <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" fill="currentColor"/>
                </svg>
              </div>
              <div class="activity-content">
                <p>Nuevo usuario registrado: <strong>Laura Martínez</strong></p>
                <span class="activity-time">Hace 1 hora</span>
              </div>
            </div>
            
            <div class="activity-item">
              <div class="activity-icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                  <path d="M18 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z" fill="currentColor"/>
                </svg>
              </div>
              <div class="activity-content">
                <p>Nueva asignatura creada: <strong>Matemáticas Avanzadas</strong></p>
                <span class="activity-time">Hace 3 horas</span>
              </div>
            </div>
            
            <div class="activity-item">
              <div class="activity-icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                  <path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6z" fill="currentColor"/>
                </svg>
              </div>
              <div class="activity-content">
                <p>Nuevo documento subido: <strong>Guía de Física</strong></p>
                <span class="activity-time">Ayer</span>
              </div>
            </div>
            
            <div class="activity-item">
              <div class="activity-icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                  <path d="M19 3h-4.18C14.4 1.84 13.3 1 12 1c-1.3 0-2.4.84-2.82 2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 0c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm2 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z" fill="currentColor"/>
                </svg>
              </div>
              <div class="activity-content">
                <p>Usuario asignado a asignatura: <strong>Carlos López</strong> a <strong>Biología</strong></p>
                <span class="activity-time">Hace 2 días</span>
              </div>
            </div>
          </div>
        </div>
        

      </div>
    </div>
  `,
  styles: [`
    .dashboard-container {
      padding: 1rem 0;
    }

    .section-header {
      margin-bottom: 1.5rem;
      h1 {
        color: #3f6464;
        font-size: 1.75rem;
        margin: 0;
      }
    }

    .stats-overview {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 1.5rem;
      margin-bottom: 2rem;
    }

    .stats-card {
      background-color: white;
      border-radius: 8px;
      border: 1px solid #e0e0e0;
      padding: 1.5rem;
      display: flex;
      flex-direction: column;
      position: relative;
      overflow: hidden;
      
      &::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        height: 4px;
        width: 100%;
      }
      
      &:nth-child(1)::before {
        background-color: #5c9ced;
      }
      
      &:nth-child(2)::before {
        background-color: #8FBC94;
      }
      
      &:nth-child(3)::before {
        background-color: #f39c12;
      }
      
      .stats-icon {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 1rem;
        
        &.users-icon {
          background-color: rgba(92, 156, 237, 0.15);
          color: #5c9ced;
        }
        
        &.subjects-icon {
          background-color: rgba(143, 188, 148, 0.15);
          color: #8FBC94;
        }
        
        &.documents-icon {
          background-color: rgba(243, 156, 18, 0.15);
          color: #f39c12;
        }
      }
      
      .stats-content {
        h3 {
          font-size: 1rem;
          font-weight: 500;
          color: #666;
          margin: 0 0 0.5rem 0;
        }
        
        .stats-value {
          font-size: 2rem;
          font-weight: 600;
          color: #333;
          margin: 0 0 0.5rem 0;
        }
        
        .stats-breakdown {
          display: flex;
          flex-wrap: wrap;
          gap: 1rem;
          margin-bottom: 1rem;
          
          span {
            font-size: 0.85rem;
            color: #666;
          }
        }
      }
      
      .stats-link {
        margin-top: auto;
        display: inline-block;
        font-size: 0.9rem;
        color: #5c9ced;
        text-decoration: none;
        
        &:hover {
          text-decoration: underline;
        }
      }
    }

    .admin-panels {
      display: grid;
      grid-template-columns: 1fr;
      gap: 1.5rem;
    }

    .panel {
      background-color: white;
      border-radius: 8px;
      border: 1px solid #e0e0e0;
      
      .panel-header {
        padding: 1rem 1.5rem;
        border-bottom: 1px solid #f0f0f0;
        
        h2 {
          font-size: 1.25rem;
          margin: 0;
          color: #3f6464;
        }
      }
    }

    .activity-list {
      padding: 0.5rem 0;
    }

    .activity-item {
      display: flex;
      padding: 1rem 1.5rem;
      border-bottom: 1px solid #f5f5f5;
      
      &:last-child {
        border-bottom: none;
      }
      
      .activity-icon {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background-color: #f5f5f5;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 1rem;
        flex-shrink: 0;
        color: #666;
      }
      
      .activity-content {
        p {
          margin: 0 0 0.25rem 0;
          color: #333;
        }
        
        .activity-time {
          font-size: 0.85rem;
          color: #999;
        }
      }
    }

    .quick-actions {
      .actions-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        padding: 1.5rem;
        
        .action-btn {
          display: flex;
          flex-direction: column;
          align-items: center;
          padding: 1rem;
          border-radius: 8px;
          background-color: #f9f9f9;
          text-decoration: none;
          color: #3f6464;
          transition: all 0.2s ease;
          
          svg {
            margin-bottom: 0.5rem;
            color: #3f6464;
          }
          
          &:hover {
            background-color: #f0f0f0;
            transform: translateY(-2px);
          }
        }
      }
    }
  `]
})
export class DashboardComponent {
  // En un caso real, estos datos vendrían de un servicio
}
