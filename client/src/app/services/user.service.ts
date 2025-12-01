import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { UserExtendedReference } from '../interfaces/user.interface';
@Injectable({
  providedIn: 'root'
})
export class UserService {
  private apiUrl = environment.apiUrl + 'users';
  private http = inject(HttpClient);
  
  getUserProfile() {
    return this.http.get<UserExtendedReference>(environment.apiUrl + 'users/me');
  }
  getUserTaskCountByState(state: string) {
    return this.http.get<any>(`${this.apiUrl}/me/task-count?state=${state}`);
  }
}