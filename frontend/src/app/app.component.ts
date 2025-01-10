import { Component } from '@angular/core';
import { MatSidenavModule } from '@angular/material/sidenav';
import { SidebarComponent } from './core/sidebar/sidebar.component';
import { PDFViewerComponent } from './core/pdf-viewer/pdf-viewer.component';



@Component({
  selector: 'app-root',
  standalone: true,
  imports: [MatSidenavModule, SidebarComponent, PDFViewerComponent],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
  
})
export class AppComponent {}
