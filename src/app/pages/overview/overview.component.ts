import { Component } from '@angular/core';
import { Router, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth.service';
import { SidebarComponent } from '../sidebar/sidebar.component';

@Component({
  selector: 'app-overview',
  standalone: true,
  imports: [
    RouterModule,
    FormsModule,
    CommonModule,
    SidebarComponent
  ],
  templateUrl: './overview.component.html',
  styleUrls: ['./overview.component.scss'],
})
export class OverviewComponent {
  date: string = new Date().toISOString().split('T')[0];
  userFirstName: string = 'User';

  basicData = {
    labels: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
    datasets: [
      {
        label: 'Calories',
        data: [1000, 1200, 1500, 800, 2000, 1200, 1300],
        backgroundColor: ['#D0DBC1', '#F8E094', '#C2D3DB', '#DBC2CF', '#EAEAEC', '#A2C587', '#FBCEC9'],
      },
    ],
  };

  basicOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
    },
  };

  constructor(private authService: AuthService, private router: Router) {}

  ngOnInit() {
    setTimeout(() => {
      const user = this.authService.getUser();
      if (user && user.first_name) {
        this.userFirstName = user.first_name;
      }
    });
  }

  logout() {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}
