import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class WaterIntakeService {
  private apiUrl = 'http://localhost:5000';

  constructor(private http: HttpClient) {}

  private getAuthHeaders(): HttpHeaders {
    const token = localStorage.getItem('token'); 
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });
  }

  getWaterIntake(): Observable<{count: number}> {
    const headers = this.getAuthHeaders();
    return this.http.get<{count: number}>(`${this.apiUrl}/water-intake`, { headers });
  }

  drinkWater(): Observable<{count: number}> {
    const headers = this.getAuthHeaders();
    return this.http.post<{count: number}>(`${this.apiUrl}/water-intake/drink`, {}, { headers });
  }
}
