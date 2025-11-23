import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { NavbarComponent } from '../shared/navbar/navbar.component';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, NavbarComponent],
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.css']
})
export class ProfileComponent {
  user = {
    first_name: 'Juddy',
    last_name: 'Andraos',
    email: 'andraos.juddy@gmail.com'
  };

  constructor(private router: Router) {
    try {
      const stored = localStorage.getItem('user');
      if (stored) {
        this.user = JSON.parse(stored);
      }
    } catch (_) {}
  }

  signOut() {
    localStorage.removeItem('user');
    // optionally clear tokens
    localStorage.removeItem('token');
    this.router.navigate(['/login']);
  }
}
