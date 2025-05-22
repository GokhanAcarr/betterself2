import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
@Component({
  selector: 'app-admin',
  templateUrl: './admin.component.html',
  styleUrls: ['./admin.component.scss'],
  imports: [
    CommonModule, FormsModule]
})
export class AdminComponent {
  userSearchTerm = '';
  users = [
    { id: 1, name: 'Alice Johnson', email: 'alice@example.com' },
    { id: 2, name: 'Bob Smith', email: 'bob@example.com' },
    { id: 3, name: 'Charlie Lee', email: 'charlie@example.com' }
  ];
  filteredUsers = [...this.users];

  exercises = [
    {
      name: 'Push Up',
      category: 'Chest',
      description: 'Upper body strength exercise',
      image_url: 'https://via.placeholder.com/60'
    }
  ];

  newExercise = {
    name: '',
    category: '',
    description: '',
    image_url: ''
  };

  searchUsers() {
    const term = this.userSearchTerm.toLowerCase();
    this.filteredUsers = this.users.filter(user =>
      user.name.toLowerCase().includes(term)
    );
  }

  deleteUser(user: any) {
    this.users = this.users.filter(u => u !== user);
    this.searchUsers();
  }

  editUser(user: any) {
    alert(`Edit user: ${user.name} (not implemented in mock)`);
  }

  addExercise() {
    if (this.newExercise.name && this.newExercise.category) {
      this.exercises.push({ ...this.newExercise });
      this.newExercise = { name: '', category: '', description: '', image_url: '' };
    }
  }
}
