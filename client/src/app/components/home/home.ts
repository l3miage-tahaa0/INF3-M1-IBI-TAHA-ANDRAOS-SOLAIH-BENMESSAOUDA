import { Component } from '@angular/core';
import { Auth } from '../../services/auth';
import { HttpClient } from '@angular/common/http';
import { CommonModule, JsonPipe } from '@angular/common';

@Component({
  selector: 'app-home',
  imports: [JsonPipe, CommonModule],
  templateUrl: './home.html',
  styleUrl: './home.css',
})
export class Home {
  protectedData: any;
  errorMessage: string | null = null;

  constructor(private authService: Auth, private http: HttpClient) { }

  logout(): void {
    this.authService.logout();
  }

  // Example of making an authenticated request
  fetchProtectedData(): void {
    this.errorMessage = null;
    this.http.get('http://localhost:8000/users/me').subscribe({
      next: (data) => {
        this.protectedData = data;
        console.log('Protected data:', data);
      },
      error: (err) => {
        this.errorMessage = err.error?.message || 'Failed to fetch protected data.';
        console.error('Error fetching protected data:', err);
      }
    });
  }
}
