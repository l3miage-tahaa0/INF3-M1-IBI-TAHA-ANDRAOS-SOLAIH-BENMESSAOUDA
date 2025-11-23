import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ProjectService } from '../../../services/project.service';
import { Router } from '@angular/router';
import { NavbarComponent } from '../../shared/navbar/navbar.component';

@Component({
  selector: 'app-project-create',
  imports: [CommonModule, FormsModule, NavbarComponent],
  templateUrl: './project-create.html',
  styleUrls: ['./project-create.css'],
})
export class ProjectCreate {

  private projectService = inject(ProjectService);
  private router = inject(Router);
  project = { title: '', description: '' };
  titleError: string | null = null;
  descriptionError: string | null = null;

  create() {
    this.titleError = null;
    this.descriptionError = null;

    if (!this.project.title) {
      this.titleError = 'Title is required';
    }
    if (!this.project.description) {
      this.descriptionError = 'Description is required';
    }

    if (this.titleError || this.descriptionError) {
      return;
    }

    this.projectService.createProject(this.project).subscribe({
      next: (response) => {
        console.log('Project created successfully:', response);
        // Navigate to the project details page or show a success message
        this.router.navigate(['/projects']);
      },
      error: (error) => {
        console.error('Error creating project:', error);
      }
    });
  }
}
