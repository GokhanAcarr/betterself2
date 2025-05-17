import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

interface UserDataResponse {
  water_intake: number;
  sleep_hours: number;
  // gerekirse diğer user alanları
}

@Injectable({
  providedIn: 'root',
})
export class TrackerService {
  private apiUrl = 'http://localhost:5000/auth';

  constructor(private http: HttpClient) {}

  private getAuthHeaders(): HttpHeaders {
    const token = localStorage.getItem('token') || '';
    return new HttpHeaders().set('Authorization', `Bearer ${token}`);
  }

  // Tek endpoint, user + water + sleep data döner
  getUserData(userId: number): Observable<UserDataResponse> {
    const headers = this.getAuthHeaders();
    return this.http.get<UserDataResponse>(`${this.apiUrl}/user/${userId}`, { headers });
  }
}
