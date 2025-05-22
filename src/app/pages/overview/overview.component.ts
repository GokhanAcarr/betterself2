import { Component, AfterViewInit, ViewChild, ElementRef } from '@angular/core';
import { Router, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth.service';
import { SleepRecordService } from '../../services/sleep-record.service';
import { SidebarComponent } from '../sidebar/sidebar.component';
import { Chart, BarController, BarElement, CategoryScale, LinearScale, Title, Tooltip, Legend, ChartConfiguration } from 'chart.js';
import { ExerciseService, Exercise, AssignedExercisesResponse } from '../../services/exercise.service';

Chart.register(BarController, BarElement, CategoryScale, LinearScale, Title, Tooltip, Legend);

@Component({
  selector: 'app-overview',
  standalone: true,
  imports: [
    RouterModule,
    FormsModule,
    CommonModule,
    SidebarComponent,
  ],
  templateUrl: './overview.component.html',
  styleUrls: ['./overview.component.scss'],
})
export class OverviewComponent implements AfterViewInit {
  @ViewChild('barChart') barChartRef!: ElementRef<HTMLCanvasElement>;
  chart!: Chart;

  userFirstName: string = 'User';
  date: string = new Date().toISOString().split('T')[0];
  sleepQuality: number | null = null;
  progressPercent: number = 0;

  assignedExercises: Exercise[] = [];

  constructor(
    private authService: AuthService,
    private sleepRecordService: SleepRecordService,
    private exerciseService: ExerciseService,
    private router: Router
  ) {}

  ngOnInit() {
    setTimeout(() => {
      const user = this.authService.getUser();
      if (user && user.first_name) {
        this.userFirstName = user.first_name;
        const preferredHours = user.preferred_sleep_hours ?? 0;
        this.loadSleepQuality(preferredHours);
        this.progressPercent = this.calculatesProgress();
        this.loadAssignedExercises();
      }
    });
  }

  ngAfterViewInit() {
    const config: ChartConfiguration = {
      type: 'bar',
      data: {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        datasets: [{
          label: 'Calories Gained',
          data: [1000, 1500, 1200, 1800, 2000, 1650, 1350],
          backgroundColor: [
            'rgba(255, 99, 132, 0.7)',
            'rgba(54, 162, 235, 0.7)',
            'rgba(255, 206, 86, 0.7)',
            'rgba(75, 192, 192, 0.7)',
            'rgba(153, 102, 255, 0.7)',
            'rgba(255, 159, 64, 0.7)',
            'rgba(199, 199, 199, 0.7)'
          ]
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: 'top' },
          title: {
            display: true,
            text: 'Calories Gained Over Days'
          }
        }
      }
    };
    this.chart = new Chart(this.barChartRef.nativeElement, config);
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

  calculatesProgress(): number {
    const user = this.authService.getUser();
    if (!user || !user.weight_kg || !user.target_weight_kg) {
      return 0;
    }

    const current = user.weight_kg;
    const target = user.target_weight_kg;

    if (current <= target) return 100;

    const totalToLose = current - target;
    const progress = (1 - (totalToLose / current)) * 100;
    console.log('Progress:', progress);
    return Math.min(Math.max(progress, 0), 100);
  }

  logout() {
    this.authService.logout();
    this.router.navigate(['/login']);
  }

  loadAssignedExercises() {
    const token = localStorage.getItem('token');
    if (!token) {
      alert('No token found.');
      return;
    }

    if (!this.date || !/^\d{4}-\d{2}-\d{2}$/.test(this.date)) {
      alert('Tarih formatı YYYY-MM-DD olmalı');
      this.assignedExercises = [];
      return;
    }

    this.exerciseService.getExercisesForDate(token, this.date).subscribe({
      next: (res: AssignedExercisesResponse) => {
        this.assignedExercises = res.exercises;
      },
      error: (err) => {
        console.log('Full error object:', err);
        console.log('Error status:', err.status);
        console.log('Error error:', err.error);
        console.log('Error message:', err.message);

        const errorMessage = typeof err.error === 'string' ? err.error : err.error?.error;

        if (err.status === 404 && errorMessage === 'No program assigned for this date') {
          this.assignedExercises = [];
        } else {
          console.error('Error fetching assigned exercises:', err);
          alert('Error fetching assigned exercises.');
          this.assignedExercises = [];
        }
      }
    });
  }

  onDateChange() {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(this.date)) {
      this.assignedExercises = [];
      return;
    }
    this.loadAssignedExercises();
  }
}
