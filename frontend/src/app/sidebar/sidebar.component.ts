import { Component } from '@angular/core';
import { MatSidenavModule } from '@angular/material/sidenav';
@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.component.html',
  imports: [MatSidenavModule],
  styleUrls: ['./sidebar.component.scss']
})
export class SidebarComponent {}
