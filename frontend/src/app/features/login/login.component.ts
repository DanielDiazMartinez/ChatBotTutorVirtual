import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { HeaderComponent } from '../../shared/components/header/header.component';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, HeaderComponent],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent {
  loginForm: FormGroup;
  registerForm: FormGroup;
  
  // Opciones para el selector de rol
  userRoles = [
    { value: 'student', label: 'Estudiante' },
    { value: 'teacher', label: 'Profesor' },
    { value: 'admin', label: 'Administrador' }
  ];

  constructor(
    private fb: FormBuilder, 
    private router: Router,
    private authService: AuthService
  ) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required],
      role: ['student', Validators.required]
    });

    this.registerForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      role: ['student', Validators.required]
    });
  }

  onLogin() {
    if (this.loginForm.valid) {
      const email = this.loginForm.get('email')?.value;
      const password = this.loginForm.get('password')?.value;
      const role = this.loginForm.get('role')?.value;
      
      console.log('Login:', this.loginForm.value);
      this.authService.login(email, password, role);
    } else {
      console.log('Formulario inválido');
      // Marcar los campos como touched para mostrar los errores
      this.loginForm.markAllAsTouched();
    }
  }

  onRegister() {
    if (this.registerForm.valid) {
      const email = this.registerForm.get('email')?.value;
      const role = this.registerForm.get('role')?.value;
      
      console.log('Register:', this.registerForm.value);
      this.authService.register(email, role);
    } else {
      console.log('Formulario de registro inválido');
      this.registerForm.markAllAsTouched();
    }
  }
}
