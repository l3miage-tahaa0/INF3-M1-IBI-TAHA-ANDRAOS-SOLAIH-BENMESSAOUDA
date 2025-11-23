import { Routes } from '@angular/router';
import { Login } from './components/login/login';
import { Signup } from './components/signup/signup';
import { Home } from './components/home/home';
import { AuthGuard } from './guards/auth.guard';
import { ProjectsComponent } from './components/projects/projects.component';
import { ProjectCreate } from './components/projects/project-create/project-create';
import { ProjectDetails } from './components/projects/project-details/project-details';
import { TaskCreateComponent } from './components/projects/task-create/task-create.component';
import { ProjectSettings } from './components/projects/project-settings/project-settings.component';
import { TaskDetailsComponent } from './components/projects/task-details/task-details.component';
import { ProfileComponent } from './components/profile/profile.component';
export const routes: Routes = [
    { path: 'login', component: Login },
    { path: 'signup', component: Signup },
    { path: 'home', component: Home, canActivate: [AuthGuard] },
    { path: 'profile', component: ProfileComponent, canActivate: [AuthGuard] },
    { path: 'projects', component: ProjectsComponent, canActivate: [AuthGuard] },
    { path: 'projects/create', component: ProjectCreate, canActivate: [AuthGuard] },
    { path: 'projects/:id', component: ProjectDetails, canActivate: [AuthGuard] },
    { path: 'projects/:id/settings', component: ProjectSettings, canActivate: [AuthGuard] },
    { path: 'projects/:id/tasks/create', component: TaskCreateComponent, canActivate: [AuthGuard] },
    { path: 'projects/:id/tasks/:taskId', component: TaskDetailsComponent, canActivate: [AuthGuard] },
    { path: '', redirectTo: '/projects', pathMatch: 'full' },
    { path: '**', redirectTo: '/projects' }
];
