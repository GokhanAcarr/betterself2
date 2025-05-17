import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule, Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterModule
  ],
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.scss']
})
export class RegisterComponent {
  first_name = '';
  last_name = '';
  email = '';
  password = '';

  constructor(private authService: AuthService, private router: Router) {}

  register() {
    const payload = {
      first_name: this.first_name,
      last_name: this.last_name,
      email: this.email,
      password: this.password
    };

    this.authService.register(payload).subscribe({
      next: () => {
        alert('Kayıt başarılı!');
        this.router.navigate(['/login']);
      },
      error: (err) => {
        console.error('Kayıt hatası', err);
        alert('Kayıt sırasında hata oluştu!');
      }
    });
  }
}
