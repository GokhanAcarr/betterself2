import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { WaterIntakeService } from '../../services/water-intake.service';
import { HttpClientModule } from '@angular/common/http';

@Component({
  selector: 'app-water-intake',
  standalone: true,
  imports: [CommonModule, HttpClientModule],
  templateUrl: './water-intake.component.html',
  styleUrls: ['./water-intake.component.scss'],
})
export class WaterIntakeComponent implements OnInit {
  private waterIntakeService = inject(WaterIntakeService);

  count = 0;
  loading = false;

  maxCups = 8;
  cups: number[] = [];

  ngOnInit() {
    this.cups = Array(this.maxCups).fill(0);
    this.loadWaterIntake();
  }

  loadWaterIntake() {
    this.waterIntakeService.getWaterIntake().subscribe({
      next: (res) => (this.count = res.count),
      error: (err) => console.error(err),
    });
  }

  drinkWater() {
    this.loading = true;
    this.waterIntakeService.drinkWater().subscribe({
      next: (res) => {
        this.count = res.count;
        this.loading = false;
      },
      error: (err) => {
        console.error(err);
        this.loading = false;
      },
    });
  }
}
