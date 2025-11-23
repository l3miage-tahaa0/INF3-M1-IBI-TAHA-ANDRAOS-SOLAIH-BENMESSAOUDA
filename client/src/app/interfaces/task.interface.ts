import { ProjectExtendedReference } from "./project.interface";
import { UserExtendedReference } from "./user.interface";

export interface Task {
    _id: string;
    title: string;
    description: string;
    state: string;
    priority: string;
    deadline: Date;
    project: ProjectExtendedReference;
    assigned_to: UserExtendedReference | null;
    created_at: Date;
    updated_at: Date;
}