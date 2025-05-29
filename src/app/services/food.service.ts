import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class FoodService {
  private baseUrl = 'http://localhost:5000/food';

  constructor(private http: HttpClient) {}

  searchFood(query: string): Observable<any> {
    return this.http.get(`${this.baseUrl}/search?query=${query}`);
  }

  logFood(data: any): Observable<any> {
    const token = localStorage.getItem('token') || '';
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
    return this.http.post(`${this.baseUrl}/log`, data, { headers });
  }

  getFoodLogs(date: string): Observable<any> {
    const token = localStorage.getItem('token') || '';
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Accept': 'application/json'
    });
    return this.http.get(`${this.baseUrl}/log?date=${date}`, { headers });
  }



  deleteFoodLog(id: number): Observable<any> {
    const token = localStorage.getItem('token');
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });
    return this.http.delete(`${this.baseUrl}/log/${id}`, { headers });
  }
  getCaloriesByDateRange(startDate: string, endDate: string): Observable<any> {
  const token = localStorage.getItem('token') || '';
  const headers = new HttpHeaders({
    'Authorization': `Bearer ${token}`,
    'Accept': 'application/json'
  });
  return this.http.get(`${this.baseUrl}/logs/calories?start=${startDate}&end=${endDate}`, { headers });
}

}
