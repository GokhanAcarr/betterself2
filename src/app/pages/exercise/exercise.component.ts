import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { SidebarComponent } from '../sidebar/sidebar.component';
import { ExerciseService } from '../../services/exercise.service';
import { Exercise, Program } from '../../services/exercise.service';

@Component({
  selector: 'app-exercise',
  templateUrl: './exercise.component.html',
  styleUrls: ['./exercise.component.scss'],
  imports: [CommonModule, FormsModule, SidebarComponent],
  standalone: true,
})
export class ExerciseComponent {
  constructor(private exerciseService: ExerciseService) {}

  ngOnInit(): void {
    this.loadExercises();
    this.loadPrograms();
  }

  loadPrograms(): void {
    const token = localStorage.getItem('token');
    if (!token) {
      alert('No token found.');
      return;
    }

    this.exerciseService.getPrograms(token).subscribe({
      next: (programs) => {
        this.savedPrograms = programs;
      },
      error: (err) => {
        console.error('Error loading programs:', err);
      }
    });
  }

  loadExercises(): void {
    const token = localStorage.getItem('token');
    if (!token) {
      alert('No token found.');
      return;
    }

    this.exerciseService.getAllExercises(token).subscribe({
      next: (data) => {
        this.exercises = data;
        this.filteredExercises = data; // ilk yüklemede filtreli listeyi de doldur
      },
      error: (err) => {
        console.error('Exercise loading error:', err);
      }
    });
  }

  savedPrograms: Program[] = [];
  exercises: Exercise[] = [];
  filteredExercises: Exercise[] = [];
  selectedExercises: Exercise[] = [];

  selectedDate: string = '';
  exerciseSearchTerm: string = '';

  newProgramName = '';
  newProgramImageUrl = '';
  isCreateProgramDialogOpen = false;

  filterExercises() {
    const term = this.exerciseSearchTerm.toLowerCase();
    this.filteredExercises = this.exercises.filter(ex =>
      ex.name.toLowerCase().includes(term) ||
      (ex.category?.toLowerCase().includes(term) ?? false)
    );
  }

  addExerciseToProgram(exercise: Exercise) {
    if (this.selectedExercises.length < 15 && !this.selectedExercises.includes(exercise)) {
      this.selectedExercises.push(exercise);
    }
  }

  removeExerciseFromProgram(exercise: Exercise) {
    this.selectedExercises = this.selectedExercises.filter(ex => ex !== exercise);
  }

  openCreateProgramDialog() {
    this.isCreateProgramDialogOpen = true;
  }

  closeCreateProgramDialog() {
    this.isCreateProgramDialogOpen = false;
  }

  saveProgram() {
  if (!this.newProgramName.trim() || !this.newProgramImageUrl.trim()) {
    alert('Please fill in program name and image URL.');
    return;
  }

  const token = localStorage.getItem('token');
  if (!token) {
    alert('No token found.');
    return;
  }

  this.exerciseService.createProgram(token, this.newProgramName, this.newProgramImageUrl).subscribe({
    next: (response) => {
      const createdProgram = response.program;  // Burada artık doğru tip
      const exerciseIds = this.selectedExercises.map(ex => ex.id);
      console.log('Selected exercise IDs:', exerciseIds);

      this.exerciseService.addExercisesToProgram(token, createdProgram.id!, exerciseIds).subscribe({
        next: () => {
          alert('Program and exercises saved successfully!');
          this.savedPrograms.push(createdProgram);
          this.newProgramName = '';
          this.newProgramImageUrl = '';
          this.selectedExercises = [];
          this.closeCreateProgramDialog();
        },
        error: (err) => {
          console.error('Error adding exercises to program:', err);
          alert('Program created but failed to add exercises.');
        }
      });
    },
    error: (err) => {
      console.error('Error saving program:', err);
      alert('Error saving program.');
    }
  });
}


  assignProgramToDate(program: Program) {
    const token = localStorage.getItem('token');
    if (!token) {
      alert('No token found.');
      return;
    }
    if (!this.selectedDate) {
      alert('Please select a date first.');
      return;
    }

    this.exerciseService.assignProgram(token, program.id!, this.selectedDate).subscribe({
      next: () => {
        alert(`Program "${program.name}" assigned to ${this.selectedDate}`);
        // UI güncellemeleri buraya
      },
      error: (err) => {
        console.error('Error assigning program:', err);
        alert('Failed to assign program.');
      }
    });
  }

  logout() {
    alert('Logging out...');
  }
}
