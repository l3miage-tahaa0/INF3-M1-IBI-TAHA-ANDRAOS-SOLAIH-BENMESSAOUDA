import { Component, inject, OnInit } from '@angular/core';
import { Auth } from '../../services/auth';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { ProjectService } from '../../services/project.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-home',
  imports: [CommonModule],
  templateUrl: './home.html',
  styleUrl: './home.css',
})
export class Home implements OnInit{
  errorMessage: string | null = null;
  router = inject(Router);
  constructor(private http: HttpClient) { }

  ngOnInit(): void {
  }

}
