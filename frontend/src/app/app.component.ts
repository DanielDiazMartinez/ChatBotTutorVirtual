import { Component } from '@angular/core';
import { MatSidenavModule } from '@angular/material/sidenav';




@Component({
  selector: 'app-root',
  standalone: true,
  imports: [MatSidenavModule],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
  
})
export class AppComponent {}
