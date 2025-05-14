import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss'],
  standalone: true,
  imports: [CommonModule]
})
export class HeaderComponent {
  constructor(private router: Router) {}
  
  goToLogin(): void {
    this.router.navigate(['/login'], { replaceUrl: true });
  }
}
