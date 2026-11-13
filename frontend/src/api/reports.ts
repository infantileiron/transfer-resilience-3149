import {request,post} from './client';import type {Report} from '../types/domain';
export const list=()=>request<Report[]>('/reports');
export const create=(data:unknown)=>post<Report>('/reports',data);
export const versions=(runId:string)=>request<{run_id:string;versions:Report[]}>(`/reports/runs/${runId}/versions`);
export const versionsOf=(id:string)=>request<{run_id:string;versions:Report[]}>(`/reports/${id}/versions`);
