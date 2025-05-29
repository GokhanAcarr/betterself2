import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Exercise {
  id: number;
  name: string;
  category?: string;
  description?: string;
  image_url?: string;
}

export interface Program {
  id?: number;
  name: string;
  image_url?: string;
  exercises?: Exercise[];
}

export interface AssignedExercisesResponse {
  date: string;
  program_id: number;
  exercises: Exercise[];
}

interface CreateProgramResponse {
  message: string;
  program: Program;
}

@Injectable({
  providedIn: 'root'
})
export class ExerciseService {
  private baseUrl = 'http://localhost:5000';

  constructor(private http: HttpClient) {}

  private getAuthHeaders(token: string): HttpHeaders {
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`,
    });
  }

  addExercise(exercise: Exercise): Observable<any> {
  const token = localStorage.getItem('token');

  const headers = new HttpHeaders({
    'Content-Type': 'application/json',
    Authorization: `Bearer ${token}`,
  });

  return this.http.post<any>(`${this.baseUrl}/add-exercise`, exercise, { headers });
}

  getPrograms(token: string): Observable<Program[]> {
    const headers = this.getAuthHeaders(token);
    return this.http.get<Program[]>(`${this.baseUrl}/programs`, { headers });
  }

  createProgram(token: string, name: string, imageUrl?: string): Observable<CreateProgramResponse> {
    const headers = this.getAuthHeaders(token);
    const body: any = { name };
    if (imageUrl) {
      body.image_url = imageUrl;
    }
    return this.http.post<CreateProgramResponse>(`${this.baseUrl}/programs`, body, { headers });
  }

  assignProgram(token: string, programId: number, date: string): Observable<any> {
    const headers = this.getAuthHeaders(token);
    const body = { program_id: programId, date };
    return this.http.post(`${this.baseUrl}/assign-program`, body, { headers });
  }

  getExercisesForDate(token: string, date: string): Observable<AssignedExercisesResponse> {
    const headers = this.getAuthHeaders(token);
    const params = new HttpParams().set('date', date);
    return this.http.get<AssignedExercisesResponse>(`${this.baseUrl}/assignments/exercises`, { headers, params });
  }

  getAllExercises(token: string): Observable<Exercise[]> {
    const headers = this.getAuthHeaders(token);
    return this.http.get<Exercise[]>(`${this.baseUrl}/exercises`, { headers });
  }

  addExercisesToProgram(token: string, programId: number, exerciseIds: number[]): Observable<any> {
    const headers = this.getAuthHeaders(token);
    const body = {
      exercise_ids: exerciseIds,
    };
    return this.http.post(`${this.baseUrl}/programs/${programId}/exercises`, body, { headers });
  }
}
