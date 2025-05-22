import { Routes } from '@angular/router';

import { OverviewComponent } from './pages/overview/overview.component';
import { ProfileComponent } from './pages/profile/profile.component';
import { ExerciseComponent } from './pages/exercise/exercise.component';
import { NutritionComponent } from './pages/nutrition/nutrition.component';
import { LoginComponent } from './auth/login/login.component';
import { RegisterComponent } from './auth/register/register.component';
import { LandingComponent } from './pages/landing/landing.component';
import { AdminComponent } from './pages/admin/admin.component';

export const routes: Routes = [
  { path: '', redirectTo: 'landing', pathMatch: 'full' },
  { path: 'landing', component: LandingComponent },
  { path: 'overview', component: OverviewComponent },
  { path: 'profile', component: ProfileComponent },
  { path: 'exercise', component: ExerciseComponent },
  { path: 'nutrition', component: NutritionComponent },
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  { path: 'admin', component: AdminComponent},

  { path: '**', redirectTo: 'landing' }
];
