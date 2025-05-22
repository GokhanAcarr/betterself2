import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SleepRecordService } from '../../services/sleep-record.service';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-sleep-record',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './sleep-record.component.html',
  styleUrls: ['./sleep-record.component.scss'],
})
export class SleepRecordComponent implements OnInit {
  private sleepRecordService = inject(SleepRecordService);

  hoursSlept: number | null = null;
  inputHours: number | null = null;
  errorMsg: string | null = null;
  loading = false;

  ngOnInit() {
    this.loadSleepRecord();
  }

  loadSleepRecord() {
    this.sleepRecordService.getSleepRecord().subscribe({
      next: (res) => (this.hoursSlept = res.hours_slept),
      error: (err) => console.error(err),
    });
  }

  saveSleepHours() {
    if (this.inputHours == null || this.inputHours < 0) {
      this.errorMsg = 'Wrong Entry.';
      return;
    }
    this.loading = true;
    this.sleepRecordService.setSleepRecord(this.inputHours).subscribe({
      next: () => {
        this.hoursSlept = this.inputHours;
        this.errorMsg = null;
        this.loading = false;
      },
      error: (err) => {
        this.errorMsg = err.error?.error || 'An Error Occured.';
        this.loading = false;
      },
    });
  }
}
