import { ProjectUserExtendedReference } from "./user.interface";

export interface Project{
    _id: string;
    title: string;
    description: string;
    members: ProjectUserExtendedReference[];
    created_at: Date;
}
export interface ProjectExtendedReference {
    id: string;
    project_title: string;
}