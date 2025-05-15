import { Component, Inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogModule } from '@angular/material/dialog';
import { SubjectService, User } from '../../../../../core/services/subject.service';

@Component({
  selector: 'app-manage-users-dialog',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule, MatDialogModule],
  templateUrl: './manage-users-dialog.component.html',
  styleUrls: ['./manage-users-dialog.component.scss']
})
export class ManageUsersDialogComponent implements OnInit {
  subject: any;
  assignedUsers: User[] = [];
  availableUsers: User[] = [];
  selectedUserId: string = '';
  searchTerm: string = '';
  showStudents: boolean = true;
  showTeachers: boolean = true;
  
  userForm: FormGroup;

  private subjectService!: SubjectService;
  isLoading: boolean = false;
  
  constructor(
    private fb: FormBuilder,
    public dialogRef: MatDialogRef<ManageUsersDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {
    this.userForm = this.fb.group({
      name: ['', [Validators.required]],
      email: ['', [Validators.required, Validators.email]],
      role: ['student', [Validators.required]]
    });
    
    if (data && data.subject) {
      this.subject = data.subject;
    }
    
    if (data && data.subjectService) {
      this.subjectService = data.subjectService;
    }
  }

  ngOnInit(): void {
    this.loadSubjectUsers();
  }
  
  loadSubjectUsers(): void {
    if (this.subject && this.subjectService) {
      this.isLoading = true;
      this.subjectService.getSubjectUsers(this.subject.id).subscribe({
        next: (response) => {
          this.assignedUsers = response.assignedUsers;
          this.availableUsers = response.availableUsers;
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Error al cargar usuarios:', error);
          this.isLoading = false;
        }
      });
    } else {
      console.error('No se pudo cargar los usuarios: falta la asignatura o el servicio.');
    }
  }

  getFilteredAvailableUsers(): User[] {
    return this.availableUsers.filter(user => {
      const nameMatch = user.name.toLowerCase().includes(this.searchTerm.toLowerCase()) || 
                       user.email.toLowerCase().includes(this.searchTerm.toLowerCase());
      const roleMatch = (this.showStudents && user.role === 'student') || 
                       (this.showTeachers && user.role === 'teacher');
      return nameMatch && roleMatch;
    });
  }

  addUser(): void {
    const selectedUser = this.availableUsers.find(u => u.id === this.selectedUserId);
    if (selectedUser) {
      this.assignedUsers.push(selectedUser);
      this.availableUsers = this.availableUsers.filter(u => u.id !== this.selectedUserId);
      this.selectedUserId = '';
    }
  }
  
  removeUser(userId: string): void {
    const user = this.assignedUsers.find(u => u.id === userId);
    if (user) {
      this.availableUsers.push(user);
      this.assignedUsers = this.assignedUsers.filter(u => u.id !== userId);
    }
  }
  
  createNewUser(): void {
    if (this.userForm.valid) {
      this.isLoading = true;
      
      const userData: Partial<User> = {
        name: this.userForm.value.name,
        email: this.userForm.value.email,
        role: this.userForm.value.role
      };
      
      this.subjectService.createUser(userData).subscribe({
        next: (newUser) => {
          // Añadir el nuevo usuario directamente a los usuarios asignados
          this.assignedUsers.push(newUser);
          this.userForm.reset({role: 'student'});
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Error al crear usuario:', error);
          this.isLoading = false;
        }
      });
    }
  }
  
  saveChanges(): void {
    this.isLoading = true;
    
    if (this.subject && this.subjectService) {
      this.subjectService.updateSubjectUsers(this.subject.id, this.assignedUsers).subscribe({
        next: (updatedUsers) => {
          console.log('Usuarios asignados guardados correctamente:', updatedUsers);
          this.isLoading = false;
          this.dialogRef.close(updatedUsers);
        },
        error: (error) => {
          console.error('Error al guardar usuarios asignados:', error);
          this.isLoading = false;
          // Cerrar el diálogo con los datos actuales para actualizar la UI
          this.dialogRef.close(this.assignedUsers);
        }
      });
    } else {
      console.error('No se pudo guardar: falta la asignatura o el servicio.');
      this.dialogRef.close(this.assignedUsers);
    }
  }
  
  cancel(): void {
    this.dialogRef.close();
  }
}
