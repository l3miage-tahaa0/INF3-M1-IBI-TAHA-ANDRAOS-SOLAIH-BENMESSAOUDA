import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { NavbarComponent } from '../shared/navbar/navbar.component';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { Auth } from '../../services/auth';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, NavbarComponent],
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.css']
})
export class ProfileComponent implements OnInit{
  private router = inject(Router);
  private http = inject(HttpClient);
  private authService = inject(Auth);
  protected user = signal<{email: string, first_name: string, last_name: string}>({email: '', first_name: '', last_name: ''});
  ngOnInit(): void {
    this.http.get<{email: string, first_name: string, last_name: string}>(environment.apiUrl + 'users/me').subscribe({
      next: (data) => this.user.set(data),
      error: () => this.user.set({email: '', first_name: '', last_name: ''})
    });
  }
  signOut() {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}
