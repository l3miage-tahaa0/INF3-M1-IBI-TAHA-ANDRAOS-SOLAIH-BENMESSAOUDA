import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { NavbarComponent } from '../shared/navbar/navbar.component';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { AuthService } from '../../services/auth.service';
import { UserService } from '../../services/user.service';
import { UserExtendedReference } from '../../interfaces/user.interface';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, NavbarComponent],
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.css']
})
export class ProfileComponent implements OnInit{
  private router = inject(Router);
  private userService = inject(UserService);
  private authService = inject(AuthService);
  protected user = signal<UserExtendedReference>({_id: '', email: '', first_name: '', last_name: ''});
  protected completedTasksCount = signal<number>(0);
  ngOnInit(): void {
    this.userService.getUserProfile().subscribe({
      next: (data) => this.user.set(data),
      error: () => this.user.set({_id: '', email: '', first_name: '', last_name: ''})
    });
    this.userService.getUserTaskCountByState('Completed').subscribe({
      next: (data) => {
        this.completedTasksCount.set(data[0].nb_of_tasks);
      },
      error: () => this.completedTasksCount.set(0)
    });
  }
  signOut() {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}
