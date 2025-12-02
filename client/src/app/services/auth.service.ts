import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject, timer } from 'rxjs';
import { tap, catchError, map, switchMap } from 'rxjs/operators';
import { Router } from '@angular/router';
import { environment } from '../../environments/environment';
import { AuthResponse } from '../interfaces/auth.interface';
@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = environment.apiUrl + 'auth';

  private accessTokenKey = 'access_token';
  private refreshTokenKey = 'refresh_token';

  private isAuthenticatedSubject = new BehaviorSubject<boolean>(this.hasTokens());
  isAuthenticated$ = this.isAuthenticatedSubject.asObservable();

  constructor(private http: HttpClient, private router: Router) {
    this.scheduleTokenRefresh(); // Start refreshing tokens when service loads
  }

  private hasTokens(): boolean {
    return !!localStorage.getItem(this.accessTokenKey) && !!localStorage.getItem(this.refreshTokenKey);
  }

  private setTokens(tokens: AuthResponse): void {
    localStorage.setItem(this.accessTokenKey, tokens.access_token);
    localStorage.setItem(this.refreshTokenKey, tokens.refresh_token);
    this.isAuthenticatedSubject.next(true);
  }

  getAccessToken(): string | null {
    return localStorage.getItem(this.accessTokenKey);
  }

  getRefreshToken(): string | null {
    return localStorage.getItem(this.refreshTokenKey);
  }

  private clearTokens(): void {
    localStorage.removeItem(this.accessTokenKey);
    localStorage.removeItem(this.refreshTokenKey);
    localStorage.removeItem("userEmail");
    this.isAuthenticatedSubject.next(false);
  }

  isAuthenticated(): boolean {
    return this.hasTokens();
  }

  login(credentials: any): Observable<AuthResponse> {
    console.log(credentials)
    return this.http.post<AuthResponse>(`${this.apiUrl}/login`, credentials).pipe(
      tap(response => {
        this.setTokens(response);
        this.scheduleTokenRefresh();
        //TODO: Decrypt token to get user email instead
        localStorage.setItem("userEmail", credentials.email);
        this.router.navigate(['/projects']);
      }),
      catchError(error => {
        console.error('Login failed:', error);
        throw error;
      })
    );
  }

  signup(credentials: any): Observable<AuthResponse> {
    const requestBody = {
      first_name: credentials.firstName,
      last_name: credentials.lastName,
      email: credentials.email,
      password: credentials.password
    }
    return this.http.post<AuthResponse>(`${this.apiUrl}/signup`, requestBody).pipe(
      tap(response => {
        this.router.navigate(['/login']);
      }),
      catchError(error => {
        console.error('Signup failed:', error);
        throw error;
      })
    );
  }

  logout(): void {
    const token = this.getAccessToken();
    if (token) {
      this.http.post(`${this.apiUrl}/logout`, {}, { headers: { Authorization: `Bearer ${token}` } }).pipe(
        catchError(error => {
          console.error('Logout API failed but clearing tokens anyway:', error);
          return []; // Continue with logout process even if API fails
        })
      ).subscribe(() => {
        this.clearTokens();
        this.router.navigate(['/login']);
      });
    } else {
      this.clearTokens();
      this.router.navigate(['/login']);
    }
  }

  // Token Refresh Logic
  refreshToken(): Observable<AuthResponse> {
    const refreshToken = this.getRefreshToken();
    const accessToken = this.getAccessToken(); // Need access token for refresh endpoint
    if (!refreshToken || !accessToken) {
      this.clearTokens();
      this.router.navigate(['/login']);
      return new Observable(); // Return an empty observable to stop the refresh
    }

    return this.http.get<AuthResponse>(`${this.apiUrl}/refresh`, { // Adjust if your /refresh expects refresh_token directly
      headers: {
        Authorization: `Bearer ${refreshToken}` // Assuming refresh endpoint also uses Bearer for refresh token
      }
    }).pipe(
      tap(response => this.setTokens(response)),
      catchError(error => {
        console.error('Token refresh failed:', error);
        this.clearTokens();
        this.router.navigate(['/login']);
        throw error;
      })
    );
  }

  // Schedule automatic token refresh
  private scheduleTokenRefresh() {
    // In a real app, calculate token expiry from JWT and refresh BEFORE it expires.
    // For simplicity, we'll refresh every 5 minutes if logged in.
    const refreshIntervalMs = 5 * 60 * 1000; // 5 minutes

    timer(0, refreshIntervalMs).pipe(
      // Only refresh if authenticated
      switchMap(() => this.isAuthenticated() ? this.refreshToken() : []),
      catchError(error => {
        console.error("Error during scheduled refresh, logging out", error);
        this.clearTokens();
        this.router.navigate(['/login']);
        return [];
      })
    ).subscribe();
  }
}
