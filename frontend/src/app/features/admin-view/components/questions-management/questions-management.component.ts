import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-questions-management',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <div class="questions-container">
      <div class="section-header">
        <h1>Análisis de Preguntas</h1>
        <div class="header-actions">
          <div class="search-box">
            <input type="text" placeholder="Buscar pregunta..." class="search-input">
            <span class="search-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
              </svg>
            </span>
          </div>
          <div class="filter-group">
            <label for="subject-filter">Asignatura:</label>
            <select id="subject-filter">
              <option value="todas">Todas</option>
              <option value="matematicas">Matemáticas</option>
              <option value="fisica">Física</option>
              <option value="biologia">Biología</option>
              <option value="literatura">Literatura</option>
            </select>
          </div>
        </div>
      </div>
      
      <div class="questions-stats">
        <div class="stats-card">
          <h3>Total de Preguntas</h3>
          <p class="stats-value">1,245</p>
        </div>
        <div class="stats-card">
          <h3>Promedio Diario</h3>
          <p class="stats-value">32</p>
        </div>
        <div class="stats-card">
          <h3>Tasa de Respuesta</h3>
          <p class="stats-value">97%</p>
        </div>
        <div class="stats-card">
          <h3>Satisfacción</h3>
          <p class="stats-value">4.8/5</p>
        </div>
      </div>
      
      <div class="questions-analysis-container">
        <div class="chart-container">
          <h2>Tendencia de preguntas por asignatura</h2>
          <div class="chart-placeholder">
            <p>Gráfico de tendencia</p>
            <p class="chart-note">En un entorno real, aquí se mostraría un gráfico con la tendencia de preguntas por asignatura a lo largo del tiempo.</p>
          </div>
        </div>
        
        <div class="questions-table">
          <h2>Preguntas frecuentes</h2>
          <table>
            <thead>
              <tr>
                <th>Pregunta</th>
                <th>Asignatura</th>
                <th>Frecuencia</th>
                <th>Última vez</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="question-text">¿Cómo se calcula la integral de una función compuesta?</td>
                <td>Matemáticas</td>
                <td>32</td>
                <td>Hace 2 horas</td>
              </tr>
              <tr>
                <td class="question-text">¿Qué es la ley de Ohm?</td>
                <td>Física</td>
                <td>28</td>
                <td>Hace 1 día</td>
              </tr>
              <tr>
                <td class="question-text">¿Cómo funciona la fotosíntesis?</td>
                <td>Biología</td>
                <td>27</td>
                <td>Hace 4 horas</td>
              </tr>
              <tr>
                <td class="question-text">¿Cuáles son las características del Realismo Literario?</td>
                <td>Literatura</td>
                <td>25</td>
                <td>Hace 2 días</td>
              </tr>
              <tr>
                <td class="question-text">¿Cómo se resuelve una ecuación diferencial?</td>
                <td>Matemáticas</td>
                <td>22</td>
                <td>Hace 8 horas</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      
      <div class="questions-by-subject">
        <h2>Distribución por asignaturas</h2>
        <div class="subjects-distribution">
          <div class="subject-bar">
            <div class="subject-info">
              <span class="subject-name">Matemáticas</span>
            </div>
            <div class="bar-container">
              <div class="bar" style="width: 75%"></div>
              <span class="bar-value">75% (932 preguntas)</span>
            </div>
          </div>
          
          <div class="subject-bar">
            <div class="subject-info">
              <span class="subject-name">Física</span>
            </div>
            <div class="bar-container">
              <div class="bar" style="width: 62%"></div>
              <span class="bar-value">62% (778 preguntas)</span>
            </div>
          </div>
          
          <div class="subject-bar">
            <div class="subject-info">
              <span class="subject-name">Biología</span>
            </div>
            <div class="bar-container">
              <div class="bar" style="width: 54%"></div>
              <span class="bar-value">54% (671 preguntas)</span>
            </div>
          </div>
          
          <div class="subject-bar">
            <div class="subject-info">
              <span class="subject-name">Literatura</span>
            </div>
            <div class="bar-container">
              <div class="bar" style="width: 48%"></div>
              <span class="bar-value">48% (598 preguntas)</span>
            </div>
          </div>
          
          <div class="subject-bar">
            <div class="subject-info">
              <span class="subject-name">Historia</span>
            </div>
            <div class="bar-container">
              <div class="bar" style="width: 41%"></div>
              <span class="bar-value">41% (515 preguntas)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .questions-container {
      padding: 1rem 0;
    }

    .section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.5rem;
      flex-wrap: wrap;
      gap: 1rem;

      h1 {
        color: #3f6464;
        font-size: 1.75rem;
        margin: 0;
      }
      
      .header-actions {
        display: flex;
        gap: 1rem;
        align-items: center;
        flex-wrap: wrap;
        
        .filter-group {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          
          label {
            font-size: 0.9rem;
            color: #666;
          }
          
          select {
            padding: 0.5rem;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            background-color: white;
            font-size: 0.9rem;
            color: #333;
          }
        }
      }
    }

    .search-box {
      position: relative;
      
      .search-input {
        padding: 0.6rem 0.75rem 0.6rem 2.25rem;
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        width: 240px;
        font-size: 0.9rem;
        
        &:focus {
          outline: none;
          border-color: #8FBC94;
          box-shadow: 0 0 0 2px rgba(143, 188, 148, 0.2);
        }
      }
      
      .search-icon {
        position: absolute;
        left: 0.75rem;
        top: 50%;
        transform: translateY(-50%);
        color: #999;
      }
    }

    .questions-stats {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 1.5rem;
      margin-bottom: 2rem;
      
      .stats-card {
        background-color: white;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        padding: 1.25rem;
        text-align: center;
        
        h3 {
          color: #666;
          font-size: 1rem;
          font-weight: 500;
          margin: 0 0 0.75rem 0;
        }
        
        .stats-value {
          color: #3f6464;
          font-size: 1.75rem;
          font-weight: 600;
          margin: 0;
        }
      }
    }

    .questions-analysis-container {
      display: grid;
      grid-template-columns: 1fr;
      gap: 2rem;
      margin-bottom: 2rem;
      
      @media (min-width: 992px) {
        grid-template-columns: 1fr 1fr;
      }
      
      h2 {
        color: #3f6464;
        font-size: 1.25rem;
        margin: 0 0 1rem 0;
      }
      
      .chart-container {
        background-color: white;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        padding: 1.5rem;
        
        .chart-placeholder {
          height: 240px;
          border: 1px dashed #ccc;
          border-radius: 4px;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          color: #999;
          
          p {
            margin: 0.5rem 0;
          }
          
          .chart-note {
            font-size: 0.8rem;
            padding: 0 1rem;
            text-align: center;
          }
        }
      }
      
      .questions-table {
        background-color: white;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        padding: 1.5rem;
        
        table {
          width: 100%;
          border-collapse: collapse;
          
          th, td {
            padding: 0.75rem 1rem;
            text-align: left;
            border-bottom: 1px solid #f0f0f0;
          }
          
          th {
            color: #666;
            font-weight: 600;
            font-size: 0.9rem;
          }
          
          .question-text {
            font-weight: 500;
            color: #333;
          }
          
          tr:last-child td {
            border-bottom: none;
          }
        }
      }
    }

    .questions-by-subject {
      background-color: white;
      border-radius: 8px;
      border: 1px solid #e0e0e0;
      padding: 1.5rem;
      margin-bottom: 2rem;
      
      h2 {
        color: #3f6464;
        font-size: 1.25rem;
        margin: 0 0 1.5rem 0;
      }
      
      .subjects-distribution {
        display: flex;
        flex-direction: column;
        gap: 1.25rem;
      }
      
      .subject-bar {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        
        .subject-info {
          display: flex;
          justify-content: space-between;
          align-items: center;
          
          .subject-name {
            font-weight: 500;
            color: #333;
          }
        }
        
        .bar-container {
          height: 24px;
          background-color: #f5f5f5;
          border-radius: 4px;
          overflow: hidden;
          position: relative;
          
          .bar {
            height: 100%;
            background-color: #8FBC94;
            border-radius: 4px;
          }
          
          .bar-value {
            position: absolute;
            right: 0.75rem;
            top: 50%;
            transform: translateY(-50%);
            font-size: 0.85rem;
            color: #333;
            font-weight: 500;
          }
        }
      }
    }
  `]
})
export class QuestionsManagementComponent {
  // En un caso real, estos datos vendrían de un servicio y se implementaría la búsqueda y filtrado
}
