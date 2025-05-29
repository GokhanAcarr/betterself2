import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService, User } from '../../services/auth.service';
import { Router } from '@angular/router';
import { SidebarComponent } from '../sidebar/sidebar.component';
import { ExerciseService, Exercise } from '../../services/exercise.service';

@Component({
  selector: 'app-admin',
  standalone: true,
  imports: [CommonModule, FormsModule, SidebarComponent],
  templateUrl: './admin.component.html',
  styleUrls: ['./admin.component.scss'],
})
export class AdminComponent implements OnInit {
  users: User[] = [];
  displayEditDialog = false;
  editUser: Partial<User> = {};
  searchTerm: string = '';

  // Yeni: Exercise için form alanları
  newExercise: Partial<Exercise> = {
    name: '',
    category: '',
    description: '',
    image_url: '',
  };

  // Yeni: Form gönderim durumu
  exerciseAdding = false;
  exerciseAddError: string | null = null;
  exerciseAddSuccess: string | null = null;

  constructor(
    private authService: AuthService,
    private router: Router,
    private exerciseService: ExerciseService
  ) {}

  ngOnInit(): void {
    this.loadUsers();
  }

  loadUsers(): void {
    this.authService.getUsers().subscribe({
      next: (data) => (this.users = data),
      error: (err) => console.error('Failed to load users:', err),
    });
  }

  showEditDialog(user: User): void {
    this.editUser = { ...user };
    this.displayEditDialog = true;
  }

  saveUser(): void {
    if (!this.editUser.id) return;

    this.authService.updateUser(this.editUser.id, this.editUser).subscribe({
      next: () => {
        this.displayEditDialog = false;
        this.loadUsers();
      },
      error: (err) => console.error('Update failed:', err),
    });
  }

  get filteredUsers() {
    return this.users.filter((user) =>
      user.first_name.toLowerCase().includes(this.searchTerm.toLowerCase())
    );
  }

  deleteUser(userId: number): void {
    if (confirm('Are you sure you want to delete this user?')) {
      this.authService.deleteUser(userId).subscribe({
        next: () => this.loadUsers(),
        error: (err) => console.error('Delete failed:', err),
      });
    }
  }

  // Yeni: Exercise ekleme fonksiyonu
  addExercise(): void {
    if (
      !this.newExercise.name ||
      !this.newExercise.category ||
      !this.newExercise.description ||
      !this.newExercise.image_url
    ) {
      this.exerciseAddError = 'Please fill all exercise fields.';
      return;
    }

    this.exerciseAdding = true;
    this.exerciseAddError = null;
    this.exerciseAddSuccess = null;

    this.exerciseService.addExercise(this.newExercise as Exercise).subscribe({
      next: (res) => {
        this.exerciseAddSuccess = res.message || 'Exercise added successfully.';
        this.exerciseAdding = false;
        // Formu temizle
        this.newExercise = {
          name: '',
          category: '',
          description: '',
          image_url: '',
        };
      },
      error: (err) => {
        this.exerciseAddError = err.error?.error || 'Failed to add exercise.';
        this.exerciseAdding = false;
      },
    });
  }
}
