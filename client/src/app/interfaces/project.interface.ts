import { UserExtendedReference } from "./user.interface";

export interface Project{
    _id: string;
    title: string;
    description: string;
    managers: UserExtendedReference[];
    members: UserExtendedReference[];
    created_at: Date;
}
export interface ProjectExtendedReference {
    id: string;
    project_title: string;
}