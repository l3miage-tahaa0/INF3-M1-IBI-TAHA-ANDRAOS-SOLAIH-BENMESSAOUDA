import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Task } from '../interfaces/task.interface';
@Injectable({
  providedIn: 'root'
})
export class TaskService {
  private apiUrl = 'http://localhost:8000/projects';
  private http = inject(HttpClient);
  getTasksByProjectId(projectId: string) {
    // Implementation for fetching tasks by project ID from the backend API
    return this.http.get<Task[]>(`${this.apiUrl}/${projectId}/tasks`);
  }
  createTask(projectId: string, task: Partial<Task>) {
    return this.http.post<Task>(`${this.apiUrl}/${projectId}/tasks`, task);
  }
  getTaskById(projectId: string, taskId: string) {
    return this.http.get<Task>(`${this.apiUrl}/${projectId}/tasks/${taskId}`);
  }
  deleteTask(projectId: string, taskId: string) {
    return this.http.delete<void>(`${this.apiUrl}/${projectId}/tasks/${taskId}`);
  }
  updateTask(projectId: string, taskId: string, patch: Partial<Task>) {
    return this.http.patch<Task>(`${this.apiUrl}/${projectId}/tasks/${taskId}`, patch);
  }
}