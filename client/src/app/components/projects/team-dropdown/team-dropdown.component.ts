import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormControl } from '@angular/forms';
import { Project } from '../../../interfaces/project.interface';
import { ProjectUserExtendedReference, TaskUserExtendedReference } from '../../../interfaces/user.interface';
@Component({
  selector: 'app-team-dropdown',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './team-dropdown.component.html',
  styleUrls: ['./team-dropdown.component.css'],
})
export class TeamDropdownComponent {
  @Input() project: Project | undefined;
  @Output() selection = new EventEmitter<TaskUserExtendedReference | null>();

  control = new FormControl('');

  onChange() {
    const val = this.control.value;
    if (!val) { this.selection.emit(null); return; }
    // value will be the JSON-stringified user reference
    try {
      const user: TaskUserExtendedReference = JSON.parse(val);
      delete (user as {role?: string}).role;
      this.selection.emit(user);
    } catch {
      this.selection.emit(null);
    }
  }
}
