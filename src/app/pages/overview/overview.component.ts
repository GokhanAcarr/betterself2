import { Component } from '@angular/core';
import { Router, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth.service';
import { SleepRecordService } from '../../services/sleep-record.service';
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
  userFirstName: string = 'User';
  date: string = new Date().toISOString().split('T')[0];
  sleepQuality: number | null = null;

  constructor(
    private authService: AuthService,
    private sleepRecordService: SleepRecordService,
    private router: Router
  ) {}

  ngOnInit() {
  setTimeout(() => {
    const user = this.authService.getUser();
    if (user && user.first_name) {
      this.userFirstName = user.first_name;
      const preferredHours = user.preferred_sleep_hours ?? 0;
      this.loadSleepQuality(preferredHours);
    }
  });
}

loadSleepQuality(preferredSleepHours: number) {
  this.sleepRecordService.getSleepRecord().subscribe({
    next: (sleepRecord) => {
      const hoursSlept = sleepRecord.hours_slept;
      this.sleepQuality = this.calculateSleepQuality(hoursSlept, preferredSleepHours);
    },
    error: (err) => {
      console.error('Sleep record loading failed', err);
      this.sleepQuality = null;
    }
  });
}

  calculateSleepQuality(hoursSlept: number | null, preferredSleepHours: number): number {
    if (hoursSlept === null || preferredSleepHours === 0) return 0;
    const quality = (hoursSlept / preferredSleepHours) * 100;
    return quality > 100 ? 100 : quality;
  }

  logout() {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}
