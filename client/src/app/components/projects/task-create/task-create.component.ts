import { CommonModule } from '@angular/common';
import { Component, output } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { UserExtendedReference } from '../../../interfaces/user.interface';

export interface TaskFormOutput {
  title: string;
  priority: string;
  deadline: Date;
  description: string;
}

@Component({
  selector: 'app-task-create',
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule],
  templateUrl: './task-create.component.html',
  styleUrls: ['./task-create.component.css'],
})
export class TaskCreateComponent {
  form: FormGroup;
  taskFormOutput = output<TaskFormOutput>();
  cancelOutput = output<void>();
  constructor(private fb: FormBuilder) {
    this.form = this.fb.group({
      title: ['', [Validators.required, Validators.minLength(3)]],
      priority: ['Medium', Validators.required],
      deadline: [''],
      description: ['', Validators.maxLength(2000)],
    });
  }

  // minDate for date input (today in yyyy-MM-dd)
  get minDate(): string {
    const d = new Date();
    const yyyy = d.getFullYear();
    const mm = String(d.getMonth() + 1).padStart(2, '0');
    const dd = String(d.getDate()).padStart(2, '0');
    return `${yyyy}-${mm}-${dd}`;
  }

  create() {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const payload = this.form.value;
    console.log('Creating task', payload);
    // TODO: call service to create the task
    this.taskFormOutput.emit(payload);
  }
  cancel() {
    this.cancelOutput.emit();
  }
}