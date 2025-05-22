import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService, User } from '../../services/auth.service';
import { SidebarComponent } from '../sidebar/sidebar.component';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { HttpClientModule } from '@angular/common/http';
import { PostsComponent } from '../../pages/posts/posts.component';
import { WaterIntakeComponent } from '../water-intake/water-intake.component';
import { SleepRecordComponent } from '../sleep-record/sleep-record.component';

@Component({
  selector: 'app-profile',
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.scss'],
  standalone: true,
  imports: [SidebarComponent, FormsModule, CommonModule, HttpClientModule, PostsComponent, WaterIntakeComponent, SleepRecordComponent],})
export class ProfileComponent implements OnInit {
  user: User | null = null;
  displayEditDialog = false;
  editUser: Partial<User> = {};

  constructor(private authService: AuthService, private router: Router) {}

  ngOnInit(): void {
    this.loadUser();
  }

  loadUser(): void {
    const localUser = this.authService.getUser();
    if (localUser) {
      this.authService.fetchUser(localUser.id).subscribe({
        next: (userData) => {
          this.user = userData;
        },
        error: (err) => {
          console.error('Failed to fetch user data:', err);
        },
      });
    }
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }

  showEditDialog(): void {
    if (this.user) {
      this.editUser = { ...this.user };
      this.displayEditDialog = true;
    }
  }

  saveUser(): void {
    if (!this.user) return;

    this.authService.updateUser(this.user.id, this.editUser).subscribe({
      next: () => {
        this.displayEditDialog = false;
        this.loadUser();
      },
      error: (err) => {
        console.error('Update failed:', err);
      },
    });
  }

  deleteUser(): void {
    if (!this.user) return;

    if (confirm('Are you sure you want to delete your account?')) {
      this.authService.deleteUser(this.user.id).subscribe({
        next: () => {
          this.authService.logout();
          alert('User deleted successfully');
          this.router.navigate(['/landing']);
        },
        error: (err) => {
          console.error('Delete failed:', err);
          alert('Failed to delete user.');
        },
      });
    }
  }
}
