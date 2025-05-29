import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { HeaderComponent } from '../../shared/components/header/header.component';
import { AuthService } from '../../core/services/auth.service';

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

  constructor(
    private fb: FormBuilder, 
    private router: Router,
    private authService: AuthService
  ) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required]
    });

    this.registerForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]]
    });
  }

  isLoggingIn = false;
  errorMessage: string | null = null;

  onLogin() {
    if (this.loginForm.valid) {
      this.isLoggingIn = true;
      this.errorMessage = null;
      
      const credentials = {
        email: this.loginForm.get('email')?.value,
        password: this.loginForm.get('password')?.value
      };
      
      console.log('Login:', this.loginForm.value);
      this.authService.login(credentials).subscribe({
        next: (response) => {
          if (response.data) {
            // Redirigir según el rol del usuario
            const userRole = response.data.user.role;
            console.log('Rol del usuario:', userRole);
            
            // Forzar un tiempo para que el token se procese
            setTimeout(() => {
              if (userRole === 'admin') {
                this.router.navigate(['/admin']);
              } else if (userRole === 'teacher') {
                this.router.navigate(['/teacher']);
              } else {
                this.router.navigate(['/subject-selection']);
              }
            }, 100);
          }
        },
        error: (error) => {
          console.error('Error en login:', error);
          this.errorMessage = error.error?.message || 'Error al iniciar sesión. Por favor, verifica tus credenciales.';
          this.isLoggingIn = false;
        },
        complete: () => {
          this.isLoggingIn = false;
        }
      });
    } else {
      console.log('Formulario inválido');
      // Marcar los campos como touched para mostrar los errores
      this.loginForm.markAllAsTouched();
    }
  }

  // Manejar evento Enter en el formulario de login
  onKeyPress(event: KeyboardEvent): void {
    if (event.key === 'Enter') {
      event.preventDefault();
      this.onLogin();
    }
  }

  onRegister() {
    if (this.registerForm.valid) {
      const newUser = {
        email: this.registerForm.get('email')?.value,
        name: this.registerForm.get('email')?.value.split('@')[0], // Usar parte del email como nombre provisional
        role: this.registerForm.get('role')?.value
      };
      
      console.log('Register:', newUser);
      alert('La funcionalidad de registro no está habilitada. Por favor, use el login.');
    } else {
      console.log('Formulario de registro inválido');
      this.registerForm.markAllAsTouched();
    }
  }
}
