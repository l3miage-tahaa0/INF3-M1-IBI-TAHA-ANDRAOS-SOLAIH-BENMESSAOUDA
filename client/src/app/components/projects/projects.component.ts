import { CommonModule } from '@angular/common';
import { Component, inject, OnInit, signal } from '@angular/core';
import { ProjectService } from '../../services/project.service';
import { Project } from '../../interfaces/project.interface';
import { Router } from '@angular/router';
import { NavbarComponent } from '../shared/navbar/navbar.component';

@Component({
  selector: 'app-projects',
  imports: [CommonModule, NavbarComponent],
  templateUrl: './projects.component.html',
  styleUrls: ['./projects.component.css'],
})
export class ProjectsComponent implements OnInit{
  private projectService = inject(ProjectService);
  private router = inject(Router);
  projects = signal<Project[]>([]);

  ngOnInit(): void {
      this.projectService.getProjects().subscribe({
      next: (projects) => {
        console.log('Projects fetched successfully:', projects);
        this.projects.set(projects);
      },
      error: (error) => {
        console.error('Error fetching projects:', error);
      }
    });
  }
  goToProject(projectId: string) {
    // Implementation for navigating to a specific project
    this.router.navigate(['/projects', projectId]);
  }
  goToProjectCreationPage() {
    // Implementation for navigating to the project creation page
    this.router.navigate(['/projects', 'create']);
  }
  


}
