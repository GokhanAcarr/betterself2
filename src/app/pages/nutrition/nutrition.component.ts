import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { SidebarComponent } from '../sidebar/sidebar.component';
import { FoodService } from '../../services/food.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-nutrition',
  templateUrl: './nutrition.component.html',
  styleUrls: ['./nutrition.component.scss'],
  standalone: true,
  imports: [CommonModule, FormsModule, SidebarComponent],
})
export class NutritionComponent implements OnInit {
  isAdmin: boolean = false;
  foodSearchTerm: string = '';
  foodQuantities: { [key: string]: number } = {};
  searchedFoods: any[] = [];
  loggedFoods: any[] = [];
  selectedDate: string = new Date().toISOString().substring(0, 10);
  totalCalories: number = 0;
  proteinPercentage: number = 0;
  carbPercentage: number = 0;
  fatPercentage: number = 0;

  constructor(private foodService: FoodService, private authService: AuthService) {}

  ngOnInit(): void {
    const user = this.authService.getUser();
    if(user) {
      this.isAdmin = user.is_admin || false;
    }
    this.loadLoggedFoods();
  }

  onSearchClick(): void {
    if (!this.foodSearchTerm.trim()) {
      return;
    }

    this.foodService.searchFood(this.foodSearchTerm).subscribe({
      next: (data) => {
        this.searchedFoods = data;
        this.searchedFoods.forEach(food => this.foodQuantities[food.name] = 100);
      },
      error: (err) => {
        console.error('Arama hatası:', err);
        this.searchedFoods = [];
      }
    });
  }

  onQuantityChange(foodName: string, value: string): void {
    const quantity = Number(value);
    this.foodQuantities[foodName] = quantity > 0 ? quantity : 100;
  }

  addFoodToLog(food: any): void {
  const quantity = this.foodQuantities[food.name] || 100;

  const payload = {
    food_name: food.name,
    calories: (food.calories_per_100g * quantity) / 100,
    carbs: (food.carbs_per_100g * quantity) / 100,
    protein: (food.protein_per_100g * quantity) / 100,
    fats: (food.fat_per_100g * quantity) / 100,
    quantity: quantity,
    date: this.selectedDate
  };

  this.foodService.logFood(payload).subscribe({
    next: () => {
      this.loadLoggedFoods();
      this.foodQuantities[food.name] = 100;
    },
    error: (err) => {
      console.error('Yemek eklenirken hata:', err);
      alert('Yemek eklenirken hata oluştu.');
    }
  });
}

  loadLoggedFoods(): void {
    if (!this.selectedDate) return;

    this.foodService.getFoodLogs(this.selectedDate).subscribe({
      next: (data) => {
        this.loggedFoods = data;
        this.calculateNutritionSummary();
      },
      error: (err) => {
        console.error('Loglar yüklenirken hata:', err);
      }
    });
  }

  onDateChange(): void {
    this.loadLoggedFoods();
  }

  removeFoodFromLog(foodLog: any): void {
    this.foodService.deleteFoodLog(foodLog.id).subscribe({
      next: () => {
        this.loadLoggedFoods();
      },
      error: (err) => {
        console.error('Silme hatası:', err);
        alert('Yemek kaydı silinirken hata oluştu.');
      }
    });
  }

  calculateNutritionSummary(): void {
    let totalCalories = 0;
    let totalProtein = 0;
    let totalCarbs = 0;
    let totalFats = 0;

    this.loggedFoods.forEach(food => {
      totalCalories += food.calories || 0;
      totalProtein += food.protein || 0;
      totalCarbs += food.carbs || 0;
      totalFats += food.fats || 0;
    });

    this.totalCalories = totalCalories;

    const totalMacros = totalProtein + totalCarbs + totalFats;
    this.proteinPercentage = totalMacros ? (totalProtein / totalMacros) * 100 : 0;
    this.carbPercentage = totalMacros ? (totalCarbs / totalMacros) * 100 : 0;
    this.fatPercentage = totalMacros ? (totalFats / totalMacros) * 100 : 0;
  }
}
