import { CommonModule } from '@angular/common';
import { AfterViewInit, Component, inject, OnChanges, OnDestroy, OnInit, signal, SimpleChanges, ViewChild } from '@angular/core';
import { ReactiveFormsModule, FormControl } from '@angular/forms';
import { ProjectService } from '../../../services/project.service';
import { Project } from '../../../interfaces/project.interface';
import { ActivatedRoute, Router } from '@angular/router';
import { NavbarComponent } from '../../shared/navbar/navbar.component';
import { NgxChartsModule } from '@swimlane/ngx-charts';

@Component({
  selector: 'app-project-settings',
  imports: [CommonModule, ReactiveFormsModule, NavbarComponent, NgxChartsModule, CommonModule],
  templateUrl: './project-settings.component.html',
  styleUrls: ['./project-settings.component.css'],
})
export class ProjectSettings implements OnInit, OnChanges, AfterViewInit{
  private projectService = inject(ProjectService);
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  protected project = signal<Project|undefined>(undefined);
  
  pieChartData: { name: string; value: number }[] = [];
  pieChartView: [number, number] = [700, 400];
  pieChartLegend = true;
  pieChartLabels = true;
  pieChartLegendPosition: 'right' | 'below' = 'below';

  protected addMemberError = signal<string>('');
  protected addManagerError = signal<string>('');
  protected topProductiveMembers = signal<{ first_name: string; tasks_completed: number }[]>([]);
  protected taskCount = signal<number>(0);
  protected taskPriorityStateDistribution = signal<{_id: {state: string, priority: string}, number_task: number}[]>([]);
  protected tasksStateDistribution = signal<{state: string, nb_of_tasks: number, percentage: number}[]>([]);
  
  open = { details: false, members: false, managers: false };
  memberEmailControl = new FormControl('');
  managerEmailControl = new FormControl('');

  ngOnInit(): void {
    this.route.params.subscribe(params => {
      const projectId = params['id'];
      if (projectId) {
        this.projectService.getProjectById(projectId).subscribe(project => {
          this.project.set(project);
        });
        this.projectService.getUserProductivity(projectId).subscribe(members => {
          this.topProductiveMembers.set(members);
        });
        this.projectService.getTaskCountByProjectId(projectId).subscribe(count => {
          this.taskCount.set(count[0].total_tasks);
        });
        this.projectService.getTasksByStatePriority(projectId).subscribe(data => {
          this.taskPriorityStateDistribution.set(data);
        });
        this.projectService.getTaskStateDistribution(projectId).subscribe(data => {
          this.tasksStateDistribution.set(data);
          this.updateStateChart();
        });
      }
    });
  }

    ngAfterViewInit(): void {
    this.updateStateChart();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['project']) {
      this.updateStateChart();
    }
  }

  private updateStateChart(): void {
    const data = this.tasksStateDistribution() ?? [];
    this.pieChartData = data.map(d => ({ name: d.state, value: d.nb_of_tasks }));
  }


  toggle(section: 'details'|'members'|'managers') {
    this.open[section] = !this.open[section];
  }
  private refreshProject(projectId: string) {
    this.projectService.getProjectById(projectId).subscribe(p => this.project.set(p));
    this.addMemberError.set('');
    this.addManagerError.set('');
  }
  addMemberByEmail() {
    const projectId = this.project()?._id;
    const email = this.memberEmailControl.value as string | null;
    if (!projectId || !email) return;
    this.projectService.addMemberToProject(projectId, email).subscribe({
      next: () => { this.memberEmailControl.setValue(''); this.refreshProject(projectId); },
      error: (err) => err.status === 404
        ? this.addMemberError.set('No user found with this email.')
        : this.addMemberError.set('User already in project.')
    });
  }
  removeMember(memberEmail: string) {
    const projectId = this.project()?._id;
    if (!projectId) return;
    this.projectService.removeMemberFromProject(projectId, memberEmail).subscribe({
      next: () => this.refreshProject(projectId),
      error: (err) => console.error('remove member error', err)
    });
  }
  addManagerByEmail() {
    const projectId = this.project()?._id;
    const email = this.managerEmailControl.value as string | null;
    if (!projectId || !email) return;
    this.projectService.promoteMemberToManager(projectId, email).subscribe({
      next: () => { this.managerEmailControl.setValue(''); this.refreshProject(projectId); },
      error: (err) => err.status === 404
        ? this.addManagerError.set('No user found with this email.')
        : this.addManagerError.set('User already is a manager in project.')
    });
  }
  removeManager(managerEmail: string) {
    const projectId = this.project()?._id;
    if (!projectId) return;
    this.projectService.demoteManagerToMember(projectId, managerEmail).subscribe({
      next: () => this.refreshProject(projectId),
      error: (err) => console.error('remove manager error', err)
    });
  }
  deleteProject() {
    const projectId = this.project()?._id;
    if (projectId) {
      this.projectService.deleteProject(projectId).subscribe({
        next: () => {
          console.log('Project deleted successfully');
          this.router.navigate(['/projects']);
        },
        error: (error) => {
          console.error('Error deleting project:', error);
        }
      });
    }
  }
} 
