import { Component, OnInit, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatDialogModule, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { SubjectService, Subject } from '../../../../../core/services/subject.service';
import { UserService } from '../../../../../core/services/user.service';
import { User as AppUser } from '../../../../../core/models/user.model';

@Component({
  selector: 'app-manage-users-dialog',
  standalone: true,
  imports: [CommonModule, FormsModule, MatDialogModule],
  templateUrl: './manage-users-dialog.component.html',
  styleUrls: ['./manage-users-dialog.component.scss']
})
export class ManageUsersDialogComponent implements OnInit {
  subject: Subject;
  assignedUsers: AppUser[] = [];
  availableUsers: AppUser[] = [];
  usersToRemove: number[] = []; // Lista para almacenar IDs de usuarios a eliminar
  isLoading = false;
  searchTerm = '';
  searchTermAssigned = '';
  searchTermAvailable = '';
  selectedUserId: string | null = null;
  showStudents = true;
  showTeachers = true;
  showAssignedStudents = true;
  showAssignedTeachers = true;
  showAvailableStudents = true;
  showAvailableTeachers = true;
  newUser = {
    name: '',
    email: '',
    role: 'student' as 'student' | 'teacher'
  };
  
  constructor(
    public dialogRef: MatDialogRef<ManageUsersDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { subject: Subject, subjectService: SubjectService },
    private userService: UserService
  ) {
      this.subject = data.subject;
  }

  ngOnInit(): void {
    this.loadSubjectUsers();
    this.loadAvailableUsers();
  }
  
  loadSubjectUsers(): void {
      this.isLoading = true;
    this.data.subjectService.getSubject(this.subject.id).subscribe({
        next: (response) => {
        if (response.data) {
          const data: any = response.data;
          const teachers = (data.teachers || []).map((u: any) => ({
            id: u.id,
            email: u.email,
            full_name: u.full_name,
            role: 'teacher' as 'teacher'
          }));
          const students = (data.students || []).map((u: any) => ({
            id: u.id,
            email: u.email,
            full_name: u.full_name,
            role: 'student' as 'student'
          }));
          this.assignedUsers = [...teachers, ...students];
        }
          this.isLoading = false;
        this.loadAvailableUsers();
        },
        error: (error) => {
          console.error('Error al cargar usuarios:', error);
          this.isLoading = false;
        }
      });
  }

  loadAvailableUsers(): void {
    this.userService.getAllUsers().subscribe({
      next: (response) => {
        if (response.data) {
          const assignedIds = this.assignedUsers.map(u => u.id);
          this.availableUsers = response.data.filter(u => !assignedIds.includes(u.id));
        }
      },
      error: (error) => {
        console.error('Error al cargar usuarios disponibles:', error);
      }
    });
  }

  getFilteredAssignedUsers(): AppUser[] {
    return this.assignedUsers.filter(user => {
      const matchesSearch = !this.searchTermAssigned || 
        user.full_name.toLowerCase().includes(this.searchTermAssigned.toLowerCase()) ||
        user.email.toLowerCase().includes(this.searchTermAssigned.toLowerCase());
      const matchesRole = (user.role === 'student' && this.showAssignedStudents) ||
                         (user.role === 'teacher' && this.showAssignedTeachers);
      return matchesSearch && matchesRole;
    });
  }

  getFilteredAvailableUsers(): AppUser[] {
    return this.availableUsers.filter(user => {
      const matchesSearch = !this.searchTermAvailable || 
        user.full_name.toLowerCase().includes(this.searchTermAvailable.toLowerCase()) ||
        user.email.toLowerCase().includes(this.searchTermAvailable.toLowerCase());
      const matchesRole = (user.role === 'student' && this.showAvailableStudents) ||
                         (user.role === 'teacher' && this.showAvailableTeachers);
      return matchesSearch && matchesRole;
    });
  }
  
  removeUser(userId: number): void {
    const user = this.assignedUsers.find(u => u.id === userId);
    if (user) {
      this.assignedUsers = this.assignedUsers.filter(u => u.id !== userId);
      this.availableUsers.push(user);
      this.usersToRemove.push(userId); // Agregar el ID del usuario a la lista de usuarios a eliminar
    }
  }

  addUser(userId: number): void {
    const user = this.availableUsers.find(u => u.id === userId);
    if (user) {
      this.assignedUsers.push(user);
      this.availableUsers = this.availableUsers.filter(u => u.id !== userId);
    }
  }
  
  createNewUser(): void {
    if (!this.newUser.name || !this.newUser.email) return;

      this.isLoading = true;
    this.data.subjectService.createUser(this.newUser).subscribe({
      next: (response) => {
        if (response.data) {
          this.assignedUsers.push(response.data);
          this.newUser = { name: '', email: '', role: 'student' };
        }
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Error al crear usuario:', error);
          this.isLoading = false;
        }
      });
    }

  cancel(): void {
    this.dialogRef.close();
  }
  
  saveChanges(): void {
    this.isLoading = true;
    const subjectId = typeof this.subject.id === 'string' ? parseInt(this.subject.id, 10) : this.subject.id;
    const userIds = this.assignedUsers.map(u => u.id);
    
    // Primero eliminamos los usuarios marcados para eliminación
    if (this.usersToRemove.length > 0) {
      this.data.subjectService.removeUsersFromSubject(subjectId, this.usersToRemove).subscribe({
        next: () => {
          // Después de eliminar usuarios, agregamos los actuales
          this.addUsersToSubject(subjectId, userIds);
        },
        error: (error: any) => {
          console.error('Error al eliminar usuarios:', error);
          this.isLoading = false;
        }
      });
    } else {
      // Si no hay usuarios para eliminar, simplemente agregamos los actuales
      this.addUsersToSubject(subjectId, userIds);
    }
  }

  addUsersToSubject(subjectId: number, userIds: number[]): void {
    // Si no hay usuarios, cerramos el modal directamente
    if (userIds.length === 0) {
      const result = {
        updated: true,
        teachers: this.assignedUsers.filter(u => u.role === 'teacher').length,
        students: this.assignedUsers.filter(u => u.role === 'student').length
      };
      this.dialogRef.close(result);
      this.isLoading = false;
      return;
    }

    this.data.subjectService.addUsersToSubject(subjectId, userIds).subscribe({
      next: () => {
        const result = {
          updated: true,
          teachers: this.assignedUsers.filter(u => u.role === 'teacher').length,
          students: this.assignedUsers.filter(u => u.role === 'student').length
        };
        this.dialogRef.close(result);
      },
      error: (error: any) => {
        // Si es error 400 por no tener usuarios, cerramos el modal igualmente
        if (error.status === 400) {
          const result = {
            updated: true,
            teachers: this.assignedUsers.filter(u => u.role === 'teacher').length,
            students: this.assignedUsers.filter(u => u.role === 'student').length
          };
          this.dialogRef.close(result);
        } else {
          console.error('Error al guardar cambios:', error);
          this.isLoading = false;
        }
      }
    });
  }
}
