import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { SidebarComponent } from '../sidebar/sidebar.component';

@Component({
  selector: 'app-nutrition',
  imports: [FormsModule, CommonModule, SidebarComponent],
  templateUrl: './nutrition.component.html',
  styleUrl: './nutrition.component.scss'
})
export class NutritionComponent {
  foodSearchTerm: string = '';
  selectedDate: string = '';
  searchedFoods: any[] = [];
  loggedFoods: any[] = [];


  foodDatabase = [
    { name: 'Chicken Breast', calories: 165, protein: 31, carbs: 0, fat: 3 },
    { name: 'Brown Rice', calories: 216, protein: 5, carbs: 45, fat: 2 },
    { name: 'Avocado', calories: 160, protein: 2, carbs: 9, fat: 15 },
    { name: 'Greek Yogurt', calories: 100, protein: 10, carbs: 4, fat: 0 },
    { name: 'Banana', calories: 105, protein: 1, carbs: 27, fat: 0 },
    { name: 'Almonds', calories: 170, protein: 6, carbs: 6, fat: 15 },
  ];


  totalCalories = 0;
  proteinPercentage = 0;
  carbPercentage = 0;
  fatPercentage = 0;

  searchFood() {
    const term = this.foodSearchTerm.toLowerCase();
    this.searchedFoods = this.foodDatabase.filter(food =>
      food.name.toLowerCase().includes(term)
    );
  }

  addFoodToLog(food: any) {
    if (!this.selectedDate) {
      alert('Please select a date first.');
      return;
    }

    this.loggedFoods.push({ ...food, date: this.selectedDate });
    this.updateSummary();
  }

  removeFoodFromLog(food: any) {
    this.loggedFoods = this.loggedFoods.filter(f => f !== food);
    this.updateSummary();
  }

  updateSummary() {
    const total = this.loggedFoods.reduce(
      (acc, food) => {
        acc.calories += food.calories;
        acc.protein += food.protein;
        acc.carbs += food.carbs;
        acc.fat += food.fat;
        return acc;
      },
      { calories: 0, protein: 0, carbs: 0, fat: 0 }
    );

    const macroSum = total.protein + total.carbs + total.fat;

    this.totalCalories = total.calories;
    this.proteinPercentage = macroSum ? (total.protein / macroSum) * 100 : 0;
    this.carbPercentage = macroSum ? (total.carbs / macroSum) * 100 : 0;
    this.fatPercentage = macroSum ? (total.fat / macroSum) * 100 : 0;
  }
}

