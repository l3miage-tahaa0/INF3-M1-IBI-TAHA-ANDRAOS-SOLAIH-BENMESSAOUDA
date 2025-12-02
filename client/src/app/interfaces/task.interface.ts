import { ProjectExtendedReference } from "./project.interface";
import { TaskUserExtendedReference } from "./user.interface";

export interface Task {
    _id: string;
    title: string;
    description: string;
    state: string;
    priority: string;
    deadline: Date;
    project: ProjectExtendedReference;
    assigned_to: TaskUserExtendedReference | null;
    created_at: Date;
    updated_at: Date;
}