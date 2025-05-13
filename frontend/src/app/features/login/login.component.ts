import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent {
  loginForm: FormGroup;
  registerForm: FormGroup;

  constructor(private fb: FormBuilder) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required]
    });

    this.registerForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]]
    });
  }

  onLogin() {
    if (this.loginForm.valid) {
      console.log('Login:', this.loginForm.value);
    }
  }

  onRegister() {
    if (this.registerForm.valid) {
      console.log('Register:', this.registerForm.value);
    }
  }
}
