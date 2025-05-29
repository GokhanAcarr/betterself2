import { Component, AfterViewInit, ViewChild, ElementRef, OnInit } from '@angular/core';
import { Router, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth.service';
import { SleepRecordService } from '../../services/sleep-record.service';
import { SidebarComponent } from '../sidebar/sidebar.component';
import {
  Chart,
  BarController,
  BarElement,
  CategoryScale,
  LinearScale,
  Title,
  Tooltip,
  Legend,
  ChartConfiguration
} from 'chart.js';
import { ExerciseService, Exercise, AssignedExercisesResponse } from '../../services/exercise.service';
import { FoodService } from '../../services/food.service';
import { addDays, format } from 'date-fns';

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
export class OverviewComponent implements OnInit, AfterViewInit {
  @ViewChild('barChart', { static: false }) barChartRef!: ElementRef<HTMLCanvasElement>;
  chart?: Chart;
  isAdmin: boolean = false;
  userFirstName: string = 'User';
  date: string = new Date().toISOString().split('T')[0];
  sleepQuality: number | null = null;
  progressPercent: number = 0;
  assignedExercises: Exercise[] = [];
  todayCalories: number = 0;

  constructor(
    private authService: AuthService,
    private sleepRecordService: SleepRecordService,
    private exerciseService: ExerciseService,
    private foodService: FoodService,
    private router: Router
  ) {}

  ngOnInit(): void {
    const user = this.authService.getUser();
    console.log('User1:', user);
    
    if (user) {
      this.isAdmin = user.is_admin ?? false;
      this.userFirstName = user.first_name ?? 'User';
      this.loadSleepQuality(user.preferred_sleep_hours ?? 0);
      this.progressPercent = this.calculateProgress();
      this.loadAssignedExercises();
      this.loadTodayCalories();
    }
  }

  ngAfterViewInit(): void {
    this.loadWeeklyCaloriesAndRenderChart();
  }

  private loadWeeklyCaloriesAndRenderChart(): void {
    const endDate = new Date();
    const startDate = addDays(endDate, -6);
    const startStr = format(startDate, 'yyyy-MM-dd');
    const endStr = format(endDate, 'yyyy-MM-dd');

    this.foodService.getCaloriesByDateRange(startStr, endStr).subscribe({
      next: (data) => {
        const labels: string[] = [];
        const caloriesData: number[] = [];

        for (let i = 0; i < 7; i++) {
          const date = addDays(startDate, i);
          const dateStr = format(date, 'yyyy-MM-dd');
          labels.push(dateStr);

          const dayData = data.find((d: any) => d.date === dateStr);
          caloriesData.push(dayData ? dayData.calories : 0);
        }

        this.renderChart(labels, caloriesData);
      },
      error: (err) => {
        console.error('Weekly calories load error', err);
      }
    });
  }

  private renderChart(labels: string[], data: number[]): void {
    if (this.chart) {
      this.chart.destroy();
    }

    const config: ChartConfiguration = {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: 'Calories Gained',
          data,
          backgroundColor: 'rgba(75, 192, 192, 0.7)',
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: 'top' },
          title: {
            display: true,
            text: 'Calories Gained Over Last 7 Days',
          }
        }
      }
    };

    if (this.barChartRef?.nativeElement) {
      this.chart = new Chart(this.barChartRef.nativeElement, config);
    }
  }

  private loadSleepQuality(preferredSleepHours: number): void {
    this.sleepRecordService.getSleepRecord().subscribe({
      next: (sleepRecord) => {
        this.sleepQuality = this.calculateSleepQuality(sleepRecord.hours_slept, preferredSleepHours);
      },
      error: (err) => {
        console.error('Sleep record loading failed', err);
        this.sleepQuality = null;
      }
    });
  }

  private calculateSleepQuality(hoursSlept: number | null, preferredSleepHours: number): number {
    if (hoursSlept === null || preferredSleepHours <= 0) return 0;
    const quality = (hoursSlept / preferredSleepHours) * 100;
    return Math.min(quality, 100);
  }

  private calculateProgress(): number {
    const user = this.authService.getUser();
    if (!user || !user.weight_kg || !user.target_weight_kg) return 0;

    const current = user.weight_kg;
    const target = user.target_weight_kg;

    if (current <= target) return 100;

    const totalToLose = current - target;
    const progress = (1 - (totalToLose / current)) * 100;
    return Math.min(Math.max(progress, 0), 100);
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }

  loadAssignedExercises(): void {
    const token = localStorage.getItem('token');
    if (!token) {
      alert('No token found.');
      this.assignedExercises = [];
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
        if (err.status === 404 && 
          (err.error === 'No program assigned for this date' || err.error?.error === 'No program assigned for this date')) {
          this.assignedExercises = [];
        } else {
          alert('Error fetching assigned exercises.');
          this.assignedExercises = [];
        }
      }
    });
  }

  onDateChange(): void {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(this.date)) {
      this.assignedExercises = [];
      this.todayCalories = 0;
      return;
    }
    this.loadAssignedExercises();
    this.loadTodayCalories();
  }

  private loadTodayCalories(): void {
    this.foodService.getFoodLogs(this.date).subscribe({
      next: (logs) => {
        this.todayCalories = this.calculateTotalCalories(logs);
      },
      error: (err) => {
        console.error('Error loading food logs', err);
        this.todayCalories = 0;
      }
    });
  }

  private calculateTotalCalories(foodLogs: any[]): number {
    return foodLogs.reduce((total, item) => total + (item.calories ?? 0), 0);
  }
}
