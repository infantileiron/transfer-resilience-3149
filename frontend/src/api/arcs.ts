import {request,post} from './client';import type {Arc} from '../types/domain';
export const list=()=>request<Arc[]>('/arcs');
export const create=(data:unknown)=>post<Arc>('/arcs',data);
