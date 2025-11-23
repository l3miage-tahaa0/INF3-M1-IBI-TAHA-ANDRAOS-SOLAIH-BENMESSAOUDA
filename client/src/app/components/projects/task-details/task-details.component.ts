import { CommonModule } from '@angular/common';
import { Component, inject, OnInit, signal } from '@angular/core';
import { ReactiveFormsModule, FormControl } from '@angular/forms';
import { TaskService } from '../../../services/task.service';
import { TaskEditComponent } from '../task-edit/task-edit.component';
import { Task } from '../../../interfaces/task.interface';
import { ActivatedRoute, Router } from '@angular/router';
import { ProjectService } from '../../../services/project.service';
import { Project } from '../../../interfaces/project.interface';
import { NavbarComponent } from '../../shared/navbar/navbar.component';

@Component({
  selector: 'app-task-details',
  imports: [CommonModule, ReactiveFormsModule, TaskEditComponent, NavbarComponent],
  templateUrl: './task-details.component.html',
  styleUrls: ['./task-details.component.css'],
})
export class TaskDetailsComponent implements OnInit {
  private taskService = inject(TaskService);
  private projectService = inject(ProjectService);
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  protected project = signal<Project | undefined>(undefined);
  protected task = signal<Task | undefined>(undefined);
  protected editing = signal(false);
  stateControl = new FormControl('');

  ngOnInit(): void {
    this.route.params.subscribe(params => {
      const projectId = params['id'];
      const taskId = params['taskId'];
      if (projectId && taskId) {
        this.projectService.getProjectById(projectId).subscribe({
          next: (p) => this.project.set(p),
          error: (err) => console.error('Failed to load project', err)
        });
        this.taskService.getTaskById(projectId, taskId).subscribe({
          next: (t) => { this.task.set(t); this.stateControl.setValue(t.state || 'Not Started'); },
          error: (err) => {
            console.error('Failed to load task', err);
          }
        });
      }
    });
  }

  changeState(newState: string) {
    const projectId = this.route.snapshot.params['projectId'] || this.route.snapshot.params['id'];
    const taskId = this.route.snapshot.params['taskId'];
    if (!projectId || !taskId) return;
    this.taskService.updateTask(projectId, taskId, { state: newState }).subscribe({
      next: (updated) => this.task.set(updated),
      error: (err) => console.error('Failed to update state', err)
    });
  }

  startEdit() {
    this.editing.set(true);
  }

  onDeleteClick() {
    const confirmed = confirm('Delete this task? This action cannot be undone.');
    if (!confirmed) return;
    const projectId = this.route.snapshot.params['projectId'] || this.route.snapshot.params['id'];
    const taskId = this.route.snapshot.params['taskId'];
    if (!projectId || !taskId) return;
    this.taskService.deleteTask(projectId, taskId).subscribe({
      next: () => {
        // navigate back to project page
        this.router.navigate(['/projects', projectId]);
      },
      error: (err) => console.error('Failed to delete task', err)
    });
  }

  onUpdate(payload: Partial<Task>) {
    const projectId = this.route.snapshot.params['projectId'] || this.route.snapshot.params['id'];
    const taskId = this.route.snapshot.params['taskId'];
    console.log('Updating task with payload', payload);
    if (!projectId || !taskId) return;
    this.taskService.updateTask(projectId, taskId, payload).subscribe({
      next: (updated) => {
        this.task.set(updated);
        this.editing.set(false);
      },
      error: (err) => console.error('Failed to update task', err)
    });
  }

  onCancelEdit() {
    this.editing.set(false);
  }

  back() {
    const p = this.route.snapshot.params['projectId'] || this.route.snapshot.params['id'];
    if (p) this.router.navigate(['/projects', p]);
    else this.router.navigate(['/projects']);
  }
  edit() {
    const projectId = this.route.snapshot.params['projectId'] || this.route.snapshot.params['id'];
    const taskId = this.route.snapshot.params['taskId'];
    if (projectId && taskId) {
      this.router.navigate(['/projects', projectId, 'tasks', taskId, 'edit']);
    }
  }
}
