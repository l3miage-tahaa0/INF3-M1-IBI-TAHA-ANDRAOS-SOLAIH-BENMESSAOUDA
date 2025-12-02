import { Component, inject, OnInit, signal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { ProjectService } from '../../../services/project.service';
import { CommonModule } from '@angular/common';
import { Project } from '../../../interfaces/project.interface';
import { Task } from '../../../interfaces/task.interface';
import { TaskService } from '../../../services/task.service';
import { TaskCreateComponent } from '../task-create/task-create.component';
import { NavbarComponent } from '../../shared/navbar/navbar.component';
import { ProjectUserExtendedReference } from '../../../interfaces/user.interface';

@Component({
  selector: 'app-project-details',
  imports: [CommonModule, TaskCreateComponent, NavbarComponent],
  templateUrl: './project-details.html',
  styleUrls: ['./project-details.css'],
})
export class ProjectDetails implements OnInit{

  private projectService = inject(ProjectService);
  private taskService = inject(TaskService);
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  protected project = signal<Project|undefined>(undefined);
  protected tasks = signal<Task[]>([]);
  protected showTaskCreate = signal<boolean>(false);

  ngOnInit() {
    const projectId = this.route.snapshot.paramMap.get('id');
    if (projectId) {
      this.projectService.getProjectById(projectId).subscribe({
        next: (proj) => {
          console.log('Project detailsundefined fetched successfully:', proj);
          this.project.set(proj);
        },
        error: (error) => {
          console.error('Error fetching project details:', error);
        }
      });
      // Fetch tasks for the project
      this.taskService.getTasksByProjectId(projectId).subscribe({
        next: (tasks) => {
          console.log('Tasks fetched successfully:', tasks);
          this.tasks.set(tasks);
        },
        error: (error) => {
          console.error('Error fetching tasks:', error);
        }
      });
    }
  }
  goToTaskDetails(taskId: string) {
    const projectId = this.project()?._id;
    if (projectId) {
      this.router.navigate(['/projects', projectId, 'tasks', taskId]);
    }
  }
  goToProjectSettings() {
    const projectId = this.project()?._id;
    if (projectId) {
      this.router.navigate(['/projects', projectId, 'settings']);
    }
  }
  toggleTaskCreate() {
    this.showTaskCreate.set(!this.showTaskCreate());
  }
  createTask(taskFormOutput: { title: string; priority: string; deadline: Date; description: string; }) {
    if(this.project()?._id){
    const projectId:string = this.project()?._id||"";
    
    this.taskService.createTask(projectId, taskFormOutput).subscribe({
      next: (task) => {
        console.log('Task created successfully:', task);
        // Fetch tasks for the project
        this.taskService.getTasksByProjectId(projectId).subscribe({
          next: (tasks) => {
            console.log('Tasks fetched successfully:', tasks);
            this.tasks.set(tasks);
          },
          error: (error) => {
            console.error('Error fetching tasks:', error);
          }
        });
        this.toggleTaskCreate();
      },
      error: (error) => {
        console.error('Error creating task:', error);
      }
    });
    }
  }
  isProjectManager(): boolean {
    const userEmail = localStorage.getItem("userEmail");
    const projectMembers: ProjectUserExtendedReference[] = this.project()?.members || [];
    return projectMembers.some(member => member.email === userEmail && member.role === 'manager');
  }
}
