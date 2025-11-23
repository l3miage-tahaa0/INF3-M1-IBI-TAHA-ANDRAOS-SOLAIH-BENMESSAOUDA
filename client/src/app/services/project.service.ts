import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Project } from '../interfaces/project.interface';
import { environment } from '../../environments/environment';
@Injectable({
  providedIn: 'root'
})
export class ProjectService {
  private apiUrl = environment.apiUrl + 'projects';
  private http = inject(HttpClient);
  getProjects() {
    // Implementation for fetching projects from the backend API
    return this.http.get<Project[]>(this.apiUrl);
  }
  createProject(projectData: { title: string; description: string }) {
    // Implementation for creating a new project via the backend API
    return this.http.post<Project>(this.apiUrl, projectData);
  }
  getProjectById(projectId: string) {
    return this.http.get<Project>(`${this.apiUrl}/${projectId}`);
  }
  deleteProject(projectId: string) {
    return this.http.delete<void>(`${this.apiUrl}/${projectId}`);
  }
  addMemberToProject(projectId: string, memberId: string) {
    return this.http.post<void>(`${this.apiUrl}/${projectId}/members/${memberId}`, {});
  }
  removeMemberFromProject(projectId: string, memberId: string) {
    return this.http.delete<void>(`${this.apiUrl}/${projectId}/members/${memberId}`);
  }
  promoteMemberToManager(projectId: string, memberId: string) {
    return this.http.post<void>(`${this.apiUrl}/${projectId}/managers/${memberId}`, {});
  }
  demoteManagerToMember(projectId: string, memberId: string) {
    return this.http.delete<void>(`${this.apiUrl}/${projectId}/managers/${memberId}`);
  }
}