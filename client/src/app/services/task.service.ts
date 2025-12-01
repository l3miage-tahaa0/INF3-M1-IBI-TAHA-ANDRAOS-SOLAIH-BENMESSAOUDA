import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Task } from '../interfaces/task.interface';
import { environment } from '../../environments/environment';
@Injectable({
  providedIn: 'root'
})
export class TaskService {
  private apiUrl = environment.apiUrl + 'projects';
  private http = inject(HttpClient);
  getTasksByProjectId(projectId: string) {
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