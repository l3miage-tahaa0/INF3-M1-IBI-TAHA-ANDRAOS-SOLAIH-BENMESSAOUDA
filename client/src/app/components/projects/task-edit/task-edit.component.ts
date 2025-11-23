import { Component, Input, Output, EventEmitter, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Project } from '../../../interfaces/project.interface';
import { Task } from '../../../interfaces/task.interface';
import { UserExtendedReference } from '../../../interfaces/user.interface';
import { TeamDropdownComponent } from '../team-dropdown/team-dropdown.component';

@Component({
  selector: 'app-task-edit',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, TeamDropdownComponent],
  templateUrl: './task-edit.component.html',
  styleUrls: ['./task-edit.component.css']
})
export class TaskEditComponent implements OnChanges {
  @Input() project: Project | undefined;
  @Input() task: Task | undefined;

  @Output() update = new EventEmitter<Partial<Task>>();
  @Output() cancel = new EventEmitter<void>();

  form: FormGroup;

  constructor(private fb: FormBuilder) {
    this.form = this.fb.group({
      title: ['', [Validators.required, Validators.minLength(3)]],
      priority: ['Medium', Validators.required],
      deadline: [''],
      description: ['', Validators.maxLength(2000)],
      assignee: [null]
    });
  }

  ngOnChanges(changes: SimpleChanges) {
    if (changes['task'] && this.task) {
      // deadline in Task is a Date object; convert to yyyy-MM-dd for the date input
      let deadlineStr = '';
      if (this.task.deadline) {
        const d = new Date(this.task.deadline);
        const yyyy = d.getFullYear();
        const mm = String(d.getMonth() + 1).padStart(2, '0');
        const dd = String(d.getDate()).padStart(2, '0');
        deadlineStr = `${yyyy}-${mm}-${dd}`;
      }

      this.form.patchValue({
        title: this.task.title ?? '',
        priority: this.task.priority ?? 'Medium',
        deadline: deadlineStr,
        description: this.task.description ?? '',
        assignee: this.task.assigned_to ?? null
      });
    }
  }

  onAssigneeSelected(user: UserExtendedReference | null) {
    this.form.get('assignee')?.setValue(user ?? null);
  }

  save() {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    // build payload matching Task interface keys
    const rawDeadline = this.form.value.deadline;
    const payload: Partial<Task> = {
      title: this.form.value.title,
      priority: this.form.value.priority,
      // convert date string back to a Date (or null)
      deadline: rawDeadline ? new Date(rawDeadline) : (null as any),
      description: this.form.value.description,
      assigned_to: this.form.value.assignee || null
    };
    this.update.emit(payload);
  }

  onCancel() {
    this.cancel.emit();
  }
}
